import os
import sys
import json
import time
from collections import defaultdict
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# ZEUS image/description enrichment (populated incrementally by
# sdi_scraper/batch_fetch_parts.py -- safe no-op if the file doesn't exist
# yet or a given part hasn't been scraped). Keyed by uppercased part number.
# ---------------------------------------------------------------------------
ENRICHED_PARTS_FILE = r"C:\Users\Public\10B\sdi_scraper\enriched_parts.json"

# Manually-submitted images (via the site's "+ Add Image" button -> "Export
# My Added Images" -> sent in and merged here). Keyed by uppercased part
# number, same shape as the exported JSON: {"PART-NO": "https://..."}.
# These take priority over ZEUS results since a human curated them.
MANUAL_OVERRIDES_FILE = r"C:\Users\Public\10B\sdi_scraper\manual_overrides.json"


def load_manual_overrides():
    try:
        with open(MANUAL_OVERRIDES_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        return {k.upper(): v for k, v in raw.items() if v and not k.startswith('_')}
    except Exception:
        return {}


def load_enriched_parts():
    try:
        with open(ENRICHED_PARTS_FILE, encoding="utf-8") as f:
            rows = json.load(f)
        result = {}
        for r in rows:
            if not r.get("pno"):
                continue
            img = r.get("image_url") or ""
            # ZEUS's own "no photo available" placeholder is a relative path
            # that only resolves on their domain -- treat it as no image.
            if img.startswith("/Images/"):
                img = ""
            r = dict(r)
            r["image_url"] = img
            result[r["pno"].upper()] = r
        return result
    except Exception:
        return {}

# ---------------------------------------------------------------------------
# Hierarchy & Mapping Config
# ---------------------------------------------------------------------------
HIER = {
    '366-A': {'mgr':'Antonio Vasquez',   'reg_mgr':'Israel Pino'},
    '367-A': {'mgr':'Michael Leanox',    'reg_mgr':'Israel Pino'},
    '368-A': {'mgr':'Thomas Balaci',     'reg_mgr':'Christopher Fuentes'},
    '369-A': {'mgr':'Alejandro Quijada', 'reg_mgr':'Christopher Fuentes'},
    '369-B': {'mgr':'Habib Musliu',      'reg_mgr':'Christopher Fuentes'},
    '370-A': {'mgr':'Aron Valdez',       'reg_mgr':'Ralph Vasquez'},
    '371-A': {'mgr':'Gustavo Ortiz',     'reg_mgr':'Ralph Vasquez'},
    '372-A': {'mgr':'Shane Christy',     'reg_mgr':'Ralph Vasquez'},
    '373-A': {'mgr':'Joshua Drezek',     'reg_mgr':'Israel Pino'},
    '375-A': {'mgr':'Cody Hoffer',       'reg_mgr':'Gabe Macias'},
    '384-A': {'mgr':'Jonathan Rivera',   'reg_mgr':'Gabe Macias'},
    '385-A': {'mgr':'Darien Molina',     'reg_mgr':'Gabe Macias'},
    '385-B': {'mgr':'John Swonger',      'reg_mgr':'Gabe Macias'},
    '387-A': {'mgr':'James Chacon',      'reg_mgr':'Gabe Macias'},
    '387-B': {'mgr':'Ward Cosgrove',     'reg_mgr':'Gabe Macias'},
}

MGR_TO_SUB = {v['mgr'].upper(): k for k, v in HIER.items()}

# Raw fs_manager_name sometimes rolls up to the REGIONAL manager's own name
# (data quality issue upstream) instead of being genuinely blank -- e.g.
# fs_manager_name='ISRAEL PINO' on rows that are actually his own RM-level
# rollup, not a real FS Manager named Israel Pino. Block all known regional
# manager names (plus nickname variants) from ever being accepted as an FS
# Manager value, so they can't leak into the FS Manager tier/dropdown.
_RM_NICKNAMES = {'GABE MACIAS': ['GABRIEL MACIAS']}
_ALL_RM_NAMES = set()
for _h in HIER.values():
    _rm_upper = _h['reg_mgr'].upper()
    _ALL_RM_NAMES.add(_rm_upper)
    _ALL_RM_NAMES.update(_RM_NICKNAMES.get(_rm_upper, []))

ROLE_MAP = {
    'GM TECHNICIAN':             'GM',
    'HVAC/R TECHNICIAN':         'HVACR',
    'FOOD EQUIPMENT TECHNICIAN': 'FE',
    'Shared/Store':              'Store',
}

MANAGERS_LIST = [
    ('Michael Leanox',   '367-A', 'Israel Pino',         '367-A', 'parts-inventory'),
    ('Antonio Vasquez',  '366-A', 'Israel Pino',         '366-A', 'vasquez-inventory'),
    ('Joshua Drezek',    '373-A', 'Israel Pino',         '373-A', 'drezek-inventory'),
    ('Thomas Balaci',    '368-A', 'Christopher Fuentes', '368-A', 'inv_368_a'),
    ('Alejandro Quijada','369-A', 'Christopher Fuentes', '369-A', 'inv_369_a'),
    ('Habib Musliu',     '369-B', 'Christopher Fuentes', '369-B', 'inv_369_b'),
    ('Aron Valdez',      '370-A', 'Ralph Vasquez',       '370-A', 'inv_370_a'),
    ('Gustavo Ortiz',    '371-A', 'Ralph Vasquez',       '371-A', 'inv_371_a'),
    ('Shane Christy',    '372-A', 'Ralph Vasquez',       '372-A', 'inv_372_a'),
    ('Cody Hoffer',      '375-A', 'Gabe Macias',         '375-A', 'inv_375_a'),
    ('Jonathan Rivera',  '384-A', 'Gabe Macias',         '384-A', 'inv_384_a'),
    ('Darien Molina',    '385-A', 'Gabe Macias',         '385-A', 'inv_385_a'),
    ('John Swonger',     '385-B', 'Gabe Macias',         '385-B', 'inv_385_b'),
    ('James Chacon',     '387-A', 'Gabe Macias',         '387-A', 'inv_387_a'),
    ('Ward Cosgrove',     '387-B', 'Gabe Macias',         '387-B', 'inv_387_b'),
]

def get_bigquery_client():
    # If in GitHub Actions, use standard credentials injection
    if os.environ.get('GITHUB_ACTIONS'):
        return bigquery.Client(project="re-ods-explorer")
        
    try:
        # Local Windows execution environment
        adc_path = os.path.join(os.environ.get('APPDATA',''), 'gcloud', 'application_default_credentials.json')
        if not os.path.exists(adc_path):
            return None
        with open(adc_path) as f:
            adc = json.load(f)
        from google.oauth2.credentials import Credentials as UserCredentials
        creds = UserCredentials(
            token=None,
            refresh_token=adc['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=adc['client_id'],
            client_secret=adc['client_secret'],
        )
        return bigquery.Client(project="re-ods-explorer", credentials=creds)
    except Exception as e:
        print(f"Failed to load BigQuery: {e}")
        return None

def build_inventory_portal():
    print(f"[{time.strftime('%X')}] Starting up-to-the-minute 10B Parts Inventory build...")
    
    client = get_bigquery_client()
    if not client:
        print("Error: BigQuery client not available. Please verify credentials!")
        return

    # STEP 1 - Query BigQuery for all 15 sub-markets
    print("Querying semantic_fs_zeus_parts_inventory from BigQuery...")
    query = """
    SELECT
      fs_sub_market,
      COALESCE(fs_manager_name,'')          AS fs_mgr,
      COALESCE(fs_regional_manager_name,'') AS fs_rm,
      COALESCE(vehicle_tech_full_name,'STORE LOCATION') AS tech,
      COALESCE(vehicle_tech_role,'Shared/Store')         AS role,
      isp_store_no            AS store_no,
      inventory_storage_area  AS area,
      inventory_storage_type  AS loc_type,
      item_id,
      item_short_description,
      item_full_description,
      item_manufacturer,
      item_manufacturer_part_no,
      item_unit_of_measure,
      CAST(item_total_qty_at_location AS INT64)   AS qty,
      ROUND(item_unit_cost,2)                      AS ucost,
      ROUND(item_total_cost_at_location,2)         AS tcost,
      ROUND(storage_area_total_cost,2)             AS area_total,
      CAST(item_reorder_point AS INT64)            AS rop,
      CAST(item_max_qty AS INT64)                  AS maxq,
      item_replenish_flag                          AS rep,
      CAST(item_last_putaway_date AS STRING)       AS putaway,
      CAST(item_last_order_date AS STRING)       AS last_order,
      CAST(item_qty_onhand_global AS INT64)        AS goh
    FROM `re-ods-prod.us_re_ods_prod_semantic_pub.semantic_fs_zeus_parts_inventory`
    WHERE fs_region = '10B'
      AND fs_sub_market IN (
        '366-A','367-A','368-A','369-A','369-B',
        '370-A','371-A','372-A','373-A','375-A',
        '384-A','385-A','385-B','387-A','387-B'
      )
    ORDER BY fs_sub_market, tech, tcost DESC
    """
    
    query_job = client.query(query)
    rows = list(query_job.result())
    print(f"Successfully retrieved {len(rows)} parts inventory rows!")

    # STEP 2 - Parse and Clean Technicians/Managers
    enriched = load_enriched_parts()
    print(f"Loaded {len(enriched)} ZEUS-enriched parts (images/descriptions) for merge...")
    manual_imgs = load_manual_overrides()
    print(f"Loaded {len(manual_imgs)} manually-submitted images for merge...")
    parts = []
    for r in rows:
        sub = r.fs_sub_market or ''
        h = HIER.get(sub, {'mgr':'Unknown','reg_mgr':'Unknown'})

        # Clean and assign real manager row-by-row to prevent incorrect groupings!
        raw_mgr = r.fs_mgr
        if (raw_mgr and raw_mgr != 'NULL'
                and '366-A' not in raw_mgr.upper() and '367-A' not in raw_mgr.upper()
                and 'UNKNOWN' not in raw_mgr.upper()
                and raw_mgr.upper() not in _ALL_RM_NAMES):
            mgr = raw_mgr.title()
        else:
            mgr = h['mgr']

        # The raw fs_sub_market column is unreliable -- ~38 tech/manager
        # combos across every region carry a stale sub-market tag (e.g.
        # Francisco Orozco shows fs_sub_market=366-A even though his real
        # manager Michael Leanox belongs to 367-A). The manager field is
        # trustworthy, so once we know the manager, always re-derive the
        # sub-market from HIER instead of trusting the raw column.
        correct_sub = MGR_TO_SUB.get(mgr.upper())
        if correct_sub:
            sub = correct_sub
            h = HIER[sub]

        # Regional Manager has the SAME data-quality problem as sub-market:
        # raw fs_regional_manager_name is inconsistent row-to-row for the
        # same manager (e.g. Joshua Drezek's rows split between Israel Pino
        # and Ralph Vasquez; Gustavo Ortiz's rows scatter across all 4 RMs).
        # Once we trust `mgr`/`h` above, always take RM from HIER too --
        # never from the raw per-row value.
        rm = h['reg_mgr']

        tech = r.tech or 'STORE LOCATION'
        # Exclude generic placeholder technicians
        if tech in ('1', '366-A-FE', '366-A-FS', '367-A-FS', ''):
            continue

        if tech == 'STORE LOCATION':
            store_no = (r.store_no or '').strip()
            display = f'WM#{store_no}' if store_no else 'Store Inventory'
        else:
            display = tech.title()
        tc = round(r.tcost, 2) if r.tcost else 0.0
        if tc <= 0:
            continue

        parts.append({
            "sub":  sub,
            "rm":   rm,
            "mgr":  mgr,
            "tech": display,
            "role": ROLE_MAP.get(r.role or '', r.role or 'Store'),
            "area": r.area or '',
            "loc":  r.loc_type or '',
            "id":   r.item_id or '',
            "desc": r.item_short_description or '',
            "fdesc":r.item_full_description or '',
            "mfr":  r.item_manufacturer or '',
            "pno":  r.item_manufacturer_part_no or '',
            "uom":  r.item_unit_of_measure or 'EA',
            "qty":  int(r.qty) if r.qty else 0,
            "ucost":round(r.ucost,2) if r.ucost else 0.0,
            "tcost":tc,
            "area_total":round(r.area_total,2) if r.area_total else 0.0,
            "rop":  int(r.rop) if r.rop else 0,
            "maxq": int(r.maxq) if r.maxq else 0,
            "rep":  r.rep or 'N',
            "putaway":  r.putaway,
            "last_order":r.last_order,
            "goh":  int(r.goh) if r.goh else 0,
            "img":  manual_imgs.get((r.item_manufacturer_part_no or '').upper()) or (enriched.get((r.item_manufacturer_part_no or '').upper()) or {}).get("image_url") or '',
        })

    # Group tech summaries dynamically based on correct manager alignments!
    tech_map = defaultdict(lambda:{"items":0,"value":0.0,"area":"","role":"","mgr":"","rm":"","sub":""})
    for p in parts:
        k = (p['mgr'], p['tech'])
        tech_map[k]['items'] += 1
        tech_map[k]['value']  = round(tech_map[k]['value'] + p['tcost'], 2)
        tech_map[k]['area']   = p['area']
        tech_map[k]['role']   = p['role']
        tech_map[k]['mgr']    = p['mgr']
        tech_map[k]['rm']     = p['rm']
        tech_map[k]['sub']    = p['sub']

    techs_summary = [{"tech":k[1],"mgr":v['mgr'],"rm":v['rm'],"role":v['role'],
                      "area":v['area'],"sub":v['sub'],
                      "items":v['items'],"value":round(v['value'],2)}
                     for k,v in tech_map.items()]
    techs_summary.sort(key=lambda x: (-x['value']))

    # STEP 3 - Compress payload into compact space-saving array
    rms   = sorted(set(p['rm']   for p in parts))
    mgrs  = sorted(set(p['mgr']  for p in parts))
    techs_l = sorted(set(p['tech'] for p in parts))
    subs  = sorted(set(p['sub']  for p in parts))
    roles = sorted(set(p['role'] for p in parts))
    rm_i={v:i for i,v in enumerate(rms)}
    mgr_i={v:i for i,v in enumerate(mgrs)}
    tech_i={v:i for i,v in enumerate(techs_l)}
    sub_i={v:i for i,v in enumerate(subs)}
    role_i={v:i for i,v in enumerate(roles)}

    compact_parts=[]
    for p in parts:
        compact_parts.append([
            sub_i[p['sub']],rm_i[p['rm']],mgr_i[p['mgr']],tech_i[p['tech']],role_i[p['role']],
            p['area'],p['id'],p['desc'],p['mfr'] or '',p['pno'] or '',
            p['qty'],p['ucost'],p['tcost'],p['area_total'],
            p['rop'],p['maxq'],p['rep'],p['putaway'] or '',p['last_order'] or '',p['goh'],
            p['fdesc'] or '',p['img'] or '',
        ])

    compact_techs=[]
    for t in techs_summary:
        compact_techs.append([
            tech_i.get(t['tech'],0),mgr_i.get(t['mgr'],0),rm_i.get(t['rm'],0),
            role_i.get(t['role'],0) if t['role'] in role_i else 0,
            t['area'],t['items'],round(t['value'],2),
        ])

    compact_payload={"rms":rms,"mgrs":mgrs,"techs":techs_l,"subs":subs,"roles":roles,
                     "parts":compact_parts,"tech_rows":compact_techs,"hier":HIER}

    # STEP 4 - Compile HTML Dashboards for all 15 managers + Hub index
    print("Compiling all 15 sub-market dashboards using accurate mappings...")
    
    # Load core template from build_inv_v2.py
    template_file = "build_inv_v2.py"
    if not os.path.exists(template_file):
        template_file = r"C:\Users\Public\build_inv_v2.py"
        
    with open(template_file, "r", encoding="utf-8") as f:
        tmpl_content = f.read()
    start_idx = tmpl_content.index('HTML = r"""') + len('HTML = r"""')
    end_idx   = tmpl_content.index('"""', start_idx)
    tmpl = tmpl_content[start_idx:end_idx]

    results_summary = []
    for mgr_name, sub, rm_name, label, outname in MANAGERS_LIST:
        mgr_parts = [p for p in parts if p['mgr'] == mgr_name]
        if not mgr_parts:
            continue
            
        mgr_tech_map = defaultdict(lambda:{"items":0,"value":0.0,"area":"","role":"","area_total":0})
        for p in mgr_parts:
            k = p['tech']
            mgr_tech_map[k]['items'] += 1
            mgr_tech_map[k]['value']  = round(mgr_tech_map[k]['value'] + p['tcost'], 2)
            mgr_tech_map[k]['area']   = p['area']
            mgr_tech_map[k]['role']   = p['role']
            mgr_tech_map[k]['area_total'] = p['area_total']
            
        mgr_tech_summary = sorted([{"tech":k,"role":v['role'],"area":v['area'],"items":v['items'],
                                    "value":round(v['value'],2)} for k,v in mgr_tech_map.items()],
                                   key=lambda x:-x['value'])

        mgr_payload = json.dumps({"parts":mgr_parts,"techs":mgr_tech_summary,"no_inv":[]},
                                 separators=(',',':'), ensure_ascii=True)

        # Render Manager Specific HTML
        html = tmpl
        html = html.replace('<title>367-A - Region 10B Parts Inventory</title>', f'<title>{sub} - Region 10B Parts Inventory</title>')
        html = html.replace('<span class="nav-title-sub">367-A</span>', f'<span class="nav-title-sub">{sub}</span>')
        html = html.replace('Parts Inventory — 367-A',        f'Parts Inventory — {sub}')
        html = html.replace('Michael Leanox · Manager 367-A', f'{mgr_name} · Manager {sub}')
        html = html.replace('Manager: M0L0IGD',               f'Sub-Market: {sub} · RM: {rm_name}')
        html = html.replace('367-A · re-ods-prod',            f'{sub} · re-ods-prod')
        
        # Add dynamic navigation links to go to Hub (index.html) or Global Search (10b-inventory.html) with cache-busting!
        _mgr_share_btn = ('<button class="nbtn" onclick="copyLink(this)" title="Copy share link">'
            '<svg width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#ffc220"/>'
            '<circle cx="8.5" cy="10" r="1.4" fill="#1a1a1a"/><circle cx="15.5" cy="10" r="1.4" fill="#1a1a1a"/>'
            '<path d="M7.5 14.5c1 1.6 2.7 2.5 4.5 2.5s3.5-.9 4.5-2.5" stroke="#1a1a1a" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
            '</svg> Share</button>')
        _mgr_home_svg = ('<svg width="18" height="18" viewBox="0 0 24 24">'
            '<g fill="#ffc220">'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z"/>'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(60 12 12)"/>'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(120 12 12)"/>'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(180 12 12)"/>'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(240 12 12)"/>'
            '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(300 12 12)"/>'
            '</g></svg>')
        html = html.replace(
            _mgr_share_btn,
            f'<a href="index.html?v={int(time.time())}" class="nbtn" style="text-decoration:none">{_mgr_home_svg} Home</a>'
            f'<a href="10b-inventory.html?v={int(time.time())}" class="nbtn" style="text-decoration:none">&#128269; Global Search</a>'
            + _mgr_share_btn
        )
        
        html = html.replace('PAYLOAD_PLACEHOLDER', mgr_payload)

        # Write file
        out_filename = f"{outname}.html"
        with open(out_filename, "w", encoding="utf-8") as f:
            f.write(html)
        # Mirror to C:\Users\Public\ for instant local testing!
        try:
            with open(os.path.join(r"C:\Users\Public", out_filename), "w", encoding="utf-8") as f:
                f.write(html)
        except Exception:
            pass
            
        results_summary.append((mgr_name, sub, out_filename, len(mgr_parts)))

    # STEP 5 - Generate Hub (index.html) organized by Regional Manager
    RM_ORDER = ['Israel Pino', 'Christopher Fuentes', 'Ralph Vasquez', 'Gabe Macias']
    RM_EXISTING = {rm_name: [] for rm_name in rms}
    for mgr_name, sub, out_file, count in results_summary:
        rm_name = HIER.get(sub, {}).get("reg_mgr", "Israel Pino")
        RM_EXISTING[rm_name].append((mgr_name, sub, out_file, count))

    # Reconstruct dynamic hub list based on our clean, accurate, non-lazy groupings
    hub_html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Region 10B Parts Inventory</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:32px 24px}}
.pagewrap{{max-width:1100px;margin:0 auto}}
h1{{font-size:1.4rem;font-weight:800;color:#fff;margin-bottom:6px}}
.sub{{font-size:.82rem;color:#8b949e;margin-bottom:28px}}
.rm-section{{margin-bottom:28px}}
.rm-title{{font-size:.78rem;font-weight:700;color:#8b949e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #30363d}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}}
@keyframes wave10bSweep{{0%{{background-position:100% 0}}100%{{background-position:0% 0}}}}
.card{{background:linear-gradient(100deg,#161b22 0%,#161b22 30%,#2a2412 48%,#0f2038 66%,#161b22 100%);background-size:260% 100%;animation:wave10bSweep 4.5s linear infinite;border:1px solid #30363d;border-radius:10px;padding:14px 16px;text-decoration:none;display:block;transition:border-color .12s}}
.card:hover{{border-color:#58a6ff}}
.ct{{font-size:.9rem;font-weight:700;margin-bottom:3px;color:#e9bf3f}}
.cs{{font-size:.7rem;color:#8b949e;margin-bottom:8px}}
.cd{{display:flex;gap:14px}}
.sv{{text-align:center}}.sv-v{{font-size:1.1rem;font-weight:800;color:#e6edf3}}.sv-l{{font-size:.58rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em}}
footer{{margin-top:28px;font-size:.65rem;color:#8b949e;border-top:1px solid #30363d;padding-top:12px}}
</style></head><body>
<div class="pagewrap">

<!-- Live Javascript Error Diagnoser Block -->
<div id="error-banner" style="display:none;background:#ffdddd;color:#ea1100;border:2px solid #ea1100;padding:15px;margin:20px 0;border-radius:8px;font-family:monospace;font-size:14px;white-space:pre-wrap;z-index:9999;position:relative;"></div>
<script>
window.onerror = function(message, source, lineno, colno, error) {{
  var div = document.getElementById('error-banner');
  if (div) {{
    div.style.display = 'block';
    div.innerHTML += '❌ <b>JS Error on Hub:</b> ' + message + '\\nAt: ' + source + ':' + lineno + ':' + colno + '\\n\\n';
  }}
  return false;
}};
</script>

<div class="nt" style="display:flex;align-items:center;gap:14px;margin-bottom:6px"><img src="upstream_logo.png" alt="Upstream Facility Services" style="height:44px;width:auto;display:block"><span style="font-size:1.4rem;font-weight:800;color:#e9bf3f">Region 10B</span></div>

<!-- Prominent Global Search Button -- red/white/blue cascading wave,
     mirrors the same animated-gradient trick used on manager names above -->
<style>
.wave10b-btn{{
  display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(100deg,#e21836 0%,#e21836 30%,#fff 48%,#0053e2 66%,#0053e2 100%);
  background-size:260% 100%;
  animation:wave10bSweep 3.2s linear infinite;
  color:#fff;font-weight:800;font-size:.98rem;
  padding:13px 22px;border-radius:10px;text-decoration:none;
  text-shadow:0 1px 3px rgba(0,0,0,.65);
  box-shadow:0 3px 12px rgba(0,0,0,.35);
}}
.wave10b-btn:hover{{animation-duration:1.4s;box-shadow:0 4px 16px rgba(0,0,0,.5)}}
</style>
<div style="margin-bottom: 25px;">
    <a href="10b-inventory.html?v={int(time.time())}" class="wave10b-btn">
      <span style="font-size:1.15rem">&#128269;</span> 10B Full Search
    </a>
</div>
"""

    for rm in RM_ORDER:
        if rm not in RM_EXISTING or not RM_EXISTING[rm]:
            continue
        hub_html += f'<div class="rm-section"><div class="rm-title">{rm.upper()}</div><div class="cards">'
        for mgr_name, sub, out_file, count in sorted(RM_EXISTING[rm], key=lambda x: x[1]):
            # Sum dynamic total cost
            mgr_val = sum(p['tcost'] for p in parts if p['mgr'] == mgr_name)
            hub_html += f"""
            <a class="card" href="{out_file}">
                <div class="ct">{mgr_name}</div>
                <div class="cs">{sub}</div>
                <div class="cd">
                    <div class="sv"><div class="sv-v">{count}</div><div class="sv-l">Items</div></div>
                    <div class="sv" style="margin-left:auto"><div class="sv-v">${mgr_val/1000:.0f}K</div><div class="sv-l">Value</div></div>
                </div>
            </a>
            """
        hub_html += '</div></div>'
        
    hub_html += f"""
<footer>
    <span>Region 10B • 15 Sub-Markets • re-ods-prod.semantic_fs_zeus_parts_inventory • Refreshed: {time.strftime('%Y-%m-%d %X')}</span>
</footer>
</div>
</body></html>
"""

    # Write final index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(hub_html)
    # Mirror to C:\Users\Public\ index.html and 10b-hub.html for instant local testing!
    try:
        with open(r"C:\Users\Public\index.html", "w", encoding="utf-8") as f:
            f.write(hub_html)
        with open(r"C:\Users\Public\10b-hub.html", "w", encoding="utf-8") as f:
            f.write(hub_html)
    except Exception:
        pass
        
    # STEP 6 - Generate Global Search page (10b-inventory.html)
    print("Compiling global search dashboard (10b-inventory.html)...")
    build_inv_file = r"C:\Users\Public\build_inv_10b.py"
    with open(build_inv_file, "r", encoding="utf-8") as f:
        global_tmpl_content = f.read()
        
    start_g = global_tmpl_content.index('HTML = """') + len('HTML = """')
    end_g   = global_tmpl_content.rindex('"""') # Use rindex to find the absolute final closing quote of the HTML block!
    global_html = global_tmpl_content[start_g:end_g]
    
    # Embed payload directly
    global_html = global_html.replace('""" + P + """', json.dumps(compact_payload, separators=(',',':')))
    
    # Inject navigation link back to hub with cache busting! (user prefers
    # calling this "Home" rather than "Hub" -- this replaces the old
    # separate built-in Home button that used to live on the far left)
    _share_btn_html = ('<button class="btn" onclick="cpLink(this)" title="Copy share link">'
        '<svg width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#ffc220"/>'
        '<circle cx="8.5" cy="10" r="1.4" fill="#1a1a1a"/><circle cx="15.5" cy="10" r="1.4" fill="#1a1a1a"/>'
        '<path d="M7.5 14.5c1 1.6 2.7 2.5 4.5 2.5s3.5-.9 4.5-2.5" stroke="#1a1a1a" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
        '</svg> Share</button>')
    _home_btn_svg = ('<svg width="18" height="18" viewBox="0 0 24 24">'
        '<g fill="#ffc220">'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z"/>'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(60 12 12)"/>'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(120 12 12)"/>'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(180 12 12)"/>'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(240 12 12)"/>'
        '<path d="M12,12 C10.3,9.3 9.8,5.6 12,2 C14.2,5.6 13.7,9.3 12,12 Z" transform="rotate(300 12 12)"/>'
        '</g></svg>')
    global_html = global_html.replace(
        _share_btn_html,
        f'<a href="index.html?v={int(time.time())}" class="btn" style="text-decoration:none">{_home_btn_svg} Home</a>'
        + _share_btn_html
    )
    
    # Inject active error banner diagnoser at top of body
    global_html = global_html.replace(
        '</style></head><body>',
        '</style></head><body>\n'
        '<div id="error-banner" style="display:none;background:#ffdddd;color:#ea1100;border:2px solid #ea1100;padding:15px;margin:20px;border-radius:8px;font-family:monospace;font-size:14px;white-space:pre-wrap;z-index:9999;position:relative;"></div>\n'
        '<script>\n'
        'window.onerror = function(message, source, lineno, colno, error) {\n'
        '  var div = document.getElementById("error-banner");\n'
        '  if (div) {\n'
        '    div.style.display = "block";\n'
        '    div.innerHTML += "❌ <b>JS Error on Global Search:</b> " + message + "\\nAt: " + source + ":" + lineno + ":" + colno + "\\n\\n";\n'
        '  }\n'
        '  return false;\n'
        '};\n'
        '</script>'
    )
    
    # Fill in the placeholders that build_inv_10b.py normally substitutes when run
    # standalone (this file only ever reads that script's HTML *text*, so those
    # substitutions never actually execute -- must be done here too, or the shipped
    # HTML ships literal "NI_PLACEHOLDER"/"BUILT_TS" tokens straight into <script> tags).
    build_ts = time.strftime('%b %d, %Y %I:%M %p')
    global_html = global_html.replace('BUILT_TS', build_ts).replace('NI_PLACEHOLDER', '[]')

    with open("10b-inventory.html", "w", encoding="utf-8") as f:
        f.write(global_html)
    
    # Mirror the newly compiled 10b-inventory.html to C:\Users\Public\ for instant local testing!
    try:
        import shutil
        shutil.copy("10b-inventory.html", r"C:\Users\Public\10b-inventory.html")
    except Exception:
        pass
        
    print(f"[{time.strftime('%X')}] Successfully completed 10B Parts Inventory build! Written to index.html and 10b-inventory.html!")

if __name__ == "__main__":
    build_inventory_portal()
