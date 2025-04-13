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
            dbname=DBNAME
        )
        print("Connection successful!")
        cursor = connection.cursor()
        # cursor.execute("INSERT INTO fruits (name) VALUES (%s);", ("Banana",))
        # cursor.execute("SELECT * FROM fruits")
        cursor.execute(query)
        print(cursor.fetchall())
        result = cursor.fetchall()

        cursor.close()
        connection.commit()
        connection.close()
        print("Connection closed.")
        result_json = {i:}
        return result
    except Exception as e:
        print(f"Failed to connect: {e}")
        result = [dict(zip(column_names, [float(val) if isinstance(val, Decimal) else val for val in row])) for row in rows]


print(get_values("Test", "name", "age"))
