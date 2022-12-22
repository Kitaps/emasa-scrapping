# Funtions to be used in other modules, to reduce repetitition
import json
from time import time
from datetime import date, timedelta
from icecream import ic
from random import randint

def load_categories(company_name):
    # Recives a company name (string). 
    # Returns the correctly formatted categories (list).
    # Theese are to be used by the corresponding company getter.
    # Theese categorys are saved in the categories json of each company.
    with open(f"categories_{company_name}.json", 'r') as file:
        return json.load(file)

def format_link(string):
    # Turns string into a link, compatible with chrome
    string = string.replace("(", "%28").replace(")", "%29")
    string = string.replace("-", "_")
    return string

def take_time(function):
    def args_wrapper(*args):
        start = time()
        result = function(*args)
        end = time()
        ic(end - start)
        return result
    return args_wrapper

def generate_params(start_price, days):
    current_price = start_price
    start_date = date.today()
    pairs = list()
    for day in range(days):
        if randint(0, 1):
            current_price += randint(-10, 10)/100 * current_price 
        current_date = start_date - timedelta(days=day)
        pairs.append((current_date, current_price))
    return pairs

def generate_data(date_price_pair, name, sku, url, store):
    kwargs = {
        "name": name,
        "product_id": sku, # For now sku and product id are the same in easy
        "brand": "DEMO",
        "description": "DEMO",
        # raw_data["breadCrumb"], # Page data (link, category, ...
        "sku": sku,
        "image_at": "DEMO",
        "price": date_price_pair[1],
        "scrap_date": date_price_pair[0],
        "url": url,
        "store": store,
        "category": "DEMO",
        "specifications": {
            "productType": "DEMO"
            }}
    return kwargs



if __name__ == "__main__":
    string = 'https://www.autoplanet.cl/producto/Filtro-de-Aceite-Mann-Filter-Jeep-(Cod.-Ref.-HU821X)-OEM-A6421840025/110177'
    print(format_link(string))

    print(generate_params(100, 10))