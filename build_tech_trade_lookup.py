import sys, json
sys.path.insert(0, r"C:\Users\Public\10B")
from build_10b_inventory import get_bigquery_client

client = get_bigquery_client()

q = """
SELECT
  gm_technician_name AS gm,
  hvacr_technician_name AS hvacr,
  food_equipment_technician_name AS fe,
  COUNT(*) AS n
FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_zeus_parts`
WHERE fs_region = '10B'
GROUP BY gm, hvacr, fe
"""
rows = list(client.query(q).result())
print(f"Got {len(rows)} distinct (gm, hvacr, fe) combos for 10B")

from collections import defaultdict
votes = defaultdict(lambda: defaultdict(int))  # tech_name_upper -> {trade: weight}

for r in rows:
    if r.gm:
        votes[r.gm.strip().upper()]['GM'] += r.n
    if r.hvacr:
        votes[r.hvacr.strip().upper()]['HVACR'] += r.n
    if r.fe:
        votes[r.fe.strip().upper()]['FE'] += r.n

tech_to_trade = {}
conflicts = []
_JUNK_NAMES = {'1', '', '366-A-FE', '366-A-FS', '367-A-FS'}
for tech, trade_votes in votes.items():
    if not tech or tech in _JUNK_NAMES:
        continue
    if len(trade_votes) > 1:
        conflicts.append((tech, dict(trade_votes)))
    best_trade = max(trade_votes.items(), key=lambda kv: kv[1])[0]
    tech_to_trade[tech] = best_trade

print(f"Built trade mapping for {len(tech_to_trade)} distinct technicians")
print(f"Techs appearing under >1 trade column (took majority vote): {len(conflicts)}")
for c in conflicts[:10]:
    print("  ", c)

with open(r"C:\Users\Public\10B\tech_to_trade.json", "w", encoding="utf-8") as f:
    json.dump(tech_to_trade, f, indent=2, sort_keys=True)
print("Saved tech_to_trade.json")

trade_counts = defaultdict(int)
for v in tech_to_trade.values():
    trade_counts[v] += 1
print("Trade distribution:", dict(trade_counts))
