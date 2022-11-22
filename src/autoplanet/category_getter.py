import time
import json
import sys
import requests
from os.path import dirname, realpath
from random import randint
from icecream import ic
from bs4 import BeautifulSoup
# Add the parent directory name of the current file into the python path
# to import module from parent dir
sys.path.append(dirname(dirname(realpath(__file__))))
from aux_functions import load_categories

categories = load_categories("autoplanet")

def init_(category):
    # First iteration needs some extra steps
    current_soup = get_page_data(category, 1)
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
        category_url = f'https://www.autoplanet.cl/webapi/search/refineSearch?q={category}&page={page_number}&sort=&pageSize=40'
        request = ic(requests.get(category_url))
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


if __name__ == "__main__":

    autoplanet_products = dict()
    current_soup = None
    last_page_number = 0
    for category in categories:
        autoplanet_products[category] = []
        ic(category)    
        
        # response = requests.get(category_url).content
        # current_soup = BeautifulSoup(response, 'html5lib')
        
        current_soup, last_page_number = init_(category)
        autoplanet_products[category].extend(extract_page_data(current_soup))
        
        # ic(soup.prettify())
        
        # Todo --> remove the last_page_number overwrite
        # last_page_number = 2
        for page_number in range(1, last_page_number):
            # Wait a bit to prevent the webpagge of kicking us out
            # Wait between 5 and 10 seconds
            time.sleep(randint(5, 10))
            ic(page_number)
            ic(len(autoplanet_products[category]))
            current_soup = get_page_data(category, page_number)
            current_soup_json = extract_page_data(current_soup)
            autoplanet_products[category].extend(current_soup_json) # Concatenate lists
            ic(len(current_soup_json))

        #     category_name = category.split("/")[-1]
        #     with open(f"request_inputs&outputs/autoplanet/{category_name}{page_number}.json", "w") as json_file:
        #         json.dump(current_soup_json, json_file)
        ic(len(autoplanet_products[category]))
