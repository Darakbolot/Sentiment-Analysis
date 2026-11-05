from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
COOKIE_DIR = PROJECT_ROOT / "private" / "cookies"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COOKIE_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(OUTPUT_DIR)

import os
import time
import json
import csv
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========== KONFIGURASI ==========
FB_USERNAME = os.environ.get("FB_USERNAME", "")
FB_PASSWORD = os.environ.get("FB_PASSWORD", "")
COOKIES_FILE = str(COOKIE_DIR / ("fb_cookies.json"))

# daftar grup yang ingin di-scrape
GROUP_INPUTS = [
    "https://web.facebook.com/groups/183039928416039?locale=id_ID",
    "https://web.facebook.com/groups/teraswarga?locale=id_ID",
    "https://web.facebook.com/groups/967901979894945?locale=id_ID"
]

# lokasi hasil scraping
OUTPUT_CSV = f"facebook_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
OUTPUT_JSON = f"facebook_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# ========== SETUP SELENIUM ==========
options = uc.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options, use_subprocess=True)
wait = WebDriverWait(driver, 15)


# ========== FUNGSI LOGIN ==========
def save_cookies(driver, path):
    with open(path, "w") as file:
        json.dump(driver.get_cookies(), file)


def load_cookies(driver, path):
    with open(path, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def fb_login(force=False):
    """
    force=True akan memaksa login pakai username/password
    walaupun ada cookies.
    """
    driver.get("https://www.facebook.com/")
    time.sleep(3)

    if not force and os.path.exists(COOKIES_FILE):
        try:
            load_cookies(driver, COOKIES_FILE)
            driver.refresh()
            time.sleep(5)
            if "login" not in driver.current_url:
                print("✅ Login pakai cookies berhasil")
                # pastikan search bar muncul sebelum keluar
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cari di Facebook"]')))
                    print("🔍 Search bar tersedia, siap mencari grup")
                except:
                    print("⚠️ Search bar belum muncul, tetap lanjutkan")
                return
        except Exception as e:
            print("⚠️ Cookies gagal dipakai:", e)

    print("🔑 Login manual pakai username/password...")

    # --- Login form handling ---
    try:
        # versi klasik (id=email, id=pass)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        pass_input = driver.find_element(By.ID, "pass")
        email_input.clear()
        email_input.send_keys(FB_USERNAME)
        pass_input.clear()
        pass_input.send_keys(FB_PASSWORD)
        driver.find_element(By.NAME, "login").click()
    except Exception:
        try:
            # versi dinamis (_r_s_, _r_17_)
            email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="email" and @type="text"]')))
            pass_input = driver.find_element(By.XPATH, '//input[@name="pass" and @type="password"]')
            email_input.clear()
            email_input.send_keys(FB_USERNAME)
            pass_input.clear()
            pass_input.send_keys(FB_PASSWORD)
            pass_input.submit()
        except Exception:
            try:
                # versi lain (data-testid)
                email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-testid="royal-email"]')))
                pass_input = driver.find_element(By.XPATH, '//input[@data-testid="royal-pass"]')
                email_input.clear()
                email_input.send_keys(FB_USERNAME)
                pass_input.clear()
                pass_input.send_keys(FB_PASSWORD)
                driver.find_element(By.NAME, "login").click()
            except Exception as e:
                raise Exception(f"❌ Tidak menemukan form login yang cocok: {e}")

    time.sleep(5)
    if "login" in driver.current_url:
        raise Exception("❌ Login gagal! Cek username/password")

    save_cookies(driver, COOKIES_FILE)
    print("✅ Login sukses & cookies disimpan")

    # setelah login sukses, pastikan search bar ada
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cari di Facebook"]')))
        print("🔍 Search bar tersedia, siap mencari grup")
    except:
        print("⚠️ Search bar belum muncul, coba manual redirect ke beranda")
        driver.get("https://www.facebook.com/")
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cari di Facebook"]')))


def ensure_logged_in():
    """Cek apakah user masih login, kalau muncul halaman login atau popup, login ulang."""
    try:
        # --- Kasus URL berubah ke login page ---
        if driver.current_url and "login" in driver.current_url:
            print("⚠️ Redirect ke halaman login, mencoba login ulang...")
            fb_login(force=True)
            return

        # --- Kasus popup 'See more on Facebook' muncul ---
        try:
            popup = driver.find_element(By.XPATH, '//div[contains(text(),"See more on Facebook")]')
            if popup.is_displayed():
                print("⚠️ Popup login terdeteksi, login ulang...")
                fb_login(force=True)
                return
        except:
            pass

        # --- Kasus ada input email/password nongol di modal ---
        try:
            login_modal = driver.find_element(By.XPATH, '//input[@type="email" or @type="text"]')
            if login_modal.is_displayed():
                print("⚠️ Form login modal terdeteksi, login ulang...")
                fb_login(force=True)
                return
        except:
            pass

    except Exception as e:
        print("⚠️ Gagal cek login:", e)

# ========== SEARCH & BUKA GRUP ==========
def open_group(group_input):
    """
    Bisa menerima nama grup ATAU link grup langsung.
    """
    # --- Kasus: input berupa link langsung ---
    if group_input.startswith("http"):
        print(f"🔗 Buka langsung link grup: {group_input}")
        driver.get(group_input)
        time.sleep(5)

        ensure_logged_in()
        return group_input

    # --- Kasus: input berupa nama grup ---
    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cari di Facebook"]'))
        )
        print(f"🔍 Mencari grup '{group_input}' via search...")
        search_box.clear()
        search_box.send_keys(group_input)
        search_box.submit()
        time.sleep(5)

        # cari hasil grup dengan nama persis
        link = None
        results = driver.find_elements(By.XPATH, f'//a[contains(text(),"{group_input}")]')
        if results:
            link = results[0].get_attribute("href")

        if link:
            print(f"✅ Grup ditemukan: {link}")
            driver.get(link)
            time.sleep(5)
            return link
        else:
            print(f"❌ Grup '{group_input}' tidak ditemukan via search")
            return None

    except Exception as e:
        print(f"⚠️ Search gagal untuk '{group_input}':", e)
        return None

def scroll_to_bottom(driver, max_scrolls=10, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ========== SCRAPING POSTINGAN GRUP ==========
def scrape_group(group_url, group_name, max_scrolls=3, max_posts=None):
    print(f"📥 Scraping grup: {group_name} ({group_url})")
    driver.get(group_url)
    time.sleep(4)
    ensure_logged_in()

    posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    for scroll_round in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        ensure_logged_in()

        post_elements = driver.find_elements(By.XPATH, '//div[@role="article"]')
        print(f"🔎 Ditemukan {len(post_elements)} postingan pada scroll {scroll_round+1}")

        for idx, post in enumerate(post_elements):
            if max_posts and len(posts) >= max_posts:
                break

            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(1)

                # --- article_ctx: konteks utama artikel/post ---
                article_ctx = None
                try:
                    # Biasanya post itu sendiri sudah konteks utama
                    article_ctx = post
                except:
                    article_ctx = None

                # --- permalink & buka halaman post ---
                permalink = None
                post_context = post  # default fallback ke post list

                try:
                    # coba ambil link /posts/
                    link_el = post.find_element(By.XPATH, ".//a[contains(@href,'/posts/')]")
                    permalink = link_el.get_attribute("href").split("?")[0]
                except:
                    try:
                        # coba ambil link /permalink/
                        link_el = post.find_element(By.XPATH, ".//a[contains(@href,'/permalink/')]")
                        permalink = link_el.get_attribute("href").split("?")[0]
                    except:
                        try:
                            # fallback ambil ID dari data-ft
                            post_id = post.get_attribute("data-ft")
                            if post_id and "top_level_post_id" in post_id:
                                import json
                                d = json.loads(post_id)
                                pid = d.get("top_level_post_id")
                                if pid:
                                    permalink = f"{group_url.rstrip('/').split('?')[0]}/posts/{pid}/"
                        except:
                            pass

                if not permalink:
                    print("⚠️ Tidak ada permalink & tidak bisa generate. Tetap lanjut simpan data.")
                    permalink = group_url  # fallback isi dengan URL grup

                # --- buka halaman permalink ---
                try:
                    driver.get(permalink)
                    time.sleep(3)
                    ensure_logged_in()

                    # ambil elemen post baru dari halaman permalink
                    post_context = driver.find_element(By.XPATH, "//div[@role='article']")
                except Exception as e:
                    print(f"⚠️ Gagal buka permalink {permalink}: {e}")
                    post_context = None  # jangan pakai lagi elemen lama

                # --- ambil author ---
                author = "Unknown"
                try:
                    if post_context:
                        try:
                            author = post_context.find_element(By.XPATH, ".//h2//span//span").text.strip()
                        except:
                            try:
                                author = post_context.find_element(By.XPATH, ".//strong//span").text.strip()
                            except:
                                author = post_context.find_element(By.XPATH, ".//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1nxh6w3 x1sibtaa x1s688f xi81zsa')]").text.strip()
                except:
                    pass

                # --- expand komentar ---
                while True:
                    try:
                        btn = post.find_element(By.XPATH, ".//span[contains(text(),'Lihat komentar') or contains(text(),'View more comments')]")
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                    except:
                        break

                while True:
                    try:
                        btn = post.find_element(By.XPATH, ".//span[contains(text(),'Lihat') and contains(text(),'balasan')] | .//span[contains(text(),'View') and contains(text(),'replies')]")
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                    except:
                        break

                # --- ambil caption & komentar dari post_context ---
                if post_context:
                    try:
                        caption_blocks = post_context.find_elements(By.XPATH, ".//div[@data-ad-rendering-role='story_message']//div[@dir='auto']")
                        caption_texts = [cb.text.strip() for cb in caption_blocks if cb.text.strip()]
                        caption = "\n".join(caption_texts)[:2000] if caption_texts else ""
                    except:
                        caption = ""

                    # ambil komentar
                    comments = []
                    try:
                        comment_blocks = post_context.find_elements(By.XPATH, ".//div[@aria-label='Komentar']//div[@dir='auto']")
                        seen = set()
                        for cb in comment_blocks:
                            text = cb.text.strip()
                            if text and text not in seen:
                                seen.add(text)
                                comments.append(text)
                    except:
                        comments = []

                data = {
                    "group_name": group_name,
                    "group_url": group_url,
                    "post_url": permalink,
                    "author": author,
                    "caption": caption,
                    "comments": comments,
                }
                print(f"✅ Post captured: {author} | {caption[:60]}... | {len(comments)} komentar")
                posts.append(data)

            except Exception as e:
                print(f"⚠️ Error baca postingan {idx}: {e}")
                continue

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return posts

# ========== MAIN ==========
all_data = []

fb_login()

for g in GROUP_INPUTS:
    group_url = open_group(g)
    if group_url:
        posts = scrape_group(group_url, g)
        all_data.extend(posts)

# simpan ke CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["group_name", "group_url", "post_url", "author", "caption", "comments"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_data:
        writer.writerow(row)

# simpan ke JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"✅ Selesai. Data disimpan ke {OUTPUT_CSV} dan {OUTPUT_JSON}")
try:
    driver.quit()
except:
    pass
