import sys
sys.path.insert(0, r'C:\Users\Public\10B')
import build_10b_inventory as b
import re, json
from collections import defaultdict

client = b.get_bigquery_client()

SUBS = ['366-A','367-A','368-A','369-A','369-B','370-A','371-A','372-A',
        '373-A','375-A','384-A','385-A','385-B','387-A','387-B']
subs_sql = ",".join(f"'{s}'" for s in SUBS)

query = f"""
SELECT DISTINCT fm_sub_region, fs_manager_name, store_number, store_address, is_active
FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_store_alignment`
WHERE fm_sub_region IN ({subs_sql})
"""
rows = list(client.query(query).result())
print(f"Total rows: {len(rows)}")

active_rows = [r for r in rows if r['is_active']]
print(f"Active rows: {len(active_rows)}")

by_sub = defaultdict(set)
unparsed = []
for r in active_rows:
    addr = r['store_address']
    if not addr:
        continue
    m = re.match(r'^.*?,\s*([A-Za-z .\'()-]+?),\s*([A-Z]{2})\s*\d{5}', addr)
    if m:
        city = m.group(1).strip()
        # Clean parenthetical suffixes like "TUCSON (FT. LOWELL)"
        city = re.sub(r'\s*\(.*?\)\s*', '', city).strip().title()
        state = m.group(2).strip()
        by_sub[r['fm_sub_region']].add((city, state))
    else:
        unparsed.append((r['fm_sub_region'], addr))

print(f"\nUnparsed: {len(unparsed)}")
for u in unparsed[:10]:
    print("  ", u)

print("\nPer sub-market:")
out = {}
for sub in SUBS:
    cs = sorted(by_sub.get(sub, []))
    print(f"{sub}: {cs}")
    out[sub] = sorted([f"{c}, {s}" for c, s in cs])

with open(r'C:\Users\Public\10B\sub_market_cities.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print("\nSaved.")
