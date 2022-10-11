import time
import requests
from icecream import ic
from bs4 import BeautifulSoup
from aux_functions import load_categories

categories = load_categories("sodimac")

def init_(category):
    # First iteration needs some extra steps
    current_soup = get_page_data(category, 1)
    last_page_number = get_category_range(current_soup)
    return current_soup, last_page_number


def get_category_range(soup):
    # Only if the get_page_data was successfull look for category pages number
    if not soup:
        ic("Error found. Aborting.")
        return 0

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

def get_page_data(category, page_number):
    # Try to connect to SODIMAC webpage and get data
    # Return data as a Beautiful HTML Soup
    try: 
        category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page={page_number}&store=sodimac'
        response = requests.get(category_url).content
        current_soup = BeautifulSoup(response, 'html5lib')
        return current_soup
    
    except Exception as error:
        # Todo --> Turn this print into a log
        ic(error)
        return None





    

if __name__ == "__main__":

    current_soup = None
    last_page_number = 0
    for category in categories:
        ic(category)    
        # category_url = f'https://sodimac.falabella.com/sodimac-cl/category/{category}?subdomain=sodimac&page=1&store=sodimac'
        # response = requests.get(category_url).content
        # current_soup = BeautifulSoup(response, 'html5lib')
        
        current_soup, last_page_number = init_(category)
        
        # ic(soup.prettify())
        
        # Todo --> remove the last_page_number overwrite
        last_page_number = 3
        for page_number in range(2, last_page_number + 1):
            # Wait a bit to prevent the webpagge of kicking us out
            time.sleep(0.5)
            ic(page_number)
            current_soup = get_page_data(category, page_number)

            
            

        break
        # https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
