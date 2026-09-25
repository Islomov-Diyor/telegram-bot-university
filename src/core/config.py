import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    ADMIN_CHAT_IDS: str = ""
    ADMIN_CHANNEL_ID: Optional[str] = None

    # Web & API
    SECRET_KEY: str = "super_secret_jwt_key_university_talented_students_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12 hours
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/university_clubs.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def admin_chat_id_list(self) -> List[int]:
        """Parse comma-separated admin chat IDs into a list of integers."""
        if not self.ADMIN_CHAT_IDS or not self.ADMIN_CHAT_IDS.strip():
            return []
        ids = []
        for raw_id in self.ADMIN_CHAT_IDS.split(","):
            raw_id = raw_id.strip()
            if raw_id:
                try:
                    ids.append(int(raw_id))
                except ValueError:
                    pass
        return ids


settings = Settings()

# Ensure data directory exists if using local SQLite
if "sqlite" in settings.DATABASE_URL:
    os.makedirs("./data", exist_ok=True)
