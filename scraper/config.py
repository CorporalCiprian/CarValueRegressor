import os

# Base Project Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LINKS_FILE = os.path.join(DATA_DIR, "links.json")
SCRAPED_DATA_FILE = os.path.join(DATA_DIR, "scraped_raw_data.json")

OLX = {
    # Index page selectors
    "SELECTOR_AD_LINK": "a.css-1tqlkj0",
    "BASE_URL": "https://www.olx.ro",
    "SEARCH_URL": "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?currency=EUR&page=",

    # Detail page selectors
    "SELECTOR_TITLE": "h4.css-1l3a0i9",
    "SELECTOR_PRICE": '[data-testid="ad-price-container"] h3',
    "SELECTOR_ATTRIBUTES": "p.css-13x8d99",
    "SELECTOR_DESCRIPTION": "div.css-19duwlz",
}

AUTOVIT = {
    "SELECTOR_TITLE": "h1",
    "SELECTOR_PRICE": "[data-testid='ad-price-container'] h3, [data-testid='ad-price'] h3, h3.offer-price__number, h3[class*='ooa-']",
    "SELECTOR_ATTRIBUTES": "div[class$='e1nqkcyc6']",
    "SELECTOR_DESCRIPTION": "div[data-testid='content-details-section-description']",
}

# Crawler Config
WAIT_TIME = 3