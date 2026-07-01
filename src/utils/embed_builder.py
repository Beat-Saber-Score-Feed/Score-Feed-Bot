import nextcord

def build_embed(data, leaderboard = None):
    if leaderboard == "ss":
        embed = nextcord.Embed(
            title=f"**{data['name']}** scored on **{data['song_name']}** [{data['extended_difficulty_name']}]!",
            description=f"# <:scoresaber:1520959607303049237> **#{data['rank']}** / **{data['acc']}%** / **{data["ss_pp"]}pp**",
            color=data["color"],
            url=f"https://beatsaver.com/maps/{data['beatsaver_id']}"
        )

        embed.set_thumbnail(url=data['cover_image'])
        embed.set_author(
            name=data['name'],
            icon_url=data['pfp'],
            url=f"https://scoresaber.com/u/{data['player_id']}"
        )

        embed.add_field(name=f"Difficulty ⭐ {data['ss_stars']}", value="\u200B", inline=True)
        embed.add_field(name=f"Max Combo 📈 {data['max_combo']}", value="\u200B", inline=True)
        embed.add_field(name=f"Mistakes ❌ {data['mistakes']}", value="\u200B", inline=True)

    elif leaderboard == "acc":
        embed = nextcord.Embed(
            title=f"**{data['name']}** scored on **{data['song_name']}** [{data['extended_difficulty_name']}]!",
            description=f"# <:accsaber:1520959605415477318> **#{data['rank']}** / **{data['acc']}%** / **{data["acc_pp"]}ap**",
            color=data["color"],
            url=f"https://beatsaver.com/maps/{data['beatsaver_id']}"
        )

        embed.set_thumbnail(url=data['cover_image'])
        embed.set_author(
            name=data['name'],
            icon_url=data['pfp'],
            url=f"https://accsaberreloaded.com/players/{data['player_id']}"
        )

        embed.add_field(name=f"Complexity ⭐ {data['acc_stars']}", value="\u200B", inline=True)
        embed.add_field(name=f"Max Combo 📈 {data['max_combo']}", value="\u200B", inline=True)
        embed.add_field(name=f"Mistakes ❌ {data['mistakes']}", value="\u200B", inline=True)

    elif leaderboard == "bl":
        embed = nextcord.Embed(
            title=f"**{data['name']}** scored on **{data['song_name']}** [{data['extended_difficulty_name']}]!",
            description=f"# <:beatleader:1520959606119993506> **#{data['rank']}** / **{data['acc']}%** / **{data["bl_pp"]}pp**",
            color=data["color"],
            url=f"https://beatsaver.com/maps/{data['beatsaver_id']}"
        )

        embed.set_thumbnail(url=data['cover_image'])
        embed.set_author(
            name=data['name'],
            icon_url=data['pfp'],
            url=f"https://beatleader.com/u/{data['player_id']}"
        )

        embed.add_field(name=f"Difficulty ⭐ {data['bl_stars']}", value="\u200B", inline=True)
        embed.add_field(name=f"Max Combo 📈 {data['max_combo']}", value="\u200B", inline=True)
        embed.add_field(name=f"Mistakes ❌ {data['mistakes']}", value="\u200B", inline=True)

    else:
        embed = nextcord.Embed(
            title=f"**{data['name']}** scored on **{data['song_name']}** [{data['extended_difficulty_name']}]!",
            description=f"# **#{data['rank']}** / **{data['acc']}%** / **Unranked**",
            color=data["color"],
            url=f"https://beatsaver.com/maps/{data['beatsaver_id']}"
        )

        embed.set_thumbnail(url=data['cover_image'])
        embed.set_author(
            name=data['name'],
            icon_url=data['pfp'],
            url=f"https://beatleader.com/u/{data['player_id']}"
        )

        embed.add_field(name=f"Difficulty ⭐ Unranked", value="\u200B", inline=True)
        embed.add_field(name=f"Max Combo 📈 {data['max_combo']}", value="\u200B", inline=True)
        embed.add_field(name=f"Mistakes ❌ {data['mistakes']}", value="\u200B", inline=True)

    return embed

def build_view(data, leaderboard = None):
    view = nextcord.ui.View()

    if leaderboard == "ss":
        view.add_item(nextcord.ui.Button(
            label="View on ScoreSaber",
            url=f"https://scoresaber.com/map/{data['ss_map_id']}/difficulty/{data['ss_difficulty_id']}",
        ))

    elif leaderboard == "acc":
        view.add_item(nextcord.ui.Button(
            label="View on AccSaber Reloaded",
            url=f"https://accsaberreloaded.com/maps/{data['beatsaver_id']}?difficulty={data['acc_difficulty_name'].lower()}",
        ))

    elif leaderboard == "bl":
        view.add_item(nextcord.ui.Button(
            label="View on BeatLeader",
            url=f"https://beatleader.com/leaderboard/global/{data['leaderboard_id']}",
        ))

    else:
        view.add_item(nextcord.ui.Button(
            label="View on BeatLeader",
            url=f"https://beatleader.com/leaderboard/global/{data['leaderboard_id']}",
        ))

    view.add_item(nextcord.ui.Button(
        label="Watch Replay",
        url=f"https://allpoland.github.io/ArcViewer/?scoreID={data['score_id']}&autoPlay=true"
    ))

    return view