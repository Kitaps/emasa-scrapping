import pandas
import pyarrow as pa
from datetime import datetime
from icecream import ic
from snowflake.connector.pandas_tools import write_pandas


class InsertBuilder:
    insertion_count = 0

    def __init__(self, max_size=None) -> None:
        self.df = pandas.DataFrame()
        self.max_size = max_size
        self.db_handler = None
        self.date = str(datetime.date(datetime.today()))
        self.headers = set()
        self.products_dic_list = list()
        self.products_df = None

    def append(self, product):
        self.products_dic_list.append(self.parse_insertion(product))
    
    def parse_insertion(self, product):
        # Prepare the command to insert the items
        # Add extra columns to table to fit all extra product specifications
        product_dict =  product.export_dict()
        keys = set(product_dict.keys())
        for new_spec in (keys-self.headers):
            self.db_handler.commands.append(f"ALTER TABLE products ADD COLUMN {new_spec} VARCHAR(255);")
            self.headers.update(keys)
            # Update schema with new column key
            new_schema = self.flavor_schema.append(pa.field(new_spec, pa.string()))
            self.flavor_schema = new_schema
        return product_dict

    def build_insert_query(self):
        # Turns the product dict list into a df and sends it to the handler
        self.df = pandas.DataFrame(self.products_dic_list)

    def send_insert_query(self, connection, table_name, database, schema):
        # Instead of doing it's previous function, now this method uses the 
        # pandas writer of the snowflake.connector
        write_pandas(
            conn=connection,
            df=self.df,
            table_name=table_name,
            database=database,
            schema=schema,
            chunk_size=self.max_size,
            quote_identifiers=False)


if __name__ == "__main__":
    test_builder = InsertBuilder()
