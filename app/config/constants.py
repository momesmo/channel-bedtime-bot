from enum import Enum

# Time formats
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# MongoDB Collections
COLLECTIONS = {
    'GUILDS': 'guilds',
    'USERS': 'users',
    'GUILD_SETTINGS': 'guild_settings'
}

# Command Cooldowns
COOLDOWN_TIMES = {
    'bedtime': 60,  # seconds
    'start': 30,
    'stop': 30
} 