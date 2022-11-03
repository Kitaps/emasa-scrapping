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
    pages_ordered_list = soup.find('ol', attrs = {'class': 'jsx-1794558402 jsx-1490357007'})
    # ic(int(tuple(pages_ordered_list)[-1].text))
    # Extract the last element from the obtained html element
    #   To do this, we turn the element into a tuple and then obtain it's last element
    last_element = tuple(pages_ordered_list)[-1]
    # This element will have a text containing the last page name, which we want
    number_name = last_element.text
    # Finally we turn the number string into an integer and return
    return int(number_name)

def get_page_data(category, page_number):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page={page_number}&store=sodimac'
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
    count = 1
    soup_data = soup.find("script", attrs={'id': '__NEXT_DATA__'})
    soup_json = json.loads(soup_data.get_text())
    page_products = get_products_json(soup_json)
    for product in page_products:
        ic(f"{count}: {product}")
        count += 1
    return soup_json    

def get_products_json(soup_json):
    # We explore the soup_json until fe find the products list
    return soup_json["props"]["pageProps"]["results"]


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
        last_page_number = 2
        for page_number in range(2, last_page_number + 1):
            # Wait a bit to prevent the webpagge of kicking us out
            # Wait between 5 and 10 seconds
            time.sleep(randint(5, 10))
            ic(page_number)
            current_soup = get_page_data(category, page_number)
            current_soup_json = extract_page_data(current_soup)

            category_name = category.split("/")[-1]
            with open(f"request_inputs&outputs/sodimac/{category_name}{page_number}.json", "w") as json_file:
                json.dump(current_soup_json, json_file)
