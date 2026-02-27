import random
from models import Effect
from utils import GREEN, RED, CYAN, YELLOW, MAGENTA, BLUE, WHITE, BOLD, RESET

class Wheel:
    def __init__(self):
        self.outcomes = [
            {"id": "power", "type": "Power", "desc": "+25 Attack for 2 Attacks", "color": RED},
            {"id": "guard", "type": "Guard", "desc": "+20 Defense for 1 Round", "color": BLUE},
            {"id": "speed", "type": "Speed", "desc": "+15 Speed for 2 Rounds", "color": CYAN},
            {"id": "time", "type": "Time", "desc": "Enemy freezes. Skip next 2 turns.", "color": YELLOW},
            {"id": "divine", "type": "Divine", "desc": "Heal 80 HP & 40 MP", "color": GREEN},
            {"id": "chaos", "type": "Chaos", "desc": "Chaos Force! (+40 ATK) | -30 HP", "color": MAGENTA},
            {"id": "reversal", "type": "Fate Reversal", "desc": "Reflect 50% damage next turn", "color": WHITE},
            {"id": "surge", "type": "Corrupted Surge", "desc": "God-like ATK (+60) | HP Drain (3 turns)", "color": BOLD + RED},
        ]

    def spin(self, luck, level):
        weights = [15, 15, 15, 5 + luck//2, 5 + luck//3, 10, 2 + luck//5, 1 + level//10]
        outcome = random.choices(self.outcomes, weights=weights, k=1)[0]
        return outcome

    def apply_outcome(self, player, enemy, outcome):
        res = f"The Wheel stops on: {outcome['color']}{BOLD}{outcome['type']}{RESET}!"
        info = outcome['desc']
        
        if outcome['id'] == "power":
            player.add_effect(Effect("Power", 3, atk_mod=25, color=RED))
        elif outcome['id'] == "guard":
            player.add_effect(Effect("Guard", 2, def_mod=20, color=BLUE))
        elif outcome['id'] == "speed":
            player.add_effect(Effect("Speed", 3, spd_mod=15, color=CYAN))
        elif outcome['id'] == "time":
            # Managed in combat.py
            pass
        elif outcome['id'] == "divine":
            player.heal(80)
            player.mp = min(player.max_mp, player.mp + 40)
        elif outcome['id'] == "chaos":
            player.add_effect(Effect("Chaos Force", 4, atk_mod=40, color=MAGENTA))
            player.hp -= 30
            if player.hp < 1: player.hp = 1
        elif outcome['id'] == "reversal":
            # Managed in combat.py
            pass
        elif outcome['id'] == "surge":
            player.add_effect(Effect("Corrupted Surge", 4, atk_mod=60, damage_per_turn=15, color=BOLD+RED))
            
        return res, info
