import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

# Load URLs from JSON
with open('urls.json', 'r') as f:
    urls = json.load(f)['urls']

# Output base folder
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
base_output_dir = os.path.join('output', timestamp)
os.makedirs(base_output_dir, exist_ok=True)

def sanitize_filename(url):
    filename = re.sub(r'^https?://', '', url)
    return re.sub(r'[^\w\-_.]', '_', filename)

def download_asset(asset_url, save_dir):
    try:
        response = requests.get(asset_url, timeout=10)
        response.raise_for_status()
        parsed = urlparse(asset_url)
        filename = os.path.basename(parsed.path) or "unnamed"
        output_path = os.path.join(save_dir, filename)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return filename
    except Exception as e:
        print(f"⚠️  Failed to download asset {asset_url}: {e}")
        return None

def scrape_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        urlname = sanitize_filename(url)
        page_dir = os.path.join(base_output_dir, urlname)
        static_dir = os.path.join(page_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)

        final_url = response.url

        # CSS
        for link in soup.find_all('link', href=True):
            if 'stylesheet' in link.get('rel', []):
                full_url = urljoin(final_url, link['href'])
                local_path = download_asset(full_url, static_dir)
                if local_path:
                    link['href'] = local_path

        # JS
        for script in soup.find_all('script', src=True):
            full_url = urljoin(final_url, script['src'])
            local_path = download_asset(full_url, static_dir)
            if local_path:
                script['src'] = local_path

        # Images
        for img in soup.find_all('img', src=True):
            full_url = urljoin(final_url, img['src'])
            local_path = download_asset(full_url, static_dir)
            if local_path:
                img['src'] = local_path


        # Save HTML
        output_file = os.path.join(page_dir, 'index.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        print(f"✅ Saved {url} → {output_file}")
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")

# Run multithreaded
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(scrape_and_save, urls)
