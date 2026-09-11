import json
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_FILE = Path(__file__).parent / "sdi_session.json"
URL = "https://walmart.sdi.com/FieldInventoryWorkbench"
OUTPUT_FILE = Path(__file__).parent / "sdi_inventory_raw.json"

SUBREGIONS = [
    '367-A', '366-A', '373-A', '368-A', '369-A', '369-B',
    '370-A', '371-A', '372-A', '375-A', '384-A', '385-A',
    '385-B', '387-A', '387-B',
]


def wait_for_loader_gone(page, timeout=30000):
    try:
        page.locator('#SDILoader').wait_for(state='hidden', timeout=timeout)
    except Exception:
        pass


def select_react_select(page, for_id, option_text):
    wait_for_loader_gone(page)
    label = page.locator(f'label[for="{for_id}"]')
    control = label.locator('xpath=following-sibling::div[1]')
    control.click()
    inp = control.locator('input[type="text"]')
    inp.fill(option_text)
    page.wait_for_timeout(1000)
    option = page.locator('div[id*="react-select"][id*="option"]', has_text=option_text).first
    option.click()
    page.wait_for_timeout(300)


def get_num_records(page):
    try:
        text = page.locator('label.no-rec-color').inner_text(timeout=5000)
        m = re.search(r'(\d+)', text)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def extract_items(page):
    items = []
    cards = page.locator('div.product-details-container')
    n = cards.count()
    for i in range(n):
        card = cards.nth(i)
        text = card.inner_text()
        fields = {}
        for line in text.split('\n'):
            if ':' in line:
                k, _, v = line.partition(':')
                fields[k.strip()] = v.strip()
        items.append(fields)
    return items


def click_next_page(page):
    wait_for_loader_gone(page)
    next_li = page.locator('ul.custom-pagination li.page-item').last
    cls = next_li.get_attribute('class') or ''
    if 'disabled' in cls:
        return False
    next_li.locator('a').click()
    page.wait_for_timeout(2500)
    wait_for_loader_gone(page)
    return True


def scrape_subregion(page, sub):
    select_react_select(page, 'Subregion', sub)
    page.wait_for_timeout(500)
    loaded = False
    for retry in range(3):
        page.get_by_role('button', name='Get data').click()
        try:
            page.wait_for_selector('div.product-details-container', timeout=25000)
            loaded = True
            break
        except Exception:
            print(f"  {sub}: attempt {retry+1} timed out waiting for cards, retrying...")
    if not loaded:
        num_records = get_num_records(page)
        print(f"  {sub}: no item cards appeared after retries (Number of records={num_records})")
        return []
    wait_for_loader_gone(page)

    num_records = get_num_records(page)
    print(f"  {sub}: {num_records} records reported")
    all_items = []
    page_num = 1
    while True:
        items = extract_items(page)
        all_items.extend(items)
        if not click_next_page(page):
            break
        page_num += 1
        if page_num > 60:
            print("  !! bailing out after 60 pages")
            break
    print(f"  {sub}: collected {len(all_items)} rows across {page_num} pages")
    return all_items


def main():
    all_data = {}
    if OUTPUT_FILE.exists():
        try:
            all_data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            print(f"Resuming -- already have: {list(all_data.keys())}")
        except Exception:
            all_data = {}
    with sync_playwright() as p:
        ok = False
        browser = None
        for attempt in range(10):
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=str(SESSION_FILE))
            page = context.new_page()
            try:
                page.goto(URL, timeout=20000)
                ok = True
                break
            except Exception:
                print(f"load attempt {attempt+1} failed")
                browser.close()
                time.sleep(2)
        if not ok:
            raise SystemExit("could not load page")

        page.wait_for_timeout(6000)
        try:
            page.get_by_text("Ok, Got it").click(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(1000)

        select_react_select(page, "Region", "10B")
        page.wait_for_timeout(1000)

        try:
            page.get_by_text("Include zero QTY").click(timeout=3000)
        except Exception as e:
            print("could not check Include zero QTY:", e)

        for sub in SUBREGIONS:
            if sub in all_data and all_data[sub]:
                print(f"Skipping {sub}, already scraped ({len(all_data[sub])} rows)")
                continue
            try:
                items = scrape_subregion(page, sub)
                all_data[sub] = items
            except Exception as e:
                print(f"FAILED on {sub}: {e}")
                all_data.setdefault(sub, [])
            OUTPUT_FILE.write_text(json.dumps(all_data, indent=2), encoding="utf-8")

        browser.close()

    total = sum(len(v) for v in all_data.values())
    print(f"\nDONE. Total rows scraped: {total}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
