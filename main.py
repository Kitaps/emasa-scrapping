from icecream import ic
import src.sodimac.product_getter as sodimac_getter
import src.easy.product_getter as easy_getter
from src.products import Product
from src.database_hanlder import DBHandler


def main():
    # We create two example products to try some things
    product_data = sodimac_getter.parse_data(sodimac_getter.get_data_for(110316112))
    bateria = Product(**product_data)

    product_data = easy_getter.parse_data(easy_getter.get_data_for(672286), 672286)
    anti_pinchazo = Product(**product_data)
    # ic(bateria.to_sql())
    # ic(anti_pinchazo.to_sql())

    handler = DBHandler()
    handler.add_product_sql(bateria)
    handler.add_product_sql(anti_pinchazo)
    ic(handler.products)
    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()

if __name__ == "__main__":
    main()