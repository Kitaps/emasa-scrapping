import os
import psycopg2
from icecream import ic


def connect():
    # Instead of doing it with environment variables it could also be done with
    # a database.ini to be read with ConfigParser
    USER = os.environ.get('USER')
    KAGI = os.environ.get('KAGI')
    PRODUCTSDB = os.environ.get('PRODUCTSDB')
    HOST = os.environ.get('HOST')
    # If psql PORT is not the default(5432) add the port variable to activate and to connect

    # Based on postgresqltutorial.com
    connection = None
    cursor = None
    try: 
        connection = psycopg2.connect(
            host = ic(HOST),
            password = KAGI, # We dont print the KAGI to keep it safe
            database = ic(PRODUCTSDB),
            user = ic(USER))

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

    # SQL commands
    def create_table(self, name): # Name should be always be singular
        sql_command = f"""CREATE TABLE IF NOT EXISTS {name}s (
            {name}_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price INTEGER NOT NULL,
            sku VARCHAR(15),
            brand VARCHAR(255),
            url VARCHAR(2083),
            image_at VARCHAR(2083),
            description TEXT
            )
            """
        # Save the command to queue and the table name for further use
        self.commands.append(sql_command)
        self.table_name = f"{name}s"

    def add_product_sql(self, product):
        # We add the product to the handlers product list
        # To do this we use the products method to be usable by executemany
        self.products.append(product.to_sql())

    def insert_items(self):
        # Prepare the command to insert the items
        sql_command = "INSERT INTO products(name, price, sku, brand, url, image_at, description) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        self.commands.append(sql_command)
        
    def execute_commands(self):
        for sql_command in self.commands:
            try:
                if sql_command[0:6] == 'INSERT':
                    # If the command starts with I it means it is an INSERT command
                    cursor, connection = connect()
                    # The multiprocessing needs it's own connection
                    # Thats why we connect and disconect in this scope
                    # !! Documentation says that a loop would be as efficient as executemany in the current version!!
                    cursor.executemany(sql_command, self.products)
                    self.save_and_disconnect(cursor, connection) 
                elif sql_command[0:6] == 'CREATE':
                    self.cursor.execute(sql_command)
                    self.__connection.commit()
                else:
                    self.cursor.execute(sql_command)
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

    handler = DBHandler()
    handler.products

    handler.create_table("product")
    handler.insert_items()
    handler.execute_commands()
        
    