import json
import os

SAVE_DIR = "saves"

def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_path(name):
    return os.path.join(SAVE_DIR, f"save_{name.lower()}.json")

def save_game(player, chapter):
    ensure_save_dir()
    data = {
        "name": player.name,
        "level": player.level,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "base_atk": player.base_atk,
        "base_def": player.base_def,
        "base_spd": player.base_spd,
        "luck": player.luck,
        "exp": player.exp,
        "exp_to_next": player.exp_to_next,
        "brotherhood_score": player.brotherhood_score,
        "mp": player.mp,
        "max_mp": player.max_mp,
        "gold": player.gold,
        "skill_stones": player.skill_stones,
        "equipment": player.equipment,
        "inventory": player.inventory,
        "skills_learned": player.skills, # Save the actual list with levels
        "chapter": chapter
    }
    path = get_save_path(player.name)
    with open(path, "w") as f:
        json.dump(data, f)
    return True

def list_saves():
    ensure_save_dir()
    saves = []
    for f in os.listdir(SAVE_DIR):
        if f.startswith("save_") and f.endswith(".json"):
            name = f[5:-5].capitalize()
            saves.append(name)
    return saves

def delete_save(name):
    path = get_save_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def load_game(player_class, name):
    path = get_save_path(name)
    if not os.path.exists(path):
        return None
    
    with open(path, "r") as f:
        data = json.load(f)
    
    player = player_class(data["name"])
    player.level = data["level"]
    player.hp = data["hp"]
    player.max_hp = data["max_hp"]
    player.base_atk = data.get("base_atk", 15)
    player.base_def = data.get("base_def", 5)
    player.base_spd = data.get("base_spd", 10)
    player.luck = data["luck"]
    player.exp = data["exp"]
    player.exp_to_next = data["exp_to_next"]
    player.brotherhood_score = data.get("brotherhood_score", 10)
    player.mp = data.get("mp", 20)
    player.max_mp = data.get("max_mp", 20)
    player.gold = data.get("gold", 0)
    player.skill_stones = data.get("skill_stones", 0)
    player.equipment = data.get("equipment", player.equipment)
    player.inventory = data.get("inventory", player.inventory)
    
    # Restore skills (learned and upgraded)
    if "skills_learned" in data:
        player.skills = data["skills_learned"]
    else:
        # Fallback for old saves
        player.skills = []
        for lv, skinf in player.skill_data.items():
            if player.level >= lv:
                player.skills.append(skinf)
    
    return player, data["chapter"]
