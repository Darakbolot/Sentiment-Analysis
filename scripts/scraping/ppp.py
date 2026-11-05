from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
COOKIE_DIR = PROJECT_ROOT / "private" / "cookies"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COOKIE_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(OUTPUT_DIR)

import time
import uspass
import pandas as pd
import json, os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta

# Konfigurasi
option = webdriver.ChromeOptions()
option.add_argument('--ignore-certificate-errors')
option.add_argument('--incognito')
option.add_experimental_option('excludeSwitches', ['enable-logging'])

username, password, verif = uspass.userpass()
ig = 'https://www.instagram.com/'
driver = webdriver.Chrome(options=option)
driver.get(f"{ig}accounts/login/")
time.sleep(2)

COOKIES_FILE = str(COOKIE_DIR / (f"ig_cookies_{username}.json"))

# --- FUNGSI-FUNGSI LOGIN DAN COOKIES (TIDAK BERUBAH) ---
def save_cookies(driver, path):
    try:
        driver.get(ig)
        time.sleep(1)
        cookies = driver.get_cookies()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"[COOKIES] Disimpan ke {path} ({len(cookies)} item)")
    except Exception as e:
        print(f"[COOKIES] Gagal simpan: {e}")

def load_cookies(driver, path):
    with open(path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    driver.get(ig)
    time.sleep(1)
    driver.delete_all_cookies()
    injected = 0
    for c in cookies:
        try:
            allowed = {k: c[k] for k in c.keys() & {"name","value","domain","path","secure","httpOnly","expiry"}}
            if "expiry" in allowed and isinstance(allowed["expiry"], float):
                allowed["expiry"] = int(allowed["expiry"])
            driver.add_cookie(allowed)
            injected += 1
        except Exception:
            allowed.pop("domain", None)
            try:
                driver.add_cookie(allowed)
                injected += 1
            except Exception:
                pass
    print(f"[COOKIES] Injected {injected}/{len(cookies)} cookies")

def has_session_cookie(driver):
    return any(c.get("name") == "sessionid" for c in driver.get_cookies())

def is_logged_in(driver, timeout=8):
    target = f"{ig}accounts/edit/"
    driver.get(target)
    try:
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.url_contains("/accounts/edit/"),
                EC.url_contains("/accounts/login/")
            )
        )
    except TimeoutException:
        return False
    return "/accounts/edit/" in driver.current_url and has_session_cookie(driver)

# --- PROSES LOGIN (TIDAK BERUBAH) ---
cookie_login_ok = False
if os.path.exists(COOKIES_FILE):
    try:
        load_cookies(driver, COOKIES_FILE)
        driver.get(ig)
        time.sleep(2)
        cookie_login_ok = is_logged_in(driver, timeout=10)
        print("[COOKIES] Status login via cookies:", "OK" if cookie_login_ok else "Gagal")
    except Exception as e:
        print(f"[COOKIES] Gagal load/inject: {e}")

if not cookie_login_ok:
    driver.get(f"{ig}accounts/login/")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        WebDriverWait(driver, 15).until(EC.url_changes(f"{ig}accounts/login/"))
        print("Login Sukses")
    except Exception as e:
        print(f"Login Gagal: {e}")
        driver.quit()
        raise SystemExit

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'verificationCode'))).send_keys(verif)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Confirm']"))).click()
        print("Verifikasi 2FA berhasil.")
        time.sleep(3)
    except Exception:
        print("Tidak ada verifikasi 2FA.")

    for _ in range(2):
        try:
            WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now') or contains(text(),'Bukan Sekarang')]"))
            ).click()
            time.sleep(1.5)
        except Exception:
            pass
    save_cookies(driver, COOKIES_FILE)


# ==============================================================================
# --- KONFIGURASI TARGET SCRAPING ---
# ==============================================================================

# PRIORITAS: Daftar akun Instagram yang akan di-scrape
profile_accounts = [
    "cirebonkab", "kang_jigus", "kangimron.rosyadi",
    "info.cirebonan", "radarcirebon", "aboutcirebonid"
]

# OPSIONAL: Daftar tagar yang akan di-scrape (kosongkan jika tidak ingin scrape tagar)
hashtags_to_scrape = [
    "magang",
    "loker"
]

all_data = []
# Tentukan batas waktu (misal: 7 bulan lalu dari sekarang)
time_limit = datetime.now() - timedelta(days=30*7)

# ==============================================================================
# --- BAGIAN 1: SCRAPING BERDASARKAN AKUN (PRIORITAS) ---
# ==============================================================================
print("\n" + "="*20 + " MEMULAI SCRAPING AKUN " + "="*20)
for account in profile_accounts:
    profile_url = f"{ig}{account}/"
    driver.get(profile_url)
    print(f"\n{'='*50}\nMemproses Akun: {account}\n{'='*50}")
    time.sleep(5)

    # LANGKAH 1 & 2: SCROLLING SAMBIL MENGAMBIL LINK
    post_links_set = set()
    max_scrolls = 20
    scroll_attempts = 0
    try:
        for i in range(max_scrolls):
            last_height = driver.execute_script("return document.body.scrollHeight")
            posts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            for post in posts:
                link = post.get_attribute('href')
                if link:
                    post_links_set.add(link)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print(f"  -> Scroll ke-{i+1}/{max_scrolls} | Total link ditemukan: {len(post_links_set)}")
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts > 2:
                    print("  -> Telah mencapai bagian bawah halaman.")
                    break
            else:
                scroll_attempts = 0
        post_links = list(post_links_set)
        print(f"Selesai scroll. Ditemukan total {len(post_links)} postingan unik di {account}.")
    except Exception as e:
        print(f"Gagal melakukan scroll atau mengambil link postingan di {account}: {e}")
        continue

    # LANGKAH 3: PROSES SETIAP POSTINGAN
    for i, link in enumerate(post_links):
        # (Kode untuk scrape detail postingan disalin ke sini)
        # ... (Sama seperti sebelumnya) ...
        # Simpan data posting
        # all_data.append({'account': account, ...})
        pass # Placeholder

# ==============================================================================
# --- BAGIAN 2: SCRAPING BERDASARKAN TAGAR (OPSIONAL) ---
# ==============================================================================
if hashtags_to_scrape:
    print("\n" + "="*20 + " MEMULAI SCRAPING TAGAR " + "="*20)
    for tag in hashtags_to_scrape:
        hashtag_url = f"https://www.instagram.com/explore/tags/{tag}/"
        driver.get(hashtag_url)
        print(f"\n{'='*50}\nMemproses Tagar: #{tag}\n{'='*50}")
        time.sleep(5)

        # LANGKAH 1 & 2: SCROLLING SAMBIL MENGAMBIL LINK
        post_links_set = set()
        max_scrolls = 40 # Mungkin butuh scroll lebih banyak untuk tagar populer
        scroll_attempts = 0
        try:
            for i in range(max_scrolls):
                last_height = driver.execute_script("return document.body.scrollHeight")
                posts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
                for post in posts:
                    link = post.get_attribute('href')
                    if link:
                        post_links_set.add(link)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                print(f"  -> Scroll ke-{i+1}/{max_scrolls} | Total link ditemukan: {len(post_links_set)}")
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                    if scroll_attempts > 2:
                        print("  -> Telah mencapai bagian bawah halaman.")
                        break
                else:
                    scroll_attempts = 0
            post_links = list(post_links_set)
            print(f"Selesai scroll. Ditemukan total {len(post_links)} postingan unik dari tagar #{tag}.")
        except Exception as e:
            print(f"Gagal melakukan scroll atau mengambil link postingan dari tagar #{tag}: {e}")
            continue

        # LANGKAH 3: PROSES SETIAP POSTINGAN
        for i, link in enumerate(post_links):
            # (Kode untuk scrape detail postingan disalin ke sini juga)
            # ... (Sama seperti sebelumnya) ...
            # Simpan data posting
            # all_data.append({'source_tag': tag, ...})
            pass # Placeholder

# ==============================================================================
# --- FUNGSI DETAIL SCRAPING DAN PENYIMPANAN (UNTUK MENGHINDARI DUPLIKASI KODE) ---
# ==============================================================================

def scrape_post_details(driver, link, source_type, source_value):
    """Fungsi untuk mengambil detail dari satu postingan."""
    print(f"\n--- Memproses postingan dari [{source_type}: {source_value}] ---")
    print(f"URL: {link}")
    driver.get(link)
    time.sleep(3)

    # Cek tanggal postingan
    try:
        time_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "time")))
        post_datetime_str = time_element.get_attribute("datetime")
        post_date = datetime.fromisoformat(post_datetime_str.replace('Z', '+00:00'))
        if post_date.replace(tzinfo=None) < time_limit:
            print(f"Postingan terlalu lama ({post_date.strftime('%Y-%m-%d')}), dilewati.")
            return None # Kembalikan None untuk menandakan postingan dilewati
    except Exception:
        print("Gagal memvalidasi datetime, postingan tetap diproses.")
        post_datetime_str = datetime.now().isoformat()

    # Ambil Caption
    caption = ""
    try:
        wait = WebDriverWait(driver, 3)
        try:
            caption_container = wait.until(EC.presence_of_element_located((By.XPATH, "//h1")))
            caption = caption_container.get_attribute('innerHTML')
        except TimeoutException:
            try:
                caption_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='post-caption']")))
                caption = caption_container.get_attribute('innerHTML')
            except TimeoutException:
                caption_container = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'x126k92a')]")))
                parent_element = caption_container.find_element(By.XPATH, "..")
                caption = parent_element.get_attribute('innerHTML')
    except Exception:
        print(f"  -> Gagal mengambil caption.")

    # Ambil Likes
    likes = 0
    try:
        like_element_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/liked_by/')]")))
        likes_text = like_element_container.text.split()[0]
        likes = int(likes_text.replace(",", "").replace(".", ""))
    except Exception:
        try:
            like_span = driver.find_element(By.XPATH, "//div[contains(@class, 'x12nagc')]/a/div/span")
            likes_text = like_span.text.split()[0]
            likes = int(likes_text.replace(",", "").replace(".", ""))
        except Exception:
            print(f"  -> Gagal mengambil likes.")

    # Ambil Komentar
    comments_list = []
    # (Logika ambil komentar yang kompleks diletakkan di sini...)

    post_data = {
        'source_type': source_type,
        'source_value': source_value,
        'post_url': link,
        'caption': caption,
        'likes': likes,
        'comments': comments_list,
        "datetime": post_datetime_str
    }
    print(f"Data postingan berhasil diambil. Likes: {likes}")
    return post_data

# ... (KODE UTAMA YANG DIPERBARUI DENGAN FUNGSI DI ATAS) ...
# (Untuk kode final yang bersih, saya akan gabungkan semuanya di bawah)

# ==============================================================================
# --- KODE FINAL YANG BERSIH DAN LENGKAP ---
# ==============================================================================

# (Salin semua dari awal sampai akhir blok login di sini)

# --- KONFIGURASI TARGET SCRAPING ---
profile_accounts = [
    "cirebonkab", "kang_jigus"
]
hashtags_to_scrape = [
    "magang"
]
all_data = []
time_limit = datetime.now() - timedelta(days=30*7)

# --- BAGIAN 1: SCRAPING AKUN ---
print("\n" + "="*20 + " MEMULAI SCRAPING AKUN " + "="*20)
for account in profile_accounts:
    pass  # Placeholder lama; implementasi scraping lengkap berada di bagian berikutnya.
    # (Logika scroll dan ambil link untuk AKUN seperti di atas)
    # ...
    # for link in post_links:
    #     scraped_data = scrape_post_details(driver, link, "account", account)
    #     if scraped_data:
    #         all_data.append(scraped_data)

# --- BAGIAN 2: SCRAPING TAGAR ---
if hashtags_to_scrape:
    print("\n" + "="*20 + " MEMULAI SCRAPING TAGAR " + "="*20)
    # for tag in hashtags_to_scrape:
    #     # (Logika scroll dan ambil link untuk TAGAR seperti di atas)
    #     # ...
    #     # for link in post_links:
    #     #     scraped_data = scrape_post_details(driver, link, "tag", tag)
    #     #     if scraped_data:
    #     #         all_data.append(scraped_data)

# ... (Kode penyimpanan file) ...
# driver.quit()

# Karena duplikasi kode sangat tidak efisien, saya akan berikan versi final yang sudah direstrukturisasi dengan benar.

# ==============================================================================
# --- VERSI FINAL DENGAN FUNGSI UNTUK MENGHINDARI PENGULANGAN KODE ---
# ==============================================================================

def get_post_links(driver, max_scrolls=20):
    """Fungsi untuk scroll dan mengumpulkan link postingan dari halaman saat ini."""
    print(f"Memulai proses scroll dan koleksi link (Maksimal {max_scrolls} scroll)...")
    post_links_set = set()
    scroll_attempts = 0
    try:
        for i in range(max_scrolls):
            last_height = driver.execute_script("return document.body.scrollHeight")
            posts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            for post in posts:
                link = post.get_attribute('href')
                if link:
                    post_links_set.add(link)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print(f"  -> Scroll ke-{i+1}/{max_scrolls} | Link unik ditemukan: {len(post_links_set)}")
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts > 2:
                    print("  -> Telah mencapai bagian bawah halaman.")
                    break
            else:
                scroll_attempts = 0
        return list(post_links_set)
    except Exception as e:
        print(f"Gagal melakukan scroll atau mengambil link: {e}")
        return list(post_links_set) # Kembalikan apa yang sudah didapat

def get_post_details(driver, link):
    """Fungsi untuk mengambil detail (caption, likes, dll) dari satu halaman postingan."""
    driver.get(link)
    time.sleep(3)

    data = {'caption': '', 'likes': 0, 'comments': [], 'datetime': datetime.now().isoformat()}

    # Cek tanggal
    try:
        time_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "time")))
        data['datetime'] = time_element.get_attribute("datetime")
        post_date = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
        if post_date.replace(tzinfo=None) < time_limit:
            print(f"  -> Postingan terlalu lama ({post_date.strftime('%Y-%m-%d')}), dilewati.")
            return None # Sinyal untuk skip
    except Exception:
        print(f"  -> Gagal memvalidasi datetime untuk {link}.")
        pass

    # Ambil Caption
    try:
        wait = WebDriverWait(driver, 3)
        try: data['caption'] = wait.until(EC.presence_of_element_located((By.XPATH, "//h1"))).get_attribute('innerHTML')
        except TimeoutException:
            try: data['caption'] = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='post-caption']"))).get_attribute('innerHTML')
            except TimeoutException:
                caption_container = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'x126k92a')]")))
                data['caption'] = caption_container.find_element(By.XPATH, "..").get_attribute('innerHTML')
    except Exception:
        print(f"  -> Gagal mengambil caption.")

    # Ambil Likes
    try:
        like_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/liked_by/')]")))
        data['likes'] = int(like_container.text.split()[0].replace(",", "").replace(".", ""))
    except Exception:
        try:
            like_span = driver.find_element(By.XPATH, "//div[contains(@class, 'x12nagc')]/a/div/span")
            data['likes'] = int(like_span.text.split()[0].replace(",", "").replace(".", ""))
        except Exception:
             print(f"  -> Gagal mengambil likes.")

    # (Logika ambil komentar bisa ditambahkan di sini jika diperlukan)

    print(f"  -> Data diambil. Likes: {data['likes']}, Caption: {data['caption'][:30]}...")
    return data

# --- KODE UTAMA YANG SUDAH DIRESTRUKTURISASI ---
# (Asumsikan kode login sudah berjalan)
all_data = []
# --- BAGIAN 1: SCRAPING AKUN (PRIORITAS) ---
if profile_accounts:
    print("\n" + "="*20 + " MEMULAI SCRAPING AKUN " + "="*20)
    for account in profile_accounts:
        print(f"\nMemproses Akun: {account}")
        driver.get(f"{ig}{account}/")
        time.sleep(5)
        post_links = get_post_links(driver, max_scrolls=20)
        print(f"Ditemukan {len(post_links)} link dari akun {account}. Memulai proses scraping detail...")
        for i, link in enumerate(post_links):
            print(f"--- Post {i+1}/{len(post_links)} ---")
            details = get_post_details(driver, link)
            if details:
                details['source_type'] = 'account'
                details['source_value'] = account
                details['post_url'] = link
                all_data.append(details)

# --- BAGIAN 2: SCRAPING TAGAR (OPSIONAL) ---
if hashtags_to_scrape:
    print("\n" + "="*20 + " MEMULAI SCRAPING TAGAR " + "="*20)
    for tag in hashtags_to_scrape:
        print(f"\nMemproses Tagar: #{tag}")
        driver.get(f"https://www.instagram.com/explore/tags/{tag}/")
        time.sleep(5)
        post_links = get_post_links(driver, max_scrolls=40)
        print(f"Ditemukan {len(post_links)} link dari tagar #{tag}. Memulai proses scraping detail...")
        for i, link in enumerate(post_links):
            print(f"--- Post {i+1}/{len(post_links)} ---")
            details = get_post_details(driver, link)
            if details:
                details['source_type'] = 'tag'
                details['source_value'] = tag
                details['post_url'] = link
                all_data.append(details)

# --- PENYIMPANAN FILE ---
try:
    print(f"\nMenyimpan total {len(all_data)} data...")
    df = pd.DataFrame(all_data)
    df.to_csv('instagram_data_combined.csv', index=False, encoding='utf-8-sig')
    print("Data telah disimpan ke instagram_data_combined.csv")
    with open('instagram_data_combined.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("Data telah disimpan ke instagram_data_combined.json")
except Exception as e:
    print(f"Gagal menyimpan file: {e}")

print("\n--- Proses Selesai ---")
driver.quit()
