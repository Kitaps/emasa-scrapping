import os
import psycopg2
from icecream import ic

if __name__ == "__main__":
    USER = os.environ.get('USER')
    KAGI = os.environ.get('KAGI')
    PRODUCTSDB = os.environ.get('PRODUCTSDB')
    ATTRIBUTESDB = os.environ.get('ATTRIBUTESDB')
    # connection = psycopg2.connect()
    ic((USER, KAGI, PRODUCTSDB, ATTRIBUTESDB))