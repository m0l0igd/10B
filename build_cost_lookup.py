import build_10b_inventory as b
import json

client = b.get_bigquery_client()
q = """
SELECT
  item_manufacturer_part_no AS part_no,
  AVG(item_unit_cost) AS avg_unit_cost,
  COUNT(*) AS n
FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_zeus_parts_inventory`
WHERE item_unit_cost > 0
GROUP BY part_no
"""
try:
    rows = list(client.query(q).result())
    print(f"Got {len(rows)} distinct part-cost rows")
    lookup = {r.part_no: round(float(r.avg_unit_cost), 4) for r in rows if r.part_no}
    with open("cost_lookup.json", "w", encoding="utf-8") as f:
        json.dump(lookup, f)
    print(f"Saved {len(lookup)} entries to cost_lookup.json")
except Exception as e:
    print("ERROR:", e)
