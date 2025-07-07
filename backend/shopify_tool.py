import os
import requests
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
import json

load_dotenv()

# ✅ Load from .env
SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")  # Should be: clevrr-test.myshopify.com
API_VERSION = os.getenv("SHOPIFY_API_VERSION")  # Should be: 2025-04
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def get_shopify_data(resource, params=None, store_url=None, max_retries=5):
    if params is None:
        params = {}

    # ✅ If resource is accidentally JSON string
    if isinstance(resource, str) and resource.startswith('{'):
        try:
            parsed_data = json.loads(resource)
            resource = parsed_data.get('resource', 'orders')
            params = parsed_data.get('params', {})
            store_url = parsed_data.get('store_url', store_url)
        except json.JSONDecodeError:
            pass  # fallback to original resource string

    # ✅ Use correct shop name
    shop_name = store_url if store_url else SHOP_NAME

    # ✅ Fix formatting
    if shop_name:
        shop_name = shop_name.replace("https://", "").replace("http://", "")
        if not shop_name.endswith(".myshopify.com"):
            shop_name += ".myshopify.com"

    # ✅ Use correct version
    api_version = API_VERSION or "2025-04"

    # ✅ Construct final URL
    base_url = f"https://{shop_name}/admin/api/{api_version}"
    url = f"{base_url}/{resource}.json"

    print(f"\n🟡 Shopify Request Details:")
    print(f"🔗 URL: {url}")
    print(f"🔐 Token present: {'Yes' if ACCESS_TOKEN else 'No'}")
    print(f"📦 Params: {params}")
    print(f"🔧 Headers: {HEADERS}\n")

    results = []
    retries = 0

    while url:
        try:
            response = requests.get(url, headers=HEADERS, params=params)

            print(f"📥 Response status: {response.status_code}")

            if response.status_code == 429:
                if retries < max_retries:
                    wait = 2 ** retries
                    print(f"⏳ Rate limited, waiting {wait} seconds...")
                    time.sleep(wait)
                    retries += 1
                    continue
                else:
                    raise Exception("Rate limit exceeded, retries failed.")

            if response.status_code == 401:
                raise Exception("❌ Unauthorized: Check your Shopify access token")

            if response.status_code == 404:
                raise Exception(f"❌ Not found: Check your shop name and API version. URL: {url}")

            response.raise_for_status()
            data = response.json()

            key = resource.split("/")[-1]
            if not key.endswith('s'):
                key += 's'

            if key in data:
                results.extend(data[key])
            else:
                print(f"⚠️ Warning: Expected key '{key}' not in response. Returning raw data.")
                return data

            # Pagination support
            link = response.headers.get('Link')
            if link and 'rel="next"' in link:
                next_url = [l for l in link.split(',') if 'rel="next"' in l][0]
                next_url = next_url[next_url.find('<')+1:next_url.find('>')]
                url = next_url
                params = {}
            else:
                url = None

        except requests.exceptions.RequestException as e:
            raise Exception(f"Shopify API request error: {e}")
        except Exception as e:
            raise Exception(f"Shopify API error: {e}")

    return results