from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key: str = "your_super_secret_key"
    authjwt_access_token_expires: int = 60 * 15   # 15분
    authjwt_refresh_token_expires: int = 60 * 60 * 24 * 7  # 7일