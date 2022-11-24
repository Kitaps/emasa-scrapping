import pandas
from datetime import datetime
from icecream import ic

class InsertBuilder:
    insertion_count = 0

    def __init__(self, max_size=100) -> None:
        self.df = pandas.DataFrame()
        self.max_size = max_size
        self.db_handler = None
        self.date = str(datetime.date(datetime.today()))
        self.headers = set()
        self.products_dic_list = list()
        self.products_df = None

    def append(self, product):
        # InsertBuilder.insertion_count += 1

        # if InsertBuilder.insertion_count >= self.max_size:
        #     self.build_insert_query()

        self.products_dic_list.append(self.parse_insertion(product))
    
    def parse_insertion(self, product):
        # Prepare the command to insert the items
        # Add extra columns to table to fit all extra product specifications
        product_dict =  ic(product.export_dict())
        keys = set(product_dict.keys())
        for new_spec in (keys-self.headers):
            self.db_handler.commands.append(f"ALTER TABLE products ADD COLUMN {new_spec} VARCHAR(255);")
            self.headers.update(keys)
        return product_dict

    def build_insert_query(self):
        # Turns the product dict list into a df and sends it to the handler
        self.df = pandas.DataFrame(self.products_dic_list)

        
        
if __name__ == "__main__":
    test_builder = InsertBuilder()

