import requests
import nextcord
from src.utils import accsaber, scoresaber


def parse_score(score_data):
    bl_converted_data = {
        "name": score_data["player"]["name"],
        "pfp": score_data["player"]["avatar"],
        "player_id": score_data["player"]["id"],
        "leaderboard_id": score_data["leaderboard"]["id"],
        "beatsaver_id": score_data["leaderboard"]["song"]["id"].rstrip("x"),
        "difficulty_id": score_data["leaderboard"]["difficulty"]["id"],
        "hash": score_data["leaderboard"]["song"]["hash"],
        "score_id": score_data["id"],
        "modifiers": score_data["modifiers"],
        "mode": score_data["leaderboard"]["difficulty"]["modeName"],
        "extended_mode": f"Solo{score_data["leaderboard"]["difficulty"]["modeName"]}",
        "difficulty_number": score_data["leaderboard"]["difficulty"]["value"],
        "difficulty_name": score_data["leaderboard"]["difficulty"]["difficultyName"],
        "extended_difficulty_name": f"{score_data["leaderboard"]["difficulty"]["modeName"]} {score_data["leaderboard"]["difficulty"]["difficultyName"]}",
        "song_name": score_data["leaderboard"]["song"]["name"],
        "song_sub_name": score_data["leaderboard"]["song"]["subName"],
        "cover_image": score_data["leaderboard"]["song"]["coverImage"],
        "acc": round(score_data["accuracy"] * 100, 2),
        "mistakes": score_data["missedNotes"] + score_data["badCuts"] + score_data["bombCuts"],
        "rank": score_data["rank"],
        "max_combo": score_data["maxCombo"],
        "bl_pp": round(score_data["pp"], 2),
        "bl_stars": score_data["leaderboard"]["difficulty"].get("stars", 0),
    }

    ss_map_data = requests.get(f"https://scoresaber.com/api/v2/leaderboards/hash/{bl_converted_data['hash']}/{bl_converted_data['extended_mode']}/{bl_converted_data['difficulty_number']}",params={"realmId": "1"}).json()

    ss_map = ss_map_data.get("map", {})
    realm = ss_map_data.get("realm", {})
    ss_difficulty = ss_map_data.get("difficulty", {})

    ss_stars = realm.get("stars", 0)
    ss_converted_data = {
        "ss_stars": ss_stars,
        "ss_pp": scoresaber.calculate_pp(bl_converted_data["acc"], ss_stars),
        "ss_map_id": ss_map.get("id"),
        "ss_difficulty_id": ss_difficulty.get("id"),
    }

    accsaber_map_data = requests.get(f"https://api.accsaberreloaded.com/v1/maps/hash/{bl_converted_data['hash']}?difficulty={accsaber.convert_difficulty(bl_converted_data['difficulty_number'])}").json()

    difficulties = accsaber_map_data.get("difficulties", [])

    if difficulties:
        acc_difficulty = difficulties[0]
    else:
        acc_difficulty = {}

    acc_stars = acc_difficulty.get("complexity", 0)
    acc_converted_data = {
        "acc_stars": acc_stars,
        "acc_pp": accsaber.calculate_ap(acc_stars, bl_converted_data["acc"]),
        "acc_difficulty_name": accsaber.convert_difficulty(bl_converted_data["difficulty_number"]),
    }

    ranked_leaderboards = []

    if bl_converted_data["bl_stars"] > 0:
        ranked_leaderboards.append("bl")

    if ss_converted_data["ss_stars"] > 0:
        ranked_leaderboards.append("ss")

    if acc_converted_data["acc_stars"] > 0:
        ranked_leaderboards.append("acc")

    other_data = {
        "ranked_leaderboards": ranked_leaderboards or ["unr"]
    }

    if bl_converted_data["rank"] == 1:
        other_data["color"] = nextcord.Color.red()
    elif bl_converted_data["rank"] <= 10:
        other_data["color"] = nextcord.Color.dark_purple()
    elif bl_converted_data["rank"] <= 25:
        other_data["color"] = nextcord.Color.green()
    elif bl_converted_data["rank"] <= 50:
        other_data["color"] = nextcord.Color.yellow()
    else:
        other_data["color"] = nextcord.Color.light_gray()

    return {**bl_converted_data, **ss_converted_data, **acc_converted_data, **other_data}