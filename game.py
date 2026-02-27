import random
from utils import type_text, slow_print, get_choice, horizontal_line, clear_screen, center_text, WHITE, CYAN, YELLOW, RED, GREEN, MAGENTA, BLUE, BOLD, RESET
from models import Player, Enemy
from combat import CombatManager
from story import get_story_data
from persistence import save_game, load_game

class Game:
    def __init__(self):
        self.player = None
        self.story = get_story_data()
        self.current_chapter = 1
        self.current_scene_id = "start"

    def start_new_game(self, name):
        self.player = Player(name)
        self.current_chapter = 1
        self.current_scene_id = "start"
        self.run_game()

    def load_existing_game(self, name):
        result = load_game(Player, name)
        if result:
            self.player, self.current_chapter = result
            self.current_scene_id = "start" # Simplification: restart chapter
            self.run_game()
            return True
        else:
            type_text("No save file found.", color=RED)
            input("\nPress Enter to return to menu...")
            return False

    def run_game(self):
        while self.current_chapter in self.story:
            chapter = self.story[self.current_chapter]
            clear_screen()
            # Level recommendation check
            recommended_levels = {1: 1, 2: 3, 3: 5, 4: 15, 5: 35}
            min_level = recommended_levels.get(self.current_chapter, 1)
            
            if self.player.level < min_level:
                type_text(f"{YELLOW}WARNING: This chapter is recommended for Level {min_level}+. You are Level {self.player.level}.{RESET}")
                type_text("The distortions here may be too great for your current resolve.", color=YELLOW)
                input("\nPress Enter to proceed anyway...")

            result = self.play_chapter(chapter)
            if result == "exit_to_menu":
                return # Back to main.py loop
            
            # Progress to next chapter
            self.current_chapter += 1
            self.current_scene_id = "start"
            save_game(self.player, self.current_chapter)
            type_text(f"\n{GREEN}Progress automatically saved.{RESET}")
            
            # Enter Ethereal Camp between chapters (if not at ending)
            if self.current_chapter in self.story:
                res = self.play_camp()
                if res == "exit_to_menu":
                    return
            else:
                input("\nPress Enter to continue your journey...")

        self.ending()

    def play_camp(self):
        while True:
            clear_screen()
            type_text(center_text("--- THE ETHEREAL CAMP ---"), color=CYAN)
            type_text("The rift is quiet here. The air is filled with the soft hum of the Wheel, "
                      "providing a temporary sanctuary between the fragments of existence.", color=WHITE)
            
            # Stats Display
            print(f"\n{BOLD}{self.player.name}{RESET} | LV: {self.player.level} | HP: {GREEN}{self.player.hp}/{self.player.max_hp}{RESET} | MP: {CYAN}{self.player.mp}/{self.player.max_mp}{RESET}")
            print(f"EXP: {YELLOW}{self.player.exp}/{self.player.exp_to_next}{RESET} | GOLD: {YELLOW}{self.player.gold}G{RESET} | STONES: {MAGENTA}{self.player.skill_stones}{RESET}")
            horizontal_line()
            
            choices = ["Rest (Restore HP/MP)", "Meditate (Brotherhood)", "Memory Gates (Farming)", "Ethereal Shop", "Alchemy Booth", "Status, Skills & Bag", "Save & Exit to Menu", "Break Camp & Proceed"]
            choice = get_choice(choices, "Camp Action: ")
            
            if choice == 1:
                self.player.hp = self.player.max_hp
                self.player.mp = self.player.max_mp
                type_text("You drift into a dreamless sleep. Your vitalities are restored.", color=GREEN)
                input("\nPress Enter...")
            elif choice == 2:
                self.player.brotherhood_score += 1
                type_text("You sit in silence, mending the frayed threads of your shared past. Brotherhood increased.", color=YELLOW)
                input("\nPress Enter...")
            elif choice == 3:
                self.enter_gate_system()
            elif choice == 4:
                self.play_shop()
            elif choice == 5:
                self.play_alchemy()
            elif choice == 6:
                self.view_status_and_skills()
            elif choice == 7:
                save_game(self.player, self.current_chapter)
                type_text("Progress saved. Returning to rift currents...", color=CYAN)
                return "exit_to_menu"
            else:
                type_text("You pack your resolve. The path ahead awaits.", color=CYAN)
                input("\nPress Enter...")
                break

    def play_shop(self):
        while True:
            clear_screen()
            type_text("--- ETHEREAL SHOP ---", color=YELLOW)
            print(f"Your Gold: {YELLOW}{self.player.gold}G{RESET}\n")
            
            items = [
                {"name": "Mend-Extract", "price": 20, "type": "heal", "val": 50, "desc": "Restores 50 HP."},
                {"name": "Mend-Greater", "price": 60, "type": "heal", "val": 150, "desc": "Restores 150 HP."},
                {"name": "Ether-Drop", "price": 30, "type": "mana", "val": 20, "desc": "Restores 20 MP."},
                {"name": "Ether-Pure", "price": 100, "type": "mana", "val": 60, "desc": "Restores 60 MP."},
                {"name": "Silver Edge", "price": 200, "type": "weapon", "val": 10, "desc": "Wep: +10 ATK"},
                {"name": "Solar Flare", "price": 800, "type": "weapon", "val": 30, "desc": "Wep: +30 ATK (High Tier)"},
                {"name": "Amber Vest", "price": 150, "type": "armor", "val": 5, "desc": "Arm: +5 DEF"},
                {"name": "Obsidian Aegis", "price": 600, "type": "armor", "val": 20, "desc": "Arm: +20 DEF (High Tier)"},
                {"name": "Phase Boots", "price": 180, "type": "boots", "val": 5, "desc": "Boot: +5 SPD"},
                {"name": "Starlight Treads", "price": 500, "type": "boots", "val": 15, "desc": "Boot: +15 SPD (High Tier)"}
            ]
            
            shop_list = [f"{i['name']} ({i['price']}G) - {i['desc']}" for i in items] + ["Back"]
            choice = get_choice(shop_list, "Select an item: ") - 1
            
            if choice == len(items): break
            
            item = items[choice]
            if self.player.gold >= item["price"]:
                self.player.gold -= item["price"]
                if item["type"] in ["heal", "mana"]:
                    self.player.add_item(item["name"], item["type"], item["val"], item["desc"])
                    type_text(f"Purchased {item['name']}!", color=GREEN)
                else: # Equipment
                    slot = item["type"]
                    bonus_key = "atk_bonus" if slot == "weapon" else "def_bonus" if slot == "armor" else "spd_bonus"
                    self.player.equipment[slot] = {"name": item["name"], bonus_key: item["val"]}
                    type_text(f"Equipped {item['name']}! Your stats surged.", color=GREEN)
            else:
                type_text("Not enough gold.", color=RED)
            input("\nPress Enter...")

    def play_alchemy(self):
        while True:
            clear_screen()
            type_text("--- ALCHEMY BOOTH ---", color=MAGENTA)
            print(f"Skill Stones: {MAGENTA}{self.player.skill_stones}{RESET}\n")
            
            options = ["Transmute (5 Stones) - Unlock New Skill", "Empower (3 Stones) - Level Up Skill", "Back"]
            choice = get_choice(options, "Action: ")
            
            if choice == 1: # Unlock
                # Find the next locked skill from skill_data
                potential_skills = []
                learned_ids = [s.get("id") for s in self.player.skills]
                for lv, sdata in self.player.skill_data.items():
                    if sdata["id"] not in learned_ids:
                        potential_skills.append(sdata)
                
                if not potential_skills:
                    type_text("You have mastered all currently known resonance.", color=CYAN)
                elif self.player.skill_stones >= 5:
                    self.player.skill_stones -= 5
                    new_skill = potential_skills[0] # Unlock the lowest level one
                    self.player.skills.append(new_skill)
                    type_text(f"The stone shatters into light... Learned {BOLD}{new_skill['name']}{RESET}!", color=GREEN)
                else:
                    type_text("Requires 5 Skill Stones.", color=RED)
            elif choice == 2: # Upgrade
                if not self.player.skills:
                    type_text("No skills to empower.", color=RED)
                elif self.player.skill_stones >= 3:
                    s_list = [f"{s['name']} (Lv {s.get('level', 1)})" for s in self.player.skills] + ["Back"]
                    s_choice = get_choice(s_list, "Empower which skill? ") - 1
                    if s_choice < len(self.player.skills):
                        self.player.skill_stones -= 3
                        skill = self.player.skills[s_choice]
                        success, msg = self.player.upgrade_skill(skill.get("id"))
                        type_text(msg, color=GREEN)
                else:
                    type_text("Requires 3 Skill Stones.", color=RED)
            else:
                break
            input("\nPress Enter...")

    def enter_gate_system(self):
        clear_screen()
        type_text("--- THE MEMORY GATES ---", color=BLUE)
        type_text("The rift here is organized into stable frequencies. "
                  "Choose a rank to challenge. Be warned: exhaustion carries over.", color=WHITE)
        
        ranks = ["F (Lv 1-10)", "E (Lv 11-20)", "D (Lv 21-30)", "C (Lv 31-40)", "B (Lv 41-50)", "Back"]
        rank_idx = get_choice(ranks, "Select Gate Rank: ") - 1
        
        if rank_idx == 5: return
        
        rank_letter = ["F", "E", "D", "C", "B"][rank_idx]
        wave = 1
        
        while True:
            clear_screen()
            print(f"{BLUE}--- Rank {rank_letter} Gate | Wave {wave} ---{RESET}")
            
            is_boss_wave = (wave % 5 == 0)
            enemy = self.generate_gate_enemy(rank_letter, is_boss_wave, wave)
            
            if is_boss_wave:
                type_text(f"A massive presence looms... {RED}{enemy.name} (BOSS){RESET} emerges!", color=RED)
            else:
                type_text(f"A {enemy.name} materializes from the mist.")
                
            combat = CombatManager(self.player, enemy)
            success = combat.start_combat()
            
            if not success:
                res = self.handle_game_over()
                if res == "retry":
                    continue # Re-try this wave
                else:
                    return # Exit Gate
            
            # Post-battle choices
            print(f"\n{GREEN}Wave {wave} Cleared!{RESET}")
            choices = ["Ventrue Deeper (Next Wave)", "Return to Camp"]
            if get_choice(choices) == 2:
                type_text("You withdraw from the Gate, breath ragged but spirit intact.", color=CYAN)
                input("\nPress Enter...")
                break
            
            wave += 1

    def generate_gate_enemy(self, rank, is_boss, wave):
        # Base rank multipliers
        rank_mult = {"F": 1, "E": 2, "D": 4, "C": 7, "B": 12}
        m = rank_mult.get(rank, 1)
        
        # Wave scaling: +10% stats per wave within the rank
        w_m = 1 + (wave - 1) * 0.1
        final_m = m * w_m
        
        if is_boss:
            boss_names = {
                "F": "The Mournful Sentinel",
                "E": "Echo of the First Burn",
                "D": "Shard of the Fallen Star",
                "C": "Calamity of the Rift",
                "B": "Nihilus, the Unraveler"
            }
            name = boss_names.get(rank, f"Guardian of {rank}")
            return Enemy(name, 200*final_m, 25*final_m, 15*final_m, 20*final_m, 15, 500*m, 100*m, rank, is_boss=True)
        else:
            monster_pools = {
                "F": ["Mist Stalker", "Grave-Walker", "Hollow Spirit", "Shard-Bug"],
                "E": ["Refracted Hound", "Ash-Wraith", "Void-Skitter", "Bone-Scribe"],
                "D": ["Chrono-Leech", "Obsidian Thrall", "Static-Remnant", "Glass-Gargoyle"],
                "C": ["Rift-Slayer", "Temporal Stalker", "Soul-Eater", "Ether-Goliath"],
                "B": ["Void-Reaper", "Cosmic Sentinel", "Fate-Eater", "Unraveling Terror"]
            }
            names = monster_pools.get(rank, ["Rift Echo"])
            name = random.choice(names)
            return Enemy(name, 80*final_m, 12*final_m, 5*final_m, 12*final_m, 5, 100*m, 20*m, rank)

    def view_status_and_skills(self):
        while True:
            clear_screen()
            type_text(center_text(f"--- {BOLD}{self.player.name}'S RESONANCE ---"), color=YELLOW)
            print(f"\n{BOLD}Attributes:{RESET}")
            print(f"LV: {self.player.level} | HP: {GREEN}{self.player.hp}/{self.player.max_hp}{RESET} | MP: {CYAN}{self.player.mp}/{self.player.max_mp}{RESET} | LUCK: {self.player.luck}")
            print(f"ATK: {RED}{self.player.atk}{RESET} | DEF: {BLUE}{self.player.def_stat}{RESET} | SPD: {CYAN}{self.player.spd}{RESET}")
            
            print(f"\n{BOLD}Equipment:{RESET}")
            for slot, item in self.player.equipment.items():
                name = item['name'] if item else "None"
                print(f"{slot.capitalize()}: {name}")

            print(f"\n{BOLD}Learned Skills:{RESET}")
            if not self.player.skills:
                print("None.")
            else:
                for s in self.player.skills:
                    lv = s.get('level', 1)
                    print(f"- {MAGENTA}{s['name']}{RESET} (Lv {lv}): {s['desc']} [{s['cost']} MP]")

            print(f"\n{BOLD}Satchel Inventory:{RESET}")
            if not self.player.inventory:
                print("Empty.")
            else:
                for i in self.player.inventory:
                    if i["count"] > 0:
                        print(f"- {i['name']} x{i['count']}: {i['desc']}")
            
            print(f"\n1. Back")
            if get_choice(["Back"]) == 1:
                break

    def handle_game_over(self):
        clear_screen()
        type_text(center_text("--- FATE UNRAVELED ---"), color=RED)
        type_text("\nYour thread has been cut. The Wheel stops, and the world begins to fade into the violet mist.", color=WHITE)
        
        # Reset State on Game Over
        self.player.clear_effects()
        
        choices = ["Retry Chapter (Full Heal)", "Go to Ethereal Camp (Train/Heal)", "Save & Exit to Main Menu"]
        choice = get_choice(choices, "Choose your resolution: ")
        
        if choice == 1:
            self.player.hp = self.player.max_hp
            self.player.mp = self.player.max_mp
            return "retry"
        elif choice == 2:
            res = self.play_camp()
            if res == "exit_to_menu":
                return "exit_to_menu"
            return "retry"
        else:
            save_game(self.player, self.current_chapter)
            return "exit_to_menu"

    def play_chapter(self, chapter):
        while self.current_scene_id in chapter.scenes:
            scene = chapter.scenes[self.current_scene_id]
            clear_screen()
            
            # Stats header
            stats = f"{BOLD}{self.player.name}{RESET} | LV: {self.player.level} | HP: {GREEN}{self.player.hp}/{self.player.max_hp}{RESET} | MP: {CYAN}{self.player.mp}/{self.player.max_mp}{RESET} | EXP: {YELLOW}{self.player.exp}/{self.player.exp_to_next}{RESET} | BROTHERHOOD: {YELLOW}{self.player.brotherhood_score}{RESET}"
            print(stats)
            horizontal_line()
            
            type_text(scene.description, delay=0.02)
            
            if scene.enemy:
                combat = CombatManager(self.player, scene.enemy)
                success = combat.start_combat()
                if not success:
                    res = self.handle_game_over()
                    if res == "retry":
                        self.current_scene_id = "start" # Reset chapter progress
                        # Reset Enemy HP for retry
                        scene.enemy.hp = scene.enemy.max_hp
                        scene.enemy.clear_effects()
                        return self.play_chapter(chapter)
                    else:
                        return "exit_to_menu"
            
            if scene.narrative_after:
                type_text(f"\n{scene.narrative_after}")
                input("\nPress Enter to proceed...")

            if scene.choices:
                choice_texts = [c["text"] for c in scene.choices]
                idx = get_choice(choice_texts) - 1
                selected_choice = scene.choices[idx]
                
                # Update scores
                self.player.brotherhood_score += selected_choice.get("brotherhood", 0)
                
                if "next_scene" in selected_choice:
                    self.current_scene_id = selected_choice["next_scene"]
                    
                    # If the next scene is "start", it's a loop (farming)
                    if self.current_scene_id == "start":
                        type_text("\nYou take a moment to breathe. The world remains fractured, but your resolve hardens.", color=CYAN)
                        # Reset all enemies in the chapter for farming
                        for s in chapter.scenes.values():
                            if s.enemy:
                                s.enemy.hp = s.enemy.max_hp
                                s.enemy.clear_effects()
                        input("\nPress Enter...")
                        continue # Restart chapter loop
                    
                    # Handle mid-chapter camp access
                    if self.current_scene_id == "camp":
                        res = self.play_camp()
                        if res == "exit_to_menu":
                            return "exit_to_menu"
                        # After camp, return to the previous scene or a specific return point
                        self.current_scene_id = selected_choice.get("return_scene", "start")
                        continue
                    
                    continue # Go to next scene
                else:
                    break # Chapter end
            else:
                break # No choices list means end of chapter logic

    def ending(self):
        clear_screen()
        type_text("The threshold of existence has been reached...", color=MAGENTA, delay=0.03)
        time.sleep(1)
        
        score = self.player.brotherhood_score
        
        # Branching Endings
        if score >= 20: # TRUE REDEMPTION
            type_text(BOLD + GREEN + "ENDING 1: THE RETURN OF BROTHERS" + RESET, delay=0.04)
            type_text("Darius falls not by your sword, but by the weight of his own realization. "
                      "He reaches out, a trembling hand grasping yours as the violet flame dies. "
                      "'We return...' he whispers, his voice finally clear. 'Not as warriors... but as brothers.'")
            type_text("You raise the Feather one last time. Its light does not burn; it heals. "
                      "The sky mends, but the price is paid. You both drift into the eternal amber-grass, finally at peace.")
        elif score >= 10: # TRAGIC VICTORY
            type_text(BOLD + YELLOW + "ENDING 2: THE ASHES OF VICTORY" + RESET, delay=0.04)
            type_text("You strike the final blow. Darius collapses, his eyes filled with a grief that never found a home. "
                      "The world is saved, the rift closed. But as you stand alone in the restored valley, "
                      "the silence is louder than any distortion. The world was saved... but something within it was forever lost.")
        elif score < 5: # DESPAIR
            type_text(BOLD + RED + "ENDING 3: THE END OF ALL THINGS" + RESET, delay=0.04)
            type_text("Darius laughs as the Feather shatters in his grip. Reality is no longer a suggestion; it is a memory. "
                      "The void consumes Kael, consumes the Arctis name, consumes the very concept of time. "
                      "And thus... fate broke... with no one left to mend it.")
        else: # KAEL'S SACRIFICE ALONE
            type_text(BOLD + CYAN + "ENDING 4: THE LONELY ANCHOR" + RESET, delay=0.04)
            type_text("Darius dies corrupted, a hollow shell of the boy you knew. You use the Feather alone. "
                      "The world is mended, but you are not there to see it. You vanish into the source, "
                      "leaving behind a world that will never know the name of the man who saved it.")
        
        type_text("\n" + YELLOW + center_text("KAEL ARCTIS: THE UNRAVELING - THE END") + RESET, delay=0.05)
