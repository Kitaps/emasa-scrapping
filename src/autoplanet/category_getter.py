import time
import sys
import requests
from itertools import chain
from os.path import dirname, realpath
from collections import defaultdict
from icecream import ic
# Add the parent directory name of the current file into the python path
# to import module from parent dir
sys.path.append(dirname(dirname(realpath(__file__))))
from aux_functions import load_categories, format_link

categories = load_categories("autoplanet")

def init_(category):
    # First iteration needs some extra steps
    current_soup = get_page_data(category, 0)
    last_page_number = get_category_range(current_soup)
    extract_page_data(current_soup)
    return current_soup, last_page_number


def get_category_range(response):
    # Only if the get_page_data was successfull look for category pages number
    if not response:
        ic("Error found. Aborting.") # Raise Exception
        return 0
    number_name = ic(response["pagination"]["numberOfPages"])
    # Finally we turn the number string into an integer and return
    return int(number_name)

def get_page_data(category, page_number):
    # Try to connect to autoplanet webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        # The webapi getSuperCategory woks with codes, so if new categorys are 
        # wanted the correct code must be inserted
        # code[01] = "Repuestos"
        # code[02] = "Baterías"
        category_url = f'https://www.autoplanet.cl/webapi/category/getSuperCategory?code={category}&q=&page={page_number}&sort=&pageSize=40'
        # category_url = f'https://www.autoplanet.cl/webapi/search/refineSearch?q={category}&page={page_number}&sort=&pageSize=40'
        request = requests.get(category_url)
        response = request.json()["data"]["data"]
        return response

    except Exception as error:
        # Todo --> Turn this print into a log
        ic(error)
        return None

def extract_page_data(response):
    # Extract and save only the useful data
    # count = 1
    page_products = response["results"]
    # for product in page_products:
        # ic(f"{count}: {product}")
        # count += 1
    return page_products 

def get_products_json(soup_json):
    # We explore the soup_json until fe find the products list
    return soup_json["props"]["pageProps"]["results"]

def parse_data(raw_data, category):
    # Turn dic into default dic that returns None on key error
    raw_data = defaultdict(lambda:None, raw_data)
    # Takes the obtained data and parses the useful parts to match the Product Object format
    separate_ref_code = raw_data["name"].strip().split(" (Cod. Ref. ")
    if len(separate_ref_code) > 1:
        separate_ref_code = separate_ref_code[1].split(")")
        mann_code = separate_ref_code[0]
    else:
        mann_code = None

    separate_oem_code = raw_data["name"].strip().split("OEM ")
    if len(separate_oem_code) > 1:
        oem_code = separate_oem_code[1]
    else:
        oem_code = None

    if raw_data["images"]:
        image = raw_data["images"][0]["url"]
    else:
        image = None

    if raw_data["StockLevelStatus"]:
        stock = raw_data["StockLevelStatus"]["code"]
    else:
        stock = None

    # ic(f"https://www.autoplanet.cl/producto/{raw_data['pageUrl']}/{raw_data['code']}")
    kwargs = {
        "name": raw_data["name"].strip(),
        "product_id": raw_data["code"], # For now sku and product id are the same in easy
        "brand": raw_data["brand"],
        "description": raw_data["description"],
        # raw_data["breadCrumb"], # Page data (link, category, ...
        "sku": raw_data["code"],
        "image_at": image,
        "price": raw_data["price"]["value"],
        "url": format_link(f"https://www.autoplanet.cl/producto/{raw_data['pageUrl']}/{raw_data['code']}"),
        "store": "autoplanet",
        "category": category,
        "specifications": {
            "discountedPrice": raw_data["discountedPrice"]["value"], 
            "stock": stock,
            "oem": oem_code,
            "manncode": mann_code}}
    return kwargs
    


if __name__ == "__main__":

    from time import sleep
    from random import random
    from products import Product

    autoplanet_products = dict()
    current_soup = None
    last_page_number = 0
    category = "109"
    aux_generator = []
    
    current_soup, last_page_number = init_(category)
    sleep(1 + random())
    aux_generator = chain([], extract_page_data(current_soup))

    for page_number in range(1, last_page_number+1):
        sleep(1 + random())
        # Sleep the minimum time of the store + some randomness to seem organic 
        # to prevent being shut out of source api for too many consecutive requests
        try:
            ic(f"{category}: {page_number} of {last_page_number}")
            current_soup = get_page_data(category, page_number)
            current_soup_json = extract_page_data(current_soup)
            aux_generator = chain(aux_generator, current_soup_json) # Concatenate lists
        except Exception as error:
            print(type(error))
            continue

    ready_data_generator = map(lambda raw_data: parse_data(raw_data, category), aux_generator)
    product_list = list(map(lambda rd: Product(**rd), ready_data_generator))