import time
import json
import requests
from random import randint
from icecream import ic
from bs4 import BeautifulSoup


def get_data_for(sku):
    # Recive SKU (or product ID) and return the soup
    soup = get_page_data(sku)
    product_data = extract_page_data(soup)
    return product_data


def get_page_data(sku):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        product_url = f'https://www.falabella.com/falabella-cl/search?Ntt={sku}'
        # Based on https://es.stackoverflow.com/questions/545411/scrap-con-beautifulsoup-pero-no-obtengo-toda-la-info-los-selectores-son-multicl
        request = requests.get(product_url)
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
    product_data = soup_json["props"]["pageProps"]["productData"]
    return product_data


if __name__ == "__main__":

    product_data = get_data_for(110316098)
    # test_url = "https://www.falabella.com/falabella-cl/search?Ntt=110316098"
    # request = requests.get(test_url)
    # data_soup = BeautifulSoup(request.text, "lxml")
    # soup_data = data_soup.find("script", attrs={'id': '__NEXT_DATA__'})
    # soup_json = json.loads(soup_data.get_text())
    # product_data = soup_json["props"]["pageProps"]["productData"]
    ic(product_data["name"])
    ic(product_data["id"])
    ic(product_data["brandName"])
    ic(product_data["description"])
    ic(product_data["breadCrumb"]) # Page data (link, category, ...)
    ic(product_data["currentVariant"])
    ic(product_data["variants"][0]["medias"][0]["url"])
    ic(product_data["attributes"]["specifications"])
    # ic(product_data["name"])

    with open("request_inputs&outputs/sodimac/product.json", 'w') as json_file:
        json.dump(product_data, json_file)
