from random import randint
from time import sleep
from itertools import chain
from icecream import ic
import src.sodimac.product_getter as sodimac_getter
import src.easy.product_getter as easy_getter
import src.autoplanet.category_getter as autoplanet_getter
from src.products import Product
from src.database_hanlder import DBHandler
from src.sku_getter import sonax_skus



def main1():
    errors = 0
    handler = DBHandler() # Create instance of database handler
    # We create two example products to try some things
    for item in sonax_skus.iterrows():
        try:
            sku, store = item[1][["sku", "store"]]
            match store:
                case "sodimac":
                    sku = sku.replace("-", "")
                    raw_data = sodimac_getter.get_data_for(sku)
                    ready_data = sodimac_getter.parse_data(raw_data)
                case "easy":
                    raw_data = easy_getter.get_data_for(sku)
                    ready_data = easy_getter.parse_data(raw_data, sku)
                case "autoplanet":
                    print("Autoplanet is currently only working with get_category")
                    continue
                case _:
                    print(f"There is no store {store} registered.")
                    continue
        except Exception as error:
            print(type(error))
            print(f"Could not find sku {sku} from {store}")
            errors += 1
            continue
        handler.products.append(Product(**ready_data))
        sleep(randint(1, 10))
    print((errors, len(handler.products)), len(sonax_skus[sonax_skus["store"]==("sodimac" or "easy")]))
    # # ic(handler.products)
    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()

def main2():
    errors = 0
    handler = DBHandler() # Create instance of database handler
    autoplanet_products = dict()
    current_soup = None
    last_page_number = 0
    for category in autoplanet_getter.categories:
        autoplanet_products[category] = []
        aux_generator = []
        ic(category)

        current_soup, last_page_number = autoplanet_getter.init_(category)
        aux_generator = chain([], autoplanet_getter.extract_page_data(current_soup))

        for page_number in range(1, last_page_number):
            sleep(randint(1, 10))
            try:
                ic(page_number)
                current_soup = autoplanet_getter.get_page_data(category, page_number)
                current_soup_json = autoplanet_getter.extract_page_data(current_soup)
                aux_generator = chain(aux_generator, current_soup_json) # Concatenate lists
            except Exception as error:
                print(type(error))
                errors += 1
                continue

        ready_data_generator = map(lambda raw_data: autoplanet_getter.parse_data(raw_data), aux_generator)
        product_list = ic(list(map(lambda rd: Product(**rd), ready_data_generator)))
        handler.products.extend(product_list)
        # # ic(handler.products)

    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()



if __name__ == "__main__":
    # main1()
    main2()