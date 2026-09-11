"""
Loads Region 10B parts inventory directly from the scraped SDI Zeus
"Manage Field Inventory" export (sdi_scraper/sdi_inventory_raw.json),
instead of the BigQuery semantic_fs_zeus_parts_inventory snapshot.

SDI is Zeus's own live system of record for tech->part->location
assignment, so unlike the BigQuery semantic layer it doesn't suffer
from the stale sub-market/manager tagging problems documented in
build_10b_inventory.py (see MGR_TO_SUB there).

IMPORTANT: SDI's "Subregion" filter is a GEOGRAPHY tag (which store
market a truck/location physically sits in), not an org-chart tag --
a tech's truck can be geo-tagged under a different subregion than the
one their actual manager owns. Earlier versions of this loader wrongly
assumed "every row returned when querying Subregion=X belongs to
manager HIER[X]" and that put real techs under the wrong manager on the
live dashboard. The fix: look up each tech's REAL manager from
tech_to_manager.json (built by build_tech_manager_lookup.py from
BigQuery's per-row manager field, cleaned the same way the original
BigQuery pipeline already does) and only fall back to the subregion's
default manager for techs BigQuery has no record of at all (e.g. very
new hires) -- and even then, flag it loudly instead of pretending it's
certain.

SDI's list view also has no dollar-cost field, so unit cost is
backfilled from a BigQuery-derived per-part-number lookup
(cost_lookup.json, built by build_cost_lookup.py). Parts with no cost
match default to $0/unit rather than guessing at a number.
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
SDI_RAW_FILE = BASE_DIR / "sdi_scraper" / "sdi_inventory_raw.json"
COST_LOOKUP_FILE = BASE_DIR / "cost_lookup.json"
TECH_TO_MGR_FILE = BASE_DIR / "tech_to_manager.json"
MANUAL_OVERRIDES_FILE = BASE_DIR / "manual_tech_manager_overrides.json"

# Trucks that have physically moved to a team outside Region 10B but whose
# old inventory rows are still lingering under the tech's name in SDI.
# Confirmed 2026-09: truck 33018 (Cody Broyles' old van) moved with his old
# team, which is no longer part of Region 10B -- excluded here since we
# don't own SDI itself and can't fix the source data directly.
EXCLUDED_TRUCK_IDS = {"33018"}


def _clean_qty(raw):
    if not raw:
        return 0
    m = re.search(r"-?\d+", raw.replace(",", ""))
    return int(m.group()) if m else 0


def _format_tech_name(raw):
    """SDI gives 'LAST,FIRST' -- convert to 'First Last' to match the
    existing dashboard's naming convention."""
    raw = (raw or "").strip()
    if "," in raw:
        last, _, first = raw.partition(",")
        return f"{first.strip().title()} {last.strip().title()}".strip()
    return raw.title()


def sdi_export_available():
    return SDI_RAW_FILE.exists()


def load_parts_from_sdi(hier, mgr_to_sub):
    """Returns a list of part dicts matching the same schema the
    BigQuery loader in build_10b_inventory.py produces, so the rest of
    the build pipeline (HTML rendering, tech/manager grouping) is
    reused unchanged."""
    raw = json.loads(SDI_RAW_FILE.read_text(encoding="utf-8"))
    cost_lookup = {}
    if COST_LOOKUP_FILE.exists():
        cost_lookup = json.loads(COST_LOOKUP_FILE.read_text(encoding="utf-8"))
    tech_to_mgr = {}
    if TECH_TO_MGR_FILE.exists():
        tech_to_mgr = json.loads(TECH_TO_MGR_FILE.read_text(encoding="utf-8"))
    else:
        print("WARNING: tech_to_manager.json not found -- every tech will "
              "fall back to their scraped subregion's default manager, "
              "which is known to be wrong for techs whose truck geography "
              "doesn't match their org chart. Run build_tech_manager_lookup.py.")
    manual_overrides = {}
    if MANUAL_OVERRIDES_FILE.exists():
        raw_overrides = json.loads(MANUAL_OVERRIDES_FILE.read_text(encoding="utf-8"))
        manual_overrides = {k.upper(): v for k, v in raw_overrides.items()}

    parts = []
    excluded_count = 0
    unmatched_cost_count = 0
    fallback_mgr_count = 0
    manual_override_count = 0

    for sub_queried, rows in raw.items():
        default_h = hier.get(sub_queried)
        if not default_h:
            continue

        for r in rows:
            location = r.get("Location", "")
            if any(tid in location for tid in EXCLUDED_TRUCK_IDS):
                excluded_count += 1
                continue

            qty = _clean_qty(r.get("QTY available (UOM)", ""))
            if qty <= 0:
                continue

            tech = _format_tech_name(r.get("Tech name", ""))
            if not tech:
                continue

            # Real manager identity comes from BigQuery's cleaned per-tech
            # roster, NOT from whichever Subregion filter happened to
            # return this row -- that filter is a geography tag, and a
            # tech's truck can sit in a different subregion than the one
            # their manager officially owns.
            #
            # One exception is unambiguous: if the "tech" IS one of our
            # 15 known managers (several of them carry their own truck),
            # they obviously manage themselves -- no lookup needed.
            override_mgr = manual_overrides.get(tech.upper())
            if override_mgr and override_mgr.upper() in mgr_to_sub:
                # Human-confirmed ground truth -- beats every other source,
                # including BigQuery, since Mike knows his own org chart
                # better than a stale semantic table does.
                mgr = override_mgr
                sub = mgr_to_sub[override_mgr.upper()]
                h = hier[sub]
                manual_override_count += 1
            elif tech.upper() in mgr_to_sub:
                sub = mgr_to_sub[tech.upper()]
                h = hier[sub]
                mgr = h["mgr"]
            else:
                real_mgr = tech_to_mgr.get(tech.upper())
                if real_mgr and real_mgr.upper() in mgr_to_sub:
                    mgr = real_mgr
                    sub = mgr_to_sub[real_mgr.upper()]
                    h = hier[sub]
                else:
                    # No BigQuery record for this tech at all (e.g. brand
                    # new hire) -- fall back to the subregion's default
                    # manager, since that's the best guess available, but
                    # this is the exact assumption that was wrong before,
                    # so keep counting it for visibility.
                    mgr = default_h["mgr"]
                    sub = sub_queried
                    h = default_h
                    fallback_mgr_count += 1

            rm = h["reg_mgr"]

            pno = (r.get("Manufacturer part number", "") or "").strip()
            ucost = cost_lookup.get(pno)
            if ucost is None:
                ucost = 0.0
                unmatched_cost_count += 1
            tcost = round(qty * ucost, 2)

            desc = (r.get("Description", "") or "").replace("More", "").strip()

            parts.append({
                "sub": sub,
                "rm": rm,
                "mgr": mgr,
                "tech": tech,
                "role": "Tech",
                "area": location,
                "loc": location,
                "id": "",
                "desc": desc,
                "fdesc": desc,
                "mfr": r.get("Manufacturer name", "") or "",
                "pno": pno,
                "uom": "EA",
                "qty": qty,
                "ucost": round(ucost, 2),
                "tcost": tcost,
                "area_total": 0.0,
                "rop": 0,
                "maxq": 0,
                "rep": r.get("Replenishment status", "N"),
                "putaway": None,
                "last_order": None,
                "goh": 0,
                "img": "",
            })

    print(f"SDI loader: {len(parts)} usable rows "
          f"({excluded_count} excluded via EXCLUDED_TRUCK_IDS, "
          f"{unmatched_cost_count} with no cost match -> $0, "
          f"{manual_override_count} via manual_tech_manager_overrides.json, "
          f"{fallback_mgr_count} with no BigQuery manager record -> "
          f"used subregion default as a best guess)")
    return parts
