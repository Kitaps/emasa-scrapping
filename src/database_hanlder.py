import os
import psycopg2

if __name__ == "__main__":
    PASSWORD = os.environ.get('KAGI')
    print(PASSWORD)
    # connection = psycopg2.connect()