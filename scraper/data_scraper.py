import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from scraper.config import OLX, AUTOVIT, WAIT_TIME

def scrape_ad_details(driver, url):
    driver.get(url)
    time.sleep(WAIT_TIME)

    data = {"url": url}

    if "autovit.ro" in url:
        selectors = AUTOVIT
        data['source'] = 'autovit'
    else:
        selectors = OLX
        data['source'] = 'olx'
    try:
        # title and price
        data['title'] = driver.find_element(By.CSS_SELECTOR, selectors['SELECTOR_TITLE']).text
        data['price'] = driver.find_element(By.CSS_SELECTOR, selectors['SELECTOR_PRICE']).text

        # tags
        raw_attributes = driver.find_elements(By.CSS_SELECTOR, selectors['SELECTOR_ATTRIBUTES'])
        attributes_dict = {}

        for attr in raw_attributes:
            if data['source'] == 'autovit':
                try:
                    key = attr.find_element(By.CSS_SELECTOR, "p[class*='e1nqkcyc9']").text.strip()
                    val = attr.find_element(By.CSS_SELECTOR, "p[class*='e1nqkcyc11']").text.strip()
                    if key:
                        attributes_dict[key] = val
                except Exception:
                    continue
            else:
                text = attr.text
                if ":" in text:
                    key, val = text.split(":", 1)
                    key=key.strip()
                    if key:
                        attributes_dict[key] = val.strip()
                elif text.strip():
                    attributes_dict[text.strip()] = "Yes"

        data['attributes'] = attributes_dict

    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None

    return data