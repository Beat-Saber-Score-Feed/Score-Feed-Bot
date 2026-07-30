import nextcord

from nextcord.ext import commands

from src.utils import perms, data_manager

class ChannelSettingsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="enable_channel",description="Enable score feed in your current channel or a chosen channel")
    async def enable_channel(self, interaction: nextcord.Interaction,channel: nextcord.TextChannel = None):
        guild_id = str(interaction.guild.id)
        channel_id = str((channel or interaction.channel).id)

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        channels = current_guild_data.setdefault("channels", {})
        channel_data = channels.setdefault(channel_id, {})

        channel_data["enabled"] = True

        data_manager.save_guild_data()

        return await interaction.response.send_message("Score Feed is now enabled in this channel!", ephemeral=True)

    @nextcord.slash_command(name="disable_channel", description="Disable score feed in your current channel")
    async def disable_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel = None):
        guild_id = str(interaction.guild.id)
        channel_id = str((channel or interaction.channel).id)

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        channels = current_guild_data.setdefault("channels", {})
        channel_data = channels.setdefault(channel_id, {})

        channel_data["enabled"] = False

        data_manager.save_guild_data()

        return await interaction.response.send_message("Score Feed is now disabled in this channel.", ephemeral=True)

    @nextcord.slash_command(name="set_channel_mode")
    async def set_channel_mode(
            self,
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

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        channels = current_guild_data.setdefault("channels", {})
        channel_data = channels.setdefault(channel_id, {})

        channel_data["mode"] = mode

        data_manager.save_guild_data()

        return await interaction.response.send_message("Set channel mode successfully!", ephemeral=True)

    @nextcord.slash_command(name="lb_settings")
    async def lb_settings(
            self,
            interaction: nextcord.Interaction,
            leaderboard: str = nextcord.SlashOption(
                choices={
                    "BeatLeader": "bl",
                    "ScoreSaber": "ss",
                    "AccSaber": "acc",
                    "Unranked": "unr",
                },
            ),
            enabled: bool = nextcord.SlashOption(
                choices={
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
        if not perms.check_perms(interaction.user, guild_id):
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

        return await interaction.response.send_message(f"Updated channel's {leaderboard} settings successfully!",
                                                       ephemeral=True)

def setup(bot):
    bot.add_cog(ChannelSettingsCommands(bot))