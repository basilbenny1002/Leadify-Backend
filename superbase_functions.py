import psycopg2
from dotenv import load_dotenv
import os
import json
from decimal import Decimal
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def get_values(table_name: str, *column_names: str, condition=None):
    query = f"SELECT {",".join(column_names)} FROM {table_name}{condition if condition else ""}"
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
        )
        print("Connection successful!")
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        json_retult = {}
        key = 0
        for row in rows:
            data = dict(zip(column_names, row))
            json_retult[str(key)] = data
            key+=1
        cursor.close()
        connection.commit()
        connection.close()
        
        return json_retult
    except Exception as e:
        print(f"Failed to connect: {e}")


print(get_values("Test", "name", "age"))
