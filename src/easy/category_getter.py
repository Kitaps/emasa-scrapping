import time
import json
import sys
import re
import requests
from random import randint
from collections import defaultdict
from os.path import dirname, realpath
from icecream import ic
from bs4 import BeautifulSoup
# Add the parent directory name of the current file into the python path
# to import module from parent dir
sys.path.append(dirname(dirname(realpath(__file__))))
from aux_functions import load_categories

categories = load_categories("easy")
## --> Continue
def init_(category):
    # First iteration needs some extra steps
    current_soup = get_page_data(category, 1)
    last_page_number = get_category_range(current_soup)
    extract_page_data(current_soup)
    return current_soup, last_page_number


def get_category_range(soup):
    # Only if the get_page_data was successfull look for category pages number
    if not soup:
        ic("Error found. Aborting.") # Raise Exception
        return 0

    # Find any of the page list elements on the site
    pages = soup.find('div', attrs = {'class': "easycl-custom-blocks-4-x-customPagination"})
    # ic(int(tuple(pages_ordered_list)[-1].text))
    if pages:
        # Get the number-of-pages
        number_name = ic(pages["data-number-of-pages"])
    # Finally we turn the number string into an integer and return
    else:
        number_name = 1
    return ic(int(number_name))

def get_page_data(category, page_number):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        category_url = f'https://www.easy.cl/automovil/{category}?page={page_number}'
        request = requests.get(category_url)
        ic(request)
        soup = BeautifulSoup(request.text, "lxml")
        return soup

    except Exception as error:
        # Todo --> Turn this print into a log
        ic(error)
        return None

def extract_page_data(soup):
    # Extract and save only the useful data
    soup_data = soup.find_all("script", attrs={'type': 'application/ld+json'})[1]
    soup_json = json.loads(soup_data.get_text())
    page_products_list = soup_json["itemListElement"]
    return page_products_list

def get_products_json(soup_json):
    # We explore the soup_json until fe find the products list
    return soup_json["props"]["pageProps"]["results"]

def parse_data(raw_data, category):
    # Turn dic into defaultdic that returns None on key error
    raw_data = defaultdict(lambda:None, raw_data["item"])
    ic(raw_data)
    kwargs = {
        "name": raw_data["name"],
        "product_id": raw_data["sku"], # For now sku and product id are the same in easy
        "brand": raw_data["brand"]["name"],
        "description": raw_data["description"],
        "sku": raw_data["sku"],
        "image_at": raw_data["image"],
        "price": raw_data["offers"]["lowPrice"],
        "url": raw_data["@id"],
        "store": "easy",
        "category": category,
        "specifications": {
            "mpn": raw_data["mpn"],
            "highPrice": raw_data["offers"]["highPrice"],
            "lowPrice": raw_data["offers"]["lowPrice"]
            }}
    return kwargs



if __name__ == "__main__":

    sodimac_products = dict()
    current_soup = None
    last_page_number = 0
    for category in categories:
        sodimac_products[category] = []
        ic(category)    
        # category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page=1&store=sodimac'
        # response = requests.get(category_url).content
        # current_soup = BeautifulSoup(response, 'html5lib')
        
        current_soup, last_page_number = init_(category)
        
        # ic(soup.prettify())
        
        # Todo --> remove the last_page_number overwrite
        ic(last_page_number)

        for page_number in range(last_page_number-1, last_page_number + 1):
        # for page_number in range(2, last_page_number + 1):
            # Wait a bit to prevent the webpagge of kicking us out
            # Wait between 5 and 10 seconds
            time.sleep(randint(1, 5))
            ic(page_number)
            current_soup = get_page_data(category, page_number)
            current_soup_json = extract_page_data(current_soup)

            category_name = category.split("/")[-1]
            with open(f"request_inputs&outputs/sodimac/{category_name}{page_number}.json", "w") as json_file:
                json.dump(current_soup_json, json_file)
