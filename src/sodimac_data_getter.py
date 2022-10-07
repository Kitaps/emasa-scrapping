import requests
from icecream import ic
from bs4 import BeautifulSoup
from aux_functions import load_categories

categories = load_categories("sodimac")
ic(categories)

if __name__ == "__main__":

    url = 'https://sodimac.falabella.com/sodimac-cl/category/CATG10731/Materiales-de-Construccion?subdomain=sodimac&page=1&store=sodimac'
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html5lib')
    # ic(soup.prettify())
    
    # https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
