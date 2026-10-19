import serial
import serial.tools.list_ports
import time
import json
import os
import sys
from collections import deque
from pynput.keyboard import Controller, Key, KeyCode

# ---------------------------------------------------------------
# Config file setup
# ---------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "port": "COM6",
    "baud_rate": 115200,
    "controller_type": "wasd"
}

def normalize_port(value):
    if value is None:
        return value
    s = str(value).strip().upper()
    if not s:
        return s
    if s.isdigit():
        return f"COM{s}"
    if s.startswith("COM") and s[3:].isdigit():
        return s
    return s

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        print(f"  [config] Created new {CONFIG_FILE} with defaults.")
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        original_port = cfg.get("port")
        cfg["port"] = normalize_port(original_port)
        if cfg["port"] != original_port:
            print(f"  [config] Normalized port '{original_port}' → '{cfg['port']}'")
            save_config(cfg)
        return cfg
    except Exception as e:
        print(f"  [config] Failed to read config ({e}). Using defaults.")
        return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"  [config] Failed to save: {e}")

# ---------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
GRAY = "\033[90m"

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_LINE = "\033[2K"
CURSOR_UP = "\033[1A"
CURSOR_DOWN = "\033[1B"

def gradient_multiline(lines, start=(255, 80, 0), end=(0, 180, 255)):
    total = sum(len(l) for l in lines) or 1
    idx = 0
    out = []
    for line in lines:
        colored = []
        for ch in line:
            t = idx / max(total - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * t)
            g = int(start[1] + (end[1] - start[1]) * t)
            b = int(start[2] + (end[2] - start[2]) * t)
            colored.append(f"\033[38;2;{r};{g};{b}m{ch}")
            idx += 1
        out.append("".join(colored) + RESET)
    return "\n".join(out)

def gradient_text(text, start=(255, 200, 0), end=(0, 255, 180)):
    n = max(len(text) - 1, 1)
    out = []
    for i, ch in enumerate(text):
        t = i / n
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        out.append(f"\033[38;2;{r};{g};{b}m{ch}")
    return "".join(out) + RESET

BANNER = [
    "  ██████╗ ███████╗██╗   ██╗    ███████╗██╗  ██╗███████╗██╗  ██╗ █████╗ ███╗   ██╗",
    "  ██╔══██╗██╔════╝██║   ██║    ██╔════╝██║  ██║██╔════╝██║  ██║██╔══██╗████╗  ██║",
    "  ██║  ██║█████╗  ██║   ██║    ███████╗███████║█████╗  ███████║███████║██╔██╗ ██║",
    "  ██║  ██║██╔══╝  ╚██╗ ██╔╝    ╚════██║██╔══██║██╔══╝  ██╔══██║██╔══██║██║╚██╗██║",
    "  ██████╔╝███████╗ ╚████╔╝     ███████║██║  ██║███████╗██║  ██║██║  ██║██║ ╚████║",
    "  ╚═════╝ ╚══════╝  ╚═══╝      ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝",
    "                                                                                ",
    "              S I G N A L   T O W E R   v1.2",
]

def print_welcome():
    print()
    print(gradient_multiline(BANNER, start=(255, 60, 0), end=(0, 200, 255)))
    print()
    print(gradient_text("        >>>  Dev Shehan Signal Tower  <<<"))
    print()

# ---------------------------------------------------------------
# Interactive settings
# ---------------------------------------------------------------
def prompt_yes_no(question, default=False):
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        ans = input(question + suffix).strip().lower()
        if not ans:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Please answer y or n.")

def list_serial_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

def prompt_port(current_default):
    available = list_serial_ports()
    current_default = normalize_port(current_default)

    print()
    print(f"{BOLD}1. Select COM port{RESET}")
    if available:
        display = []
        for p in available:
            mark = "*" if p.upper() == str(current_default).upper() else ""
            display.append(f"{p}{mark}")
        print(f"   Available: ({', '.join(display)})")
    else:
        print(f"   {YELLOW}No serial ports detected.{RESET}")

    ans = input(f"   Enter port (default {current_default}): ").strip()
    if not ans:
        return str(current_default)

    port = normalize_port(ans)
    if available and port.upper() not in [p.upper() for p in available]:
        print(f"   {YELLOW}Warning: {port} not detected.{RESET}")
    return port

def prompt_baud(current_default):
    print()
    print(f"{BOLD}2. Select Baud Rate{RESET}")
    ans = input(f"   Baud rate (default {current_default}): ").strip()
    if not ans:
        return int(current_default)
    try:
        return int(ans)
    except ValueError:
        print(f"   {RED}Invalid number — keeping {current_default}.{RESET}")
        return int(current_default)

def prompt_controller(current_default):
    print()
    print(f"{BOLD}3. Select Controller Type{RESET}")
    print("   1. W A S D Controller")
    print("   2. Arrow Keys")
    cur_label = "1" if current_default == "wasd" else "2"
    ans = input(f"   Choose (1/2) (default {cur_label}): ").strip()
    if not ans:
        return current_default
    if ans == "1":
        return "wasd"
    if ans == "2":
        return "arrow"
    print(f"   {RED}Invalid choice — keeping {current_default}.{RESET}")
    return current_default

def run_setup(cfg):
    print(f"\n{BOLD}{CYAN}─── Update Configuration ───{RESET}")
    cfg["port"] = prompt_port(cfg["port"])
    cfg["baud_rate"] = prompt_baud(cfg["baud_rate"])
    cfg["controller_type"] = prompt_controller(cfg["controller_type"])
    save_config(cfg)
    print(f"\n{GREEN}✔ Configuration saved{RESET}")
    return cfg

# ---------------------------------------------------------------
# Docker-style live log (3 lines, banner stays)
# ---------------------------------------------------------------
class LiveLog:
    """
    Keeps a fixed-size tail of 'docker-style' log lines.
    Redraws in place under the banner — only the last N lines visible,
    older lines scroll up & disappear.
    """
    def __init__(self, max_lines=3):
        self.max_lines = max_lines
        self.lines = deque(maxlen=max_lines)
        self.drawn_once = False

    def _render(self):
        if not self.drawn_once:
            return ""
        # Move cursor up max_lines and clear them
        out = []
        for _ in range(self.max_lines):
            out.append(CURSOR_UP + CLEAR_LINE)
        return "".join(out)

    def log(self, message):
        self.lines.append(message)
        # Draw
        buf = [self._render()]
        for i in range(self.max_lines):
            if i < len(self.lines):
                buf.append(self.lines[i] + "\n")
            else:
                buf.append("\n")
        self.drawn_once = True
        sys.stdout.write("".join(buf))
        sys.stdout.flush()

    def stop(self):
        # ensure cursor visible again
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()

# ---------------------------------------------------------------
# Key mapping
# ---------------------------------------------------------------
def build_keymap(controller_type):
    if controller_type == "arrow":
        return {"R": Key.right, "F": Key.up, "L": Key.left, "B": Key.down}
    return {
        "R": KeyCode.from_char('d'),
        "F": KeyCode.from_char('w'),
        "L": KeyCode.from_char('a'),
        "B": KeyCode.from_char('s'),
    }

keyboard = Controller()
pressed_keys = set()

def update_keys(signal, keymap):
    global pressed_keys
    new_keys = set()
    if signal[0] == "0": new_keys.add(keymap["R"])
    if signal[1] == "0": new_keys.add(keymap["F"])
    if signal[2] == "0": new_keys.add(keymap["L"])
    if signal[3] == "0": new_keys.add(keymap["B"])

    for key in pressed_keys - new_keys:
        keyboard.release(key)
    for key in new_keys - pressed_keys:
        keyboard.press(key)
    pressed_keys = new_keys

def print_instructions(cfg):
    print(f"{BOLD}  ── Active Settings ────────────────────────────────{RESET}")
    print(f"   Port        : {CYAN}{cfg['port']}{RESET}")
    print(f"   Baud rate   : {CYAN}{cfg['baud_rate']}{RESET}")
    print(f"   Controller  : {CYAN}{cfg['controller_type'].upper()}{RESET}")
    print(f"{BOLD}  ── Log (last 3 signals) ───────────────────────────{RESET}")
    print()

# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    print_welcome()
    cfg = load_config()

    if prompt_yes_no(
        f"Update settings with start? (current: "
        f"{cfg['port']}, {cfg['baud_rate']}, {cfg['controller_type']})",
        default=False,
    ):
        cfg = run_setup(cfg)

    keymap = build_keymap(cfg["controller_type"])
    print_instructions(cfg)

    log = LiveLog(max_lines=3)
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        with serial.Serial(cfg["port"], cfg["baud_rate"], timeout=0.1) as ser:
            time.sleep(2)
            ser.reset_input_buffer()

            log.log(f"{GREEN}✔ RC Game Controller Ready on {cfg['port']}{RESET}")
            log.log(f"{GRAY}   Focus your game window now…{RESET}")

            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                bits = line.replace(",", "").replace(" ", "")

                if len(bits) == 4 and all(b in "01" for b in bits):
                    update_keys(bits, keymap)
                    active = "".join(
                        name for name, key in [
                            ('R', keymap["R"]),
                            ('F', keymap["F"]),
                            ('L', keymap["L"]),
                            ('B', keymap["B"]),
                        ] if key in pressed_keys
                    ) or "None"
                    log.log(f"  {CYAN}{bits}{RESET} | Active: {YELLOW}{active}{RESET}")

    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        print(f"\n  {YELLOW}Controller stopped.{RESET}")
    except Exception as e:
        sys.stdout.write(SHOW_CURSOR)
        print(f"\n  {RED}Error: {e}{RESET}")
    finally:
        for key in list(pressed_keys):
            keyboard.release(key)
        log.stop()

if __name__ == "__main__":
    main()