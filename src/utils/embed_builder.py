import nextcord

from src.utils import customizations, logger

def build_embed(data, leaderboard, channel_data):
    parsed_customizations = customizations.get_parsed_customizations(data, channel_data)
    lb_customizations = parsed_customizations[leaderboard]

    embed = nextcord.Embed(
        title=lb_customizations["score_text"],
        description=lb_customizations["main_line"],
        color=data["color"],
        url=f"https://beatsaver.com/maps/{data['beatsaver_id']}"
    )

    if leaderboard == "ss":
        profile_link = f"https://scoresaber.com/u/{data['player_id']}"
    elif leaderboard == "acc":
        profile_link = f"https://accsaberreloaded.com/players/{data['player_id']}"
    else:
        profile_link = f"https://beatleader.com/u/{data['player_id']}"

    embed.set_thumbnail(url=data['cover_image'])
    embed.set_author(
        name=data['name'],
        icon_url=data['pfp'],
        url=profile_link
    )

    embed.add_field(name=lb_customizations["data_1"], value="\u200B", inline=True)
    embed.add_field(name=lb_customizations["data_2"], value="\u200B", inline=True)
    embed.add_field(name=lb_customizations["data_3"], value="\u200B", inline=True)
    embed.add_field(name=lb_customizations["data_4"], value="\u200B", inline=True)
    embed.add_field(name=lb_customizations["data_5"], value="\u200B", inline=True)
    embed.add_field(name=lb_customizations["data_6"], value="\u200B", inline=True)

    return embed

def build_view(data, leaderboard = None):
    view = nextcord.ui.View()

    if leaderboard == "ss":
        text = "View on ScoreSaber"
        leaderboard_link = f"https://scoresaber.com/map/{data['ss_map_id']}/difficulty/{data['ss_difficulty_id']}"
    elif leaderboard == "acc":
        text = "View on AccSaber Reloaded"
        leaderboard_link = f"https://accsaberreloaded.com/maps/{data['beatsaver_id']}?difficulty={data['acc_difficulty_name'].lower()}"
    else:
        text = "View on BeatLeader"
        leaderboard_link = f"https://beatleader.com/leaderboard/global/{data['leaderboard_id']}"

    view.add_item(nextcord.ui.Button(
        label=text,
        url=leaderboard_link,
    ))

    view.add_item(nextcord.ui.Button(
        label="Watch Replay",
        url=f"https://allpoland.github.io/ArcViewer/?scoreID={data['score_id']}&autoPlay=true"
    ))

    return view