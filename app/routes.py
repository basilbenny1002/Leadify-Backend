from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union
from uuid import UUID
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Request
import threading
import scrapers
import json
import sys
from app.utils.functions import load_config
from scrapers.twitch_Scraper import start
from scrapers.scraper_functions import AnyValue
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Query
from scrapers.scraper_functions import scrape_twitch_about
from scrapers.twitch_Scraper import active_scrapers
from app.utils.functions import category_to_id
import io
from .utils.superbase_functions import add_streamer_to_folder, create_folder, delete_saved_filter, get_folders, get_saved_filters, get_saved_streamers, save_filter_to_supabase, save_streamers_to_supabase, fetch_saved_streamers, toggle_favourite
from typing import Optional

load_config()

ANYT = AnyValue(choice=True)

class FolderCreate(BaseModel):
    name: str

class FolderMove(BaseModel):
    streamer_id: UUID
    folder_id: UUID

class FavouriteToggle(BaseModel):
    streamer_id: UUID
    is_favourite: bool

class FilterSave(BaseModel):
    name: str
    language: Optional[str]
    category: Optional[str]
    min_followers: Optional[int]
    max_followers: Optional[int]
    min_viewers: Optional[int]
    max_viewers: Optional[int]
    

router = APIRouter()

@router.post("/streamers/save")
def save_scraped_streamers(user_id: str, streamers: list[dict] = Body(...)):
    try:
        save_streamers_to_supabase(user_id, streamers)
        return JSONResponse(status_code=200, content={"status": "saved"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    
@router.post("/folders/create")
async def create_folder_route(folder: FolderCreate, request: Request):
    user_id = request.headers.get("x-user-id")   
    result = await create_folder(user_id, folder.name)
    return JSONResponse(result)

@router.get("/folders")
async def get_folders_route(user_id: str = Query(...)):
    folders = await get_folders(user_id)
    return folders

@router.get("/streamers/{folder_id}")
async def get_streamers_route(folder_id: str, user_id: str = Query(...)):
    streamers = await get_saved_streamers(user_id, folder_id)
    return streamers

@router.post("/streamers/move")
async def move_streamer_to_folder(payload: FolderMove, request: Request):
    print('route hit to move streamers')
    user_id = request.headers.get("x-user-id")
    print(user_id)
    print(payload)
    await add_streamer_to_folder(user_id, str(payload.streamer_id), str(payload.folder_id))
    return {"status": "moved"}

@router.post("/streamers/favourite")
async def toggle_fav_route(payload: FavouriteToggle, request: Request):
    user_id = request.headers.get("x-user-id")
    await toggle_favourite(user_id, str(payload.streamer_id), payload.is_favourite)
    return {"status": "updated"}

def start_scraper(**kwargs):
    data = dict(kwargs)
    data["time_remaining"]= "50240"
    return data
@router.get("/Twitch_scraper")
def run_Scraper(category: str, user_id: str, minimum_followers: Union[int, None] = Query(default=None), language: Union[str, None] = Query(default=None), viewer_count: Union[str, None] = Query(default=None),  maximum_followers: Union[str, None] = Query(default=None)):
    thread = threading.Thread(target=start,kwargs={"c":category_to_id(category), "user_id":user_id, "min_f":minimum_followers if minimum_followers else ANYT, "choice_l":language if language else ANYT, "min_viewer_c":viewer_count if viewer_count else ANYT, "max_f": maximum_followers if maximum_followers else ANYT})
    thread.start()  
    data = {"Status": "Started"}
    return JSONResponse(status_code=200, content=data)

@router.get("/Twitch_scraper/get_progress")
def get_progress(user_id: str):
    return JSONResponse(status_code=200, content={k: v for k, v in active_scrapers[user_id].items() if k != 'progress_data'})


@router.post("/filters/save")
async def save_filter_route(filter_data: FilterSave, request: Request):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user ID")

    try:
        result = await save_filter_to_supabase(user_id, filter_data)
        return JSONResponse(status_code=200, content={"status": "saved", "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filters/save")
async def save_filter_route(filter_data: FilterSave, request: Request):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user ID")

    try:
        result = await save_filter_to_supabase(user_id, filter_data)
        return JSONResponse(status_code=200, content={"status": "saved", "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters")
async def get_filters_route(user_id: str = Query(...)):
    try:
        result = await get_saved_filters(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/filters/{filter_id}")
async def delete_filter_route(filter_id: str, request: Request):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user ID")

    try:
        result = await delete_saved_filter(user_id, filter_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/twitch_scraper/get_category_data")
# def get_categories(paid: bool):
#     with open("Leadify-Backend\app\utils\datas\live_data.json", "r", encoding="utf-8") as f:
#         data = json.load(f)
#     return {i:(k if paid else "") for i, k in data}
    
