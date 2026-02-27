from utils import type_text, get_choice, horizontal_line, RED, GREEN, YELLOW, CYAN, MAGENTA, BLUE, WHITE, BOLD, RESET, clear_screen
from wheel import Wheel
from models import Effect
import time
import random

class CombatManager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.wheel = Wheel()
        self.skip_enemy_turn = 0 # Counter for skipped turns
        self.reversal_active = False

    def start_combat(self):
        rank_color = YELLOW if self.enemy.rank in ["S", "A", "B"] else WHITE
        type_text(f"\n--- {RED}COMBAT INITIATED{RESET}: vs {BOLD}{self.enemy.name}{RESET} "
                  f"[{rank_color}Rank {self.enemy.rank}{RESET}] "
                  f"(Reward: {YELLOW}{self.enemy.exp_reward} EXP{RESET}) ---", color=RED)
        
        while self.player.is_alive() and self.enemy.is_alive():
            # Round Boundary: Trigger Start logic
            self.player.process_turn_start()
            self.enemy.process_turn_start()

            res = self.player_turn()
            if res == "escaped":
                return True # Escape is a 'success' in terms of not dying
            p_msgs = self.player.process_turn_end()
            for m in p_msgs: type_text(m, delay=0.01)
            
            if not self.enemy.is_alive(): break

            if self.skip_enemy_turn > 0:
                type_text(f"{self.enemy.name} is frozen in a fracture of time! ({self.skip_enemy_turn} turns remaining)", color=CYAN)
                self.skip_enemy_turn -= 1
            else:
                self.enemy_turn()
                e_msgs = self.enemy.process_turn_end()
                for m in e_msgs: type_text(m, delay=0.01)
            
            # Reversal only lasts one action cycle
            self.reversal_active = False
            time.sleep(0.5)

        if self.player.is_alive():
            type_text(f"{GREEN}Victory! {self.enemy.name} has been defeated.{RESET}")
            
            # Rewards
            self.player.gold += self.enemy.gold_reward
            type_text(f"Gained {YELLOW}{self.enemy.gold_reward} Gold{RESET}.")
            
            if self.enemy.is_boss:
                stones = random.randint(1, 2)
                self.player.skill_stones += stones
                type_text(f"The boss shattered... Gained {MAGENTA}{stones} Skill Stone(s){RESET}!", color=MAGENTA)

            upgrade_msgs = self.player.gain_exp(self.enemy.exp_reward)
            for msg in upgrade_msgs:
                type_text(f"{YELLOW}{BOLD}{msg}{RESET}")
            return True
        else:
            type_text(f"{RED}You have been unraveled... The Wheel stops turning.{RESET}")
            return False

    def player_turn(self):
        horizontal_line()
        p_status = self.player.get_status_str()
        e_status = self.enemy.get_status_str()
        
        # Calculate Dodge Chance
        dodge_chance = min(75, max(5, int((self.player.spd / self.enemy.spd) * 20)))
        
        print(f"{BOLD}{self.player.name}{RESET} [HP: {GREEN}{self.player.hp}/{self.player.max_hp}{RESET}] [MP: {CYAN}{self.player.mp}/{self.player.max_mp}{RESET}] [Dodge: {YELLOW}{dodge_chance}%{RESET}] {p_status}")
        print(f"{BOLD}{self.enemy.name}{RESET} [HP: {RED}{self.enemy.hp}/{self.enemy.max_hp}{RESET}] {e_status}")
        
        choices = ["Attack", "Spin the Wheel", "Use Skill", "Items", "Defend", "Retreat Safely"]
        choice = get_choice(choices, "Action: ")

        if choice == 1: # Attack
            dmg = self.enemy.take_damage(self.player.atk)
            type_text(f"You strike {self.enemy.name} for {RED}{dmg}{RESET} damage!")
        elif choice == 2: # Spin
            outcome = self.wheel.spin(self.player.luck, self.player.level)
            res, info = self.wheel.apply_outcome(self.player, self.enemy, outcome)
            type_text(res)
            type_text(info, color=CYAN)
            if outcome['id'] == "time":
                self.skip_enemy_turn = 2
            elif outcome['id'] == "reversal":
                self.reversal_active = True
        elif choice == 3: # Use Skill
            if not self.player.skills:
                type_text("No skills available yet.", color=RED)
                return self.player_turn()
            
            skill_names = [f"{s['name']} ({s['cost']} MP)" for s in self.player.skills] + ["Back"]
            s_idx = get_choice(skill_names, "Skill: ") - 1
            
            if s_idx == len(self.player.skills):
                return self.player_turn()
            
            skill = self.player.skills[s_idx]
            success, result = self.player.use_skill(skill['name'])
            if success:
                type_text(f"You evoke {MAGENTA}{skill['name']}{RESET}: {skill['desc']}")
                self.handle_skill_effect(skill)
            else:
                type_text(result, color=RED)
                return self.player_turn()
        elif choice == 4: # Items
            available_items = [i for i in self.player.inventory if i["count"] > 0]
            if not available_items:
                type_text("Your satchel is empty.", color=YELLOW)
                return self.player_turn()
            
            item_names = [f"{i['name']} x{i['count']} ({i['desc']})" for i in available_items] + ["Back"]
            i_idx = get_choice(item_names, "Use Item: ") - 1
            
            if i_idx == len(available_items):
                return self.player_turn()
            
            item = available_items[i_idx]
            success, msg = self.player.use_item(item["name"])
            if success:
                type_text(msg, color=GREEN)
            else:
                type_text(msg, color=RED)
                return self.player_turn()
        elif choice == 6: # Retreat
            type_text("You find a gap in the enemy's stance and withdraw swiftly.", color=CYAN)
            return "escaped"
        else:
            return self.player_turn()

    def handle_skill_effect(self, skill):
        name = skill['name']
        if name == "Echo Step":
            self.player.add_effect(Effect("Echo Step", 3, spd_mod=self.player.base_spd, color=CYAN))
        elif name == "Fate Guard":
            self.player.add_effect(Effect("Fate Guard", 2, def_mod=self.player.base_def, color=BLUE))
        elif name == "Time Split":
            self.skip_enemy_turn = 2
        elif name == "Light Arc":
            dmg = self.enemy.take_damage(self.player.atk * 3) # Burst damage
            type_text(f"A horizontal arc of hope sears {self.enemy.name} for {RED}{dmg}{RESET} damage!")
        elif name == "Final Mercy":
            dmg = self.enemy.take_damage(self.player.atk * 5)
            type_text(f"Final Mercy struck for {RED}{dmg}{RESET} damage.")

    def enemy_turn(self):
        type_text(f"\n{self.enemy.name}'s turn...")
        time.sleep(0.5)
        
        # Dodge logic
        dodge_chance = min(75, max(5, int((self.player.spd / self.enemy.spd) * 20)))
        if random.randint(1, 100) <= dodge_chance:
            type_text(f"{CYAN}{BOLD}DODGED!{RESET} You nimbly avoid {self.enemy.name}'s attack!", color=CYAN)
            return

        # Enemy Attack logic
        dmg_taken = self.player.take_damage(self.enemy.atk)
        type_text(f"{self.enemy.name} attacks for {RED}{dmg_taken}{RESET} damage!")
        
        if self.reversal_active:
            reversal_dmg = int(dmg_taken * 0.5)
            # Reversal damage ignores some defense as it's reflected power
            actual_reversal = self.enemy.take_damage(reversal_dmg + self.enemy.def_stat)
            type_text(f"{CYAN}Fate Reversal! {self.enemy.name} is struck by their own power for {RED}{actual_reversal}{RESET} damage!{RESET}")
