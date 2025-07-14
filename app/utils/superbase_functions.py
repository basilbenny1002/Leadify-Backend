import datetime
import uuid
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import psycopg2
from dotenv import load_dotenv
import os
import json
from decimal import Decimal
import decimal
from supabase import create_client, Client
from app.utils.billing_functions import add_credits
from app.utils.functions import load_config
# from datetime import datetime, timezone
load_config()

psycopg2.extensions.register_adapter(decimal.Decimal, str)
psycopg2.extensions.register_adapter(decimal.Decimal, str)




# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_csv(search_id_uuid, user_id, filters, file_name, total, valid):
    with open(file_name, "rb") as f:
        res = supabase.storage.from_("results").upload(file_name, f)
        print(res)
    if not res.path:
        raise Exception(f"CSV upload failed: {res}")
    filters_json = json.dumps(filters)
    
    res =  supabase.table("search_results").insert({ 
    "user_id": user_id,
    "search_id": search_id_uuid,
    "filters": filters_json,
    "valid_streamers": valid,   
    "total_streamers": total,
    "file_path": file_name
    }).execute()
    print(res)


def get_values(table_name: str, *column_names: str, condition=None):
    query = f'SELECT {",".join(column_names)} FROM {table_name}{condition if condition else ""}'
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
        raise Exception(response)
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
    print(response)
    if not response.data:
        return {"error": response}
    

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
        response = (
            supabase
            .from_("twitch_streamers")
            .select("*")
            .eq("user_id", user_id)
            .order("saved_at", desc=True)
            .execute()
        )

    elif folder_id == "favourites":
        response = (
            supabase
            .from_("twitch_streamers")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_favourite", True)
            .order("saved_at", desc=True)
            .execute()
        )

    else:
        response = (
            supabase
            .from_("twitch_streamers")
            .select("*")
            .eq("user_id", user_id)
            .eq("folder_id", folder_id)
            .order("saved_at", desc=True)            
            .execute()
        )
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
        return {"error": response}
    return {"success": True}


async def save_filter_to_supabase(user_id: str, data):
    response = supabase.from_("saved_filters").insert({
        "user_id": user_id,
        "name": data.name,
        "language": data.language,
        "category": data.category,
        "min_followers": data.min_followers,
        "max_followers": data.max_followers,
        "min_viewers": data.min_viewers,
        "max_viewers": data.max_viewers
    }).execute()

    if not response.data:
        raise Exception(response)
    return response.data

async def get_saved_filters(user_id: str):
    response = supabase.from_("saved_filters").select("*").eq("user_id", user_id).execute()

    if not response.data:
        print(response)
        return response.data
    return response.data

async def delete_saved_filter(user_id: str, filter_id: str):
    response = supabase.from_("saved_filters").delete().eq("id", filter_id).eq("user_id", user_id).execute()

    if not response.data:
        raise Exception(response)
    return {"status": "deleted"}

async def initialize_user_onSignup(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    # Free plan default setup
    FREE_CREDITS = 25

    add_credits(user_id,"Signup Bonus", FREE_CREDITS, "bonus")



def add_notification(user_id: str,title: str,  message: str):
    supabase.from_("notifications").insert({
        "user_id": user_id,
        "title": title,
        "description": message,
        "read": False,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": "info"
    }).execute()

def clean_old_notifications():
    now = datetime.datetime.now(datetime.timezone.utc)

    # 1. Delete unread notifications older than 7 days
    seven_days_ago = (now - datetime.timedelta(days=7)).isoformat()
    supabase.from_("notifications").delete().lt("created_at", seven_days_ago).eq("read", False).execute()

    # 2. Delete read notifications older than 3 days
    three_days_ago = (now - datetime.timedelta(days=3)).isoformat()
    supabase.from_("notifications").delete().lt("created_at", three_days_ago).eq("read", True).execute()


def get_search_history(user_id: str):
    user_id = uuid.UUID(user_id)
    print("get_search_history function called", flush=True)
    try:
        response = supabase.table("search_history").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        data = response.data

        history = []
        for row in data:
            dt = datetime.datetime.fromisoformat(row["created_at"])
            filters = []

            if row.get("language"):
                filters.append(row["language"])

            min_f = row.get("min_followers")
            max_f = row.get("max_followers")
            if min_f is not None and max_f is not None:
                filters.append(f"{min_f}-{max_f} followers")
            elif min_f is not None:
                filters.append(f"{min_f}+ followers")

            if row.get("min_viewers") is not None:
                filters.append(f"{row['min_viewers']}+ viewers")

            history.append({
                "id": row.get("search_id", 0),
                "title": row.get("title", ""),
                "date": dt.strftime("%B %d, %Y"),
                "time": dt.strftime("%I:%M %p").lstrip("0"),
                "results": row.get("result_count", 0),
                "category": row.get("category", ""),
                "filters": filters
            })

        return JSONResponse(content={
            "status": "success",
            "data": history
        }, status_code=200)

    except Exception as e:
        print(f"EXCEPTION OFFUCRED {e}", flush=True)
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)
    
def add_search_history(user_id, title, result_count, category, language, min_followers, max_followers, min_viewers ):
    try:
        supabase.from_("search_history").insert({
            "user_id": user_id,
        "title": title,
        "result_count": result_count,
        "category": category,
        "language": language,
        "min_followers": min_followers,
        "max_followers": max_followers,
        "min_viewers": min_viewers
        }).execute()
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error occurred {e}"})
    else:
        return JSONResponse(status_code=200, content={"message": "Success"})

def delete_notification(user_id: str, notificationId: str):
    try:
        if notificationId:
            supabase.from_("notifications").delete().eq("id", notificationId).eq("user_id", user_id).execute()
        else:
            supabase.from_("notifications").delete().eq("user_id", user_id).execute()
    except Exception as e:
        return JSONResponse(status_code=500, content={"message: Failed {e}"})
    else:
        return JSONResponse(status_code=200, content={"message": "Success"})

def mark_as_read(user_id: str, notificationId):
    try:
        if notificationId:
            supabase.from_("notifications").update({ "read": True }).eq("id", notificationId).eq("user_id", user_id).execute()
        else:
            supabase.from_("notifications").update({ "read": True }).eq("user_id", user_id).execute()
    except Exception as e:
        return JSONResponse(status_code=500, content={"message: Failed {e}"})
    else:
        return JSONResponse(status_code=200, content={"message": "Success"})

def format_time_ago(created_at: str) -> str:
    created = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - created
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        return f"{seconds // 60}m ago"
    elif seconds < 86400:
        return f"{seconds // 3600}h ago"
    else:
        return f"{seconds // 86400}d ago"

def get_user_notifications(user_id: str):
    print("Thingy called", flush=True)
    try:
        response = supabase.from_("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    except Exception as e:
        print(e, flush=True)
    data = response.data or []
    print(response, flush=True)

    notifications = [
        {
            "id": n["id"],
            "title": n["title"],
            "description": n["description"],
            "time": format_time_ago(n["created_at"]),
            "unread": not n["read"],
            "type": n.get("type", None),
            "created_at": n["created_at"],
        }
        for n in data
    ]

    return notifications

