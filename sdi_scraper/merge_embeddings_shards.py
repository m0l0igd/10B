"""
merge_embeddings_shards.py
-----------------------------
Combines all embed_shard*.json files into the single embeddings_cache.json
that build_10b_inventory.py reads and embeds into the page's lazy-loaded
Search-by-Photo data file.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "embeddings_cache.json"


def main():
    merged = {}
    shard_files = sorted(HERE.glob("embed_shard*.json"))
    print(f"Found {len(shard_files)} shard files.")
    for sf in shard_files:
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            merged.update(data)
            print(f"  {sf.name}: {len(data)} entries")
        except Exception as e:
            print(f"  {sf.name}: FAILED to load ({e})")

    ok = sum(1 for v in merged.values() if v.get("q"))
    fail = len(merged) - ok
    OUT.write_text(json.dumps(merged, separators=(',', ':')), encoding="utf-8")
    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Merged {len(merged)} total entries ({ok} with valid embedding, {fail} failed) "
          f"-> {OUT} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
