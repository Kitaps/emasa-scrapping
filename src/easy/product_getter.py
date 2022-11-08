import json
import requests
from icecream import ic
from bs4 import BeautifulSoup


def get_data_for(sku):
    # Recive SKU (or product ID) and return the soup
    soup = get_page_data(sku)
    # print(soup.prettify())
    product_data = extract_page_data(soup)
    return product_data


def get_page_data(sku):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        product_url = f'https://www.easy.cl/{sku}'
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
    # The second link is wanted:
    soup_data = soup.find_all("script", attrs={'type': 'application/ld+json'})[1]
    soup_json = json.loads(soup_data.get_text())
    product_data = soup_json["itemListElement"][0]["item"]
    return product_data

def parse_data(raw_data, sku):
    # Takes the obtained data and parses the useful parts to match the Product Object format
    # Currently the sku is not returned by the API after the request, 
    # just in the url, so we pass it for now
    kwargs = {
        "name": raw_data["name"],
        "product_id": sku, # For now sku and product id are the same in easy
        "brand": raw_data["brand"]["name"],
        "description": raw_data["description"],
        # raw_data["breadCrumb"], # Page data (link, category, ...
        "sku": sku,
        "image_at": raw_data["image"],
        "price": raw_data["offers"]["offers"][0]["price"],
        "url": raw_data["@id"],
        "specifications": None} # For now there are no extra specifications, 
                                # these must be found on the url page of the product
    return kwargs

def trim(raw_specifications):
    pass

def clean(price):
    pass

if __name__ == "__main__":

    product_data = get_data_for(672286)
    ready_data = parse_data(product_data)
    # ic(", ".join(ready_data.keys()))

    # with open("request_inputs&outputs/sodimac/product.json", 'w') as json_file:
    #     json.dump(product_data, json_file)
