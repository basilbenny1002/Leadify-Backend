from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import (FastAPI, Query)
from Scrapers.twitch_Scraper import start


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
def run_Scraper(category: str, minimum_followers: Union[int, None] = Query(default=None), language: Union[str, None] = Query(default=None), viewer_count: Union[str, None] = Query(default=None) ):
    data = start_scraper(category=category, minimum_followers=minimum_followers, language=language , viewer_count=viewer_count)
    return JSONResponse(status_code=200, content=data)


