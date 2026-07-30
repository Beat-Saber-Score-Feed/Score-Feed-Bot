import nextcord
from nextcord.ext import commands

from src.utils import perms, data_manager

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="add_admin_role")
    async def add_admin_role(self, interaction: nextcord.Interaction, role: nextcord.Role):
        guild_id = str(interaction.guild.id)

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        admin_roles = current_guild_data.setdefault("admin_roles", [])

        if role.id in admin_roles:
            return await interaction.response.send_message("This admin role is already registered.", ephemeral=True)

        admin_roles.append(role.id)

        data_manager.save_guild_data()

        return await interaction.response.send_message("Admin role added successfully!", ephemeral=True)

    @nextcord.slash_command(name="remove_admin_role")
    async def remove_admin_role(self, interaction: nextcord.Interaction, role: nextcord.Role):
        guild_id = str(interaction.guild.id)

        if not perms.check_perms(interaction.user, guild_id):
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)

        guild_data = data_manager.get_guild_data()

        current_guild_data = guild_data["guilds"].setdefault(guild_id, {})
        admin_roles = current_guild_data.setdefault("admin_roles", [])

        if role.id not in admin_roles:
            return await interaction.response.send_message("This role already isn't in your guild's admin roles.",
                                                           ephemeral=True)

        admin_roles.remove(role.id)

        data_manager.save_guild_data()

        return await interaction.response.send_message("Admin role removed successfully!", ephemeral=True)

def setup(bot):
    bot.add_cog(ServerCommands(bot))