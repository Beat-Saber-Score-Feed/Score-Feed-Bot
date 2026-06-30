from nextcord.ext import commands

LOGS_CHANNEL = 1520921973901889596

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
        with open("log.txt", "a", encoding="utf-8") as file:
            file.write(f"{log_text}\n")
    except UnicodeEncodeError:
        safe = log_text.encode("utf-8", "replace").decode("utf-8")
        with open("log.txt", "a", encoding="utf-8") as file:
            file.write(f"{safe}\n")

    if bot_instance:
        channel = bot_instance.get_channel(LOGS_CHANNEL)
        if channel:
            bot_instance.loop.create_task(channel.send(log_text))
