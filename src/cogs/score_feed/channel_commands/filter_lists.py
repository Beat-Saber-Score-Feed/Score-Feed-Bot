import nextcord

from nextcord.ext import commands

from src.utils import perms, data_manager


class ChannelFilterListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="enable_allowlist")
    async def enable_allowlist(
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        allowlist = filter_lists.setdefault("allowlist", {})

        allowlist["enabled"] = True

        data_manager.save_guild_data()

        return await interaction.response.send_message("Enabled allowlist successfully.", ephemeral=True)

    @nextcord.slash_command(name="disable_allowlist")
    async def disable_allowlist(
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        allowlist = filter_lists.setdefault("allowlist", {})

        allowlist["enabled"] = False

        data_manager.save_guild_data()

        return await interaction.response.send_message("Disabled allowlist successfully.", ephemeral=True)

    @nextcord.slash_command(name="enable_blocklist")
    async def enable_blocklist(
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        blocklist = filter_lists.setdefault("blocklist", {})

        blocklist["enabled"] = True

        data_manager.save_guild_data()

        return await interaction.response.send_message("Enabled blocklist successfully.", ephemeral=True)

    @nextcord.slash_command(name="disable_blocklist")
    async def disable_blocklist(
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        blocklist = filter_lists.setdefault("blocklist", {})

        blocklist["enabled"] = False

        data_manager.save_guild_data()

        return await interaction.response.send_message("Disabled blocklist successfully.", ephemeral=True)

    @nextcord.slash_command(name="allowlist_add")
    async def allowlist_add(
            self,
            interaction: nextcord.Interaction,
            bl_id,
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

    @nextcord.slash_command(name="allowlist_remove")
    async def allowlist_remove(
            self,
            interaction: nextcord.Interaction,
            bl_id,
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        allowlist = filter_lists.setdefault("allowlist", {})
        allowlist_players = allowlist.setdefault("players", [])

        if bl_id not in allowlist_players:
            return await interaction.response.send_message("This player is already not in the allowlist!",
                                                           ephemeral=True)
        allowlist_players.remove(bl_id)

        data_manager.save_guild_data()

        return await interaction.response.send_message(f"Removed player from allowlist successfully!", ephemeral=True)

    @nextcord.slash_command(name="blocklist_add")
    async def blocklist_add(
            self,
            interaction: nextcord.Interaction,
            bl_id,
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

    @nextcord.slash_command(name="blocklist_remove")
    async def blocklist_remove(
            self,
            interaction: nextcord.Interaction,
            bl_id,
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
        filter_lists = channel_data.setdefault("filter_lists", {})
        blocklist = filter_lists.setdefault("blocklist", {})
        blocklist_players = blocklist.setdefault("players", [])

        if bl_id not in blocklist_players:
            return await interaction.response.send_message("This player is already not in the allowlist!",
                                                           ephemeral=True)
        blocklist_players.remove(bl_id)

        data_manager.save_guild_data()

        return await interaction.response.send_message(f"Removed player from allowlist successfully!", ephemeral=True)

def setup(bot):
    bot.add_cog(ChannelFilterListCommands(bot))