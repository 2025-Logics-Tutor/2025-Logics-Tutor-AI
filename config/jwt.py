import os

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv("JWT_KEY")

class Settings(BaseModel):
    authjwt_secret_key: str = JWT_KEY
    authjwt_access_token_expires: int = 60 * 15   # 15분
    authjwt_refresh_token_expires: int = 60 * 60 * 24 * 7  # 7일