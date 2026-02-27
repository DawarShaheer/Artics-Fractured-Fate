import os
import time
import sys
import random

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    import termios
    import tty
    import select
    _WINDOWS = False

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

def move_up(n=1):
    """Moves the cursor up n lines."""
    if n > 0:
        sys.stdout.write(f"\033[{n}A")
        sys.stdout.flush()

def delete_lines(n=1):
    """Clears n lines above the current cursor position."""
    for _ in range(n):
        sys.stdout.write("\033[F") # Move up one line
        sys.stdout.write("\033[K") # Clear the line
    sys.stdout.flush()

def get_key():
    """Reads a single keypress without waiting for Enter."""
    if _WINDOWS:
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'): # Function/arrow keys
            ch = msvcrt.getch()
            if ch == b'H': return "up"
            if ch == b'P': return "down"
            if ch == b'K': return "left"
            if ch == b'M': return "right"
        ch = ch.decode('utf-8', errors='ignore').lower()
        if ch == '\r': return "enter"
        return ch
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b': # Escape sequence
                seq = sys.stdin.read(2)
                if seq == '[A': return "up"
                if seq == '[B': return "down"
                if seq == '[C': return "right"
                if seq == '[D': return "left"
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch == '\n' or ch == '\r': return "enter"
        return ch.lower()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, delay=0.01, color=WHITE):
    """Prints text with a typing effect. Pressing Enter skips the animation."""
    sys.stdout.write(color)
    skip = False
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        
        if not skip and delay > 0:
            if _WINDOWS:
                if msvcrt.kbhit():
                    # Check if the key pressed was Enter (13) or Space (32)
                    key = msvcrt.getch()
                    skip = True
            else:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline() # Consume the newline
                    skip = True
            
            if not skip:
                time.sleep(delay)
                
    sys.stdout.write(RESET + "\n")

def slow_print(text, delay=0.5, color=WHITE):
    """Prints text line by line with a delay."""
    print(color + text + RESET)
    time.sleep(delay)

def wait_any_key(prompt="\nPress any key to continue..."):
    """Pauses and waits for any keypress."""
    print(f"{prompt}", end="", flush=True)
    get_key()
    print() # Newline after press

def get_choice(options, prompt="Choose an option: "):
    """Handles user input with a highlighted selector."""
    selected = 0
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        while True:
            # Display menu
            print(f"\n{BOLD}{CYAN}{prompt}{RESET}")
            for i, option in enumerate(options):
                if i == selected:
                    print(f"{MAGENTA}  > {BOLD}{WHITE}{option}{RESET}")
                else:
                    print(f"    {WHITE}{option}{RESET}")
            
            key = get_key()
            
            if key in ('w', 'up'):
                selected = (selected - 1) % len(options)
            elif key in ('s', 'down'):
                selected = (selected + 1) % len(options)
            elif key == 'enter':
                # Show cursor before returning
                sys.stdout.write("\033[?25h")
                sys.stdout.flush()
                return selected + 1
            
            # Use ANSI to clear the menu lines for redraw
            # lines = prompt (1) + options + extra separator (1)
            sys.stdout.write(f"\033[{len(options) + 2}A\r")
            sys.stdout.flush()
    except Exception:
        # Emergency cursor restore
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        raise

def horizontal_line(char="-", length=50, color=WHITE):
    print(color + char * length + RESET)

def center_text(text, width=80):
    return text.center(width)
