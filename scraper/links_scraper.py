import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from scraper.config import OLX, DATA_DIR, LINKS_FILE  # Using your variables

def save_links(links):
    # folder_path = os.path.join("..", "data")
    folder_path = DATA_DIR

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Directory {folder_path} was created.")

    # file_path = os.path.join(folder_path, "links.json")
    file_path = LINKS_FILE

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=4)

    print(f"Saved data in {file_path}")

def get_olx_links(num_pages):
    print(f"Starting extraction for {num_pages} pages...")

    # Start minimized
    chrome_options = Options()
    chrome_options.add_argument("--window-position=-2000,0")
    driver = webdriver.Chrome(options=chrome_options)
    driver.minimize_window()

    all_links = []
    # base_url = "https://www.olx.ro"
    base_url = OLX["BASE_URL"]

    for page in range(1, num_pages + 1):
        print(f"-> Processing page: {page} out of {num_pages}...")

        # setting the url to the current page nr
        # url = f"{base_url}/auto-masini-moto-ambarcatiuni/autoturisme/?currency=EUR&page={page}"
        url = f"{OLX['SEARCH_URL']}{page}"
        driver.get(url)

        elements = driver.find_elements(By.CSS_SELECTOR, OLX["SELECTOR_AD_LINK"])

        for el in elements:
            href = el.get_attribute("href")
            if href:
                if not href.startswith("http"):
                    href = base_url + href
                all_links.append(href)

    driver.quit()

    unique_links = list(set(all_links))

    # saving the list in a json
    save_links(unique_links)

    print(f"Extracted {len(unique_links)} unique links.")
    print("Links saved in data/links.json")

    time.sleep(1)
    return unique_links

# for testing
if __name__ == "__main__":
    get_olx_links(num_pages=25)