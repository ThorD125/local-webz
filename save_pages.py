import hashlib
import os
import json
import requests
import threading
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib
import hashlib
import re

# CONFIG
OUTPUT_DIR = "./output"
NUM_THREADS = 5
HEADERS = {"User-Agent": "Mozilla/5.0"}

def timestamp_folder():
    return time.strftime("%Y-%m-%d_%H-%M-%S")

def sanitize_url(url):
    return urlparse(url).netloc.replace('.', '-') + urlparse(url).path.replace('/', '-').strip('-')


def flatten_filename(url):
    """Flatten full asset URL path into a safe filename."""
    parsed = urlparse(url)
    path = parsed.path or ""
    name = path.strip("/").replace("/", "_")

    # Add file extension if missing
    if not os.path.splitext(name)[1]:
        name += ".bin"

    # Add hash to avoid name collisions
    hash_suffix = hashlib.md5(url.encode()).hexdigest()[:8]
    name, ext = os.path.splitext(name)
    return f"{name}_{hash_suffix}{ext}"

def download_asset(session, base_url, tag, attr, asset_dir):
    src = tag.get(attr)
    if not src or src.startswith("data:"):
        return

    full_url = urljoin(base_url, src)
    try:
        response = session.get(full_url, timeout=10)
        response.raise_for_status()

        filename = flatten_filename(full_url)
        asset_path = os.path.join(asset_dir, filename)

        with open(asset_path, "wb") as f:
            f.write(response.content)

        # ✅ This is crucial: directly update the tag
        tag[attr] = filename

        # Optional: log to confirm
        print(f"[✓] {tag.name} asset replaced: {src} → {filename}")
    except Exception as e:
        print(f"[!] Failed to download {full_url}: {e}")



def scrape_page(session, url, base_output):
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        asset_dir = Path(base_output)
        asset_dir.mkdir(parents=True, exist_ok=True)

        for tag in soup.find_all(["script", "link", "img"]):
            if tag.name == "script" and tag.get("src"):
                download_asset(session, response.url, tag, "src", asset_dir)
            elif tag.name == "link" and "stylesheet" in (tag.get("rel") or []):
                download_asset(session, response.url, tag, "href", asset_dir)
            elif tag.name == "img" and tag.get("src"):
                download_asset(session, response.url, tag, "src", asset_dir)


        output_html = soup.prettify()
        with open(asset_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(output_html)

        print(f"[+] Saved {url}")
    except Exception as e:
        print(f"[!] Error scraping {url}: {e}")


def worker(urls, base_folder):
    session = requests.Session()
    session.headers.update(HEADERS)
    while urls:
        url = urls.pop()
        folder = os.path.join(base_folder, sanitize_url(url))
        scrape_page(session, url, folder)

def main():
    with open("urls.json", "r") as f:
        url_list = json.load(f)

    timestamped_dir = os.path.join(OUTPUT_DIR, timestamp_folder())
    os.makedirs(timestamped_dir, exist_ok=True)

    urls = url_list.copy()
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(urls, timestamped_dir))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("[✓] All done.")

if __name__ == "__main__":
    main()
