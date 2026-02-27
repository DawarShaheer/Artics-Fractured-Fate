import random

class Effect:
    def __init__(self, name, turns, atk_mod=0, def_mod=0, spd_mod=0, damage_per_turn=0, color="\033[37m"):
        self.name = name
        self.turns = turns
        self.atk_mod = atk_mod
        self.def_mod = def_mod
        self.spd_mod = spd_mod
        self.damage_per_turn = damage_per_turn
        self.color = color

class Entity:
    def __init__(self, name, hp, max_hp, atk, def_stat, spd, luck):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.base_atk = atk
        self.base_def = def_stat
        self.base_spd = spd
        self.luck = luck
        self.effects = []
        self.gold = 0

    def clear_effects(self):
        self.effects = []

    @property
    def atk(self):
        mod = sum(e.atk_mod for e in self.effects)
        equip_mod = 0
        if hasattr(self, 'equipment') and self.equipment.get("weapon"):
            equip_mod = self.equipment["weapon"].get("atk_bonus", 0)
        return max(1, self.base_atk + mod + equip_mod)

    @property
    def def_stat(self):
        mod = sum(e.def_mod for e in self.effects)
        equip_mod = 0
        if hasattr(self, 'equipment') and self.equipment.get("armor"):
            equip_mod = self.equipment["armor"].get("def_bonus", 0)
        return max(0, self.base_def + mod + equip_mod)

    @property
    def spd(self):
        mod = sum(e.spd_mod for e in self.effects)
        equip_mod = 0
        if hasattr(self, 'equipment') and self.equipment.get("boots"):
            equip_mod = self.equipment["boots"].get("spd_bonus", 0)
        return max(1, self.base_spd + mod + equip_mod)

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, attacker_atk):
        # Professional Scaling: (Atk^2) / (Atk + Def)
        # This prevents 0 damage and feels more "RPG-like"
        denominator = attacker_atk + self.def_stat
        if denominator == 0: denominator = 1
        actual_damage = int((attacker_atk * attacker_atk) / denominator)
        
        # Minimum damage based on attacker's level or base power (approx 5% of atk)
        min_dmg = max(1, int(attacker_atk * 0.1))
        actual_damage = max(min_dmg, actual_damage)
        
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_effect(self, effect):
        # Professional Stacking: Allow multiple instances
        self.effects.append(effect)

    def process_turn_start(self):
        """Called at the very start of a combat round."""
        pass

    def process_turn_end(self):
        """Called after the entity takes their action."""
        msgs = []
        expired = []
        for e in self.effects:
            # Handle per-turn tick (damage/drain)
            if e.damage_per_turn != 0:
                self.hp = max(0, self.hp - e.damage_per_turn)
                msgs.append(f"{e.color}{e.name} affects {self.name}! (-{e.damage_per_turn} HP)\033[0m")
            
            # Decrement duration
            e.turns -= 1
            if e.turns <= 0:
                expired.append(e)
        
        for e in expired:
            if e in self.effects:
                self.effects.remove(e)
                msgs.append(f"{e.color}Effect '{e.name}' has worn off.\033[0m")
        
        return msgs

    def get_status_str(self):
        if not self.effects:
            return ""
        
        # Group same-name effects for UI cleanliness
        counts = {}
        for e in self.effects:
            key = (e.name, e.color)
            counts[key] = counts.get(key, 0) + 1
        
        status_items = []
        for (name, color), count in counts.items():
            display = f"{name} x{count}" if count > 1 else name
            status_items.append(f"{color}[{display}]\033[0m")
            
        return " ".join(status_items)

class Player(Entity):
    def __init__(self, name):
        super().__init__(name, hp=100, max_hp=100, atk=15, def_stat=5, spd=10, luck=5)
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.gold = 50
        self.skill_stones = 0
        self.brotherhood_score = 10
        self.skills = []
        self.skill_data = {
            5: {"id": "echo", "name": "Echo Step", "desc": "Blur your form, doubling SPD for 3 Rounds.", "cost": 10, "level": 1},
            10: {"id": "guard", "name": "Fate Guard", "desc": "Brace against destiny, doubling DEF for 2 Rounds.", "cost": 15, "level": 1},
            15: {"id": "light", "name": "Light Arc", "desc": "A horizontal strike of pure hope. High damage.", "cost": 45, "level": 1},
            25: {"id": "time", "name": "Time Split", "desc": "Fracture the moment. Enemy skips turn.", "cost": 40, "level": 1},
            40: {"id": "mercy", "name": "Final Mercy", "desc": "A strike that ends the conflict with peace.", "cost": 60, "level": 1}
        }
        self.mp = 20
        self.max_mp = 20
        self.gold = 50
        self.skill_stones = 0
        self.equipment = {
            "weapon": None,
            "armor": None,
            "boots": None
        }
        self.inventory = [
            {"name": "Mend-Extract", "type": "heal", "value": 50, "count": 2, "desc": "Restores 50 HP."},
            {"name": "Ether-Drop", "type": "mana", "value": 20, "count": 1, "desc": "Restores 20 MP."}
        ]

    def add_item(self, name, item_type, value, desc):
        for item in self.inventory:
            if item["name"] == name:
                item["count"] += 1
                return
        self.inventory.append({"name": name, "type": item_type, "value": value, "count": 1, "desc": desc})

    def use_item(self, item_name):
        for item in self.inventory:
            if item["name"] == item_name and item["count"] > 0:
                item["count"] -= 1
                if item["type"] == "heal":
                    self.heal(item["value"])
                    return True, f"You used {item['name']}. Restored {item['value']} HP."
                elif item["type"] == "mana":
                    self.mp = min(self.max_mp, self.mp + item["value"])
                    return True, f"You used {item['name']}. Restored {item['value']} MP."
        return False, "Item not found or depleted."

    def upgrade_skill(self, skill_id):
        # Find skill in learned skills
        for s in self.skills:
            if s.get("id") == skill_id:
                s["level"] = s.get("level", 1) + 1
                # Scaling logic: increase effectiveness or reduce cost
                if "cost" in s:
                    s["cost"] = max(5, int(s["cost"] * 0.9))
                return True, f"Skill {s['name']} upgraded to Level {s['level']}!"
        return False, "Skill not found."

    def level_up(self):
        if self.level >= 50:
            return False
            
        self.level += 1
        self.max_hp += 10 # Increased for better late game
        self.hp = self.max_hp
        self.base_atk += 4
        self.base_def += 3
        self.base_spd += 2
        self.luck += 1
        self.max_mp += 10
        self.mp = self.max_mp
        
        self.exp_to_next = int(self.exp_to_next * 1.25)
        
        if self.level in self.skill_data:
            new_skill = self.skill_data[self.level]
            self.skills.append(new_skill)
            return f"LEVEL UP! Reach Level {self.level}. New Skill: {new_skill['name']}!"
            
        return f"LEVEL UP! Reach Level {self.level}."

    def gain_exp(self, amount):
        self.exp += amount
        messages = []
        while self.exp >= self.exp_to_next and self.level < 50:
            self.exp -= self.exp_to_next
            msg = self.level_up()
            if msg:
                messages.append(msg)
        return messages

    def use_skill(self, skill_name):
        for s in self.skills:
            if s['name'] == skill_name:
                if self.mp >= s['cost']:
                    self.mp -= s['cost']
                    return True, s
                return False, "Insufficient Mana (MP)."
        return False, "Skill not mastered."

class Enemy(Entity):
    def __init__(self, name, hp, atk, def_stat, spd, luck, exp_reward, gold_reward=0, rank="F", is_boss=False):
        super().__init__(name, hp, hp, atk, def_stat, spd, luck)
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.rank = rank
        self.is_boss = is_boss
