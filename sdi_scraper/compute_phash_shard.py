"""
compute_phash_shard.py
------------------------
One shard of the phash computation job. Takes a shard index and total
shard count, processes only the images assigned to this shard (by simple
modulo split), and writes its own partial cache file. Run several shards
in parallel (separate processes/browsers) for speed, then merge with
merge_phash_shards.py.

IMPORTANT: hashes must be computed with the EXACT same algorithm the
browser uses at search time (build_inv_10b.py's computeDHashFromImage),
or catalog hashes won't match user-uploaded-photo hashes closely enough
to be useful. PIL's LANCZOS resize and a <canvas> drawImage() downscale
produce meaningfully different pixel values at this tiny 10x9 target
size, so this script runs the real browser canvas algorithm (via
Playwright) instead of PIL, guaranteeing pixel-for-pixel parity.

Usage:
    python compute_phash_shard.py <shard_index> <total_shards>
"""
import json
import sys
import time
import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ENRICHED_FILE = HERE / "enriched_parts.json"
MANUAL_OVERRIDES_FILE = HERE / "manual_overrides.json"
HASH_SIZE = 9

# Must stay byte-identical to computeDHashFromImage() in build_inv_10b.py
JS_HASH_FN = """
() => {
  window.__dhash = function(img) {
    const PM_HASH_SIZE = 9;
    const w = PM_HASH_SIZE + 1, h = PM_HASH_SIZE;
    const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
    const ctx = cv.getContext('2d');
    ctx.drawImage(img, 0, 0, w, h);
    const data = ctx.getImageData(0, 0, w, h).data;
    const gray = [];
    for (let i = 0; i < data.length; i += 4) {
      gray.push(0.299*data[i] + 0.587*data[i+1] + 0.114*data[i+2]);
    }
    const bits = [];
    for (let row = 0; row < h; row++) {
      const rowStart = row * w;
      for (let col = 0; col < PM_HASH_SIZE; col++) {
        bits.push(gray[rowStart+col] > gray[rowStart+col+1] ? 1 : 0);
      }
    }
    let val = 0n;
    for (let b = 0; b < bits.length; b++) {
      val = (val << 1n) | BigInt(bits[b]);
    }
    const nbits = PM_HASH_SIZE * PM_HASH_SIZE;
    const hexLen = Math.ceil(nbits / 4);
    return val.toString(16).padStart(hexLen, '0');
  };
}
"""

JS_HASH_URL = """
(dataUrl) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      try { resolve(window.__dhash(img)); }
      catch(e) { reject(String(e)); }
    };
    img.onerror = () => reject('image load failed');
    img.src = dataUrl;
  });
}
"""


def _guess_mime(url):
    u = url.lower()
    if u.endswith('.png'):
        return 'image/png'
    if u.endswith('.gif'):
        return 'image/gif'
    if u.endswith('.webp'):
        return 'image/webp'
    if u.endswith('.bmp'):
        return 'image/bmp'
    return 'image/jpeg'


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


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def main():
    shard_idx = int(sys.argv[1])
    total_shards = int(sys.argv[2])
    out_file = HERE / f"phash_shard{shard_idx}.json"

    enriched = load_json(ENRICHED_FILE, [])
    manual = load_json(MANUAL_OVERRIDES_FILE, {})

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

    all_urls = sorted(targets.keys())
    my_urls = [u for i, u in enumerate(all_urls) if i % total_shards == shard_idx]

    cache = load_json(out_file, {})
    to_process = [u for u in my_urls if u not in cache]

    print(f"[shard {shard_idx}] {len(my_urls)} assigned, {len(to_process)} remaining to process.")

    ok = 0
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROMIUM_EXECUTABLE)
        fetch_page = browser.new_page(ignore_https_errors=True)
        hash_page = browser.new_page(ignore_https_errors=True)
        hash_page.evaluate(JS_HASH_FN)

        for i, url in enumerate(to_process, 1):
            pno = targets[url]
            try:
                resp = fetch_page.goto(url, timeout=15000)
                if not (resp and resp.ok):
                    raise RuntimeError(f"HTTP {resp.status if resp else '?'}")
                img_bytes = resp.body()
                b64 = base64.b64encode(img_bytes).decode('ascii')
                data_url = f"data:{_guess_mime(url)};base64,{b64}"
                h = hash_page.evaluate(JS_HASH_URL, data_url)
                cache[url] = {"hash": h, "pno": pno}
                ok += 1
            except Exception as e:
                cache[url] = {"hash": None, "pno": pno, "error": str(e)[:120]}
                fail += 1

            if i % 25 == 0 or i == len(to_process):
                print(f"[shard {shard_idx}] [{time.strftime('%H:%M:%S')}] {i}/{len(to_process)} "
                      f"(ok={ok}, fail={fail})")
                out_file.write_text(json.dumps(cache, indent=0), encoding="utf-8")

        browser.close()

    out_file.write_text(json.dumps(cache, indent=0), encoding="utf-8")
    print(f"[shard {shard_idx}] DONE. {ok} hashed, {fail} failed.")


if __name__ == "__main__":
    main()
