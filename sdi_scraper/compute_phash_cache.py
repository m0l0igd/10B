"""
compute_phash_cache.py
-----------------------
Downloads every part-catalog image referenced in enriched_parts.json and
computes a perceptual difference-hash (dHash) for each one so the
"Search by Photo" feature on the global search page can do client-side
visual similarity matching without any server/AI backend.

Uses Playwright's browser-based request context to fetch images (this
environment's direct Python network access can't resolve some vendor
image hosts, but a real browser session can).

Caches results in phash_cache.json keyed by image_url so re-runs only
process new/changed images (fast incremental builds).

Usage:
    python compute_phash_cache.py
"""
import json
import time
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ENRICHED_FILE = HERE / "enriched_parts.json"
CACHE_FILE = HERE / "phash_cache.json"
MANUAL_OVERRIDES_FILE = HERE / "manual_overrides.json"

HASH_SIZE = 9  # dHash -> HASH_SIZE*HASH_SIZE bits of signal


def _find_installed_chromium():
    base = Path.home() / "AppData" / "Local" / "ms-playwright"
    if not base.exists():
        return None
    for candidate in sorted(base.glob("chromium-*"), reverse=True):
        for sub in ("chrome-win64", "chrome-win"):
            exe = candidate / sub / "chrome.exe"
            if exe.exists():
                return str(exe)
    return None


CHROMIUM_EXECUTABLE = _find_installed_chromium()


def dhash(image_bytes, hash_size=HASH_SIZE):
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = img.resize((hash_size + 1, hash_size), Image.LANCZOS)
    pixels = list(img.getdata())
    bits = []
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            left = pixels[row_start + col]
            right = pixels[row_start + col + 1]
            bits.append(1 if left > right else 0)
    val = 0
    for b in bits:
        val = (val << 1) | b
    nbits = hash_size * hash_size
    return format(val, f"0{(nbits + 3)//4}x")


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def main():
    enriched = load_json(ENRICHED_FILE, [])
    manual = load_json(MANUAL_OVERRIDES_FILE, {})
    cache = load_json(CACHE_FILE, {})

    targets = {}
    for p in enriched:
        url = p.get("image_url")
        pno = p.get("pno")
        if url and pno:
            targets[url] = pno
    if isinstance(manual, dict):
        for pno, url in manual.items():
            if url:
                targets[url] = pno

    print(f"[{time.strftime('%H:%M:%S')}] {len(targets)} unique images referenced. "
          f"{len(cache)} already cached.")

    to_process = [(url, pno) for url, pno in targets.items() if url not in cache]
    print(f"[{time.strftime('%H:%M:%S')}] {len(to_process)} new/uncached images to hash.")

    if not to_process:
        print("Nothing new to process.")
        return

    ok = 0
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROMIUM_EXECUTABLE)
        page = browser.new_page(ignore_https_errors=True)

        for i, (url, pno) in enumerate(to_process, 1):
            try:
                resp = page.goto(url, timeout=15000)
                if resp and resp.ok:
                    img_bytes = resp.body()
                    h = dhash(img_bytes)
                    cache[url] = {"hash": h, "pno": pno}
                    ok += 1
                else:
                    cache[url] = {"hash": None, "pno": pno, "error": f"HTTP {resp.status if resp else '?'}"}
                    fail += 1
            except Exception as e:
                cache[url] = {"hash": None, "pno": pno, "error": str(e)[:120]}
                fail += 1

            if i % 50 == 0 or i == len(to_process):
                print(f"[{time.strftime('%H:%M:%S')}] {i}/{len(to_process)} processed "
                      f"(ok={ok}, fail={fail})")
                CACHE_FILE.write_text(json.dumps(cache, indent=0), encoding="utf-8")

        browser.close()

    CACHE_FILE.write_text(json.dumps(cache, indent=0), encoding="utf-8")
    print(f"[{time.strftime('%H:%M:%S')}] Done. {ok} hashed, {fail} failed. "
          f"Cache saved to {CACHE_FILE}")


if __name__ == "__main__":
    main()
