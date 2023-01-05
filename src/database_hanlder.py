import snowflake.connector
from collections import deque
from icecream import ic


def connect(secrets):
    # Instead of local variables we are now using AWS secrets
    SFUSER = secrets['SFUSER']
    SFKAGI = secrets['SFKAGI']
    SFACCOUNT = secrets["SFACCOUNT"]
    SFWAREHOUSE = secrets["SFWAREHOUSE"]
    SFDATABASE = secrets["SFDATABASE"]
    SFSCHEMA = secrets["SFSCHEMA"]
    SFROLE = secrets["SFROLE"]

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

    # return connection, engine
    return cursor, connection


class DBHandler:
    def __init__(self, secrets):
        self.cursor, self.__connection = connect(secrets)
        self.table_name_base = None # todo: amplify to generic table name, for now it will just be product
        self.__products = list() # Temporary products fetched and to be add to db
        self.commands = deque()
        self.error = None # Last error encountered
        self.__insertor = None

        self.commands.append(f"USE WAREHOUSE {secrets['SFWAREHOUSE']}")
        self.commands.append(f"USE DATABASE {secrets['SFDATABASE']}") 
        self.commands.append(f"USE SCHEMA {secrets['SFDATABASE']}.{secrets['SFSCHEMA']}")

        self.secrets = secrets

        self.create_table("product")
        

    # SQL commands
    def create_table(self, name): # Name should be always be singular
        sql_command = f"""CREATE TABLE IF NOT EXISTS {name}s (
            NAME VARCHAR(255) NOT NULL,
            PRICE INTEGER NOT NULL,
            SKU VARCHAR(15),
            BRAND VARCHAR(255),
            DATE DATE, 
            STORE VARCHAR(10),
            CATEGORY VARCHAR(255),
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
        self.__insertor.send_insert_query(
            self.__connection, "products", 
            self.secrets['SFDATABASE'], self.secrets['SFSCHEMA'])

    def execute_commands(self):
        for sql_command in self.commands:
            try:
                self.cursor.execute(sql_command)
                # self.cursor.execute(ic(sql_command))
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
        # If no headedrs are provided (for example if there is no table) 
        # returns empty set
        try:
            name_tuples = self.cursor.execute(F"SELECT COLUMN_NAME FROM {self.secrets['SFDATABASE']}.information_schema.columns WHERE TABLE_NAME = 'PRODUCTS';")
            column_names = map(lambda name_tuple: name_tuple[0], name_tuples)
            return ic(set(column_names))
        except Exception as e:
            ic(e)
            return set()

    def append(self, product):
        # ic(product)
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
        
    