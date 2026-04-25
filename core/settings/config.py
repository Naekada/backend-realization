from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


CURRENT_PATH = Path(__file__).parent.parent
DATABASE_PATH = CURRENT_PATH / "db.sqlite3"


class Settings(BaseSettings):
    #===============JWT===============#
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_access_token_expire_days: int = 7
    #===============JWT===============#

    #===============DATABASE===============#
    db_url: str = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    db_echo: bool = False
    #===============DATABASE===============#

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
        

settings = Settings()
