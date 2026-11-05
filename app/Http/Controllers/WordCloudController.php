<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Http;

class WordCloudController extends Controller
{
    private function getAndFixApiData()
    {
        // inisialisasi default agar selalu punya struktur yang konsisten
        $result = [
            'medsos' => ['positif' => [], 'netral' => [], 'negatif' => []],
            'berita' => ['positif' => [], 'netral' => [], 'negatif' => []],
        ];

        // --- Ambil API medsos (sentiment) ---
        $respMedsos = @file_get_contents("http://127.0.0.1:5000/api/sentiment");
        if ($respMedsos !== false) {
            $fixed = str_replace("'", "\"", $respMedsos);
            $json = json_decode($fixed, true);
            if (is_array($json) && isset($json['data']) && is_array($json['data'])) {
                // pastikan setiap key positif/netral/negatif ada
                foreach (['positif','netral','negatif'] as $k) {
                    $result['medsos'][$k] = is_array($json['data'][$k] ?? null) ? $json['data'][$k] : [];
                }
            }
        }

        // --- Ambil API berita ---
        $respBerita = @file_get_contents("http://127.0.0.1:5000/api/berita");
        if ($respBerita !== false) {
            $fixed = str_replace("'", "\"", $respBerita);
            $json = json_decode($fixed, true);
            // API berita beberapa kemungkinan: { "data": { "positif": [...], ... } } atau langsung { "positif": [...] }
            $beritaData = [];
            if (is_array($json)) {
                if (isset($json['data']) && is_array($json['data'])) {
                    $beritaData = $json['data'];
                } else {
                    // mungkin API langsung mengembalikan object dengan keys positif/netral/negatif
                    $beritaData = $json;
                }
            }
            foreach (['positif','netral','negatif'] as $k) {
                $result['berita'][$k] = is_array($beritaData[$k] ?? null) ? $beritaData[$k] : [];
            }
        }

        return $result;
    }

    public function index()
    {
        // [BARU] Ambil data lengkap dari sumber (yang memiliki keyword dan count)
        // Pastikan method getAndFixApiData() sudah ada di controller Anda
        $apiData = $this->getAndFixApiData();

        // Baca konfigurasi yang disimpan (daftar keyword yang dipilih)
        $path = public_path("storage/wordcloud_config.json");
        $savedConfig = file_exists($path) ? json_decode(file_get_contents($path), true) : [];

        $wordcloudData = [];

        foreach (['medsos', 'berita'] as $source) {
            foreach (['positif', 'netral', 'negatif'] as $sentiment) {
                // Ambil daftar keyword yang dipilih untuk kategori ini
                $selectedKeywords = $savedConfig[$source][$sentiment] ?? [];

                if (empty($selectedKeywords)) {
                    $wordcloudData[$source][$sentiment] = [];
                    continue; // Lanjut ke iterasi berikutnya jika tidak ada keyword yang dipilih
                }

                // Ambil data lengkap untuk kategori ini
                $fullDataForCategory = collect($apiData[$source][$sentiment] ?? []);

                // [LOGIKA UTAMA] Filter data lengkap berdasarkan keyword yang dipilih
                $filteredData = $fullDataForCategory->filter(function ($item) use ($selectedKeywords) {
                    return isset($item['keyword']) && in_array($item['keyword'], $selectedKeywords);
                });

                // Ubah format data menjadi 'text' dan 'weight' (dari 'count' asli)
                $wordcloudData[$source][$sentiment] = $filteredData->map(function ($item) {
                    return [
                        "text" => $item['keyword'],
                        "weight" => (int)($item['count'] ?? 1) // Ambil count asli
                    ];
                })->values()->all();
            }
        }

        return view("admin.wordcloud.index", [
            "wordcloudData" => $wordcloudData
        ]);
    }

    public function getDetail($source, $sentiment, $keyword)
    {
        // normalisasi input
        $source = mb_strtolower($source);
        $sentiment = mb_strtolower($sentiment);
        $keyword = mb_strtolower($keyword);

        // ambil data terstruktur dari helper
        $apiData = $this->getAndFixApiData();

        // validasi source/sentiment ada
        if (!in_array($source, ['medsos','berita'])) {
            abort(404, 'Source tidak valid');
        }
        if (!in_array($sentiment, ['positif','netral','negatif'])) {
            abort(404, 'Sentiment tidak valid');
        }

        // ambil daftar items hanya untuk source+sentiment
        $items = $apiData[$source][$sentiment] ?? [];

        // cari hanya yang keyword sama (case-insensitive)
        $filtered = collect($items)->filter(function ($item) use ($keyword) {
            return is_array($item)
                && isset($item['keyword'])
                && mb_strtolower($item['keyword']) === $keyword;
        });

        // kembangkan summary sesuai sumber
        if ($source === 'medsos') {
            // medsos → caption, comment, link
            $expanded = $filtered->flatMap(function ($item) {
                if (!empty($item['summary']) && is_array($item['summary'])) {
                    return collect($item['summary'])->map(function ($s) use ($item) {
                        return (object)[
                            'keyword' => $item['keyword'],
                            'count'   => $item['count'] ?? 0,
                            'caption' => $s['caption'] ?? '-',
                            'comment' => $s['comment'] ?? '-',
                            'link'    => $s['link'] ?? null,
                        ];
                    });
                }
                return collect();
            });
        } else {
            // berita → judul, tag, isi_berita, link
            $expanded = $filtered->flatMap(function ($item) {
                if (!empty($item['summary']) && is_array($item['summary'])) {
                    return collect($item['summary'])->map(function ($s) use ($item) {
                        return (object)[
                            'keyword'    => $item['keyword'],
                            'count'      => $item['count'] ?? 0,
                            'judul'      => $s['judul'] ?? '-',
                            'tag'        => $s['tag'] ?? '-',
                            'isi_berita' => $s['isi_berita'] ?? '-',
                            'link'       => $s['link'] ?? null,
                        ];
                    });
                }
                return collect();
            });
        }

        // kirim source & sentiment ke blade juga (blade sudah diperbarui sesuai permintaan)
        return view('admin.wordcloud.detail', [
            'keyword' => $keyword,
            'source'  => $source,
            'sentiment' => $sentiment,
            'data'    => $expanded,
        ]);
    }

    public function config()
    {
        // === API Medsos ===
        $responseMedsos = @file_get_contents("http://127.0.0.1:5000/api/sentiment");
        $validJsonMedsos = str_replace("'", "\"", $responseMedsos);
        $jsonMedsos = json_decode($validJsonMedsos, true);
        $dataMedsos = $jsonMedsos['data'] ?? [];

        foreach (['positif','netral','negatif'] as $key) {
            if (!isset($dataMedsos[$key]) || !is_array($dataMedsos[$key])) {
                $dataMedsos[$key] = [];
            } else {
                $dataMedsos[$key] = array_filter($dataMedsos[$key], fn($item) => isset($item['count']) && $item['count'] >= 10);
                usort($dataMedsos[$key], fn($a,$b) => $b['count'] <=> $a['count']);
            }
        }

        // === API Berita ===
        $responseBerita = @file_get_contents("http://127.0.0.1:5000/api/berita");
        $validJsonBerita = str_replace("'", "\"", $responseBerita);
        $jsonBerita = json_decode($validJsonBerita, true);
        $dataBerita = $jsonBerita['data'] ?? [];   // ✅ ambil hanya bagian data

        foreach (['positif','netral','negatif'] as $key) {
            if (!isset($dataBerita[$key]) || !is_array($dataBerita[$key])) {
                $dataBerita[$key] = [];
            } else {
                $dataBerita[$key] = array_filter($dataBerita[$key], fn($item) => isset($item['count']) && $item['count'] >= 10);
                usort($dataBerita[$key], fn($a,$b) => $b['count'] <=> $a['count']);
            }
        }

        // === Final data untuk Blade ===
        $data = [
            'medsos' => $dataMedsos,
            'berita' => $dataBerita,
        ];

        $savedConfig = [];
        if (Storage::disk('public')->exists("wordcloud_config.json")) {
            $savedConfig = json_decode(Storage::disk('public')->get("wordcloud_config.json"), true);
        }

        return view('admin.wordcloud.config', compact('data', 'savedConfig'));
    }

    public function saveConfig(Request $request)
    {
        $configData = [
            'medsos' => $request->input('keywords_medsos', []),
            'berita' => $request->input('keywords_berita', []),
        ];

        // simpan ke storage/app/public/wordcloud_config.json
        Storage::disk('public')->put("wordcloud_config.json", json_encode($configData, JSON_PRETTY_PRINT));

        // cek apakah tersimpan
        if (Storage::disk('public')->exists("wordcloud_config.json")) {
            session()->flash('success', '✅ Konfigurasi berhasil disimpan');
        } else {
            session()->flash('error', '❌ Gagal menyimpan konfigurasi');
        }

        // langsung kembali ke halaman config (bukan index)
        return redirect()->route('wordcloud.config');
    }
}
