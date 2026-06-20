from datetime import datetime
from shutil import get_terminal_size
from threading import Lock
from colorama import init

init(autoreset=True)

print_lock = Lock()

PASTEL_PINK  = "\033[38;2;255;182;193m"  # For your messages (Main Highlight)
LAVENDER     = "\033[38;2;230;230;250m"  # For peer/other user messages
MINT         = "\033[38;2;162;210;255m"  # For status and success logs
BABY_BLUE    = "\033[38;2;173;216;230m"  # For banners and system logs
SOFT_GRAY    = "\033[38;2;180;180;180m"  # For the timestamp [HH:MM:SS]
SOFT_PEACH   = "\033[38;2;255;179;142m"  # For errors (a gentle "red" alternative)
RESET        = "\033[0m"


def now_stamp():
    return f"{SOFT_GRAY}[{datetime.now().strftime('%H:%M:%S')}]{RESET}"


def line(char="=", width=None):
    if width is None:
        width = get_terminal_size((80, 20)).columns
    return char * max(24, width)


def banner(title, subtitle=None):
    with print_lock:
        border = line("~")
        print(BABY_BLUE + border)
        print(BABY_BLUE + title.center(len(border)))
        if subtitle:
            print(LAVENDER + subtitle.center(len(border)))
        print(BABY_BLUE + border + RESET)


def status(message):
    with print_lock:
        print(f"{now_stamp()} {MINT}✦ {message}{RESET}")


def system(message):
    with print_lock:
        print(f"{now_stamp()} {BABY_BLUE}⚙ {message}{RESET}")


def peer_message(name, message):
    with print_lock:
        print(f"{now_stamp()} {LAVENDER}{name}: {message}{RESET}")


def your_message(message):
    with print_lock:
        width = get_terminal_size((80, 20)).columns
        stamp = f"[{datetime.now().strftime('%H:%M:%S')}]"
        padding = max(0, width - len(stamp) - 1 - len(message))
        print("\033[1A\033[2K", end="", flush=True)
        print(f"{' ' * padding}{SOFT_GRAY}{stamp}{RESET} \033[1m{PASTEL_PINK}{message}{RESET}")


def error(message):
    with print_lock:
        print(f"{now_stamp()} {SOFT_PEACH}⚠ {message}{RESET}")


def prompt_text(prompt):
    return f"{PASTEL_PINK}{prompt}{RESET} "