import os
import time
import sys

# Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
BLUE = "\033[34m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

import select

def type_text(text, delay=0.01, color=WHITE):
    """Prints text with a typing effect. Pressing Enter skips the animation."""
    sys.stdout.write(color)
    skip = False
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        
        if not skip and delay > 0:
            # Check if Enter was pressed (non-blocking)
            # This works on Unix-like systems (Linux/macOS)
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline() # Consume the newline
                skip = True
            else:
                time.sleep(delay)
                
    sys.stdout.write(RESET + "\n")

def slow_print(text, delay=0.5, color=WHITE):
    """Prints text line by line with a delay."""
    print(color + text + RESET)
    time.sleep(delay)

def get_choice(options, prompt="Choose an option: "):
    """Handles user input for menu choices."""
    while True:
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        choice = input(f"\n{prompt}")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print(f"{RED}Invalid choice. Please try again.{RESET}")

def horizontal_line(char="-", length=50, color=WHITE):
    print(color + char * length + RESET)

def center_text(text, width=80):
    return text.center(width)
