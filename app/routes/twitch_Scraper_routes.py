from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union
import threading
from app.utils.functions import load_config
from scrapers.twitch_Scraper import start
from scrapers.scraper_functions import AnyValue, format_time
from fastapi.responses import JSONResponse
import time
import json
from scrapers.twitch_Scraper import active_scrapers
from app.utils.functions import category_to_id
from app.utils.customThread import CancellableThread

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
class User(BaseModel):
    user_id: str

data_template = {
    "Stage": 0, "Rate":0 , "ETA": format_time(0), "Streamers":0,
    "Completed": 0, "Percentage": 0, "Total_Streamers": 0, 
    "Done": False, "search_id": "", "download_url": "", "progress_data":[], "data":None
}




@router.post("/Twitch_scraper")
def run_Scraper(details: scrape_details):
    try:
        thread = CancellableThread(target=start,kwargs={"c":category_to_id(details.category), "user_id":details.user_id, "min_f":details.minimum_followers if details.minimum_followers else ANYT, "choice_l":details.language if details.language else ANYT, "min_viewer_c":details.viewer_count if details.viewer_count else ANYT, "max_f": details.maximum_followers if details.maximum_followers else ANYT})
        thread.start()
        if details.user_id not in active_scrapers:
            active_scrapers[details.user_id] = data_template.copy()
        active_scrapers[details.user_id]['process'] = thread
        return JSONResponse(status_code=200, content={"Status": "Started"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"Status": "Failed", "Error": str(e)})


@router.get("/Twitch_scraper/get_progress")
def get_progress(user_id: str):
    try:
        data = {k: v for k, v in active_scrapers[user_id].items() if (k != 'progress_data' and k!='process')}
    except KeyError as e:
        return JSONResponse(status_code=404, content={"message": "User id not found, user migth have been removed"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed, error {e}"})
    else:
        return JSONResponse(status_code=200, content=data)


@router.get("/twitch/categories")
def get_categories(eligible: bool):
    with open(r".\app\utils\datas\categories.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
        return JSONResponse(status_code=200, content={i:("" if not eligible else data[i])for i in data})
    
@router.get("/twitch/live_categories")
def get_languages():
    with open(r".\app\utils\datas\live_categories.json", 'r', encoding='utf-8') as file:
        data = json.loads(file)
        return JSONResponse(status_code=200, content=data)
    
    
@router.post("/Twitch_scraper/terminate")
def terminate_scrape(user: User):
    try:
        active_scrapers[user.user_id]['process'].kill() 
        try:
            del active_scrapers[user.user_id]
        except:
            print("failed to delete")
            return JSONResponse(status_code=500, content={"message": "Failed to delete progress values"})
        else:
            pass
    except SystemExit:
        return JSONResponse(status_code=200, content={"message": "Success"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"Error":e })
    else:
        return JSONResponse(status_code=200, content={"message": "Success"})
