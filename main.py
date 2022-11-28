from random import randint
from time import sleep
from icecream import ic
import src.sodimac.product_getter as sodimac_getter
import src.easy.product_getter as easy_getter
from src.products import Product
from src.database_hanlder import DBHandler
from src.insert_builder import InsertBuilder
from src.sku_getter import sonax_skus



def main():
    errors = 0
    handler = DBHandler() # Create instance of database handler
    handler.add_insertor(InsertBuilder())
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
                case _:
                    print(f"There is no store {store} registered.")
                    continue
        except Exception as error:
            print(type(error))
            print(f"Could not find sku {sku} from {store}")
            errors += 1
            continue
        handler.append(Product(**ready_data))
        sleep(randint(1, 10))
    print((errors, len(handler.products)), len(sonax_skus[sonax_skus["store"]==("sodimac" or "easy")]))
    # # ic(handler.products)
    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()

if __name__ == "__main__":
    main()