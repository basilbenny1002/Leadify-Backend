
from fastapi import FastAPI
import sys
from app.utils.functions import load_config
from fastapi.middleware.cors import CORSMiddleware
import io
from .request_handlers.lemon_squeezy_webhooks import router as webhook_router
# from app.routes import router as main_router
from app.routes.supabase_routes import router as supabase_router
from app.routes.twitch_Scraper_routes import router as twitch_scraper_router
from app.routes.billing_routes import router as billing_router
from app.routes.scraper_routes import router as scraper_router


load_config()

# try:
#     sys.stdout.reconfigure(encoding='utf-8')
# except:
#     print("Error: Unable to set stdout encoding to UTF-8. This may affect the dixsplay of non-ASCII characters.", flush=True)
#     pass
# try:
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# except Exception as e:
#     print("Could not reconfigure stdout encoding:", e)    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all, but not safe for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.include_router(main_router)
app.include_router(webhook_router)
app.include_router(supabase_router)
app.include_router(twitch_scraper_router)
app.include_router(billing_router)
app.include_router(scraper_router)


@app.get("/")
def read_root():
    return {"Status": "Running"}