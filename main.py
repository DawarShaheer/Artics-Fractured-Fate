from game import Game
from utils import clear_screen, type_text, get_choice, center_text, CYAN, YELLOW, RED, BOLD, RESET
from persistence import list_saves, delete_save

def main_menu():
    game = Game()
    
    while True:
        clear_screen()
        type_text(center_text("KAEL ARCTIS: THE UNRAVELING"), color=CYAN, delay=0.03)
        
        choices = ["New Game", "Load Game", "Delete Save", "Exit"]
        choice = get_choice(choices, "Main Menu Choice: ")
        
        if choice == 1:
            name = input("\nEnter your name: ").strip()
            if not name: name = "Kael"
            
            existing = list_saves()
            if name.capitalize() in [s.capitalize() for s in existing]:
                type_text(f"{YELLOW}A save file for '{name}' already exists.{RESET}")
                ov_choice = get_choice(["Overwrite & Start", "Back"], "Action: ")
                if ov_choice == 2: continue
            
            game.start_new_game(name)
        elif choice == 2:
            saves = list_saves()
            if not saves:
                type_text("No threads of destiny found... (No save files)", color=RED)
                input("\nPress Enter to return...")
                continue
            
            print(f"\n{BOLD}Select your Thread:{RESET}")
            s_choice = get_choice(saves + ["Back"], "Load Save: ")
            if s_choice <= len(saves):
                game.load_existing_game(saves[s_choice-1])
        elif choice == 3:
            saves = list_saves()
            if not saves:
                type_text("Nothing to erase.", color=RED)
                input("\nPress Enter to return...")
                continue
            
            print(f"\n{RED}Select Save to DELETE:{RESET}")
            d_choice = get_choice(saves + ["Back"], "Erase destiny: ")
            if d_choice <= len(saves):
                target = saves[d_choice-1]
                type_text(f"{RED}Are you sure you want to permanently erase '{target}'?{RESET}")
                confirm = get_choice(["Erase Forever", "Cancel"], "Confirm: ")
                if confirm == 1:
                    delete_save(target)
                    type_text(f"Thread '{target}' has been severed.", color=YELLOW)
                    input("\nPress Enter...")
        else:
            type_text("The Wheel awaits your return, Traveler.", color=CYAN)
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{CYAN}The Wheel awaits your return, Traveler.{RESET}")
