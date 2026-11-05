# Sentiment Analysis

Dashboard sentimen berita dan media sosial menggunakan Laravel 12 dan API Flask. Fitur mencakup autentikasi Laravel Breeze, profil pengguna, word cloud berdasarkan sumber dan kategori sentimen, detail kata kunci, serta konfigurasi word cloud.

Proyek menyajikan hasil analisis yang sudah tersedia. Pipeline pelatihan model belum tersedia dalam kode yang diperiksa.

## Struktur proyek

```text
app/, routes/, config/    Kode dan konfigurasi Laravel
bootstrap/, database/     Bootstrap, migration, factory, dan seeder
resources/, public/       Tampilan dan aset frontend
storage/, tests/          Penyimpanan runtime dan pengujian
services/sentiment_api/   API Flask dan requirements.txt
scripts/scraping/         Scraper Facebook, Instagram, TikTok
data/raw/                Hasil scraping lokal (tidak masuk Git)
data/processed/          Hasil analisis lokal (tidak masuk Git)
private/                  Cookie dan cadangan kredensial lokal (tidak masuk Git)
```

Konfigurasi Laravel, Composer, npm, Vite, dan Tailwind tetap di root agar perintah standar proyek bekerja.

## Instalasi Laravel

Kebutuhan: PHP 8.2+, Composer, Node.js yang kompatibel dengan Vite 7, npm, serta Python 3 untuk API.

```powershell
git clone https://github.com/Darakbolot/Sentiment-Analysis.git
cd Sentiment-Analysis
composer install
npm ci
Copy-Item .env.example .env
php artisan key:generate
```

Atur database pada `.env`. Untuk SQLite, buat `database/database.sqlite` jika belum ada, lalu jalankan:

```powershell
php artisan migrate
php artisan storage:link
npm run build
php artisan serve
```

Daftar di `http://127.0.0.1:8000/register`, lalu buka `http://127.0.0.1:8000/admin/wordcloud`. Untuk pengembangan frontend jalankan `npm run dev` pada terminal terpisah.

## API Flask

Jalankan dari root proyek. API membaca dataset menggunakan jalur absolut relatif terhadap lokasi kode:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r services/sentiment_api/requirements.txt
.\.venv\Scripts\python services/sentiment_api/api.py
```

Siapkan `berita_analysis_result.json` dan `sentiment_analysis_result.json` di `data/processed/`. Dataset tidak disertakan dalam Git; gunakan salinan data lokal proyek.

| Endpoint | Data |
| --- | --- |
| `GET http://127.0.0.1:5000/api/berita` | Analisis berita |
| `GET http://127.0.0.1:5000/api/sentiment` | Analisis media sosial |

Respons sukses berisi `status` dan `data`. File hilang atau JSON tidak valid menghasilkan HTTP 500. Laravel memakai API lokal port 5000; jalankan kedua server bersamaan. API menggunakan mode debug untuk pengembangan lokal.

## Scraping opsional

Siapkan Google Chrome dan pasang dependensi:

```powershell
.\.venv\Scripts\python -m pip install -r scripts/scraping/requirements.txt
```

Skrip berada di `scripts/scraping/`: `facebook.py`, `ppa.py`, `ppp.py`, dan `tiktiktik.py`. Periksa target sebelum menjalankan. Output ditulis ke `data/raw/` dan cookie ke `private/cookies/`.

Kredensial dibaca dari variabel lingkungan: `FB_USERNAME`, `FB_PASSWORD`, `IG_USERNAME`, `IG_PASSWORD`, serta `IG_VERIFICATION` opsional. Isi pada terminal lokal sebelum menjalankan skrip terkait. Skrip tidak otomatis membaca file `.env` Laravel.

Contoh menjalankan scraper TikTok:

```powershell
.\.venv\Scripts\python scripts/scraping/tiktiktik.py
```

## Pemeriksaan aplikasi

```powershell
php artisan test
npm run build
```

## File lokal

`.env`, cookie, kredensial, database SQLite, dataset, hasil scraping, `vendor/`, dan `node_modules/` dikecualikan melalui `.gitignore`. File asli tetap disimpan lokal. Jangan memasukkannya dengan `git add -f`.
