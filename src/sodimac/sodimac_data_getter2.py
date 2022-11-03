import time
import json
import requests
from random import randint
from icecream import ic
from bs4 import BeautifulSoup



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

    test_url = "https://www.falabella.com/falabella-cl/search?Ntt=110318820"
    request = requests.get(test_url)
    data_soup = BeautifulSoup(request.text, "lxml")
    soup_data = data_soup.find("script", attrs={'id': '__NEXT_DATA__'})
    soup_json = json.loads(soup_data.get_text())
    print(soup_json)
