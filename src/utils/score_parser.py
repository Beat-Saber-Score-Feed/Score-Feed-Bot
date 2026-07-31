import json

import requests
import nextcord
from src.utils import accsaber, scoresaber, beatleader


def parse_score(score_data):
    ss_score_id = score_data["score"]["id"]
    ss_resp = requests.get(f"https://scoresaber.com/api/v2/scores/{ss_score_id}").json()

    ss_converted_data = {
        "score_id": ss_score_id,
        "name": ss_resp["score"]["player"]["name"],
        "pfp": ss_resp["score"]["player"]["avatar"],
        "player_id": ss_resp["score"]["player"]["id"],
        "leaderboard_id": ss_resp["leaderboard"]["id"],
        "beatsaver_id": ss_resp["leaderboard"]["map"]["bsid"],
        "difficulty_id": ss_resp["leaderboard"]["difficulty"]["id"],
        "hash": ss_resp["leaderboard"]["map"]["hash"],
        "modifiers": ss_resp["score"]["mods"],
        "mode": ss_resp["leaderboard"]["difficulty"]["gameMode"][4:],
        "extended_mode": ss_resp["leaderboard"]["difficulty"]["gameMode"],
        "difficulty_number": ss_resp["leaderboard"]["difficulty"]["difficulty"],
        "difficulty_name": scoresaber.convert_difficulty(ss_resp["leaderboard"]["difficulty"]["difficulty"]),
        "extended_difficulty_name": f"{ss_resp["leaderboard"]["difficulty"]["gameMode"][4:]} {scoresaber.convert_difficulty(score_data["leaderboard"]["difficulty"]["difficulty"])}",
        "song_name": ss_resp["leaderboard"]["map"]["songName"],
        "song_sub_name": ss_resp["leaderboard"]["map"]["songSubName"],
        "cover_image": ss_resp["leaderboard"]["map"]["coverUrl"],
        "acc": round(ss_resp["score"]["accuracy"] * 100, 2),
        "mistakes": ss_resp["score"]["missedNotes"] + ss_resp["score"]["badCuts"],
        "rank": ss_resp["score"]["rank"],
        "max_combo": ss_resp["score"]["maxCombo"],
        "ss_pp": round(ss_resp["score"]["pp"], 2),
        "ss_stars": round(ss_resp["leaderboard"]["realm"]["stars"], 2),
        "ss_map_id": ss_resp["leaderboard"]["map"]["id"],
        "ss_difficulty_id": ss_resp["leaderboard"]["difficulty"]["id"],
    }

    bl_resp = requests.get(f"https://api.beatleader.com/leaderboard/{ss_converted_data["hash"]}/{ss_converted_data["difficulty_name"]}/{ss_converted_data["mode"]}")

    try:
        bl_map_data = bl_resp.json()
    except json.decoder.JSONDecodeError:
        bl_map_data = {}

    bl_difficulty = bl_map_data.get("difficulty", {})

    bl_pass_stars = bl_difficulty.get("passRating", 0)
    bl_acc_stars = bl_difficulty.get("accRating", 0)
    bl_tech_stars = bl_difficulty.get("techRating", 0)
    bl_converted_data = {
        "bl_stars": round(bl_difficulty.get("stars") or 0, 2),
        "bl_pp": round(beatleader.calculate_pp(bl_acc_stars, bl_pass_stars, bl_tech_stars, ss_resp["score"]["accuracy"] * 100) or 0, 2),
        "bl_map_id": bl_map_data.get("id"),
    }

    accsaber_resp = requests.get(f"https://api.accsaberreloaded.com/v1/maps/hash/{ss_converted_data['hash']}?difficulty={accsaber.convert_difficulty(ss_converted_data['difficulty_number'])}")
    try:
        accsaber_map_data = accsaber_resp.json()
    except json.decoder.JSONDecodeError:
        accsaber_map_data = {}

    difficulties = accsaber_map_data.get("difficulties", [])

    if difficulties:
        acc_difficulty = difficulties[0]
    else:
        acc_difficulty = {}

    acc_stars = acc_difficulty.get("complexity", 0)
    acc_converted_data = {
        "acc_stars": acc_stars,
        "acc_pp": accsaber.calculate_ap(acc_stars, ss_resp["score"]["accuracy"] * 100),
        "acc_difficulty_name": accsaber.convert_difficulty(ss_converted_data["difficulty_number"]),
    }

    other_data = {}

    if ss_converted_data["rank"] == 1:
        other_data["color"] = nextcord.Color.red()
    elif ss_converted_data["rank"] <= 10:
        other_data["color"] = nextcord.Color.dark_purple()
    elif ss_converted_data["rank"] <= 25:
        other_data["color"] = nextcord.Color.green()
    elif ss_converted_data["rank"] <= 50:
        other_data["color"] = nextcord.Color.yellow()
    else:
        other_data["color"] = nextcord.Color.light_gray()

    return {**ss_converted_data, **bl_converted_data, **acc_converted_data, **other_data}