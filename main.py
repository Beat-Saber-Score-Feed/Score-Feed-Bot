import nextcord
import websockets
import math
import asyncio
import os
import json
import traceback

from nextcord.ext import commands, tasks
from dotenv import load_dotenv

from utils import logger, score_parser, embed_builder, save_data

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot_instance = bot

GUILD_DATA = save_data.load_data("bot_data/guild_data.json")
if "guilds" not in GUILD_DATA:
    GUILD_DATA["guilds"] = {}

USER_DATA = save_data.load_data("bot_data/user_data.json")
if "users" not in USER_DATA:
    USER_DATA["users"] = {}

FILTER_LISTS = {
    "BL ID Allowlist": "bl_id_allowlist",
    "BL ID Blocklist": "bl_id_blocklist"
}

@tasks.loop(seconds=0)
async def listener():
    logger.log("Connecting to the BeatLeader WSS...")
    while True:
        try:
            async with websockets.connect("wss://api.beatleader.com/scores") as websocket:
                logger.log("Connected to the BeatLeader WSS")
                async for score in websocket:
                    try:
                        score = json.loads(score)
                        parsed_data = score_parser.parse_score(score)

                        if parsed_data:
                            send_tasks = []

                            for guild in GUILD_DATA["guilds"]:
                                guild_data = GUILD_DATA["guilds"][guild]
                                filter_lists = guild_data.get("filter_lists", {})
                                bl_id_allowlist = filter_lists.get("bl_id_allowlist", {})
                                bl_id_blocklist = filter_lists.get("bl_id_blocklist", {})

                                if bl_id_allowlist.get("enabled", False):
                                    if parsed_data["player_id"] not in bl_id_allowlist["items"]:
                                        continue

                                if bl_id_blocklist.get("enabled", False):
                                    if parsed_data["player_id"] in bl_id_blocklist["items"]:
                                        continue

                                channels = GUILD_DATA["guilds"][guild].get("channels", {})
                                for channel_id in channels:
                                    channel = bot.get_channel(int(channel_id))

                                    if not channel:
                                        continue

                                    channel_data = GUILD_DATA["guilds"][guild]["channels"][channel_id]

                                    if not channel_data["enabled"]:
                                        continue

                                    all_leaderboard_settings = channel_data.get("leaderboard_settings", {})

                                    for leaderboard in parsed_data["ranked_leaderboards"]:
                                        leaderboard_settings = all_leaderboard_settings.get(leaderboard, {})

                                        if not leaderboard_settings.get("enabled", True):
                                            continue

                                        if parsed_data.get(f"{leaderboard}_pp", 0) < leaderboard_settings.get("pp_threshold", 0):
                                            continue

                                        if parsed_data.get("rank") > leaderboard_settings.get("rank_threshold",math.inf):
                                            continue

                                        embed = embed_builder.build_embed(parsed_data, leaderboard)
                                        view = embed_builder.build_view(parsed_data, leaderboard)
                                        send_tasks.append(channel.send(embed=embed, view=view))

                            await asyncio.gather(*send_tasks)

                            logger.log(f"Posted {parsed_data['ss_pp']}pp score by {parsed_data['name']} on {parsed_data['song_name']} {parsed_data['extended_difficulty_name']}")

                    except websockets.ConnectionClosed:
                        logger.log("Websocket closed, reconnecting...")
                        break

        except Exception as e:
            logger.log(f"Websocket error: {e}")
            traceback.print_exc()

        await asyncio.sleep(3)

def check_perms(user, guild_id):
    if user.guild_permissions.administrator:
        return True

    user_roles = {role.id for role in user.roles}
    allowed_roles = GUILD_DATA["guilds"][guild_id].get("admin_role_ids", [])

    return bool(user_roles & set(allowed_roles))

@bot.slash_command(name="enable_channel",description="Enable score feed in your current channel")
async def enable_channel(interaction: nextcord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!",ephermeral=True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    channels = guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})

    channel_data["enabled"] = True

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message("Score Feed is now enabled in this channel!", ephemeral = True)

@bot.slash_command(name="disable_channel", description="Disable score feed in your current channel")
async def disable_channel(interaction: nextcord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!",ephermeral = True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    channels = guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})

    channel_data["enabled"] = False

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message("Score Feed is now disabled in this channel.", ephemeral=True)

@bot.slash_command(name="filter_list_settings")
async def filter_list_settings(
        interaction: nextcord.Interaction,
        filter_list: str = nextcord.SlashOption(
            choices=FILTER_LISTS,
        ),
        filter_list_enabled: bool = nextcord.SlashOption(
            choices={
                "True": True,
                "False": False
            },
        )
):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephermeral = True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    filter_lists = guild_data.setdefault("filter_lists", {})
    filter_list = filter_lists.setdefault(filter_list, {})
    filter_list["enabled"] = filter_list_enabled

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message("Updated filter list settings successfully.", ephemeral=True)

@bot.slash_command(name="edit_filter_list")
async def edit_filter_list(
        interaction: nextcord.Interaction,
        filter_list: str = nextcord.SlashOption(
            choices=FILTER_LISTS
        ),
        operation: str = nextcord.SlashOption(
            choices = {
                "Add Value": "add_value",
                "Remove Value": "remove_value"
            }
        ),
        value = nextcord.SlashOption(
            required=True
        )
):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephermeral=True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    filter_lists = guild_data.setdefault("filter_lists", {})
    filter_list = filter_lists.setdefault(filter_list, {})
    filter_list_items = filter_list.setdefault("items", [])

    filter_list_enabled = filter_list.get("enabled")

    if operation == "add_value":
        if filter_list_enabled is None:
            filter_list["enabled"] = True
        if value in filter_list_items:
            return await interaction.response.send_message("This item is already in this filter list!", ephemeral=True)
        filter_list_items.append(value)

    if operation == "remove_value":
        if value not in filter_list_items:
            return await interaction.response.send_message("This item is already not in this filter list!", ephemeral=True)
        filter_list_items.remove(value)

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message(f"Edited {filter_list} successfully.", ephemeral=True)

@bot.slash_command(name="add_admin_role")
async def add_admin_role(interaction: nextcord.Interaction, role: nextcord.Role):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephermeral=True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    admin_roles = guild_data.setdefault("admin_roles", [])

    if role.id in admin_roles:
        return await interaction.response.send_message("This admin role is already registered.", ephemeral=True)

    admin_roles.append(role.id)

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message("Admin role added successfully!", ephemeral=True)


@bot.slash_command(name="remove_admin_role")
async def add_admin_role(interaction: nextcord.Interaction, role: nextcord.Role):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephermeral=True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    admin_roles = guild_data.setdefault("admin_roles", [])

    if role.id not in admin_roles:
        return await interaction.response.send_message("This role already isn't in your guild's admin roles.", ephemeral=True)

    admin_roles.remove(role.id)

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message("Admin role removed successfully!", ephemeral=True)

@bot.slash_command(name="lb_settings")
async def lb_settings(
        interaction: nextcord.Interaction,
        leaderboard: str = nextcord.SlashOption(
            choices = {
                "BeatLeader": "bl",
                "ScoreSaber": "ss",
                "AccSaber": "acc",
                "Unranked": "unr",
            },
        ),
        enabled: bool = nextcord.SlashOption(
            choices = {
                "True": True,
                "False": False
            },
        ),
        pp_threshold: int = None,
        rank_threshold: int = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)
    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = GUILD_DATA["guilds"].setdefault(guild_id, {})
    channels = guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    all_leaderboard_settings = channel_data.setdefault("leaderboard_settings", {})
    leaderboard_settings = all_leaderboard_settings.setdefault(leaderboard, {})

    leaderboard_settings["enabled"] = enabled

    if pp_threshold and leaderboard != "unr":
        if pp_threshold == 0:
            leaderboard_settings["pp_threshold"] = None
        else:
            leaderboard_settings["pp_threshold"] = pp_threshold

    if rank_threshold:
        if rank_threshold == 0:
            leaderboard_settings["rank_threshold"] = None
        else:
            leaderboard_settings["rank_threshold"] = rank_threshold

    save_data.save_data(GUILD_DATA, "bot_data/guild_data.json")

    return await interaction.response.send_message(f"Updated channel's {leaderboard} settings successfully!", ephemeral=True)

@bot.event
async def on_ready():
    logger.init_logger(bot)
    logger.log("Score Feed started successfully!")
    listener.start()

bot.run(token)