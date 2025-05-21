from dotenv import load_dotenv
from pathlib import Path

def load_config():
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')
