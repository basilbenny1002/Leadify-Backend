from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union
import threading
from app.utils.functions import load_config
from scrapers.twitch_Scraper import start
from scrapers.scraper_functions import AnyValue
from fastapi.responses import JSONResponse
import time
from scrapers.twitch_Scraper import active_scrapers
from app.utils.functions import category_to_id


load_config()
ANYT = AnyValue(choice=True)
router = APIRouter()

class scrape_details(BaseModel):
    category: str
    user_id: str
    minimum_followers: Union[int, str,None] = ANYT
    language: Union[str, None] = ANYT
    viewer_count: Union[int, str,None] = ANYT
    maximum_followers: Union[int,str, None] = ANYT



@router.post("/Twitch_scraper/")
def run_Scraper(details: scrape_details):
    try:
        thread = threading.Thread(target=start,kwargs={"c":category_to_id(details.category), "user_id":details.user_id, "min_f":details.minimum_followers if details.minimum_followers else ANYT, "choice_l":details.language if details.language else ANYT, "min_viewer_c":details.viewer_count if details.viewer_count else ANYT, "max_f": details.maximum_followers if details.maximum_followers else ANYT})
        thread.start()
        return JSONResponse(status_code=200, content={"Status": "Started"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"Status": "Failed", "Error": str(e)})


@router.get("/Twitch_scraper/get_progress")
def get_progress(user_id: str):
    return JSONResponse(status_code=200, content={k: v for k, v in active_scrapers[user_id].items() if k != 'progress_data'})