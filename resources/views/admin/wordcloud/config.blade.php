@extends('layouts.admin')

@section('title', 'Konfigurasi Word Cloud')
@section('page_title', 'Konfigurasi Word Cloud')

@section('content')
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

<section class="w-full mx-auto">
    <form method="POST" action="{{ route('wordcloud.config.save') }}">
        @csrf

        <div class="flex flex-col gap-8">

            <div class="bg-sky-100 p-6 rounded-2xl shadow-lg">
                <h2 class="font-bold text-xl mb-6 text-center">Konfigurasi Word Cloud - Medsos</h2>
                <div class="swiper mySwiperMedsos">
                    <div class="swiper-wrapper pb-12">
                        @foreach(['positif', 'netral', 'negatif'] as $sentiment)
                            @php
                                $colorClasses = ['positif' => 'text-green-600', 'netral' => 'text-gray-600', 'negatif' => 'text-red-600'];
                            @endphp
                            <div class="swiper-slide bg-white rounded-2xl shadow-lg p-6 flex flex-col cursor-grab active:cursor-grabbing">
                                <div class="text-center mb-4">
                                    <h3 class="inline-block bg-sky-50 px-6 py-2 rounded-full font-bold text-lg {{ $colorClasses[$sentiment] }} shadow-sm">
                                        {{ ucfirst($sentiment) }}
                                    </h3>
                                </div>
                                <div class="overflow-y-auto max-h-96">
                                    <table class="w-full text-sm text-left">
                                        <thead class="bg-gray-100 sticky top-0">
                                            <tr>
                                                {{-- [BARU] Menambahkan checkbox untuk "Pilih Semua" --}}
                                                <th class="px-4 py-2 w-1/12 text-center">
                                                    <input type="checkbox" title="Pilih/Batal Pilih Semua"
                                                           class="select-all-checkbox rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500">
                                                </th>
                                                <th class="px-4 py-2">Keyword</th>
                                                <th class="px-4 py-2 w-2/12 text-center">Count</th>
                                                <th class="px-4 py-2 w-2/12 text-center">Detail</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-gray-200">
                                            @foreach($data['medsos'][$sentiment] ?? [] as $word)
                                                @if($word['count'] > 15)
                                                    @php
                                                        $keyword = $word['keyword'];
                                                        $isChecked = in_array($keyword, $savedConfig['medsos'][$sentiment] ?? []);
                                                    @endphp
                                                    <tr class="hover:bg-gray-50">
                                                        <td class="px-4 py-2 text-center">
                                                            <input type="checkbox" name="keywords_medsos[{{ $sentiment }}][]" value="{{ $keyword }}" @checked($isChecked)
                                                                   class="row-checkbox rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500">
                                                        </td>
                                                        <td class="px-4 py-2 font-semibold">{{ $keyword }}</td>
                                                        <td class="px-4 py-2 text-center">{{ $word['count'] }}</td>
                                                        <td class="px-4 py-2 text-center">
                                                            <a href="{{ route('wordcloud.detail', ['source' => 'medsos', 'sentiment' => $sentiment, 'keyword' => $keyword]) }}" target="_blank" class="text-indigo-600 hover:underline">Lihat</a>
                                                        </td>
                                                    </tr>
                                                @endif
                                            @endforeach
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        @endforeach
                    </div>
                    <div class="swiper-pagination"></div>
                </div>
            </div>

            <div class="bg-sky-100 p-6 rounded-2xl shadow-lg">
                <h2 class="font-bold text-xl mb-6 text-center">Konfigurasi Word Cloud - Berita</h2>
                <div class="swiper mySwiperBerita">
                    <div class="swiper-wrapper pb-12">
                        @foreach(['positif', 'netral', 'negatif'] as $sentiment)
                            @php
                                $colorClasses = ['positif' => 'text-green-600', 'netral' => 'text-gray-600', 'negatif' => 'text-red-600'];
                            @endphp
                            <div class="swiper-slide bg-white rounded-2xl shadow-lg p-6 flex flex-col cursor-grab active:cursor-grabbing">
                                <div class="text-center mb-4">
                                    <h3 class="inline-block bg-sky-50 px-6 py-2 rounded-full font-bold text-lg {{ $colorClasses[$sentiment] }} shadow-sm">
                                        {{ ucfirst($sentiment) }}
                                    </h3>
                                </div>
                                <div class="overflow-y-auto max-h-96">
                                    <table class="w-full text-sm text-left">
                                        <thead class="bg-gray-100 sticky top-0">
                                            <tr>
                                                {{-- [BARU] Menambahkan checkbox untuk "Pilih Semua" --}}
                                                <th class="px-4 py-2 w-1/12 text-center">
                                                    <input type="checkbox" title="Pilih/Batal Pilih Semua"
                                                           class="select-all-checkbox rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500">
                                                </th>
                                                <th class="px-4 py-2">Keyword</th>
                                                <th class="px-4 py-2 w-2/12 text-center">Count</th>
                                                <th class="px-4 py-2 w-2/12 text-center">Detail</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-gray-200">
                                            @foreach($data['berita'][$sentiment] ?? [] as $word)
                                                @if($word['count'] > 90)
                                                    @php
                                                        $keyword = $word['keyword'];
                                                        $isChecked = in_array($keyword, $savedConfig['berita'][$sentiment] ?? []);
                                                    @endphp
                                                    <tr class="hover:bg-gray-50">
                                                        <td class="px-4 py-2 text-center">
                                                            <input type="checkbox" name="keywords_berita[{{ $sentiment }}][]" value="{{ $keyword }}" @checked($isChecked)
                                                                   class="row-checkbox rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500">
                                                        </td>
                                                        <td class="px-4 py-2 font-semibold">{{ $keyword }}</td>
                                                        <td class="px-4 py-2 text-center">{{ $word['count'] }}</td>
                                                        <td class="px-4 py-2 text-center">
                                                            <a href="{{ route('wordcloud.detail', ['source' => 'berita', 'sentiment' => $sentiment, 'keyword' => $keyword]) }}" target="_blank" class="text-indigo-600 hover:underline">Lihat</a>
                                                        </td>
                                                    </tr>
                                                @endif
                                            @endforeach
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        @endforeach
                    </div>
                    <div class="swiper-pagination"></div>
                </div>
            </div>

            <div class="pt-6 text-center">
                <button type="submit" class="bg-blue-600 text-white font-bold px-8 py-3 rounded-full hover:bg-blue-700 shadow-lg transform hover:scale-105 transition-transform duration-300">
                    Simpan Konfigurasi
                </button>
            </div>
        </div>
    </form>
</section>
@endsection

@section('scripts')
<script>
document.addEventListener("DOMContentLoaded", function () {
    const swiperOptions = {
        effect: "cards",
        grabCursor: true,
        cardsEffect: { slideShadows: false },
        autoHeight: true,
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
            dynamicBullets: true,
        },
    };
    new Swiper(".mySwiperMedsos", { ...swiperOptions, pagination: { ...swiperOptions.pagination, el: ".mySwiperMedsos .swiper-pagination" } });
    new Swiper(".mySwiperBerita", { ...swiperOptions, pagination: { ...swiperOptions.pagination, el: ".mySwiperBerita .swiper-pagination" } });

    // --- [BARU] LOGIKA UNTUK FUNGSI "PILIH SEMUA" ---

    // Fungsi untuk memperbarui status master checkbox (centang, kosong, atau strip)
    function updateMasterCheckbox(table) {
        const masterCheckbox = table.querySelector('.select-all-checkbox');
        const rowCheckboxes = table.querySelectorAll('tbody .row-checkbox');

        if (!masterCheckbox || rowCheckboxes.length === 0) return;

        const totalRows = rowCheckboxes.length;
        const checkedRows = table.querySelectorAll('tbody .row-checkbox:checked').length;

        if (checkedRows === 0) {
            masterCheckbox.checked = false;
            masterCheckbox.indeterminate = false;
        } else if (checkedRows === totalRows) {
            masterCheckbox.checked = true;
            masterCheckbox.indeterminate = false;
        } else {
            masterCheckbox.checked = false;
            masterCheckbox.indeterminate = true; // Ini akan menampilkan tanda strip
        }
    }

    // Event listener untuk semua master checkbox di header
    document.querySelectorAll('.select-all-checkbox').forEach(master => {
        master.addEventListener('click', function() {
            const table = this.closest('table');
            const isChecked = this.checked;
            table.querySelectorAll('tbody .row-checkbox').forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateMasterCheckbox(table); // Perbarui status setelah diubah
        });
    });

    // Event listener untuk semua checkbox di setiap baris
    document.querySelectorAll('tbody .row-checkbox').forEach(checkbox => {
        checkbox.addEventListener('click', function() {
            const table = this.closest('table');
            updateMasterCheckbox(table);
        });
    });

    // Jalankan pengecekan awal saat halaman pertama kali dimuat
    document.querySelectorAll('table').forEach(table => {
        updateMasterCheckbox(table);
    });
});
</script>
@endsection
