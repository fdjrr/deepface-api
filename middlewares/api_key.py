import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()


def verify_api_key(x_api_key: str = Header(...)):
    api_key = os.getenv("API_KEY")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
