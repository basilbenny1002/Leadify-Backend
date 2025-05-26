from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union
import threading
from app.utils.functions import load_config
from scrapers.twitch_Scraper import start
from scrapers.scraper_functions import AnyValue
from fastapi.responses import JSONResponse
from fastapi import  Query
from scrapers.twitch_Scraper import active_scrapers
from app.utils.functions import category_to_id


load_config()
ANYT = AnyValue(choice=True)
router = APIRouter()

class scrape_details(BaseModel):
    category: str
    user_id: str
    minimum_followers: Union[int, None] = ANYT
    language: Union[str, None] = ANYT
    viewer_count: Union[str, None] = ANYT
    maximum_followers: Union[str, None] = ANYT



def start_scraper(**kwargs):
    data = dict(kwargs)
    data["time_remaining"]= "50240"
    return data


@router.post("/Twitch_scraper/")
def run_Scraper(details: scrape_details):
    try:
        thread = threading.Thread(target=start_scraper,kwargs=details.model_dump())
        thread.start()
        return JSONResponse(status_code=200, content={"Status": "Started"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"Status": "Failed", "Error": str(e)})

@router.get("/Twitch_scraper")
def run_Scraper(category: str, user_id: str, minimum_followers: Union[int, None] = Query(default=None), language: Union[str, None] = Query(default=None), viewer_count: Union[str, None] = Query(default=None),  maximum_followers: Union[str, None] = Query(default=None)):
    thread = threading.Thread(target=start,kwargs={"c":category_to_id(category), "user_id":user_id, "min_f":minimum_followers if minimum_followers else ANYT, "choice_l":language if language else ANYT, "min_viewer_c":viewer_count if viewer_count else ANYT, "max_f": maximum_followers if maximum_followers else ANYT})
    thread.start()  
    data = {"Status": "Started"}
    return JSONResponse(status_code=200, content=data)

@router.get("/Twitch_scraper/get_progress")
def get_progress(user_id: str):
    return JSONResponse(status_code=200, content={k: v for k, v in active_scrapers[user_id].items() if k != 'progress_data'})