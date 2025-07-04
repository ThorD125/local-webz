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
    print(json_out.keys())
    print(f"name: {json_out['name']}")
    print(f"description: {description}") if (description := json_out.get('description')) else None
    print(f"namespaces: {namespace}") if (namespace := json_out.get('namespaces')) else None
    print(f"authentication: {auth}") if (auth := json_out.get('authentication')) else None

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
    print(f"[+] Found {len(routes)} routes.\n")

    for route in routes:
        if not route.startswith("/"): continue

        full_url = urljoin(index_url, route.lstrip("/"))
        resp = fetch_json(full_url)

        if isinstance(resp, str):  # error string
            if show_all:
                print_result("ERR", full_url, resp)
            continue

        if resp is None:
            if show_all:
                print_result("ERR", full_url, "No response")
            continue

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wp_routes.py <url> [--all]")
        sys.exit(1)

    the_base_url = sys.argv[1]
    the_show_all = "--all" in sys.argv

    main(the_base_url, the_show_all)
