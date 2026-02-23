import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colorama import init, Fore, Style

init(autoreset=True)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from scraper.links_scraper import get_olx_links
from scraper.data_scraper import scrape_ad_details
from scraper.config import LINKS_FILE, SCRAPED_DATA_FILE


def print_banner():
    print("\n" + Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "       AutoScraper")
    print(Fore.CYAN + "=" * 50 + "\n")


def ask_int(prompt, min_val=1, max_val=None):
    while True:
        try:
            value = int(input(Fore.YELLOW + prompt + Style.RESET_ALL).strip())
            if value < min_val:
                print(Fore.RED + f"  Please enter a number >= {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(Fore.RED + f"  Please enter a number <= {max_val}.")
                continue
            return value
        except ValueError:
            print(Fore.RED + "  Invalid input. Please enter a whole number.")


def step_1_get_links():
    print(Fore.CYAN + "STEP 1: Collect listing links from OLX")
    print(Fore.CYAN + "-" * 40)
    print("Each page contains ~40 ads.")
    num_pages = ask_int("How many pages do you want to scrape? (e.g. 5): ")

    print(f"\nScraping {Fore.YELLOW}{num_pages}{Style.RESET_ALL} page(s)... this may take a moment.\n")
    links = get_olx_links(num_pages=num_pages)
    print(Fore.GREEN + f"\n✓ Done! Collected {len(links)} unique links.\n")
    return links


def step_2_scrape_ads(links):
    print(Fore.CYAN + "STEP 2: Scrape car details from collected links")
    print(Fore.CYAN + "-" * 40)
    total = len(links)
    print(f"You have {Fore.YELLOW}{total}{Style.RESET_ALL} links available.")

    num_ads = ask_int(
        f"How many cars do you want to scrape? (1 - {total}): ",
        min_val=1,
        max_val=total,
    )

    print(f"\nScraping {Fore.YELLOW}{num_ads}{Style.RESET_ALL} car(s)... please wait.\n")

    options = Options()
    options.add_argument("--window-position=-2000,0")
    driver = webdriver.Chrome(options=options)
    driver.minimize_window()

    scraped_results = []

    try:
        for link in links:
            current = len(scraped_results) + 1
            print(Fore.WHITE + f"[{current}/{num_ads}] Scraping: " + Style.DIM + link)
            ad_data = scrape_ad_details(driver, link)

            if ad_data:
                scraped_results.append(ad_data)
                title = ad_data.get("title", "N/A")[:50]
                print(Fore.GREEN + f"   ✓ {title}")
            else:
                print(Fore.RED + "   ✗ Could not extract data, skipping.")

            if len(scraped_results) >= num_ads:
                break

        os.makedirs(os.path.dirname(SCRAPED_DATA_FILE), exist_ok=True)
        with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(scraped_results, f, indent=4, ensure_ascii=False)

        print(Fore.GREEN + f"\n✓ Done! Scraped {len(scraped_results)} car(s).")
        print(Fore.GREEN + f"✓ Data saved to: {SCRAPED_DATA_FILE}\n")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nScraping interrupted by user.")
        if scraped_results:
            os.makedirs(os.path.dirname(SCRAPED_DATA_FILE), exist_ok=True)
            with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(scraped_results, f, indent=4, ensure_ascii=False)
            print(Fore.YELLOW + f"Partial results ({len(scraped_results)} cars) saved to: {SCRAPED_DATA_FILE}")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}")
    finally:
        driver.quit()


def load_existing_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            links = json.load(f)
        return links
    return None


def main():
    print_banner()

    existing_links = load_existing_links()
    links = None

    if existing_links:
        print(f"Found existing links file with {Fore.YELLOW}{len(existing_links)}{Style.RESET_ALL} links.")
        choice = input(Fore.YELLOW + "Do you want to use these existing links? (y/n): " + Style.RESET_ALL).strip().lower()
        if choice == "y":
            links = existing_links
            print(Fore.GREEN + f"✓ Loaded {len(links)} existing links.\n")
        else:
            print()

    if links is None:
        links = step_1_get_links()

    print()
    step_2_scrape_ads(links)

    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "  All done! Check your data folder for results.")
    print(Fore.CYAN + "=" * 50 + "\n")


if __name__ == "__main__":
    main()