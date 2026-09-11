"""
One-off: build a Tech Name -> Manager lookup from BigQuery's cleaned
manager field, so sdi_data_loader.py can assign each SDI-scraped row to
its REAL manager instead of naively trusting SDI's "Subregion" filter
(which is a geography tag, not an org-chart tag -- a tech's truck can be
geo-tagged under a different subregion than the one their manager owns).

Reuses the exact same manager-cleaning rules as build_10b_inventory.py's
main loop (raw_mgr validity checks) so the two stay consistent.
"""
import json
import build_10b_inventory as b

client = b.get_bigquery_client()
query = """
SELECT
  COALESCE(vehicle_tech_full_name, '') AS tech,
  COALESCE(fs_manager_name, '') AS raw_mgr,
  COUNT(*) AS n
FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_zeus_parts_inventory`
WHERE fs_region = '10B' AND vehicle_tech_full_name IS NOT NULL
GROUP BY tech, raw_mgr
"""
rows = list(client.query(query).result())
print(f"Got {len(rows)} distinct (tech, raw_mgr) combos")

# For each tech, pick whichever cleaned manager name appears most often
# across their rows (handles the same stale-tag noise the main build
# already works around).
from collections import defaultdict
tech_mgr_votes = defaultdict(lambda: defaultdict(int))

for r in rows:
    tech = (r.tech or '').strip().upper()
    if not tech:
        continue
    raw_mgr = r.raw_mgr
    if (raw_mgr and raw_mgr != 'NULL'
            and '366-A' not in raw_mgr.upper() and '367-A' not in raw_mgr.upper()
            and 'UNKNOWN' not in raw_mgr.upper()
            and raw_mgr.upper() not in b._ALL_RM_NAMES):
        mgr = raw_mgr.title()
        tech_mgr_votes[tech][mgr] += r.n

tech_to_manager = {}
for tech, votes in tech_mgr_votes.items():
    best_mgr = max(votes.items(), key=lambda kv: kv[1])[0]
    tech_to_manager[tech] = best_mgr

with open('tech_to_manager.json', 'w', encoding='utf-8') as f:
    json.dump(tech_to_manager, f, indent=2, sort_keys=True)

print(f"Saved {len(tech_to_manager)} tech -> manager mappings to tech_to_manager.json")
