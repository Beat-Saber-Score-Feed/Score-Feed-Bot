import websockets
import json
import math
import traceback
import asyncio
from src.utils import logger, score_parser, data_manager, embed_builder
from nextcord.ext import commands, tasks

class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=0)
    async def listener(self):
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
                                        channel = self.bot.get_channel(int(channel_id))

                                        if not channel:
                                            continue

                                        channel_data = current_guild_data["channels"][channel_id]

                                        if not channel_data.get("enabled", False):
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

                                                if parsed_data.get(f"{leaderboard}_pp", 0) < leaderboard_settings.get(
                                                        "pp_threshold", 0.001):
                                                    continue

                                                if parsed_data.get("rank") > leaderboard_settings.get("rank_threshold",
                                                                                                      math.inf):
                                                    continue

                                                if not leaderboard_settings.get("enabled", True):
                                                    unranked_settings = all_leaderboard_settings.get("unr", {})
                                                    if parsed_data.get("rank") > unranked_settings.get("rank_threshold",
                                                                                                       math.inf):
                                                        continue
                                                    if unranked_settings.get("enabled",
                                                                             True) and "unr" not in valid_leaderboards:
                                                        valid_leaderboards.append("unr")
                                                    continue

                                                valid_leaderboards.append(leaderboard)

                                            if not valid_leaderboards:
                                                unranked_settings = all_leaderboard_settings.get("unr", {})
                                                if parsed_data.get("rank") > unranked_settings.get("rank_threshold",
                                                                                                   math.inf):
                                                    continue
                                                if unranked_settings.get("enabled",
                                                                         True) and "unr" not in valid_leaderboards:
                                                    valid_leaderboards.append("unr")
                                        else:
                                            for leaderboard in leaderboards:
                                                leaderboard_settings = all_leaderboard_settings.get(leaderboard, {})

                                                if parsed_data.get(f"{leaderboard}_pp", 0) < leaderboard_settings.get(
                                                        "pp_threshold", 0.001):
                                                    continue

                                                if parsed_data.get("rank") > leaderboard_settings.get("rank_threshold",
                                                                                                      math.inf):
                                                    continue

                                                if leaderboard_settings.get("enabled",
                                                                            True) and "unr" not in valid_leaderboards:
                                                    valid_leaderboards.append("unr")

                                            if not valid_leaderboards:
                                                unranked_settings = all_leaderboard_settings.get("unr", {})

                                                if parsed_data.get("rank") > unranked_settings.get("rank_threshold",
                                                                                                   math.inf):
                                                    continue
                                                if unranked_settings.get("enabled",
                                                                         True) and "unr" not in valid_leaderboards:
                                                    valid_leaderboards.append("unr")

                                        for leaderboard in valid_leaderboards:
                                            embed = embed_builder.build_embed(parsed_data, leaderboard, channel_data)
                                            view = embed_builder.build_view(parsed_data, leaderboard)
                                            send_tasks.append(channel.send(embed=embed, view=view))

                                await asyncio.gather(*send_tasks, return_exceptions=True)

                                logger.log(
                                    f"Posted {parsed_data['ss_pp']}pp score by {parsed_data['name']} on {parsed_data['song_name']} {parsed_data['extended_difficulty_name']}")

                        except websockets.ConnectionClosed:
                            logger.log("Websocket closed, reconnecting...")
                            break

            except Exception as e:
                logger.log(f"Websocket error: {e}")
                traceback.print_exc()

            await asyncio.sleep(3)

def setup(bot):
    bot.add_cog(Listener(bot))