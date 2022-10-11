from xml.dom.minidom import AttributeList
import requests
from icecream import ic
from bs4 import BeautifulSoup
from aux_functions import load_categories

categories = load_categories("sodimac")

def get_page_range(soup):
    # Find any of the page list elements on the site
    pages_ordered_list = soup.find('ol', attrs = {'class': 'jsx-1794558402 jsx-1490357007'})
    # ic(int(tuple(pages_ordered_list)[-1].text))
    # Extract the last element from the obtained html element
    #   To do this, we turn the element into a tuple and then obtain it's last element
    last_element = tuple(pages_ordered_list)[-1]
    # This element will have a text containing the last page name, which we want
    number_name = last_element.text
    # Finally we turn the number string into a number and return
    return int(number_name)
    

if __name__ == "__main__":

    for category in categories:
        ic(category)    
        category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page=1&store=sodimac'
        response = requests.get(category_url).content
        soup = BeautifulSoup(response, 'html5lib')
        # ic(soup.prettify())
        ic(get_page_range(soup))
        
        # https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
