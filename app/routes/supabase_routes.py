import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from uuid import UUID
from pydantic import BaseModel
from fastapi import Body, HTTPException, Request
from app.utils.functions import load_config
from fastapi.responses import JSONResponse
from fastapi import Query
from app.utils.superbase_functions import add_search_history, add_streamer_to_folder, create_folder, delete_saved_filter, get_folders, get_saved_filters, get_saved_streamers, get_user_notifications, initialize_user_onSignup, save_filter_to_supabase, save_streamers_to_supabase, toggle_favourite, get_search_history, add_notification
from typing import Optional

load_config()

class History(BaseModel):
    user_id: str
    title: str
    result_count: int
    category: str
    language: str
    min_followers: int
    max_followers: int
    min_viewers: int


class Notifications(BaseModel):
    user_id: str
    title: str
    message: str

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

@router.post("/initialize-user")
async def initialize_user(user_id: str):
    try:
        initialize_user_onSignup(user_id)
        print("function passed", flush=True)
        return JSONResponse(status_code=200, content={"status": "success"})     
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


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
    

@router.post("/search_history")
def addSearchHistory(history: History):
    return add_search_history()


    
@router.get("/search_history")
def getSearchHistory(user_id: str):
    return get_search_history(user_id=user_id)
    
    
@router.post("/add_notifications")
def addNotifications(notification: Notifications):
    try:
        add_notification(notification.user_id, notification.title, notification.message)
    except Exception as e:
        print(e, flush=True)
        return JSONResponse(status_code=500, content={"message": "Failed"})
    else:
        return JSONResponse(status_code=200, content={"message": "Success"})


@router.post("/notifications")
async def notifications_handler(request: Request):
    body = await request.json()
    user_id = body.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    try:
        notifications = get_user_notifications(user_id)
        return {"success": True, "notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


        
    
    
