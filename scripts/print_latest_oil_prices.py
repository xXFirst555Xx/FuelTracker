import json
import requests

API_URL = "https://api.chnwt.dev/thai-oil-api/latest"


def main() -> None:
    resp = requests.get(API_URL, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
