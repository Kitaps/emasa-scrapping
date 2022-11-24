import os
import snowflake.connector
from snowflake.connector.pandas_tools import pd_writer
from icecream import ic


def connect():
    # Instead of doing it with environment variables it could also be done with
    # a database.ini to be read with ConfigParser
    SFUSER = os.environ.get('SFUSER')
    SFKAGI = os.environ.get('SFKAGI')
    SFACCOUNT = os.environ.get("SFACCOUNT")
    SFWAREHOUSE = os.environ.get("SFWAREHOUSE")
    SFDATABASE = os.environ.get("SFDATABASE")
    SFSCHEMA = os.environ.get("SFSCHEMA")
    SFROLE = os.environ.get("SFROLE")
    
    # If psql PORT is not the default(5432) add the port variable to activate and to connect

    # Based on postgresqltutorial.com
    try: 
        connection = snowflake.connector.connect(
                user=ic(SFUSER),
                password=SFKAGI,
                account=ic(SFACCOUNT),
                warehouse=ic(SFWAREHOUSE),
                database=ic(SFDATABASE),
                schema=ic(".".join((SFDATABASE, SFSCHEMA))),
                role=ic(SFROLE)
                )

        cursor = connection.cursor()

    except Exception as error:
        ic("Encountered an error trying to connect to the database:")
        ic(error)
        if connection:
            connection.rollback()
            connection.close()

    return cursor, connection


class DBHandler:
    def __init__(self):
        self.cursor, self.__connection = connect()
        self.table_name_base = None # todo: amplify to generic table name, for now it will just be product
        self.products = list() # Temporary products fetched and to be add to db
        self.commands = list()
        self.error = None # Last error encountered
        self.insertor = None

        SFWAREHOUSE = os.environ.get("SFWAREHOUSE")
        SFDATABASE = os.environ.get("SFDATABASE")
        SFSCHEMA = os.environ.get("SFSCHEMA")

        self.commands.append(f"USE WAREHOUSE {SFWAREHOUSE}")
        self.commands.append(f"USE DATABASE {SFDATABASE}") 
        self.commands.append(f"USE SCHEMA {SFDATABASE}.{SFSCHEMA}")
        

    # SQL commands
    def create_table(self, name): # Name should be always be singular
        sql_command = f"""CREATE TABLE IF NOT EXISTS {name}s (
            name VARCHAR(255) NOT NULL,
            price INTEGER NOT NULL,
            sku VARCHAR(15),
            brand VARCHAR(255),
            date DATE, 
            store VARCHAR(10),
            url VARCHAR(2083),
            image_at VARCHAR(2083),
            description TEXT
            );
            """
        # Save the command to queue and the table name for further use
        self.commands.append(sql_command)
        self.table_name = f"{name}s"

    def insert_items(self):
        # Creates the db insertion query with insertor
        self.insertor.build_insert_query()
        # Execute previous commands, to complete table with columns 
        # that may be missing
        self.execute_commands()
        # Do the insertion (with SQL ALquemy)
        self.insertor.df.to_sql(
            name = "products",
            con = self.__connection,
            schema = os.environ.get("SFSCHEMA"),
            if_exists = "append",
            index = False,
            chunksize = self.insertor.max_size,
            method = pd_writer
        )

    def execute_commands(self):
        for sql_command in self.commands:
            try:
                self.cursor.execute(ic(sql_command))
                self.__connection.commit()

            except Exception as error:
                self.error = error
                ic(error)
        # Clean already executed commands
        self.commands = list()
    
    def save_and_disconnect(self, cursor=None, connection=None):
        if cursor == None: cursor = self.cursor
        if connection == None: connection = self.__connection
        if cursor: cursor.close()
        # Save changes if no error
        if not self.error: connection.commit()
        else:
            ic(f"Can't save changes due to error:\n {self.error}")
            connection.rollback()

        if connection: connection.close()
        ic("Connection to database closed.")

    def get_headers(self):
        # Gets the table metadate and returns a set with the headers
        metadata = self.cursor.describe("SELECT * FROM products")
        return set(col.name for col in metadata)

    def append(self, product):
        self.products.append(product)
        self.insertor.append(product)

    def add_insertor(self, insert_builder):
        self.insertor = insert_builder
        self.insertor.headers = self.get_headers()
        self.insertor.db_handler = self
        



    
if __name__ == "__main__":
    import sys
    from os.path import dirname, realpath
    sys.path.append(dirname(dirname(realpath(__file__))))
    
    from src.products import Product
    from src.insert_builder import InsertBuilder

    handler = DBHandler()
    handler.add_insertor(InsertBuilder())    
    
    example_product = Product("Martillo", "42", "Bosch", "Super Martillo", "24", "https://i.kym-cdn.com/entries/icons/original/000/000/615/BANHAMMER.png", "1990", "www.sodimac.cl", {}, "SODIMAC")
    
    handler.append(example_product)

    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()
    

    print(handler.get_headers())

    handler.save_and_disconnect()
        
    