import os
import psycopg2
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

    except (Exception, psycopg2.DatabaseError, psycopg2.OperationalError) as error:
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
            url VARCHAR(2083),
            image_at VARCHAR(2083),
            description TEXT
            );
            """
        # Save the command to queue and the table name for further use
        self.commands.append(sql_command)
        self.table_name = f"{name}s"

    def insert_items(self):

        for product in self.products:
            # Prepare the command to insert the items
            # Add extra columns to table to fit all extra product specifications
            keys, values = list(), list()
            if product.specifications:
                keys = list(product.specifications.keys())
                values = product.specifications.values()
            for spec in keys:
                self.commands.append(f"ALTER TABLE products ADD COLUMN IF NOT EXISTS {spec} VARCHAR(255);")
            # Add the product row
            keys.insert(0, "") # We add an empty string so that after the join the keys_str looks like:
                               # ", First, Second, ..., Last"
            keys_str = ", ".join(keys)
            sql_command = f"""INSERT INTO 
            products(name, price, sku, brand, url, image_at, description{keys_str}) 
            VALUES{
                (product.name, product.price, product.sku, product.brand, 
                product.url, product.image_at, product.description, *values)};"""
            self.commands.append(sql_command)
        
    def execute_commands(self):
        for sql_command in self.commands:
            try:
                self.cursor.execute(ic(sql_command))
                self.__connection.commit()
            except psycopg2.errors.DuplicateTable:
                # Added IF NOT EXISTS to create command, 
                # so this exception should not happen 
                ic("The table already exists: Command Skipped")
            except psycopg2.errors.InFailedSqlTransaction as error:
                self.error = error
                ic(error)
    
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

    
if __name__ == "__main__":
    import sys
    from os.path import dirname, realpath
    sys.path.append(dirname(dirname(realpath(__file__))))
    
    from src.products import Product

    handler = DBHandler()
    example_product = Product("Martillo", "42", "Bosch", "Super Martillo", "24", "https://i.kym-cdn.com/entries/icons/original/000/000/615/BANHAMMER.png", "1990", "www.sodimac.cl", [])
    
    handler.products.append(example_product)

    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()
    handler.save_and_disconnect()
        
    