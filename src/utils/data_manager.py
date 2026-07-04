import os
from src.utils import save_data

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
guild_data_path = os.path.join(PROJECT_ROOT, "bot_data", "guild_data.json")
user_data_path = os.path.join(PROJECT_ROOT, "bot_data", "user_data.json")

GUILD_DATA = save_data.load_data(guild_data_path)
if "guilds" not in GUILD_DATA:
    GUILD_DATA["guilds"] = {}

USER_DATA = save_data.load_data(user_data_path)
if "users" not in USER_DATA:
    USER_DATA["users"] = {}

def get_guild_data():
    return GUILD_DATA

def get_user_data():
    return USER_DATA

def save_guild_data():
    save_data.save_data(GUILD_DATA, guild_data_path)

def save_user_data():
    save_data.save_data(USER_DATA, guild_data_path)