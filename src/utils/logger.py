from nextcord.ext import commands
import os

LOGS_CHANNEL = 1520921973901889596

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_path = os.path.join(PROJECT_ROOT, "logs", "log.txt")

bot_instance: commands.Bot | None = None

def init_logger(bot):
    global bot_instance
    bot_instance = bot

def log(log_text: str):
    try:
        print(log_text)
    except UnicodeEncodeError:
        safe = log_text.encode("utf-8", "replace").decode("utf-8")
        print(safe)

    try:
        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"{log_text}\n")
    except UnicodeEncodeError:
        safe = log_text.encode("utf-8", "replace").decode("utf-8")
        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"{safe}\n")

    if bot_instance:
        channel = bot_instance.get_channel(LOGS_CHANNEL)
        if channel:
            bot_instance.loop.create_task(channel.send(log_text))
