from string import Template
from deepmerge import always_merger

import copy

DEFAULT_CUSTOMIZATIONS = {
    "ss": {
        "score_text": {
            "text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
            "autohide": None
        },
        "main_line": {
            "text": "# <:scoresaber:1520959607303049237> **#${rank}** / **${acc}%** / **${ss_pp}pp**",
            "autohide": None
        },
        "data_1": {
            "text": "Stars ⭐ ${ss_stars}",
            "autohide": None
        },
        "data_2": {
            "text": "Max Combo 📈 ${max_combo}",
            "autohide": None
        },
        "data_3": {
            "text": "Mistakes ❌ ${mistakes}",
            "autohide": None
        },
        "data_4": {
            "text": "",
            "autohide": None
        },
        "data_5": {
            "text": "",
            "autohide": None
        },
        "data_6": {
            "text": "",
            "autohide": None
        }
    },
    "bl": {
        "score_text": {
            "text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
            "autohide": None
        },
        "main_line": {
            "text": "# <:beatleader:1520959606119993506> **#${rank}** / **${acc}%** / **${bl_pp}pp**",
            "autohide": None
        },
        "data_1": {
            "text": "Stars ⭐ ${bl_stars}",
            "autohide": None
        },
        "data_2": {
            "text": "Max Combo 📈 ${max_combo}",
            "autohide": None
        },
        "data_3": {
            "text": "Mistakes ❌ ${mistakes}",
            "autohide": None
        },
        "data_4": {
            "text": "Mods: ${formatted_mods}",
            "autohide": "formatted_mods"
        },
        "data_5": {
            "text": "",
            "autohide": None
        },
        "data_6": {
            "text": "",
            "autohide": None
        }
    },
    "acc": {
        "score_text": {
            "text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
            "autohide": None
        },
        "main_line": {
            "text": "# <:accsaber:1520959605415477318> **#${rank}** / **${acc}%** / **${acc_pp}ap**",
            "autohide": None
        },
        "data_1": {
            "text": "Stars ⭐ ${acc_stars}",
            "autohide": None
        },
        "data_2": {
            "text": "Max Combo 📈 ${max_combo}",
            "autohide": None
        },
        "data_3": {
            "text": "Mistakes ❌ ${mistakes}",
            "autohide": None
        },
        "data_4": {
            "text": "",
            "autohide": None
        },
        "data_5": {
            "text": "",
            "autohide": None
        },
        "data_6": {
            "text": "",
            "autohide": None
        }
    },
    "unr": {
        "score_text": {
            "text": "**${name}** scored on **${song_name}** [${extended_difficulty_name}]!",
            "autohide": None
        },
        "main_line": {
            "text": "# **#${rank}** / **${acc}%** / **Unranked**",
            "autohide": None
        },
        "data_1": {
            "text": "Stars ⭐ Unranked",
            "autohide": None
        },
        "data_2": {
            "text": "Max Combo 📈 ${max_combo}",
            "autohide": None
        },
        "data_3": {
            "text": "Mistakes ❌ ${mistakes}",
            "autohide": None
        },
        "data_4": {
            "text": "",
            "autohide": None
        },
        "data_5": {
            "text": "",
            "autohide": None
        },
        "data_6": {
            "text": "",
            "autohide": None
        }
    }
}

def get_customizations(channel_data):
    channel_customizations = channel_data.get("customization", {})
    if channel_customizations.get("enabled", True):
        customized_elements = channel_customizations.get("customizations", {})
    else:
        customized_elements = {}

    return always_merger.merge(copy.deepcopy(DEFAULT_CUSTOMIZATIONS), copy.deepcopy(customized_elements))

def get_parsed_customizations(data, channel_data):
    customizations = get_customizations(channel_data)

    for lb in customizations:
        for element in customizations[lb]:
            customizations[lb][element]["text"] = parse_template_string(customizations[lb][element]["text"], data)

    return customizations

def parse_template_string(template: str, data):
    template = Template(template)
    return template.safe_substitute(**data)