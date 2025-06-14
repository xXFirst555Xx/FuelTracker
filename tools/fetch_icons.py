import urllib.request, pathlib

ICON_NAMES = ["home", "plus-square", "bar-chart-2", "settings"]
BASE_URL = "https://raw.githubusercontent.com/feathericons/feather/main/icons/"
icons_dir = pathlib.Path(__file__).resolve().parents[1] / "assets" / "icons"
icons_dir.mkdir(parents=True, exist_ok=True)

for name in ICON_NAMES:
    url = f"{BASE_URL}{name}.svg"
    dest = icons_dir / f"{name}.svg"
    if not dest.exists():
        print("\u2193 downloading", url)
        urllib.request.urlretrieve(url, dest)
print("\u2713 all icons ready at", icons_dir)
