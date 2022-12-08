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

categories = load_categories("sodimac")

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
    pages_ordered_list = soup.find_all('button', attrs = {'id': re.compile("testId-pagination-top-button\d+")})
    # ic(int(tuple(pages_ordered_list)[-1].text))
    if pages_ordered_list:
        # Extract the last element from the obtained html element
        #   To do this, we turn the element into a tuple and then obtain it's last element
        last_element = tuple(pages_ordered_list)[-1]
        # This element will have a text containing the last page name, which we want
        number_name = last_element.text
    # Finally we turn the number string into an integer and return
    else:
        number_name = 1
    return ic(int(number_name))

def get_page_data(category, page_number):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        category_url = f'https://www.falabella.com/falabella-cl/category/{category}?page={page_number}'
        # category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page={page_number}&store=sodimac'
        # Based on https://es.stackoverflow.com/questions/545411/scrap-con-beautifulsoup-pero-no-obtengo-toda-la-info-los-selectores-son-multicl
        request = requests.get(category_url)
        soup = BeautifulSoup(request.text, "lxml")
        return soup

    except Exception as error:
        # Todo --> Turn this print into a log
        ic(error)
        return None

def extract_page_data(soup):
    # Extract and save only the useful data
    soup_data = soup.find("script", attrs={'id': '__NEXT_DATA__'})
    soup_json = json.loads(soup_data.get_text())
    page_products_list = get_products_json(soup_json)
    return page_products_list

def get_products_json(soup_json):
    # We explore the soup_json until fe find the products list
    return soup_json["props"]["pageProps"]["results"]

def parse_data(raw_data, category):
    # Turn dic into defaultdic that returns None on key error
    raw_data = defaultdict(lambda:None, raw_data)
    extra_specs = list()
    price, price_key, parent_price= set_price(raw_data)
    media_url = get_mediaUrl(raw_data)
    kwargs = {
        "name": raw_data["displayName"],
        "product_id": raw_data["productId"], # For now sku and product id are the same in easy
        "brand": raw_data["brand"],
        "description": None,
        # raw_data["breadCrumb"], # Page data (link, category, ...
        "sku": raw_data["skuId"],
        "image_at": media_url,
        "price": price,
        "url": raw_data["url"],
        "store": "sodimac",
        "category": category,
        "specifications": {
            "productType": raw_data["productType"],
            "prices": raw_data[price_key],
            "availability": raw_data["availability"]
            # Todo: raw_data["variants"][index]["sellerId"]
            # Todo: raw_data["variants"][index]["sellerName"]
            }}
    if "topSpecifications" in raw_data.keys():
        extra_specs.append(get_top_(raw_data["topSpecifications"]))
    if "rating" in raw_data.keys():
        kwargs["specifications"]["rating"] = raw_data["rating"]
    if parent_price: kwargs["specifications"]["prices"] = str(parent_price)

    update_(kwargs["specifications"], extra_specs)
    return kwargs

def set_price(raw_data):
    keys = raw_data.keys()
    if "price" in keys: 
        price = raw_data["price"]
        key = "price"
    elif "prices" in keys: 
        price = raw_data["prices"][0]["price"]
        key = "prices"
    # We unpack the price to obtain the numeric value, not a list
    new_price = extract_price(price)
    return new_price, key, price

def extract_price(price):
    # Function to recursively find an int in a nested price structure
    # When found returns the price and also the parent directory
    # ic(price)
    if type(price) == int: return price
    elif type(price) == str:
        price = price.replace(".", "")
        if price.isnumeric(): return int(price)
    else:
        for element in price:
            new_price = extract_price(element)
            if type(new_price) == int: return new_price

def get_mediaUrl(raw_data):
    # raw_data is a defaultdict
    if raw_data["mediaUrls"]: return raw_data["mediaUrls"][0]
    else: return None

def update_(specifications_dic, spec_list):
    # ic(spec_list)
    for spec in spec_list:
        specifications_dic.update(spec)

def get_top_(specs):
    # ic(specs)
    spec_dic = dict(map(lambda string: string.split(":", maxsplit=1), specs))
    return spec_dic

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
