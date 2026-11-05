from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
COOKIE_DIR = PROJECT_ROOT / "private" / "cookies"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COOKIE_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(OUTPUT_DIR)

import time
import pandas as pd
import json
import os

from datetime import datetime
from json import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# ==============================================================================
# KONFIGURASI SELENIUM
# ==============================================================================

def setup_driver():
    """Menyiapkan instance Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error saat memulai WebDriver: {e}")
        print("Pastikan chromedriver sudah diunduh dan berada di folder yang sama.")
        return None

# ==============================================================================
# FUNGSI COOKIES & CAPTCHA
# ==============================================================================

def save_cookies(driver, path):
    """Menyimpan cookies dari sesi browser ke file JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(driver.get_cookies(), f, indent=2)
    print(f"\nCookies berhasil disimpan ke {path}")

# [PERBAIKAN] Fungsi ini dibuat lebih tangguh terhadap file kosong/rusak
def load_cookies(driver, path):
    """Memuat cookies dari file JSON. Mengembalikan True jika berhasil, False jika gagal."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f"File cookies '{path}' tidak ditemukan atau kosong.")
        return False

    try:
        with open(path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        if not isinstance(cookies, list):
            print(f"Format data di '{path}' tidak valid (bukan list).")
            return False

        for cookie in cookies:
            driver.add_cookie(cookie)
        print(f"Cookies berhasil dimuat dari {path}")
        return True
    except JSONDecodeError:
        print(f"Gagal membaca '{path}' karena file rusak (JSONDecodeError).")
        return False
    except Exception as e:
        print(f"Terjadi error saat memuat cookies dari '{path}': {e}")
        return False

def establish_and_verify_session(driver, base_cookies_path, profile_cookies_path, profile_url):
    """
    Menangani alur CAPTCHA dengan membangun sesi dasar terlebih dahulu.
    """
    # --- TAHAP 1: MEMBANGUN SESI DASAR (HOMEPAGE) ---
    print("\n--- Tahap 1: Membangun Sesi Dasar di tiktok.com ---")
    driver.get("https://www.tiktok.com/")

    # [PERBAIKAN] Cek hasil dari load_cookies
    if not load_cookies(driver, base_cookies_path):
        print("\n" + "="*50)
        print("‼️ TINDAKAN AWAL DIPERLUKAN ‼️")
        input("File cookies dasar tidak valid/tidak ada. Selesaikan CAPTCHA di tiktok.com, lalu tekan [Enter]...")
        save_cookies(driver, base_cookies_path)

    driver.refresh()
    print("Sesi dasar telah dibuat/dimuat.")

    # --- TAHAP 2: VERIFIKASI SESI PROFIL ---
    print(f"\n--- Tahap 2: Verifikasi Sesi di Halaman Profil ---")
    driver.get(profile_url)

    # [PERBAIKAN] Cek hasil dari load_cookies
    if load_cookies(driver, profile_cookies_path):
        print("Mencoba memvalidasi sesi dengan cookies profil...")
        driver.refresh()
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a'))
            )
            print("✅ Sesi profil berhasil dipulihkan.")
            return True
        except TimeoutException:
            print("⚠️ Cookies profil tidak valid. Diperlukan verifikasi manual.")

    print("\n" + "="*50)
    print("‼️ VERIFIKASI SEBELUM SCRAPING ‼️")
    input("Halaman profil telah dimuat. Jika ada CAPTCHA, selesaikan sekarang. Tekan [Enter]...")
    save_cookies(driver, profile_cookies_path)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a'))
        )
        print("✅ Sesi profil berhasil dibuat/diperbarui.")
        return True
    except TimeoutException:
        print("❌ Gagal memverifikasi halaman profil.")
        return False

# ==============================================================================
# FUNGSI-FUNGSI BANTUAN SCRAPING (Tidak Berubah)
# ==============================================================================

def get_video_links(driver, max_videos):
    """
    Mengambil link video dari halaman profil dengan melakukan scroll
    hingga batas maksimal tercapai atau halaman paling bawah.
    """
    print(f"\n🔎 Mulai mengumpulkan link video (target: {max_videos} video)...")
    video_links = set()

    try:
        # 1. Tunggu hingga elemen video pertama kali muncul
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a'))
        )
        print("✅ Halaman profil berhasil dimuat.")

        # 2. Loop untuk scroll dan kumpulkan link
        while len(video_links) < max_videos:
            # Simpan jumlah link sebelum scroll untuk deteksi akhir halaman
            links_before_scroll = len(video_links)

            # Kumpulkan semua link yang ada di DOM saat ini
            video_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a')
            for elem in video_elements:
                href = elem.get_attribute('href')
                if href:
                    video_links.add(href)

            # Cek apakah target sudah tercapai setelah pengumpulan
            if len(video_links) >= max_videos:
                print(f"🎯 Target {max_videos} video tercapai ({len(video_links)} ditemukan). Berhenti scroll.")
                break

            # Lakukan scroll ke paling bawah halaman
            print(f"📜 Scrolling... Ditemukan {len(video_links)}/{max_videos} video.")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Beri waktu agar konten baru sempat dimuat
            time.sleep(3)

            # 3. Deteksi jika sudah tidak ada video baru yang dimuat (paling bawah)
            #   Untuk menghindari infinite loop, kita cek apakah jumlah link bertambah.
            if len(video_links) == links_before_scroll:
                print("🏁 Halaman sudah paling bawah atau tidak ada video baru yang dimuat.")
                break

    except TimeoutException:
        print("❌ Gagal memuat halaman profil atau tidak ada video ditemukan.")
        return []

    print(f"\n👍 Selesai mengumpulkan. Total {len(video_links)} link video unik ditemukan.")

    # Pastikan hasil akhir tidak melebihi max_videos
    return list(video_links)[:max_videos]

def check_for_captcha(driver):
    """
    [PERBAIKAN V2] Memeriksa CAPTCHA, termasuk di dalam iFrame.
    """
    captcha_texts = [
        "Drag the slider to fit the puzzle",
        "Drag the puzzle piece into place",
        "Geser puzzle untuk melengkapi gambar",
        "Verify to continue"
    ]
    # Menggunakan contains(., '...') agar lebih kuat dalam mencari teks
    xpath_query = "//*[" + " or ".join([f"contains(., '{text}')" for text in captcha_texts]) + "]"

    # 1. Cek di dalam iFrame terlebih dahulu (penyebab paling umum)
    try:
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            print(f"\n    Mendeteksi {len(iframes)} iFrame, memeriksa satu per satu untuk CAPTCHA...")
            for frame in iframes:
                try:
                    # Pindah fokus ke dalam iFrame
                    driver.switch_to.frame(frame)
                    # Cari elemen CAPTCHA di dalam iFrame
                    driver.find_element(By.XPATH, xpath_query)
                    print("\n⚠️  CAPTCHA terdeteksi di dalam sebuah iFrame!")
                    # PENTING: Kembali ke konteks halaman utama agar sisa skrip tidak error
                    driver.switch_to.default_content()
                    return True
                except NoSuchElementException:
                    # Jika tidak ditemukan di iFrame ini, kembali dan lanjut ke iFrame berikutnya
                    driver.switch_to.default_content()
                    continue
    except Exception as e:
        print(f"\n    Error saat memeriksa iFrame: {e}")
        # Pastikan kembali ke konteks utama jika ada error tak terduga
        driver.switch_to.default_content()

    # 2. Jika tidak ada di iFrame, cek di halaman utama (sebagai cadangan)
    try:
        driver.find_element(By.XPATH, xpath_query)
        print("\n⚠️  CAPTCHA terdeteksi di halaman utama!")
        return True
    except NoSuchElementException:
        return False

def scrape_video_details(driver, video_url):
    """Mengambil caption dan seluruh komentar, dengan penanganan CAPTCHA dan logika ekspansi konten."""
    print(f"\n--- Memproses video: {video_url} ---")
    driver.get(video_url)

    max_retries = 2
    for attempt in range(max_retries):
        try:
            upload_date = "N/A"
            like_count = "N/A"

            try:
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-e2e="browser-video-meta-date"]'))
                )
                upload_date = date_element.text
            except TimeoutException:
                print("  -> Info tanggal video tidak ditemukan.")

            try:
                like_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="like-count"]'))
                )
                like_count = like_element.text
                print(f"  -> Jumlah 'like' ditemukan: {like_count}")
            except TimeoutException:
                print("  -> Info jumlah 'like' tidak ditemukan.")

            video_data = {'url': video_url, 'upload_date': upload_date, 'like_count': like_count, 'caption_short': '', 'caption_detail': '', 'comments': []}

            # --- [PERBAIKAN DIMULAI DI SINI] ---
            try:
                # 1. Tetap tunggu container utamanya
                desc_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-e2e='browse-video-desc']"))
                )

                # 2. Cari caption di dalam try...except baru
                try:
                    video_data['caption_short'] = desc_container.find_element(By.CSS_SELECTOR, 'span[data-e2e="new-desc-span"]').text
                    print(f"  -> Caption singkat ditemukan: {video_data['caption_short'][:50]}...")

                    # 3. Logika untuk tombol 'more' hanya dijalankan jika caption ditemukan
                    try:
                        more_button = driver.find_element(By.CSS_SELECTOR, "span[class*='-SpanExpandIcon']")
                        driver.execute_script("arguments[0].click();", more_button)
                        print("  -> Tombol 'more' (ikon) pada caption diklik.")
                        time.sleep(2)
                        detail_container = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='DivCustomTDKContainer']"))
                        )
                        desc_text = detail_container.find_element(By.CSS_SELECTOR, "div[data-e2e='v2t-desc']").text
                        keywords_text = ""
                        try:
                            keywords_text = detail_container.find_element(By.CSS_SELECTOR, "div[data-e2e='v2t-keywords']").text
                        except NoSuchElementException: pass
                        video_data['caption_detail'] = f"Deskripsi: {desc_text}\nKeywords: {keywords_text}".strip()
                        print(f"  -> Caption detail ditemukan: {video_data['caption_detail'][:50]}...")
                    except (NoSuchElementException, TimeoutException):
                        print("  -> Tidak ada tombol 'more' untuk caption detail.")

                except NoSuchElementException:
                    # Jika elemen caption tidak ada, cetak pesan dan lanjutkan
                    print("  -> Video ini tidak memiliki caption.")

            except TimeoutException:
                # Jika bahkan container deskripsinya tidak ada, anggap halaman gagal dimuat
                print("  -> Bagian deskripsi/caption tidak ditemukan, kemungkinan halaman terhalang.")
            # --- [PERBAIKAN SELESAI DI SINI] ---

            # ... (Sisa kode untuk mengambil komentar tidak perlu diubah) ...
            try:
                comment_container = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='DivCommentListContainer']"))
                )
                print("  -> Bagian komentar ditemukan. Memuat seluruh komentar...")
                body = driver.find_element(By.TAG_NAME, 'body')
            except TimeoutException:
                print("  -> Bagian komentar tidak ditemukan.")
                return video_data

            try:
                print("  -> Memulai proses scroll dan klik balasan secara dinamis...")
                reply_button_xpath = "//span[contains(text(), 'balasan') or (contains(text(), 'View') and contains(text(), 'reply') or contains(text(), 'replies'))]"

                last_comment_count = 0
                stalled_attempts = 0
                max_stalled_attempts = 5

                while stalled_attempts < max_stalled_attempts:
                    try:
                        view_buttons = driver.find_elements(By.XPATH, reply_button_xpath)
                        if view_buttons:
                            print(f"    -> Menemukan {len(view_buttons)} tombol balasan. Mengklik satu...")
                            driver.execute_script("arguments[0].click();", view_buttons[0])
                            time.sleep(2)
                            stalled_attempts = 0
                            continue
                    except Exception as e:
                        print(f"    -> Error minor saat mengklik tombol balasan: {e}")

                    print("    -> Tidak ada tombol balasan terlihat. Melakukan scroll...")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)

                    current_comment_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "DivCommentItemWrapper")]'))
                    if current_comment_count > last_comment_count:
                        print(f"    -> Konten baru dimuat. Total item sekarang: {current_comment_count}")
                        last_comment_count = current_comment_count
                        stalled_attempts = 0
                    else:
                        stalled_attempts += 1
                        print(f"    -> Konten tidak bertambah, percobaan ke-{stalled_attempts}/{max_stalled_attempts}.")

                print("  -> Scroll dan klik selesai. Memulai ekstraksi final...")

                comment_item_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "DivCommentItemWrapper")]'))
                print(f"  -> Ditemukan total {comment_item_count} item komentar. Memproses satu per satu...")

                for i in range(comment_item_count):
                    try:
                        all_comment_items = driver.find_elements(By.XPATH, '//div[contains(@class, "DivCommentItemWrapper")]')
                        item = all_comment_items[i]

                        try:
                            author_element = item.find_element(By.XPATH, './/div[@data-e2e="comment-username-1"]//p')
                            comment_element = item.find_element(By.XPATH, './/span[@data-e2e="comment-level-1"]')
                            new_comment = {
                                'author': author_element.text,
                                'comment': comment_element.text,
                                'replies': []
                            }
                            video_data['comments'].append(new_comment)
                            continue
                        except NoSuchElementException:
                            pass

                        try:
                            reply_author_element = item.find_element(By.XPATH, './/div[@data-e2e="comment-username-2"]//p')
                            reply_comment_element = item.find_element(By.XPATH, './/span[@data-e2e="comment-level-2"]')
                            if video_data['comments']:
                                new_reply = {
                                    'author': reply_author_element.text,
                                    'comment': reply_comment_element.text
                                }
                                video_data['comments'][-1]['replies'].append(new_reply)
                        except NoSuchElementException:
                            pass
                    except IndexError:
                        print(f"    -> Peringatan: Jumlah komentar berubah saat proses. Melewatkan indeks ke-{i}.")
                        break
                    except Exception as e:
                        print(f"    -> Terjadi error pada item ke-{i}, melewati. Error: {e}")

                print("  -> Selesai. Berhasil memproses dan mengelompokkan komentar.")

            except Exception as e:
                print(f"  -> Gagal pada proses utama karena: {e}")

            return video_data

        except TimeoutException:
            print("  -> Gagal memuat elemen halaman (Timeout).")
            if check_for_captcha(driver):
                print("\n" + "="*50)
                print(f"⚠️ CAPTCHA terdeteksi pada percobaan ke-{attempt + 1} untuk video: {video_url}")
                input("   Silakan selesaikan CAPTCHA di browser, lalu tekan [Enter] untuk mencoba lagi...")
                driver.refresh()
                print("   Mencoba lagi...")
                continue
            else:
                print("  -> Tidak ada CAPTCHA. Melewati video ini.")
                return None

    print(f"  -> Gagal memproses video setelah {max_retries} kali percobaan. Melewati video ini.")
    return None
# ==============================================================================
# EKSEKUSI UTAMA (Tidak Berubah)
# ==============================================================================
if __name__ == "__main__":
    PROFILE_USERNAMES = ["rctvcirebon", "cirebonkabtv", "kang_jigus", "kangimron_", "info.cirebonan"]
#
    MAX_VIDEOS_PER_PROFILE = 200

    BASE_COOKIES_FILE = str(COOKIE_DIR / ("tiktok_base_cookies.json"))
    PROFILE_COOKIES_FILE = str(COOKIE_DIR / ("tiktok_profile_cookies.json"))

    all_data = []
    driver = setup_driver()

    if driver:
        try:
            if not PROFILE_USERNAMES:
                print("Daftar PROFILE_USERNAMES kosong.")
            else:
                first_profile_url = f"https://www.tiktok.com/@{PROFILE_USERNAMES[0]}"
                session_ok = establish_and_verify_session(driver, BASE_COOKIES_FILE, PROFILE_COOKIES_FILE, first_profile_url)

                if session_ok:
                    for username in PROFILE_USERNAMES:
                        print("\n" + "="*70)
                        print(f"MEMULAI SCRAPING UNTUK PROFIL: @{username}")
                        print("="*70)

                        profile_url = f"https://www.tiktok.com/@{username}"
                        driver.get(profile_url)

                        # [PERUBAHAN] Panggilan fungsi disederhanakan
                        video_urls = get_video_links(driver, MAX_VIDEOS_PER_PROFILE)

                        for url in video_urls:
                            data = scrape_video_details(driver, url)
                            if data:
                                data['profile_username'] = username
                                data['scrape_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                all_data.append(data)
                            time.sleep(2)

            # ... sisa kode untuk menyimpan file tidak perlu diubah ...
            if all_data:
                print("\nMenyimpan semua data yang terkumpul...")
                df = pd.DataFrame(all_data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"tiktok_data_multi_{timestamp}"
                df.to_csv(f'{output_filename}.csv', index=False, encoding='utf-8-sig')
                print(f"Data telah disimpan ke {output_filename}.csv")
                with open(f'{output_filename}.json', 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
                print(f"Data telah disimpan ke {output_filename}.json")
            else:
                print("\nTidak ada data yang berhasil dikumpulkan untuk disimpan.")

        except Exception as e:
            print(f"\nTerjadi kesalahan fatal selama proses: {e}")
        finally:
            print("\n--- PROSES SELESAI ---")
            driver.quit()
