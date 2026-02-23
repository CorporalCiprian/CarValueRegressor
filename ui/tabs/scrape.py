import json
import os
import sys
import asyncio
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nicegui import ui, run

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from scraper.links_scraper import get_olx_links
from scraper.data_scraper import scrape_ad_details
from scraper.config import LINKS_FILE, SCRAPED_DATA_FILE


def load_existing_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


async def popup_int(prompt_text, min_val=1, max_val=None):
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-sm bg-gray-900 rounded-xl p-6'):
        ui.label(prompt_text).classes('text-lg font-bold text-white')
        val_input = ui.number('Value', value=min_val, min=min_val, max=max_val, format='%d').props(
            'outlined dense dark').classes('w-full text-white')
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Confirm', on_click=lambda: dialog.submit(int(val_input.value))).props(
                'unelevated rounded color=primary')
    return await dialog


async def popup_yes_no(prompt_text):
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-sm bg-gray-900 rounded-xl p-6'):
        ui.label(prompt_text).classes('text-lg font-bold text-white')
        with ui.row().classes('w-full justify-end mt-4 gap-2'):
            ui.button('No', color='red', on_click=lambda: dialog.submit(False)).props('unelevated rounded')
            ui.button('Yes', color='green', on_click=lambda: dialog.submit(True)).props('unelevated rounded')
    return await dialog


async def start_scraping(gui_log, start_button):
    start_button.props('loading')
    gui_log.clear()
    gui_log.push("=== AutoScraper deployed! ===")

    existing_links = load_existing_links()
    links = None

    if existing_links:
        gui_log.push(f"Found {len(existing_links)} saved links.")
        use_existing = await popup_yes_no("Do you wish to use existing links?")
        if use_existing:
            links = existing_links
            gui_log.push(f"✓ Loaded {len(links)} links.")

    if links is None:
        gui_log.push("STEP 1: Collecting links from OLX...")
        num_pages = await popup_int("How many pages do you want to extract? (~40 ads/page)", min_val=1)

        gui_log.push(f"Extracting {num_pages} pages. Please wait...")
        links = await run.io_bound(get_olx_links, num_pages=num_pages)
        gui_log.push(f"✓ Collected {len(links)} unique links.")

    if not links:
        gui_log.push("Link error.")
        start_button.props(remove='loading')
        return

    total = len(links)
    gui_log.push(f"STEP 2: Extracting details (Total: {total} links).")
    num_ads = await popup_int(f"How many cars do you want to extract? (1 - {total})", min_val=1, max_val=total)

    gui_log.push(f"Starting Chrome to extract {num_ads} cars...")
    options = Options()
    options.add_argument("--window-position=-2000,0")
    driver = await run.io_bound(webdriver.Chrome, options=options)
    driver.minimize_window()

    scraped_results = []

    try:
        for link in links:
            current = len(scraped_results) + 1
            gui_log.push(f"[{current}/{num_ads}] Scraping: {link.split('?')[0][-30:]}")

            ad_data = await run.io_bound(scrape_ad_details, driver, link)

            if ad_data:
                scraped_results.append(ad_data)
                title = ad_data.get("title", "N/A")[:40]
                gui_log.push(f"   ✓ {title}...")
            else:
                gui_log.push("   ✗ Couldn't extract data.")

            if len(scraped_results) >= num_ads:
                break

        os.makedirs(os.path.dirname(SCRAPED_DATA_FILE), exist_ok=True)
        with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(scraped_results, f, indent=4, ensure_ascii=False)

        gui_log.push(f"\n✓ Done! Saved {len(scraped_results)} cars.")
        ui.notify(f'Scraping complete! Result saved in: {SCRAPED_DATA_FILE}', type='positive')

    except Exception as e:
        gui_log.push(f"\nError: {e}")
        ui.notify(str(e), type='negative')
    finally:
        driver.quit()
        gui_log.push("=== Process Stopped ===")
        start_button.props(remove='loading')


def scraper_tab():
    with ui.column().classes('w-full gap-4 p-4'):
        ui.label('OLX AutoScraper').classes('text-2xl font-bold text-white')
        ui.separator()

        ui.label('Configure and start scraping data from OLX.') \
            .classes('text-gray-400 text-sm')

        gui_log = ui.log(max_lines=100).classes(
            'w-full h-64 bg-black text-green-400 font-mono text-sm p-4 rounded-xl shadow-inner mb-2')

        start_btn = ui.button('Start AutoScraper', on_click=lambda: start_scraping(gui_log, start_btn),
                              icon='manage_search') \
            .props('unelevated rounded size=lg color=primary') \
            .classes('w-full')