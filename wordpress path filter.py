import requests

def print_json_keys(url, length):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    try:
        data = response.json()
    except ValueError:
        print("Response content is not valid JSON.")
        return
    
    filtered_keys = [k for k in data["routes"].keys() if len(k.split("/")) == length]
    print(filtered_keys)

if __name__ == "__main__":
    domain = "https://example.com"
    url = f"{domain}/wp-json/"
    print_json_keys(url, 3)
    url = f"{domain}/wp-json/wp/v2"
    print_json_keys(url, 4)
