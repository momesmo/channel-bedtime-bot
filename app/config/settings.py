from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

@dataclass
class Settings:
    # Discord Settings
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    
    # MongoDB Settings
    MONGO_HOST: str = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT: int = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USERNAME: str = os.getenv('MONGO_USERNAME', 'user')
    MONGO_PASSWORD: str = os.getenv('MONGO_PASSWORD', 'password')
    MONGO_DB: str = os.getenv('MONGO_DB', 'discord_bot')
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE: str = os.getenv('LOG_FILE', 'discord.log')
    
    # Bot Settings
    DEFAULT_PREFIX: str = os.getenv('DEFAULT_PREFIX', '!')
    DEFAULT_TIMEZONE: str = os.getenv('DEFAULT_TIMEZONE', 'UTC')
    
    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from environment variables"""
        return cls()

    def validate(self) -> None:
        """Validate required settings"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required") 