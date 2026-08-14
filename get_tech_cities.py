"""
Derives tech_cities.json and store_cities.json for the Region 10B Parts
Inventory dashboards' sidebar (shows each tech's city/state coverage
beneath their name). Re-run this whenever store/tech assignments change
meaningfully, then re-run build_10b_inventory.py to pick up the fresh data.

Source: semantic_fs_store_alignment (re-ods-prod), which has real
store-to-technician assignments across every trade (GM, HVACR, FE,
electrician, plumber, door, generator, landscape, etc.) -- NOT the
parts-inventory table itself, which only has vehicle/tech data for rows
that happen to have a van assigned (no store-level assignment at all for
some sub-markets, e.g. 369-B).

tech_cities.json: {tech_name (title-cased): [sorted "City, ST" strings]}
  -- built by scanning every technician-role name column against every
  active store row and unioning that store's city into the tech's set.
store_cities.json: {store_number: "City, ST"} -- fallback for the
  'WM#1234'-style placeholder "techs" in the dashboard (which are really
  just unassigned store locations, not real people), keyed by bare store
  number so build_10b_inventory.py's resolve_tech_city() can look them up.
"""
import sys
sys.path.insert(0, r'C:\Users\Public\10B')
import build_10b_inventory as b
import re, json
from collections import defaultdict

client = b.get_bigquery_client()

TECH_COLS = [
    'gm_technician_name', 'hvacr_technician_name', 'food_equipment_technician_name',
    'landscape_technician_one_name', 'landscape_technician_two_name',
    'landscape_technician_three_name', 'landscape_technician_four_name',
    'irrigation_tech_one_name', 'irrigation_tech_two_name',
    'parking_lot_sweeping_tech_name', 'generator_tech_one_name',
    'generator_tech_two_name', 'generator_tech_three_name',
    'electrician_tech_one_name', 'electrician_tech_two_name',
    'powerwashing_tech_one_name', 'powerwashing_tech_two_name',
    'portering_tech_one_name', 'portering_tech_two_name',
    'portering_tech_three_name', 'portering_tech_four_name',
    'security_services_tech_name', 'door_tech_name', 'automation_tech_name',
    'licensed_electrician_technician_name', 'licensed_plumber_technician_name',
]
cols_sql = ', '.join(TECH_COLS)

query = f"""
SELECT fm_sub_region, store_number, store_address, {cols_sql}
FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_store_alignment`
WHERE fm_region = '10B' AND is_active = true
"""
rows = list(client.query(query).result())
print(f"Total active store rows: {len(rows)}")

def parse_city_state(addr):
    if not addr:
        return None
    m = re.match(r'^.*?,\s*([A-Za-z .\'()-]+?),\s*([A-Z]{2})\s*\d{5}', addr)
    if not m:
        return None
    city = re.sub(r'\s*\(.*?\)\s*', '', m.group(1)).strip().title()
    state = m.group(2).strip()
    return f"{city}, {state}"

tech_cities = defaultdict(set)
store_cities = {}
for r in rows:
    cs = parse_city_state(r['store_address'])
    if not cs:
        continue
    if r['store_number']:
        store_cities[str(r['store_number']).strip()] = cs
    for col in TECH_COLS:
        name = r[col]
        if name:
            name_clean = re.sub(r'\s+', ' ', name.strip()).title()
            tech_cities[name_clean].add(cs)

print(f"Distinct techs found with city data: {len(tech_cities)}")
print(f"Distinct stores with city data: {len(store_cities)}")

out = {name: sorted(cities) for name, cities in tech_cities.items()}
with open(r'C:\Users\Public\10B\tech_cities.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
with open(r'C:\Users\Public\10B\store_cities.json', 'w', encoding='utf-8') as f:
    json.dump(store_cities, f, indent=2)
print("Saved tech_cities.json and store_cities.json")
