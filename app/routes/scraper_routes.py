import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from uuid import UUID
from pydantic import BaseModel
from fastapi import Body, HTTPException, Request
from app.utils.functions import load_config
from fastapi.responses import JSONResponse
from app.utils.mail_scraper import scrapeEmails
from fastapi import Query

router = APIRouter()

class Socials:
    socials: list[str]

router.post("/mail_scraper")
def extract_mails(socialsObject: Socials):
    try:
        return scrapeEmails(socialsObject.socials)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"failed, error {e}"})