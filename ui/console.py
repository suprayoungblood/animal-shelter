"""Console UI helpers: ANSI colors, banners, dividers, and validated prompts.

No external dependencies. All input is validated through small atomic helpers.
"""
import os
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

WIDTH = 60


def clear_screen() -> None:
    """Clear the terminal screen on any OS."""
    os.system("cls" if os.name == "nt" else "clear")


def divider(char: str = "-", color: str = DIM) -> None:
    """Print a horizontal divider line."""
    print(f"{color}{char * WIDTH}{RESET}")


def banner(text: str) -> None:
    """Print a centered bold banner inside a box."""
    divider("=", CYAN)
    print(f"{BOLD}{CYAN}{text.center(WIDTH)}{RESET}")
    divider("=", CYAN)


def title(text: str) -> None:
    """Print a section title."""
    print(f"\n{BOLD}{MAGENTA}>> {text}{RESET}")
    divider("-", DIM)


def info(text: str) -> None:
    """Print an informational message."""
    print(f"{BLUE}[i]{RESET} {text}")


def success(text: str) -> None:
    """Print a success message."""
    print(f"{GREEN}[✓]{RESET} {text}")


def error(text: str) -> None:
    """Print an error message."""
    print(f"{RED}[!]{RESET} {text}")


def pause(message: str = "Press Enter to continue...") -> None:
    """Wait for the user to press Enter."""
    input(f"{DIM}{message}{RESET}")


def _read_line(prompt: str) -> str:
    """Read one line from stdin with a styled prompt. Atomic helper."""
    sys.stdout.write(f"{YELLOW}? {prompt}{RESET} ")
    sys.stdout.flush()
    return input().strip()


def prompt_text(prompt: str, allow_empty: bool = False) -> str:
    """Prompt for non-empty text (or any text when allow_empty=True)."""
    while True:
        value = _read_line(prompt)
        if value or allow_empty:
            return value
        error("Value cannot be empty. Please try again.")


def prompt_int(prompt: str, minimum: int = 0, maximum: int = 100) -> int:
    """Prompt for a bounded integer."""
    while True:
        raw = _read_line(f"{prompt} ({minimum}-{maximum})")
        try:
            value = int(raw)
        except ValueError:
            error("Please enter a whole number.")
            continue
        if minimum <= value <= maximum:
            return value
        error(f"Number must be between {minimum} and {maximum}.")


def prompt_float(prompt: str, minimum: float = 0.0, maximum: float = 500.0) -> float:
    """Prompt for a bounded floating-point number."""
    while True:
        raw = _read_line(f"{prompt} ({minimum}-{maximum})")
        try:
            value = float(raw)
        except ValueError:
            error("Please enter a valid number.")
            continue
        if minimum <= value <= maximum:
            return value
        error(f"Number must be between {minimum} and {maximum}.")


def prompt_choice(prompt: str, choices: dict[str, str]) -> str:
    """Prompt for one of a set of labeled choices.

    :param prompt: Question shown above the choices.
    :param choices: Mapping of key -> human-readable label.
    :return: The selected key.
    """
    print(f"\n{BOLD}{prompt}{RESET}")
    for key, label in choices.items():
        print(f"  {CYAN}{key}{RESET}) {label}")
    valid_keys = set(choices.keys())
    while True:
        raw = _read_line("Select an option").lower()
        if raw in valid_keys:
            return raw
        error(f"Choose one of: {', '.join(sorted(valid_keys))}")
