import threading
from random import random
from time import sleep, time
from itertools import chain
from icecream import ic
import src.sodimac.category_getter as sodimac_getter
import src.easy.category_getter as easy_getter
import src.autoplanet.category_getter as autoplanet_getter
from src.products import Product
from src.database_hanlder import DBHandler
from src.insert_builder import InsertBuilder
from src.aux_functions import take_time, generate_params, generate_data, get_secrets_dic


@take_time
def main(getter, lock, min_wait_time, secrets):
    errors = 0

    lock.acquire()
    handler = DBHandler(secrets) # Create instance of database handler
    handler.add_insertor(InsertBuilder())
    lock.release()

    current_soup = None
    last_page_number = 0
    for category in getter.categories:
        aux_generator = []
        current_soup, last_page_number = getter.init_(category)
        sleep(min_wait_time + random())
        aux_generator = chain([], getter.extract_page_data(current_soup))

        for page_number in range(1, last_page_number+1):
            sleep(min_wait_time + random())
            # Sleep the minimum time of the store + some randomness to seem organic 
            # to prevent being shut out of source api for too many consecutive requests
            try:
                ic(f"{category}: {page_number} of {last_page_number}")
                current_soup = getter.get_page_data(category, page_number)
                current_soup_json = getter.extract_page_data(current_soup)
                aux_generator = chain(aux_generator, current_soup_json) # Concatenate lists
            except Exception as error:
                print(type(error))
                errors += 1
                continue

        ready_data_generator = map(lambda raw_data: getter.parse_data(raw_data, category), aux_generator)
        product_list = list(map(lambda rd: Product(**rd), ready_data_generator))
        # ic(len(product_list))
        handler.extend(product_list)
        # # ic(handler.products)
    
    handler.create_table("product")
    handler.insert_items()
    lock.acquire()
    handler.execute_commands()
    lock.release()

def demo():
    handler = DBHandler() # Create instance of database handler
    handler.add_insertor(InsertBuilder())

    generated_params = generate_params(227000, 90)

    ready_data_generator = map(lambda raw_params: generate_data(raw_params, 
                                                                "Juego 4 Amortiguadores Toyota Starlet 96/99", 
                                                                "113551301D2", 
                                                                "https://www.falabella.com/falabella-cl/product/113551300/Juego-4-Amortiguadores-Toyota-Starlet-96-99/113551301", 
                                                                "sodimac"), generated_params)
    product_list = list(map(lambda rd: Product(**rd), ready_data_generator))
    ic(len(product_list))
    handler.extend(product_list)
    # # ic(handler.products)
    
    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()


if __name__ == "__main__":
    # We build a lock so that no conflicts happen when writing to the database
    start = time()
    hiketsu = get_secrets_dic()

    db_lock = threading.Lock()
    t1 = threading.Thread(target=main, args=(easy_getter, db_lock, 4, hiketsu))
    t2 = threading.Thread(target=main, args=(sodimac_getter, db_lock, 1, hiketsu))
    t3 = threading.Thread(target=main, args=(autoplanet_getter, db_lock, 1, hiketsu))
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    # demo()
    end = time()
    ic(f"Runtime: {(end - start) / 60} minutes")

    # 113551301 sodimac