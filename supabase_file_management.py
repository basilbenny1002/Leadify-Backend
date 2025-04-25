import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import uuid


def upload_csv(search_id_uuid, user_id, filters, file_name, total, valid):
    supabase = create_client(os.getenv("NEXT_PUBLIC_SUPABASE_URL"), os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"))
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
# if __name__ == "__main__":
#     load_dotenv()
#     # upload_csv("search_id", "user_id", {"filter1": "value1"}, "file_name.csv", 100, 50)
#     search_id_uuid = str(uuid.uuid4()) 
#     file_name = fr"Leadify-Backend/test.csv"
    
#     filters = {
#         "min_followers": 8,
#         "max_followers": 20,
#         "language": "en",
#         "min_viewers": 60,
#         "category": "4354"
#     }
#     upload_csv(search_id_uuid, "5ccb7a11-6135-48fd-80ba-98e8601977c6", filters, file_name, 67, 40)

    # # file_name = f"{user_id}/{str(uuid.uuid4())}.csv"  # you must pass user_id to this function

    # with open("test.csv", "rb") as f:
    #     res = supabase.storage.from_("results").upload(file_name, f)
    #     print(res)
    # if not res.path:
    #     raise Exception(f"CSV upload failed: {res}")