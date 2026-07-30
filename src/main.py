import nextcord
import os

from nextcord.ext import commands
from dotenv import load_dotenv

from src.utils import logger

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot_instance = bot

EXTENSIONS = [
    "cogs.score_feed.listener",
    "cogs.score_feed.server_commands",
    "cogs.score_feed.channel_commands.customizations",
    "cogs.score_feed.channel_commands.filter_lists",
    "cogs.score_feed.channel_commands.settings",
]

EXTENSIONS_LOADED = False

@bot.event
async def on_ready():
    global EXTENSIONS_LOADED

    logger.init_logger(bot)
    logger.log("Score Feed started successfully!")

    if EXTENSIONS_LOADED:
        return

    EXTENSIONS_LOADED = True

    logger.log("Loading extensions...")

    for extension in EXTENSIONS:
        bot.load_extension(extension)

    logger.log("All extensions loaded.")

    logger.log("Syncing application commands...")
    await bot.sync_application_commands()
    logger.log("Application commands synced.")

bot.run(token)