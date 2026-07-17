import nextcord
import websockets
import math
import asyncio
import os
import json
import traceback

from nextcord.ext import commands, tasks
from dotenv import load_dotenv

from src.utils import logger, score_parser, embed_builder, data_manager

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot_instance = bot

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

                            guild_data = data_manager.get_guild_data()

                            for guild in guild_data["guilds"]:
                                current_guild_data = guild_data["guilds"][guild]

                                channels = current_guild_data.get("channels", {})
                                for channel_id in channels:
                                    channel = bot.get_channel(int(channel_id))

                                    if not channel:
                                        continue

                                    channel_data = current_guild_data["channels"][channel_id]

                                    if not channel_data["enabled"]:
                                        continue

                                    filter_lists = channel_data.get("filter_lists", {})
                                    allowlist = filter_lists.get("allowlist", {})
                                    blocklist = filter_lists.get("blocklist", {})

                                    if allowlist.get("enabled", False):
                                        if parsed_data["player_id"] not in allowlist.get("players", []):
                                            continue

                                    if blocklist.get("enabled", False):
                                        if parsed_data["player_id"] in blocklist.get("players", []):
                                            continue

                                    all_leaderboard_settings = channel_data.get("leaderboard_settings", {})

                                    leaderboards = [
                                        "ss",
                                        "bl",
                                        "acc",
                                    ]

                                    valid_leaderboards = []
                                    if channel_data.get("mode", "multi") == "multi":
                                        for leaderboard in leaderboards:
                                            leaderboard_settings = all_leaderboard_settings.get(leaderboard, {})

                                            if parsed_data.get(f"{leaderboard}_pp", 0) < leaderboard_settings.get("pp_threshold", 0.001):
                                                continue

                                            if parsed_data.get("rank") > leaderboard_settings.get("rank_threshold",math.inf):
                                                continue

                                            if not leaderboard_settings.get("enabled", True):
                                                unranked_settings = all_leaderboard_settings.get("unr", {})
                                                if parsed_data.get("rank") > unranked_settings.get("rank_threshold",math.inf):
                                                    continue
                                                if unranked_settings.get("enabled", True) and "unr" not in valid_leaderboards:
                                                    valid_leaderboards.append("unr")
                                                continue

                                            valid_leaderboards.append(leaderboard)

                                        if not valid_leaderboards:
                                            unranked_settings = all_leaderboard_settings.get("unr", {})
                                            if parsed_data.get("rank") > unranked_settings.get("rank_threshold", math.inf):
                                                continue
                                            if unranked_settings.get("enabled", True) and "unr" not in valid_leaderboards:
                                                valid_leaderboards.append("unr")
                                    else:
                                        for leaderboard in leaderboards:
                                            leaderboard_settings = all_leaderboard_settings.get(leaderboard, {})

                                            if parsed_data.get(f"{leaderboard}_pp", 0) < leaderboard_settings.get("pp_threshold", 0.001):
                                                continue

                                            if parsed_data.get("rank") > leaderboard_settings.get("rank_threshold",math.inf):
                                                continue

                                            if "unr" not in valid_leaderboards:
                                                valid_leaderboards.append("unr")

                                        if not valid_leaderboards:
                                            unranked_settings = all_leaderboard_settings.get("unr", {})
                                            if parsed_data.get("unr_pp", 0) < unranked_settings.get("pp_threshold",0.001):
                                                continue

                                            if parsed_data.get("rank") > unranked_settings.get("rank_threshold",math.inf):
                                                continue
                                            if unranked_settings.get("enabled",True) and "unr" not in valid_leaderboards:
                                                valid_leaderboards.append("unr")

                                    for leaderboard in valid_leaderboards:
                                        embed = embed_builder.build_embed(parsed_data, leaderboard, channel_data)
                                        view = embed_builder.build_view(parsed_data, leaderboard)
                                        send_tasks.append(channel.send(embed=embed, view=view))

                            await asyncio.gather(*send_tasks, return_exceptions=True)

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

    guild_data = data_manager.get_guild_data()

    user_roles = {role.id for role in user.roles}
    allowed_roles = guild_data["guilds"][guild_id].get("admin_roles", [])

    return bool(user_roles & set(allowed_roles))

@bot.slash_command(name="enable_channel",description="Enable score feed in your current channel or a chosen channel")
async def enable_channel(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!",ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})

    channel_data["enabled"] = True

    data_manager.save_guild_data()

    return await interaction.response.send_message("Score Feed is now enabled in this channel!", ephemeral = True)

@bot.slash_command(name="disable_channel", description="Disable score feed in your current channel")
async def disable_channel(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!",ephemeral = True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})

    channel_data["enabled"] = False

    data_manager.save_guild_data()

    return await interaction.response.send_message("Score Feed is now disabled in this channel.", ephemeral=True)

@bot.slash_command(name="set_channel_mode")
async def set_channel_mode(
        interaction: nextcord.Interaction,
        mode: str = nextcord.SlashOption(
            choices={
                "Multi": "multi",
                "Single": "single",
            }
        ),
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})

    channel_data["mode"] = mode

    data_manager.save_guild_data()

    return await interaction.response.send_message("Set channel mode successfully!", ephemeral=True)

@bot.slash_command(name="enable_customizations")
async def enable_customizations(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    channel_customizations = channel_data.setdefault("customization", {})

    channel_customizations["enabled"] = True

    data_manager.save_guild_data()

    return await interaction.response.send_message("Enabled customization successfully.", ephemeral=True)


@bot.slash_command(name="disable_customizations")
async def disable_customizations(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    channel_customizations = channel_data.setdefault("customization", {})

    channel_customizations["enabled"] = False

    data_manager.save_guild_data()

    return await interaction.response.send_message("Disabled customization successfully.", ephemeral=True)

@bot.slash_command(name="customize_element")
async def customize_element(
        interaction: nextcord.Interaction,
        element: str = nextcord.SlashOption(
            choices={
                "Score Text": "score_text",
                "Main Line": "main_line",
                "Data Slot 1": "data_1",
                "Data Slot 2": "data_2",
                "Data Slot 3": "data_3",
                "Data Slot 4": "data_4",
                "Data Slot 5": "data_5",
                "Data Slot 6": "data_6",
            }
        ),
        leaderboard: str = nextcord.SlashOption(
            choices={
                "ScoreSaber": "ss",
                "BeatLeader": "bl",
                "AccSaber": "acc",
                "Unranked": "unr",
                "All": "all"
            }
        ),
        text: str = "",
        autohide: str = None,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    lb_mapping = {
        "ss": ["ss"],
        "bl": ["bl"],
        "acc": ["acc"],
        "unr": ["unr"],
        "all": ["ss", "bl", "acc", "unr"],
    }

    leaderboards = lb_mapping[leaderboard]

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    channel_customizations = channel_data.setdefault("customization", {})
    customized_elements = channel_customizations.setdefault("customizations", {})

    for lb in leaderboards:
        lb_elements = customized_elements.setdefault(lb, {})
        current_element = lb_elements.setdefault(element, {})
        current_element["text"] = text
        current_element["autohide"] = autohide

    data_manager.save_guild_data()

    return await interaction.response.send_message("Element edited successfully.", ephemeral=True)

@bot.slash_command(name="reset_element")
async def reset_element(
        interaction: nextcord.Interaction,
        element: str = nextcord.SlashOption(
            choices={
                "Score Text": "score_text",
                "Main Line": "main_line",
                "Data Slot 1": "data_1",
                "Data Slot 2": "data_2",
                "Data Slot 3": "data_3",
                "Data Slot 4": "data_4",
                "Data Slot 5": "data_5",
                "Data Slot 6": "data_6",
                "All": "all"
            }
        ),
        leaderboard: str = nextcord.SlashOption(
            choices={
                "ScoreSaber": "ss",
                "BeatLeader": "bl",
                "AccSaber": "acc",
                "Unranked": "unr",
                "All": "all"
            }
        ),
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    lb_mapping = {
        "ss": ["ss"],
        "bl": ["bl"],
        "acc": ["acc"],
        "unr": ["unr"],
        "all": ["ss", "bl", "acc", "unr"],
    }

    leaderboards = lb_mapping[leaderboard]

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    channel_customizations = channel_data.setdefault("customization", {})
    customized_elements = channel_customizations.setdefault("customizations", {})

    if element == "all":
        for lb in leaderboards:
            try:
                customized_elements.pop(lb)
            except KeyError:
                pass

    else:
        for lb in leaderboards:
            lb_elements = customized_elements.setdefault(lb, {})
            try:
                lb_elements.pop(element)
            except KeyError:
                pass

    data_manager.save_guild_data()

    return await interaction.response.send_message("Element reset successfully.", ephemeral=True)

@bot.slash_command(name="enable_allowlist")
async def enable_allowlist(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    allowlist = filter_lists.setdefault("allowlist", {})

    allowlist["enabled"] = True

    data_manager.save_guild_data()

    return await interaction.response.send_message("Enabled allowlist successfully.", ephemeral=True)

@bot.slash_command(name="disable_allowlist")
async def disable_allowlist(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral = True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    allowlist = filter_lists.setdefault("allowlist", {})

    allowlist["enabled"] = False

    data_manager.save_guild_data()

    return await interaction.response.send_message("Disabled allowlist successfully.", ephemeral=True)


@bot.slash_command(name="enable_blocklist")
async def enable_blocklist(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    blocklist = filter_lists.setdefault("blocklist", {})

    blocklist["enabled"] = True

    data_manager.save_guild_data()

    return await interaction.response.send_message("Enabled blocklist successfully.", ephemeral=True)


@bot.slash_command(name="disable_blocklist")
async def disable_blocklist(
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    blocklist = filter_lists.setdefault("blocklist", {})

    blocklist["enabled"] = False

    data_manager.save_guild_data()

    return await interaction.response.send_message("Disabled blocklist successfully.", ephemeral=True)

@bot.slash_command(name="allowlist_add")
async def allowlist_add(
        interaction: nextcord.Interaction,
        bl_id,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    allowlist = filter_lists.setdefault("allowlist", {})
    allowlist_players = allowlist.setdefault("players", [])

    allowlist_enabled = allowlist.get("enabled")

    if allowlist_enabled is None:
        allowlist["enabled"] = True

    if bl_id in allowlist_players:
        return await interaction.response.send_message("This item is already in this filter list!", ephemeral=True)
    allowlist_players.append(bl_id)

    data_manager.save_guild_data()

    return await interaction.response.send_message(f"Added player to allowlist successfully!", ephemeral=True)


@bot.slash_command(name="allowlist_remove")
async def allowlist_remove(
        interaction: nextcord.Interaction,
        bl_id,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    allowlist = filter_lists.setdefault("allowlist", {})
    allowlist_players = allowlist.setdefault("players", [])

    if bl_id not in allowlist_players:
        return await interaction.response.send_message("This player is already not in the allowlist!", ephemeral=True)
    allowlist_players.remove(bl_id)

    data_manager.save_guild_data()

    return await interaction.response.send_message(f"Removed player from allowlist successfully!", ephemeral=True)

@bot.slash_command(name="blocklist_add")
async def blocklist_add(
        interaction: nextcord.Interaction,
        bl_id,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    blocklist = filter_lists.setdefault("blocklist", {})
    blocklist_players = blocklist.setdefault("players", [])

    allowlist_enabled = blocklist.get("enabled")

    if allowlist_enabled is None:
        blocklist["enabled"] = True

    if bl_id in blocklist_players:
        return await interaction.response.send_message("This item is already in this filter list!", ephemeral=True)
    blocklist_players.append(bl_id)

    data_manager.save_guild_data()

    return await interaction.response.send_message(f"Added player to allowlist successfully!", ephemeral=True)


@bot.slash_command(name="blocklist_remove")
async def blocklist_remove(
        interaction: nextcord.Interaction,
        bl_id,
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    filter_lists = channel_data.setdefault("filter_lists", {})
    blocklist = filter_lists.setdefault("blocklist", {})
    blocklist_players = blocklist.setdefault("players", [])

    if bl_id not in blocklist_players:
        return await interaction.response.send_message("This player is already not in the allowlist!", ephemeral=True)
    blocklist_players.remove(bl_id)

    data_manager.save_guild_data()

    return await interaction.response.send_message(f"Removed player from allowlist successfully!", ephemeral=True)

@bot.slash_command(name="add_admin_role")
async def add_admin_role(interaction: nextcord.Interaction, role: nextcord.Role):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    admin_roles = current_guild_data.setdefault("admin_roles", [])

    if role.id in admin_roles:
        return await interaction.response.send_message("This admin role is already registered.", ephemeral=True)

    admin_roles.append(role.id)

    data_manager.save_guild_data()

    return await interaction.response.send_message("Admin role added successfully!", ephemeral=True)


@bot.slash_command(name="remove_admin_role")
async def add_admin_role(interaction: nextcord.Interaction, role: nextcord.Role):
    guild_id = str(interaction.guild.id)

    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    admin_roles = current_guild_data.setdefault("admin_roles", [])

    if role.id not in admin_roles:
        return await interaction.response.send_message("This role already isn't in your guild's admin roles.", ephemeral=True)

    admin_roles.remove(role.id)

    data_manager.save_guild_data()

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
        channel: nextcord.TextChannel = None,
):
    guild_id = str(interaction.guild.id)
    channel_id = str((channel or interaction.channel).id)
    if not check_perms(interaction.user, guild_id):
        return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

    guild_data = data_manager.get_guild_data()

    current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
    channels = current_guild_data.setdefault("channels", {})
    channel_data = channels.setdefault(channel_id, {})
    all_leaderboard_settings = channel_data.setdefault("leaderboard_settings", {})
    leaderboard_settings = all_leaderboard_settings.setdefault(leaderboard, {})

    leaderboard_settings["enabled"] = enabled

    if pp_threshold:
        if pp_threshold == 0:
            leaderboard_settings["pp_threshold"] = None
        else:
            leaderboard_settings["pp_threshold"] = pp_threshold

    if rank_threshold:
        if rank_threshold == 0:
            leaderboard_settings["rank_threshold"] = None
        else:
            leaderboard_settings["rank_threshold"] = rank_threshold

    data_manager.save_guild_data()

    return await interaction.response.send_message(f"Updated channel's {leaderboard} settings successfully!", ephemeral=True)

@bot.event
async def on_ready():
    logger.init_logger(bot)
    logger.log("Score Feed started successfully!")
    listener.start()

bot.run(token)