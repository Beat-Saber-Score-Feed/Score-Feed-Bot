from string import Template
from src.utils import logger

DEFAULT_CUSTOMIZATIONS = {
    "ss": {
        "score_text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
        "main_line": "# <:scoresaber:1520959607303049237> **#${rank}** / **${acc}%** / **${ss_pp}pp**",
        "data_1": "Stars ⭐ ${ss_stars}",
        "data_2": "Max Combo 📈 ${max_combo}",
        "data_3": "Mistakes ❌ ${mistakes}",
        "data_4": "",
        "data_5": "",
        "data_6": "",
    },
    "bl": {
        "score_text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
        "main_line": "# <:beatleader:1520959606119993506> **#${rank}** / **${acc}%** / **${bl_pp}pp**",
        "data_1": "Stars ⭐ ${bl_stars}",
        "data_2": "Max Combo 📈 ${max_combo}",
        "data_3": "Mistakes ❌ ${mistakes}",
        "data_4": "",
        "data_5": "",
        "data_6": "",
    },
    "acc": {
        "score_text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
        "main_line": "# <:accsaber:1520959605415477318> **#${rank}** / **${acc}%** / **${acc_pp}pp**",
        "data_1": "Complexity ⭐ ${acc_stars}",
        "data_2": "Max Combo 📈 ${max_combo}",
        "data_3": "Mistakes ❌ ${mistakes}",
        "data_4": "",
        "data_5": "",
        "data_6": "",
    },
    "unr": {
        "score_text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
        "main_line": "# **#${rank}** / **${acc}%** / **Unranked**",
        "data_1": "Stars ⭐ Unranked",
        "data_2": "Max Combo 📈 ${max_combo}",
        "data_3": "Mistakes ❌ ${mistakes}",
        "data_4": "",
        "data_5": "",
        "data_6": "",
    }
}

def get_customizations(channel_data):
    channel_customizations = channel_data.get("customization", {})
    if channel_customizations.get("enabled", False):
        customized_elements = channel_customizations.get("customizations", {})
    else:
        customized_elements = {}

    return {**DEFAULT_CUSTOMIZATIONS, **customized_elements}

def get_parsed_customizations(data, channel_data):
    customizations = get_customizations(channel_data)

    for lb in customizations:
        for element in customizations[lb]:
            customizations[lb][element] = parse_template_string(customizations[lb][element], data)

    return customizations

def parse_template_string(template: str, data):
    template = Template(template)
    return template.safe_substitute(**data)