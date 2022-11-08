import json
import requests
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

def parse_data(raw_data):
    # Takes the obtained data and parses the useful parts to match the Product Object format
    kwargs = {
        "name": raw_data["name"],
        "product_id": raw_data["id"],
        "brand": raw_data["brandName"],
        "description": raw_data["description"],
        # raw_data["breadCrumb"], # Page data (link, category, ...
        "sku": raw_data["currentVariant"],
        "image_at": raw_data["variants"][0]["medias"][0]["url"],
        "price": clean(raw_data["variants"][0]["prices"][0]["price"][0]),
        "url": raw_data["shareIcons"][0]["url"],
        "specifications": trim(raw_data["attributes"]["specifications"])}
    return kwargs

def trim(raw_specifications):
    # Recives specifications as 
    # [{'id': 'Marca', 'name': 'Marca', 'value': 'Mamut'},
    # {'id': 'Largo_de_la_rosca', 'name': 'Largo de la rosca', 'value': '2 "'},
    # {'id': 'Diámetro', 'name': 'Diámetro', 'value': '1/4 "'}]
    # and resturns it as key: value
    # {"Marca": "Mamut",
    # "Largo_de_la_rosca": "2 "",
    # "Diámetro": 1/4 ""}
    specifications_dict = {entry["id"]: entry["value"] for entry in raw_specifications}
    return specifications_dict

def clean(price):
    # Remove . and transform from str to int
    
    return int(price.replace(".", ""))

if __name__ == "__main__":

    # product_data = get_data_for(110316112)
    # ready_data = parse_data(product_data)
    # ic(", ".join(ready_data.keys()))

    ic(clean('15.690'))

    # with open("request_inputs&outputs/sodimac/product.json", 'w') as json_file:
    #     json.dump(product_data, json_file)
