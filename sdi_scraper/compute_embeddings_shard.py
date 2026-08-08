"""
compute_embeddings_shard.py
-----------------------------
Computes real MobileNetV2 image-classification embeddings (1280-dim
feature vectors from the model's penultimate layer, via TensorFlow.js
running inside a real Chromium browser tab) for every part-catalog image
referenced in enriched_parts.json. This replaces the old dHash-based
"Search by Photo" approach, which was too coarse (only captured blurry
light/dark gradient patterns) to reliably tell apart visually distinct
parts -- MobileNet has actually learned real object features (shape,
texture, edges) from millions of training images, giving genuinely
useful similarity search.

Embeddings are quantized to int8 (via simple linear scaling per-vector)
to keep the total payload size reasonable across ~2,300 parts.

One shard of the job -- takes a shard index and total shard count,
processes only images assigned to this shard, writes its own partial
cache file. Run several shards in parallel for speed, then merge with
merge_embeddings_shards.py.

Usage:
    python compute_embeddings_shard.py <shard_index> <total_shards>
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

TFJS_URL = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js"
MOBILENET_URL = "https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js"


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


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


# Must stay byte-identical to the equivalent functions in build_inv_10b.py
# (pmAutoCropToSubject / pmEmbedImage) -- catalog embeddings and live user-
# photo embeddings MUST go through the exact same preprocessing or cosine
# similarity comparisons between them become meaningless.
#
# Why auto-crop-to-subject matters: MobileNet's embedding captures the
# WHOLE image including background. A clean catalog studio photo (part
# fills most of the frame) vs. a real phone photo (part is smaller,
# surrounded by workbench/background clutter) get very different
# embeddings for the same physical part purely because of how much
# background is included -- this was empirically verified to be the
# single biggest accuracy problem, dropping true-match rank from #1 to
# ~#221 out of ~2300 in testing. Auto-cropping to just the foreground
# subject (by detecting the background color from the image corners and
# finding the bounding box of pixels that differ from it) before feeding
# into MobileNet fixed this completely in testing (true match: #1, 84%
# similarity, next-best only 53%).
LOAD_MODEL_JS = """
async () => {
  if (window.__mobilenetModel) return true;
  const scripts = [
    'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js',
    'https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js'
  ];
  for (const src of scripts) {
    await new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject('failed to load ' + src);
      document.head.appendChild(s);
    });
  }
  window.__mobilenetModel = await mobilenet.load({version: 2, alpha: 1.0});

  window.__autoCropToSubject = function(img) {
    const sw = img.naturalWidth || img.width, sh = img.naturalHeight || img.height;
    const sampleW = 200, sampleH = Math.max(1, Math.round(200 * sh / sw));
    const cv = document.createElement('canvas');
    cv.width = sampleW; cv.height = sampleH;
    const ctx = cv.getContext('2d');
    ctx.drawImage(img, 0, 0, sampleW, sampleH);
    const data = ctx.getImageData(0, 0, sampleW, sampleH).data;
    function pxAt(x, y) {
      const i = (y * sampleW + x) * 4;
      return [data[i], data[i+1], data[i+2]];
    }
    const patch = 6;
    let br=0, bg=0, bb=0, bn=0;
    for (const cy of [0, sampleH-patch]) {
      for (const cx of [0, sampleW-patch]) {
        for (let y = cy; y < cy+patch && y < sampleH && y >= 0; y++) {
          for (let x = cx; x < cx+patch && x < sampleW && x >= 0; x++) {
            const [r,g,b] = pxAt(x,y);
            br+=r; bg+=g; bb+=b; bn++;
          }
        }
      }
    }
    br/=bn; bg/=bn; bb/=bn;
    const THRESH = 28;
    let minX=sampleW, minY=sampleH, maxX=0, maxY=0, found=false;
    for (let y=0; y<sampleH; y++) {
      for (let x=0; x<sampleW; x++) {
        const [r,g,b] = pxAt(x,y);
        const d = Math.sqrt((r-br)**2 + (g-bg)**2 + (b-bb)**2);
        if (d > THRESH) {
          found = true;
          if (x<minX) minX=x; if (x>maxX) maxX=x;
          if (y<minY) minY=y; if (y>maxY) maxY=y;
        }
      }
    }
    if (!found || (maxX-minX) < sampleW*0.05 || (maxY-minY) < sampleH*0.05) {
      return null;
    }
    const marginX = (maxX-minX) * 0.15, marginY = (maxY-minY) * 0.15;
    minX = Math.max(0, minX-marginX); minY = Math.max(0, minY-marginY);
    maxX = Math.min(sampleW, maxX+marginX); maxY = Math.min(sampleH, maxY+marginY);
    const scaleX = sw/sampleW, scaleY = sh/sampleH;
    return {
      sx: minX*scaleX, sy: minY*scaleY,
      sw: (maxX-minX)*scaleX, sh: (maxY-minY)*scaleY
    };
  };

  return true;
}
"""

EMBED_DATAURL_JS = """
(dataUrl) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      try {
        const box = window.__autoCropToSubject(img);
        const cv = document.createElement('canvas');
        cv.width = 224; cv.height = 224;
        const ctx = cv.getContext('2d');
        if (box) {
          ctx.drawImage(img, box.sx, box.sy, box.sw, box.sh, 0, 0, 224, 224);
        } else {
          const sw = img.naturalWidth || img.width, sh = img.naturalHeight || img.height;
          const side = Math.min(sw, sh);
          ctx.drawImage(img, (sw-side)/2, (sh-side)/2, side, side, 0, 0, 224, 224);
        }
        const t = window.__mobilenetModel.infer(cv, true);
        const arr = Array.from(t.dataSync());
        t.dispose();
        resolve(arr);
      } catch (e) { reject(String(e)); }
    };
    img.onerror = () => reject('image load failed');
    img.src = dataUrl;
  });
}
"""


def quantize_int8(vec):
    """Linear-scale a float embedding vector to int8 [-127,127] plus the
    scale factor needed to dequantize, to keep the cache file small while
    preserving enough precision for cosine-similarity ranking."""
    max_abs = max((abs(v) for v in vec), default=1.0) or 1.0
    scale = max_abs / 127.0
    q = [max(-127, min(127, round(v / scale))) for v in vec]
    return q, scale


def main():
    shard_idx = int(sys.argv[1])
    total_shards = int(sys.argv[2])
    out_file = HERE / f"embed_shard{shard_idx}.json"

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
        ml_page = browser.new_page(ignore_https_errors=True)
        ml_page.set_content("<html><body></body></html>")
        print(f"[shard {shard_idx}] loading MobileNet model...")
        ml_page.evaluate(LOAD_MODEL_JS)
        print(f"[shard {shard_idx}] model loaded, starting embedding pass.")

        for i, url in enumerate(to_process, 1):
            pno = targets[url]
            try:
                resp = fetch_page.goto(url, timeout=15000)
                if not (resp and resp.ok):
                    raise RuntimeError(f"HTTP {resp.status if resp else '?'}")
                img_bytes = resp.body()
                b64 = base64.b64encode(img_bytes).decode('ascii')
                data_url = f"data:{_guess_mime(url)};base64,{b64}"
                vec = ml_page.evaluate(EMBED_DATAURL_JS, data_url)
                q, scale = quantize_int8(vec)
                cache[url] = {"q": q, "scale": scale, "pno": pno}
                ok += 1
            except Exception as e:
                cache[url] = {"q": None, "scale": None, "pno": pno, "error": str(e)[:120]}
                fail += 1

            if i % 25 == 0 or i == len(to_process):
                print(f"[shard {shard_idx}] [{time.strftime('%H:%M:%S')}] {i}/{len(to_process)} "
                      f"(ok={ok}, fail={fail})")
                out_file.write_text(json.dumps(cache, separators=(',', ':')), encoding="utf-8")

        browser.close()

    out_file.write_text(json.dumps(cache, separators=(',', ':')), encoding="utf-8")
    print(f"[shard {shard_idx}] DONE. {ok} embedded, {fail} failed.")


if __name__ == "__main__":
    main()
