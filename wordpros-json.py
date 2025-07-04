import threading
import json
import time
import sys
from urllib.parse import urljoin
import requests


def fetch_json(url):
    if not url.startswith("http"):
        url = f"https://{url}"

    url = url.replace("http://", "https://")  # this line was ineffective before

    try:
        response = requests.get(url, timeout=10)
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response
    except Exception as e:
        return f"ERR: {e}"

    # Fallback: try index.json
    if url.endswith("/"):
        fallback_url = url + "index.json"
    else:
        fallback_url = url + "/index.json"

    try:
        response = requests.get(fallback_url, timeout=10)
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response
    except Exception as e:
        return f"ERR (fallback): {e}"

    return None


def print_result(status, url, extra=""):
    print(f"[{status}] {url} - {extra}")

def attacks(resp,status,full_url,base_url, index_url):
    print(full_url,base_url, index_url)
    data = f"Length: {len(resp.content)}"
    print_result(status, full_url, data)

    if "oembed/1.0/embed" in full_url:
        embed_url = urljoin(index_url, f"oembed/1.0/embed?url={base_url}&format=json")
        embed_resp = fetch_json(embed_url)
        if embed_resp:
            print_result(embed_resp.status_code, embed_url, f"Length: {len(embed_resp.content)}")
    elif "wp/v2/users" in full_url:
        users_url = urljoin(index_url, "wp/v2/users/?page=1")
        users_resp = fetch_json(users_url)
        if users_resp:
            print_result(users_resp.status_code, users_url, f"Users: {len(users_resp.json()) if users_resp.ok else 'N/A'}")

def print_default_blob_info(json_out):
    # print(json_out.keys())
    # print(json_out["routes"].keys())
    print(f"name: {json_out['name']}")
    print(f"description: {description}") if (description := json_out.get('description')) else None
    print(f"namespaces: {namespace}") if (namespace := json_out.get('namespaces')) else None
    print(f"authentication: {auth}") if (auth := json_out.get('authentication')) else None

    print(f"[+] Found {len(json_out['routes'])} routes.\n")


def dostuffonstatus(resp, full_url, base_url, index_url, show_all):
    status = resp.status_code
    data = ""
    if status == 200:
        attacks(resp,status,full_url,base_url, index_url)
    elif status == 400:
        try:
            json_data = resp.json()
            if isinstance(json_data, dict) and "data" in json_data and "params" in json_data["data"]:
                params = json_data["data"]["params"]
                data = f"Params: {params}"
        except:
            data = "Could not parse JSON params"

        print_result(status, full_url, data)

    elif show_all:
        print_result(status, full_url, f"Length: {len(resp.content)}")

def spinner_task(stop_event):
    spinner = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\rProcessing... {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\rDone!           \n")
    sys.stdout.flush()


def main(base_url, show_all=False):
    base_url = base_url.rstrip("/")
    index_url = base_url + "/wp-json/"
    print(f"[i] Fetching API index: {index_url}")

    root_response = fetch_json(index_url)

    json_output = root_response.json()
    if not root_response or not root_response.ok or "routes" not in json_output:
        print_result("ERR48", index_url, "No valid WP REST API 'routes' found.")
        return

    print_default_blob_info(json_output)

    routes = json_output["routes"]

    for route in routes:
        if not route.startswith("/"): continue

        full_url = urljoin(index_url, route.lstrip("/"))
        resp = fetch_json(full_url)

        if isinstance(resp, str):
            if show_all:
                print_result("ERR", full_url, resp)
            continue

        if resp is None:
            if show_all:
                print_result("ERR", full_url, "No response")
            continue

        dostuffonstatus(resp, full_url, base_url, index_url, show_all)

def run_with_spinner(url, show_all):
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_spinner,))
    spinner_thread.start()
    try:
        main(url, show_all)
    finally:
        stop_spinner.set()
        spinner_thread.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wp_routes.py <url> [--all]")
        print("  python wp_routes.py --input file.json [--all]")
        sys.exit(1)

    show_all = "--all" in sys.argv

    if "--input" in sys.argv:
        try:
            input_index = sys.argv.index("--input")
            input_file = sys.argv[input_index + 1]
        except IndexError:
            print("[ERR] --input requires a filename.")
            sys.exit(1)

        try:
            with open(input_file, 'r', encoding="utf-8") as f:
                urls = json.load(f)
        except Exception as e:
            print(f"[ERR] Failed to load JSON file: {e}")
            sys.exit(1)

        if not isinstance(urls, list):
            print("[ERR] JSON file must contain a list of URLs.")
            sys.exit(1)

        for url in urls:
            print(f"\n[i] Processing: {url}")
            run_with_spinner(url, show_all)

    else:
        base_url = sys.argv[1]
        run_with_spinner(base_url, show_all)
