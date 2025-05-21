from typing import Union
from uuid import UUID
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Request
import threading
import scrapers
import sys
from scrapers.twitch_Scraper import start
from scrapers.functions import AnyValue
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Query
from scrapers.functions import scrape_twitch_about
from scrapers.twitch_Scraper import active_scrapers
import io
from .request_handlers.lemon_squeezy_webhooks import router as webhook_router
# from .re.lemon_squeezy_webhooks import router as webhook_router
from .utils.superbase_functions import add_streamer_to_folder, create_folder, get_folders, get_saved_streamers, save_streamers_to_supabase, fetch_saved_streamers, toggle_favourite

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    print("Error: Unable to set stdout encoding to UTF-8. This may affect the display of non-ASCII characters.")
    pass
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception as e:
    print("Could not reconfigure stdout encoding:", e)

ANYT = AnyValue(choice=True)

class FolderMove(BaseModel):
    streamer_id: str
    folder_id: str | None

class FolderCreate(BaseModel):
    name: str

class FolderMove(BaseModel):
    streamer_id: UUID
    folder_id: UUID

class FavouriteToggle(BaseModel):
    streamer_id: UUID
    is_favourite: bool
    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all, but not safe for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(webhook_router)
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/streamers/save")
def save_scraped_streamers(user_id: str, streamers: list[dict] = Body(...)):
    try:
        save_streamers_to_supabase(user_id, streamers)
        return JSONResponse(status_code=200, content={"status": "saved"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
# @app.get("/saved-streamers")
# def get_saved_streamers(user_id: str):
#     print('route hit')
#     print(user_id + '56')
#     try:
#         data = fetch_saved_streamers(user_id)
#         print(data)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/folders/create")
async def create_folder_route(folder: FolderCreate, request: Request):
    user_id = request.headers.get("x-user-id")   
    result = await create_folder(user_id, folder.name)
    return JSONResponse(result)

@app.get("/folders")
async def get_folders_route(user_id: str = Query(...)):
    folders = await get_folders(user_id)
    return folders

@app.get("/streamers/{folder_id}")
async def get_streamers_route(folder_id: str, user_id: str = Query(...)):
    streamers = await get_saved_streamers(user_id, folder_id)
    return streamers

@app.post("/streamers/move")
async def move_streamer_to_folder(payload: FolderMove, request: Request):
    print('route hit to move streamers')
    user_id = request.headers.get("x-user-id")
    print(user_id)
    print(payload)
    await add_streamer_to_folder(user_id, str(payload.streamer_id), str(payload.folder_id))
    return {"status": "moved"}

@app.post("/streamers/favourite")
async def toggle_fav_route(payload: FavouriteToggle, request: Request):
    user_id = request.headers.get("x-user-id")
    await toggle_favourite(user_id, str(payload.streamer_id), payload.is_favourite)
    return {"status": "updated"}

def start_scraper(**kwargs):
    data = dict(kwargs)
    data["time_remaining"]= "50240"
    return data
@app.get("/Twitch_scraper")
def run_Scraper(category: str, user_id: str, minimum_followers: Union[int, None] = Query(default=None), language: Union[str, None] = Query(default=None), viewer_count: Union[str, None] = Query(default=None),  maximum_followers: Union[str, None] = Query(default=None)):
    thread = threading.Thread(target=start,kwargs={"c":category, "user_id":user_id, "min_f":minimum_followers if minimum_followers else ANYT, "choice_l":language if language else ANYT, "min_viewer_c":viewer_count if viewer_count else ANYT, "max_f": maximum_followers if maximum_followers else ANYT})
    thread.start()  
    # data = start_scraper(category=category, minimum_followers=minimum_followers if minimum_followers else ANYT, language=language if minimum_followers else ANYT, viewer_count=viewer_count if viewer_count else ANYT)
    data = {"Status": "Started"}
    return JSONResponse(status_code=200, content=data)

@app.get("/Twitch_scraper/get_progress")

def get_progress(user_id: str):
    # return JSONResponse(status_code=200, content={"Stage": Scrapers.twitch_Scraper.current_process, "Rate": Scrapers.twitch_Scraper.rate, "ETA": Scrapers.twitch_Scraper.remaining, "Streamers": Scrapers.twitch_Scraper.valid_streamers, "Completed": Scrapers.twitch_Scraper.completed, "Percentage": Scrapers.twitch_Scraper.percentage, "Total Streamers": Scrapers.twitch_Scraper.total_streamers, "Done": Scrapers.twitch_Scraper.done, "search_id": Scrapers.twitch_Scraper.search_id, "download_url": Scrapers.twitch_Scraper.download_url
    # })
    return JSONResponse(status_code=200, content={k: v for k, v in active_scrapers[user_id].items() if k != 'progress_data'})
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
def create_item(item: Item):
    print(item)
    return f"{item}"

