"""
Loads Region 10B parts inventory directly from the scraped SDI Zeus
"Manage Field Inventory" export (sdi_scraper/sdi_inventory_raw.json),
instead of the BigQuery semantic_fs_zeus_parts_inventory snapshot.

SDI is Zeus's own live system of record for tech->part->location
assignment, so unlike the BigQuery semantic layer it doesn't suffer
from the stale sub-market/manager tagging problems documented in
build_10b_inventory.py (see MGR_TO_SUB there). Each subregion was
scraped under its own correct sub-market filter, so we trust it
directly via HIER[sub] instead of re-deriving anything from a raw
column.

SDI's list view has no dollar-cost field, so unit cost is backfilled
from a BigQuery-derived per-part-number lookup (cost_lookup.json,
built by build_cost_lookup.py). Parts with no cost match default to
$0/unit rather than guessing at a number.
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
SDI_RAW_FILE = BASE_DIR / "sdi_scraper" / "sdi_inventory_raw.json"
COST_LOOKUP_FILE = BASE_DIR / "cost_lookup.json"

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


def load_parts_from_sdi(hier):
    """Returns a list of part dicts matching the same schema the
    BigQuery loader in build_10b_inventory.py produces, so the rest of
    the build pipeline (HTML rendering, tech/manager grouping) is
    reused unchanged."""
    raw = json.loads(SDI_RAW_FILE.read_text(encoding="utf-8"))
    cost_lookup = {}
    if COST_LOOKUP_FILE.exists():
        cost_lookup = json.loads(COST_LOOKUP_FILE.read_text(encoding="utf-8"))

    parts = []
    excluded_count = 0
    unmatched_cost_count = 0

    for sub, rows in raw.items():
        h = hier.get(sub)
        if not h:
            continue
        mgr = h["mgr"]
        rm = h["reg_mgr"]

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
          f"{unmatched_cost_count} with no cost match -> $0)")
    return parts
