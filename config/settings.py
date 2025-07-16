from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DB: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    JWT_KEY: str

    authjwt_secret_key: str = None
    authjwt_access_token_expires: int = 60 * 15       # 15분
    authjwt_refresh_token_expires: int = 60 * 60 * 24 * 7  # 7일

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authjwt_secret_key = self.JWT_KEY
