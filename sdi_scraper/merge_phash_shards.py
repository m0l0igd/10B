"""
merge_phash_shards.py
-----------------------
Combines all phash_shard*.json files into the single phash_cache.json
that build_10b_inventory.py reads.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "phash_cache.json"


def main():
    merged = {}
    shard_files = sorted(HERE.glob("phash_shard*.json"))
    print(f"Found {len(shard_files)} shard files.")
    for sf in shard_files:
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            merged.update(data)
            print(f"  {sf.name}: {len(data)} entries")
        except Exception as e:
            print(f"  {sf.name}: FAILED to load ({e})")

    ok = sum(1 for v in merged.values() if v.get("hash"))
    fail = len(merged) - ok
    OUT.write_text(json.dumps(merged, indent=0), encoding="utf-8")
    print(f"Merged {len(merged)} total entries ({ok} with valid hash, {fail} failed) -> {OUT}")


if __name__ == "__main__":
    main()
