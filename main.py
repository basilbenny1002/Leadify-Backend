from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
import threading
import Scrapers

from Scrapers.twitch_Scraper import start
from Scrapers.functions import AnyValue
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Query
ANYT = AnyValue(choice=True)


app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

def start_scraper(**kwargs):
    data = dict(kwargs)
    data["time_remaining"]= "50240"
    return data
@app.get("/Twitch_scraper")
def run_Scraper(category: str, minimum_followers: Union[int, None] = Query(default=None), language: Union[str, None] = Query(default=None), viewer_count: Union[str, None] = Query(default=None),  maximum_followers: Union[str, None] = Query(default=None) ):
    thread = threading.Thread(target=start,kwargs={"c":category, "min_f":minimum_followers if minimum_followers else ANYT, "choice_l":language if language else ANYT, "min_viewer_c":viewer_count if viewer_count else ANYT, "max_f": maximum_followers if maximum_followers else ANYT})
    thread.start()  
    # data = start_scraper(category=category, minimum_followers=minimum_followers if minimum_followers else ANYT, language=language if minimum_followers else ANYT, viewer_count=viewer_count if viewer_count else ANYT)
    data = {"Status": "Started"}
    return JSONResponse(status_code=200, content=data)

@app.get("/Twitch_scraper/get_progress")
def get_progress():
    return JSONResponse(status_code=200, content={"Stage": Scrapers.twitch_Scraper.current_process, "Rate": Scrapers.twitch_Scraper.rate, "ETA": Scrapers.twitch_Scraper.remaining, "Streamers": Scrapers.twitch_Scraper.valid_streamers, "Completed": Scrapers.twitch_Scraper.completed})
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
def create_item(item: Item):
    print(item)
    return f"{item}"

