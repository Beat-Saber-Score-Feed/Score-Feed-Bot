from src.utils import data_manager

def check_perms(user, guild_id):
    if user.guild_permissions.administrator:
        return True

    guild_data = data_manager.get_guild_data()

    user_roles = {role.id for role in user.roles}
    allowed_roles = guild_data["guilds"][guild_id].get("admin_roles", [])

    return bool(user_roles & set(allowed_roles))