import os
# from snowflake.sqlalchemy import URL
# from sqlalchemy import create_engine, text
import snowflake.connector
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

    # url = URL(
    #             user=ic(SFUSER),
    #             password=SFKAGI,
    #             account=ic(SFACCOUNT),
    #             warehouse=ic(SFWAREHOUSE),
    #             database=ic(SFDATABASE),
    #             schema=ic(".".join((SFDATABASE, SFSCHEMA))),
    #             role=ic(SFROLE)
    #             )    
    # If psql PORT is not the default(5432) add the port variable to activate and to connect

    # Based on postgresqltutorial.com
    try: 
        # engine = create_engine(url, future=True) # future is to autocommit executions
        # connection = engine.connect()
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
            connection.close()
            # engine.dispose()

    # return connection, engine
    return cursor, connection


class DBHandler:
    SFWAREHOUSE = os.environ.get("SFWAREHOUSE")
    SFDATABASE = os.environ.get("SFDATABASE")
    SFSCHEMA = os.environ.get("SFSCHEMA")

    def __init__(self):
        self.cursor, self.__connection = connect()
        self.table_name_base = None # todo: amplify to generic table name, for now it will just be product
        self.__products = list() # Temporary products fetched and to be add to db
        self.commands = list()
        self.error = None # Last error encountered
        self.__insertor = None

        self.commands.append(f"USE WAREHOUSE {DBHandler.SFWAREHOUSE}")
        self.commands.append(f"USE DATABASE {DBHandler.SFDATABASE}") 
        self.commands.append(f"USE SCHEMA {DBHandler.SFDATABASE}.{DBHandler.SFSCHEMA}")
        

    # SQL commands
    def create_table(self, name): # Name should be always be singular
        sql_command = f"""CREATE TABLE IF NOT EXISTS {name}s (
            NAME VARCHAR(255) NOT NULL,
            PRICE INTEGER NOT NULL,
            SKU VARCHAR(15),
            BRAND VARCHAR(255),
            DATE DATE, 
            STORE VARCHAR(10),
            URL VARCHAR(2083),
            IMAGE_AT VARCHAR(2083),
            DESCRIPTION TEXT
            );
            """
        # Save the command to queue and the table name for further use
        self.commands.append(sql_command)
        self.table_name = f"{name}s"

    def insert_items(self):
        # Creates the db insertion query with insertor
        self.__insertor.build_insert_query()
        # Execute previous commands, to complete table with columns 
        # that may be missing
        self.execute_commands()
        # Do the insertion (with SQL ALquemy)
        self.__insertor.send_insert_query(self.__connection, "products", DBHandler.SFDATABASE, DBHandler.SFSCHEMA)

    def execute_commands(self):
        for sql_command in self.commands:
            try:
                self.cursor.execute(ic(sql_command))
                self.__connection.commit()
                # self.__connection.execute(text(ic(sql_command)))

            except Exception as error:
                self.error = error
                ic(error)
        # Clean already executed commands
        self.commands = list()
    
    def save_and_disconnect(self, connection=None, cursor=None):
        if connection == None: connection = self.__connection
        # if engine == None: engine = self.__engine
        if cursor == None: cursor = self.cursor
        # Save changes if no error
        connection.commit()
        # connection.execute(text("COMMIT"))
        if cursor: cursor.close()
        if connection: connection.close()
        # if engine: engine.dispose()
        ic("Connection to database closed.")

    def get_headers(self):
        # Gets the table metadate and returns a set with headers 
        name_tuples = self.cursor.execute(F"SELECT COLUMN_NAME FROM {DBHandler.SFDATABASE}.information_schema.columns WHERE TABLE_NAME = 'PRODUCTS';")
        column_names = map(lambda name_tuple: name_tuple[0], name_tuples)
        return ic(set(column_names))

    def append(self, product):
        ic(product)
        self.__insertor.append(product)
        self.__products.append(product)
        
    def extend(self, product_list):
        for product in product_list:
            self.append(product)

    def add_insertor(self, insert_builder):
        self.__insertor = insert_builder
        self.__insertor.headers = self.get_headers()
        self.__insertor.db_handler = self
    
if __name__ == "__main__":
    import sys
    from os.path import dirname, realpath
    sys.path.append(dirname(dirname(realpath(__file__))))
    
    from src.products import Product
    from src.insert_builder import InsertBuilder

    handler = DBHandler()
    handler.add_insertor(InsertBuilder())    
    
    example_product = Product("Martillo", "42", "Bosch", "Super Martillo", "24", "https://i.kym-cdn.com/entries/icons/original/000/000/615/BANHAMMER.png", "1990", "www.sodimac.cl", {}, "SODIMAC")
    
    

    handler.create_table("product")

    handler.get_headers()

    # handler.append(example_product)
    # ic("Hola")
    # handler.insert_items()
    # handler.execute_commands()
    

    handler.save_and_disconnect()
        
    