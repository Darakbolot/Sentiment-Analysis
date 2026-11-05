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
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta

# ==============================================================================
# KONFIGURASI DAN FUNGSI LOGIN (TIDAK ADA PERUBAHAN)
# ==============================================================================
# Konfigurasi
option = webdriver.ChromeOptions()

# Headless Code
# option.add_argument('--headless')
# option.add_argument('--window-size=1920x1080')
# option.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
# option.add_argument('--disable-gpu')

option.add_argument('--ignore-certificate-errors')
option.add_argument('--incognito')
option.add_experimental_option('excludeSwitches', ['enable-logging'])

username, password, verif = uspass.userpass()
ig = 'https://www.instagram.com/'
driver = webdriver.Chrome(options=option)
driver.get(f"{ig}accounts/login/")
time.sleep(2)

COOKIES_FILE = str(COOKIE_DIR / (f"ig_cookies_{username}.json"))

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

# --- PROSES LOGIN ---
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
# FUNGSI-FUNGSI BANTUAN SCRAPING BARU
# ==============================================================================

def parse_comment_li(element):
    """Fungsi kecil untuk mem-parsing satu item <li> komentar atau balasan."""
    try:
        # Cari semua span dengan atribut dir='auto' di dalam elemen
        spans = element.find_elements(By.XPATH, ".//span[@dir='auto']")
        if len(spans) >= 2:
            author = spans[0].text
            comment_text = spans[1].text

            # Validasi untuk menyaring teks UI seperti "Edited", "Reply", dll.
            if author and comment_text and len(author) < 30 and len(comment_text.split()) < 100:
                return {"author": author, "comment": comment_text}
    except Exception:
        return None
    return None

# ==============================================================================
# FUNGSI UTAMA SCRAPING (MASTER FUNCTION) DENGAN PERBAIKAN TOTAL
# ==============================================================================

def scrape_target(target_url, source_type, source_name, max_scrolls):
    global all_data
    driver.get(target_url)
    print(f"\n{'='*50}\nMemproses {source_type}: {source_name}\n{'='*50}")
    time.sleep(5)

    # LANGKAH 1 & 2: SCROLLING SAMBIL MENGAMBIL LINK
    # ... (Tidak ada perubahan di bagian ini) ...
    print(f"Memulai proses scroll dan koleksi link untuk {source_type} '{source_name}'...")
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
        print(f"Selesai scroll. Ditemukan total {len(post_links)} postingan unik.")
    except Exception as e:
        print(f"Gagal melakukan scroll atau mengambil link postingan dari {source_name}: {e}")
        return

    # Tentukan batas waktu
    time_limit = datetime.now() - timedelta(days=30*7)

    # LANGKAH 3: PROSES SETIAP POSTINGAN
    for i, link in enumerate(post_links):
        print(f"\n--- Memproses postingan {i+1}/{len(post_links)} dari {source_name} ---")
        driver.get(link)
        time.sleep(4)

        caption, post_datetime_str, likes, comments_list = "", "", 0, []

        try:
            time_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "time")))
            post_datetime_str = time_element.get_attribute("datetime")
            post_date = datetime.fromisoformat(post_datetime_str.replace('Z', '+00:00'))
            if post_date.replace(tzinfo=None) < time_limit:
                print(f"Postingan terlalu lama ({post_date.strftime('%Y-%m-%d')}), berhenti.")
                break
        except Exception as e:
            print(f"  -> Gagal mengambil tanggal: {e}")
            post_datetime_str = datetime.now().isoformat()

        # Ambil Caption (LOGIKA DIPERBARUI)
        try:
            caption_xpaths = [
                "//div[@data-testid='post-caption']",
                "//h1",
                "//span[contains(@class, 'x126k92a')]"
            ]
            for xpath in caption_xpaths:
                try:
                    caption_element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    caption = caption_element.get_attribute('innerHTML')
                    if caption:
                        print(f"  -> Caption ditemukan menggunakan metode [{xpath.split('/')[-1].split('[')[0]}]")
                        break
                except TimeoutException:
                    continue
        except Exception as e:
            print(f"  -> Gagal mengambil Caption: {e}")

# Ambil Likes (LOGIKA BARU DENGAN 3 KALI PENGECEKAN & NILAI TERBESAR)
        likes = 0
        try:
            # Daftar XPath untuk menemukan jumlah 'likes' dengan berbagai cara
            like_xpaths = [
                # 1. Metode Paling Andal: Cari di dalam link menuju halaman 'liked_by'
                "//a[contains(@href, '/liked_by/')]/span",
                # 2. Metode Cadangan: Cari span yang berisi kata 'likes' atau 'suka'
                "//section//span[contains(text(), 'likes') or contains(text(), 'suka')]",
                # 3. Metode Lain: Cari angka di sebelah tombol 'View Insights'
                "//span[contains(text(), 'View insights') or contains(text(), 'Lihat Insight')]/preceding-sibling::span"
            ]

            found_likes = []

            # Coba setiap XPath
            for xpath in like_xpaths:
                try:
                    # Gunakan find_elements agar tidak error jika tidak ditemukan
                    like_elements = driver.find_elements(By.XPATH, xpath)
                    for element in like_elements:
                        # Ambil semua digit angka dari teks
                        numbers = re.findall(r'\d+', element.text)
                        if numbers:
                            # Gabungkan angka (misal: ['1', '032'] -> '1032') dan konversi ke integer
                            likes_num = int("".join(numbers))
                            found_likes.append(likes_num)
                except Exception:
                    continue # Lanjut ke xpath berikutnya jika ada error

            # Ambil nilai 'likes' terbesar dari semua yang berhasil ditemukan
            if found_likes:
                likes = max(found_likes)

        except Exception as e:
            print(f"  -> Gagal mengambil Likes: {e}")

        # Ambil Komentar (LOGIKA FINAL DENGAN PENDEKATAN HIBRIDA)
        comments_list = []
        try:
            # Tahap 1: Ekspansi (Tidak berubah, logika ini sudah benar)\
            while True:
                try:
                    load_more_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Load more comments'], svg[aria-label='Muat komentar lainnya']")))
                    driver.execute_script("arguments[0].click();", load_more_button)
                    time.sleep(2)
                except: break

            max_expansions = 50
            for _ in range(max_expansions):
                try:
                    view_replies_buttons = driver.find_elements(By.XPATH, "//div[@role='button']/span[contains(text(), 'balasan') or contains(text(), 'replies')]")
                    clickable_buttons = [btn for btn in view_replies_buttons if "Sembunyikan" not in btn.text and "Hide" not in btn.text]
                    if not clickable_buttons: break
                    for button in clickable_buttons:
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1.5)
                except: break
            print("  -> Semua komentar dan balasan telah dimuat.")

            # Tahap 2: Ekstraksi dengan logika hibrida
            top_level_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1xegmmw')]/ancestor::div[contains(@class, 'xsag5q8')]")

            if len(top_level_blocks) > 1:
                # Loop dimulai dari 1 untuk melewati caption
                for block in top_level_blocks[1:]:
                    try:
                        # Parsing komentar utama
                        main_comment_author = block.find_element(By.XPATH, ".//span[contains(@class, '_aaco')]").text
                        main_comment_text = block.find_element(By.XPATH, ".//div[contains(@class, 'x1cy8zhl')]/span").text

                        comment_data = {
                            "author": main_comment_author,
                            "comment": main_comment_text,
                            "replies": []
                        }

                        # Cari dan proses balasan di dalam blok ini
                        try:
                            reply_ul = block.find_element(By.XPATH, ".//ul")
                            reply_items = reply_ul.find_elements(By.XPATH, "./li")

                            for reply_item in reply_items:
                                # Parsing balasan menggunakan pola yang sama di dalam <li>
                                reply_author = reply_item.find_element(By.XPATH, ".//span[contains(@class, '_aaco')]").text
                                reply_text = reply_item.find_element(By.XPATH, ".//div[contains(@class, 'x1cy8zhl')]/span").text

                                if reply_author and reply_text:
                                    comment_data["replies"].append({"author": reply_author, "comment": reply_text})
                        except NoSuchElementException:
                            pass # Tidak ada balasan

                        comments_list.append(comment_data)
                    except Exception:
                        continue # Jika satu blok gagal, lanjut
        except Exception as e:
            print(f"  -> Gagal mengambil Komentar: {e}")

        all_data.append({
            'source_type': source_type, 'source_name': source_name,
            'post_url': link, 'caption': caption, 'likes': likes,
            'comments': comments_list, "datetime": post_datetime_str
        })
        print(f"Data postingan berhasil diambil. Likes: {likes}, Komentar: {len(comments_list)}")

# ==============================================================================
# EKSEKUSI UTAMA (TIDAK ADA PERUBAHAN)
# ==============================================================================
profile_accounts = ["cirebonkab"]
hashtags_to_scrape = ["jalanrusak"]
max_scrolls = 1
all_data = []

if profile_accounts:
    print("\n\n>>> MEMULAI PROSES SCRAPING AKUN PROFIL <<<")
    for account in profile_accounts:
        profile_url = f"{ig}{account}/"
        scrape_target(profile_url, "account", account, max_scrolls)

if hashtags_to_scrape:
    print("\n\n>>> MEMULAI PROSES SCRAPING TAGAR <<<")
    for tag in hashtags_to_scrape:
        hashtag_url = f"{ig}explore/tags/{tag}/"
        scrape_target(hashtag_url, "tag", tag, max_scrolls)

if all_data:
    try:
        print("\nMenyimpan semua data yang terkumpul...")
        df = pd.DataFrame(all_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"instagram_data_{timestamp}"
        df.to_csv(f'{output_filename}.csv', index=False, encoding='utf-8-sig')
        print(f"Data telah disimpan ke {output_filename}.csv")
        with open(f'{output_filename}.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"Data telah disimpan ke {output_filename}.json")
    except Exception as e:
        print(f"\nGagal menyimpan file: {e}")
else:
    print("\nTidak ada data untuk disimpan.")

print("\n--- PROSES SELESAI ---")
driver.quit()
