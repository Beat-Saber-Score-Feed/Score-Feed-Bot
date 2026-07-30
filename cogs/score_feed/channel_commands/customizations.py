import nextcord
from nextcord.ext import commands
from src.utils import perms, data_manager


class ChannelCustomizationsCommands(commands.Cog):
    @nextcord.slash_command(name="enable_customizations")
    async def enable_customizations(
            self,
            interaction: nextcord.Interaction,
            channel: nextcord.TextChannel = None, ):
        guild_id = str(interaction.guild.id)
        channel_id = str((channel or interaction.channel).id)

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        channels = current_guild_data.setdefault("channels", {})
        channel_data = channels.setdefault(channel_id, {})
        channel_customizations = channel_data.setdefault("customization", {})

        channel_customizations["enabled"] = True

        data_manager.save_guild_data()

        return await interaction.response.send_message("Enabled customization successfully.", ephemeral=True)

    @nextcord.slash_command(name="disable_customizations")
    async def disable_customizations(
            self,
            interaction: nextcord.Interaction,
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
        channel_customizations = channel_data.setdefault("customization", {})

        channel_customizations["enabled"] = False

        data_manager.save_guild_data()

        return await interaction.response.send_message("Disabled customization successfully.", ephemeral=True)

    @nextcord.slash_command(name="customize_element")
    async def customize_element(
            self,
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

        if not perms.check_perms(interaction.user, guild_id):
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

    @nextcord.slash_command(name="reset_element")
    async def reset_element(
            self,
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

        if not perms.check_perms(interaction.user, guild_id):
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

def setup(bot):
    bot.add_cog(ChannelCustomizationsCommands(bot))