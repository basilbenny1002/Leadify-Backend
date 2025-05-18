import psycopg2
from dotenv import load_dotenv
import os
import json
from decimal import Decimal
import decimal
from supabase import create_client, Client

psycopg2.extensions.register_adapter(decimal.Decimal, str)
psycopg2.extensions.register_adapter(decimal.Decimal, str)

load_dotenv()


# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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
        # cursor.execute("INSERT INTO fruits (name) VALUES (%s);", ("Banana",))
        # cursor.execute("SELECT * FROM fruits")
        cursor.execute(query)
        # print(cursor.fetchall())
        rows = cursor.fetchall()
        json_retult = {}
        key = 0
        for row in rows:
            data = dict(zip(column_names, row))
            json_retult[str(key)] = data
            key+=1
        print(rows)
        cursor.close()
        connection.commit()
        connection.close()
        print(type(rows[0]))
        print(type(rows[0][0]))
        return json_retult
    except Exception as e:
        print(f"Failed to connect: {e}")

def save_streamers_to_supabase(user_id: str, streamers: list[dict]):
    inserted = 0
    skipped = 0

    for streamer in streamers:
        data = {
            "user_id": user_id,
            "username": streamer.get("username"),
            "followers": int(streamer.get("followers", 0)),
            "subscriber_count": int(streamer.get("subscriber_count", 0)),
            "viewer_count": int(streamer.get("viewer_count", 0)),
            "language": streamer.get("language"),
            "game_name": streamer.get("game_name"),
            "gmail": streamer.get("gmail"),
            "twitter": streamer.get("twitter"),
            "instagram": streamer.get("instagram"),
            "youtube": streamer.get("youtube"),
            "facebook": streamer.get("facebook"),
            "tiktok": streamer.get("tiktok"),
            "linkedin": streamer.get("linkedin"),
            "discord": streamer.get("discord"),
        }

        try:
            supabase.table("twitch_streamers").insert(data).execute()
            inserted += 1
        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                skipped += 1
            else:
                print("Error inserting streamer:", e)

    print(f"Inserted: {inserted}, Skipped (duplicates): {skipped}")

def fetch_saved_streamers(user_id: str):
    print(user_id)
    response = (
        supabase
        .from_("twitch_streamers")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise Exception(response.error.message)
    return response.data

print(get_values("Test", "name", "age"))