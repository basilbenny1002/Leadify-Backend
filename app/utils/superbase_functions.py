import datetime
import uuid
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



async def create_folder(user_id: str, name: str):
    if name.lower() in ["all", "favourites"]:
        return {"error": "Reserved folder name."}

    folder_id = str(uuid.uuid4())

    response = (
        supabase
        .from_("folders")
        .insert({
            "id": folder_id,
            "user_id": user_id,
            "name": name,
            "is_mandatory": False,
            "created_at": datetime.datetime.now().isoformat()
        })
        .execute()
    )

    if not response.data:
        return {"error": response}

    return {"id": folder_id, "name": name}

async def get_folders(user_id: str):
    # Select folders along with a count of streamers per folder
    response = (
        supabase
        .from_("folders")
        .select("*, twitch_streamers(count)")
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        return {"error": response.error.message}

    # response.data is a list of folders with a nested `twitch_streamers` array containing count
    # transform to add streamer_count easily
    folders = []
    for folder in response.data:
        streamer_count = folder.get("twitch_streamers", [{}])[0].get("count", 0) if folder.get("twitch_streamers") else 0
        folder["streamer_count"] = streamer_count
        # optionally remove the nested twitch_streamers key if you don't want to send it
        folder.pop("twitch_streamers", None)
        folders.append(folder)
    return folders

async def get_saved_streamers(user_id: str, folder_id: str):
    response = None
    if folder_id == "all":
        response = supabase.from_("twitch_streamers").select("*").eq("user_id", user_id).execute()
    elif folder_id == "favourites":
        response = supabase.from_("twitch_streamers").select("*").eq("user_id", user_id).eq("is_favourite", True).execute()
    else:
        response = supabase.from_("twitch_streamers").select("*").eq("user_id", user_id).eq("folder_id", folder_id).execute()


    if not response.data:
        return []
    return response.data


async def add_streamer_to_folder(user_id: str, streamer_id: str, folder_id: str):
    print('function hit')
    print(user_id, streamer_id, folder_id)
    response = (
        supabase
        .from_("twitch_streamers")
        .update({"folder_id": folder_id})
        .eq("id", streamer_id)
        .eq("user_id", user_id)
        .execute()
    )

    print(response)

    if not response.data:
        return {"error": response}
    return {"success": True}

async def toggle_favourite(user_id: str, streamer_id: str, is_fav: bool):
    response = (
       supabase
        .from_("twitch_streamers")
        .update({"is_favourite": is_fav})
        .eq("id", streamer_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return {"error": response.error.message}
    return {"success": True}