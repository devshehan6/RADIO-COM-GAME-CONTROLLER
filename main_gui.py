import serial
import serial.tools.list_ports
import time
import json
import os
import threading
import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pynput.keyboard import Controller, Key, KeyCode

# ---------------------------------------------------------------
# Theme
# ---------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT       = "#00e0b0"
ACCENT_HOVER = "#00c49a"
DANGER       = "#e74c3c"
DANGER_HOVER = "#ff6b5a"
WARN         = "#f39c12"
WARN_HOVER   = "#ffb732"
BG           = "#0f1116"
CARD         = "#161a22"
CARD_2       = "#1d2230"
FG           = "#e6e6e6"
MUTED        = "#8b93a7"
CYAN         = "#8be9fd"

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "port": "COM6",
    "baud_rate": 115200,
    "controller_type": "wasd",
    "game_path": "",
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
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        original = cfg.get("port")
        cfg["port"] = normalize_port(original)
        if cfg["port"] != original:
            save_config(cfg)
        return cfg
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print("save_config:", e)

def build_keymap(controller_type):
    if controller_type == "arrow":
        return {"R": Key.right, "F": Key.up, "L": Key.left, "B": Key.down}
    return {
        "R": KeyCode.from_char('d'),
        "F": KeyCode.from_char('w'),
        "L": KeyCode.from_char('a'),
        "B": KeyCode.from_char('s'),
    }

# ---------------------------------------------------------------
# App
# ---------------------------------------------------------------
class SignalTowerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dev Shehan • Signal Tower")
        self.geometry("980x740")
        self.minsize(860, 640)
        self.configure(fg_color=BG)

        self.cfg = load_config()
        self.keyboard = Controller()
        self.pressed_keys = set()
        self.serial_ser = None
        self.running = False
        self.reader_thread = None
        self.keymap = build_keymap(self.cfg.get("controller_type", "wasd"))

        self._build_ui()
        self._load_cfg_into_ui()
        self._refresh_ports(silent=True)

    # ---------- Banner ----------
    def _build_banner(self):
        self.banner_canvas = tk.Canvas(
            self, height=110, bg=BG, highlightthickness=0
        )
        self.banner_canvas.pack(fill="x", padx=20, pady=(18, 6))
        self.banner_canvas.bind("<Configure>", lambda e: self._draw_banner())
        self._draw_banner()

    def _draw_banner(self):
        c = self.banner_canvas
        c.delete("all")
        title = "DEV SHEHAN"
        sub   = "S I G N A L   T O W E R"
        ver   = "v2.0"
        start = (255, 60, 0)
        end   = (0, 200, 255)
        n = max(len(title) - 1, 1)

        # center the title
        w = c.winfo_width() or 900
        font_size = 32
        char_w = 22
        total_w = len(title) * char_w
        x = (w - total_w) // 2
        y = 20

        for i, ch in enumerate(title):
            t = i / n
            r = int(start[0] + (end[0] - start[0]) * t)
            g = int(start[1] + (end[1] - start[1]) * t)
            b = int(start[2] + (end[2] - start[2]) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            c.create_text(x, y, text=ch, fill=color,
                          font=("Consolas", font_size, "bold"), anchor="nw")
            x += char_w

        c.create_text(w // 2, y + 50, text=sub, fill=CYAN,
                      font=("Consolas", 11, "bold"), anchor="n")
        c.create_text(w - 30, y + 50, text=ver, fill=MUTED,
                      font=("Consolas", 9), anchor="ne")

    # ---------- UI ----------
    def _build_ui(self):
        self._build_banner()

        # ===== Config card =====
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            card, text="  ⚙  Configuration",
            font=("Consolas", 14, "bold"), text_color=CYAN, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 6))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 14))
        grid.grid_columnconfigure(1, weight=1)

        # --- Port row ---
        ctk.CTkLabel(grid, text="COM Port", width=110, anchor="w",
                     font=("Consolas", 12), text_color=FG
                     ).grid(row=0, column=0, padx=(0, 10), pady=6, sticky="w")
        self.port_var = tk.StringVar()
        self.port_combo = ctk.CTkComboBox(
            grid, variable=self.port_var, values=[],
            width=220, height=32, corner_radius=8,
            fg_color=CARD_2, border_color=CARD_2,
            button_color=CARD_2, button_hover_color="#2a3040",
            dropdown_fg_color=CARD_2, font=("Consolas", 12),
        )
        self.port_combo.grid(row=0, column=1, padx=(0, 8), pady=6, sticky="w")

        ctk.CTkButton(
            grid, text="⟳  Refresh", width=110, height=32, corner_radius=8,
            fg_color=CARD_2, hover_color="#2a3040",
            font=("Consolas", 12), command=self._refresh_ports,
        ).grid(row=0, column=2, padx=(0, 0), pady=6, sticky="w")

        # --- Baud row ---
        ctk.CTkLabel(grid, text="Baud Rate", width=110, anchor="w",
                     font=("Consolas", 12), text_color=FG
                     ).grid(row=1, column=0, padx=(0, 10), pady=6, sticky="w")
        self.baud_var = tk.StringVar()
        ctk.CTkComboBox(
            grid, variable=self.baud_var,
            values=["9600", "19200", "38400", "57600", "115200", "230400"],
            width=220, height=32, corner_radius=8,
            fg_color=CARD_2, border_color=CARD_2,
            button_color=CARD_2, button_hover_color="#2a3040",
            dropdown_fg_color=CARD_2, font=("Consolas", 12),
        ).grid(row=1, column=1, padx=(0, 8), pady=6, sticky="w")

        # --- Controller row ---
        ctk.CTkLabel(grid, text="Controller", width=110, anchor="w",
                     font=("Consolas", 12), text_color=FG
                     ).grid(row=2, column=0, padx=(0, 10), pady=6, sticky="w")

        ctrl_row = ctk.CTkFrame(grid, fg_color="transparent")
        ctrl_row.grid(row=2, column=1, columnspan=2, sticky="w", pady=6)

        self.ctrl_var = tk.StringVar(value="wasd")
        ctk.CTkRadioButton(
            ctrl_row, text="W A S D", variable=self.ctrl_var, value="wasd",
            font=("Consolas", 12), text_color=FG,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            radiobutton_width=16, radiobutton_height=16,
        ).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(
            ctrl_row, text="Arrow Keys", variable=self.ctrl_var, value="arrow",
            font=("Consolas", 12), text_color=FG,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            radiobutton_width=16, radiobutton_height=16,
        ).pack(side="left")

        # --- Game EXE row ---
        ctk.CTkLabel(grid, text="Game EXE", width=110, anchor="w",
                     font=("Consolas", 12), text_color=FG
                     ).grid(row=3, column=0, padx=(0, 10), pady=6, sticky="w")
        self.game_var = tk.StringVar()
        ctk.CTkEntry(
            grid, textvariable=self.game_var,
            height=32, corner_radius=8,
            fg_color=CARD_2, border_color=CARD_2,
            font=("Consolas", 11),
        ).grid(row=3, column=1, padx=(0, 8), pady=6, sticky="ew")
        ctk.CTkButton(
            grid, text="Browse…", width=110, height=32, corner_radius=8,
            fg_color=CARD_2, hover_color="#2a3040",
            font=("Consolas", 12), command=self._browse_game,
        ).grid(row=3, column=2, pady=6, sticky="w")

        # ===== Actions =====
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(6, 6))

        self.btn_start = ctk.CTkButton(
            actions, text="▶  Start Controller", width=190, height=42,
            corner_radius=10, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#0f1116", font=("Consolas", 13, "bold"),
            command=self.toggle_run,
        )
        self.btn_start.pack(side="left")

        ctk.CTkButton(
            actions, text="🎮  Run Game", width=160, height=42,
            corner_radius=10, fg_color=WARN, hover_color=WARN_HOVER,
            text_color="#0f1116", font=("Consolas", 13, "bold"),
            command=self.run_game,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            actions, text="💾  Save Config", width=160, height=42,
            corner_radius=10, fg_color=CARD_2, hover_color="#2a3040",
            text_color=FG, font=("Consolas", 13, "bold"),
            command=self.save_ui_cfg,
        ).pack(side="left")

        # Status dot + label
        status_frame = ctk.CTkFrame(actions, fg_color="transparent")
        status_frame.pack(side="right")
        self.status_dot = ctk.CTkLabel(
            status_frame, text="●", font=("Consolas", 20),
            text_color=MUTED, width=20,
        )
        self.status_dot.pack(side="left")
        self.status_var = tk.StringVar(value="Idle")
        ctk.CTkLabel(
            status_frame, textvariable=self.status_var,
            font=("Consolas", 12, "bold"), text_color=MUTED,
        ).pack(side="left", padx=(4, 8))

        # ===== Log card =====
        log_card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        log_card.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        header = ctk.CTkFrame(log_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            header, text="  ▤  Live Log",
            font=("Consolas", 14, "bold"), text_color=CYAN, anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            header, text="Clear", width=80, height=26, corner_radius=6,
            fg_color=CARD_2, hover_color="#2a3040",
            font=("Consolas", 11), command=self._clear_log,
        ).pack(side="right")

        log_wrap = ctk.CTkFrame(log_card, fg_color="#0b0d12", corner_radius=10)
        log_wrap.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        self.log_text = tk.Text(
            log_wrap, bg="#0b0d12", fg=FG, insertbackground=CYAN,
            relief="flat", font=("Consolas", 10), wrap="none",
            state="disabled", padx=10, pady=8,
            selectbackground="#2a3040", borderwidth=0,
        )
        sb = ctk.CTkScrollbar(log_wrap, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self.log_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        for tag, color in [
            ("info", CYAN), ("ok", "#50fa7b"), ("warn", "#f1fa8c"),
            ("err", "#ff5555"), ("sig", "#bd93f9"), ("muted", "#6272a4"),
        ]:
            self.log_text.tag_config(tag, foreground=color)

    # ---------- Config <-> UI ----------
    def _load_cfg_into_ui(self):
        self.port_var.set(self.cfg.get("port", "COM6"))
        self.baud_var.set(str(self.cfg.get("baud_rate", 115200)))
        self.ctrl_var.set(self.cfg.get("controller_type", "wasd"))
        self.game_var.set(self.cfg.get("game_path", ""))

    def _collect_ui_cfg(self):
        return {
            "port": normalize_port(self.port_var.get().strip()),
            "baud_rate": int(self.baud_var.get().strip() or 115200),
            "controller_type": self.ctrl_var.get(),
            "game_path": self.game_var.get().strip(),
        }

    def save_ui_cfg(self):
        try:
            self.cfg = self._collect_ui_cfg()
            save_config(self.cfg)
            self.log(f"Config saved → {os.path.basename(CONFIG_FILE)}", "ok")
        except Exception as e:
            self.log(f"Save failed: {e}", "err")

    def _refresh_ports(self, silent=False):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.configure(values=ports)
        if ports and self.port_var.get() not in ports:
            self.port_var.set(ports[0])
        if not silent:
            self.log(f"Detected ports: {', '.join(ports) if ports else 'none'}", "muted")

    def _browse_game(self):
        path = filedialog.askopenfilename(
            title="Select Game Executable",
            filetypes=[("Executables", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.game_var.set(path)
            self.cfg["game_path"] = path
            save_config(self.cfg)
            self.log(f"Game selected: {path}", "info")

    # ---------- Log ----------
    def log(self, msg, tag="info"):
        ts = time.strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{ts}] ", "muted")
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ---------- Controller ----------
    def toggle_run(self):
        if self.running:
            self.stop_controller()
        else:
            self.start_controller()

    def start_controller(self):
        if self.running:
            return
        try:
            self.cfg = self._collect_ui_cfg()
            save_config(self.cfg)

            self.serial_ser = serial.Serial(
                self.cfg["port"], self.cfg["baud_rate"], timeout=0.1
            )
            time.sleep(2)
            self.serial_ser.reset_input_buffer()

            self.keymap = build_keymap(self.cfg["controller_type"])
            self.running = True

            self.btn_start.configure(
                text="■  Stop Controller", fg_color=DANGER,
                hover_color=DANGER_HOVER,
            )
            self.status_dot.configure(text_color=ACCENT)
            self.status_var.set(f"Running on {self.cfg['port']}")

            self.log(f"Serial opened on {self.cfg['port']} @ {self.cfg['baud_rate']}", "ok")
            self.log(f"Controller: {self.cfg['controller_type'].upper()} — focus your game!", "info")

            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            self.log(f"Failed to start: {e}", "err")
            self.serial_ser = None
            self.running = False

    def stop_controller(self):
        self.running = False
        try:
            if self.serial_ser and self.serial_ser.is_open:
                self.serial_ser.close()
        except Exception:
            pass
        self.serial_ser = None

        for key in list(self.pressed_keys):
            try:
                self.keyboard.release(key)
            except Exception:
                pass
        self.pressed_keys.clear()

        self.btn_start.configure(
            text="▶  Start Controller", fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
        )
        self.status_dot.configure(text_color=MUTED)
        self.status_var.set("Idle")
        self.log("Controller stopped.", "warn")

    def _reader_loop(self):
        keymap = self.keymap
        while self.running and self.serial_ser:
            try:
                line = self.serial_ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                bits = line.replace(",", "").replace(" ", "")
                if len(bits) == 4 and all(b in "01" for b in bits):
                    self._update_keys(bits, keymap)
                    active = "".join(
                        name for name, key in [
                            ('R', keymap["R"]),
                            ('F', keymap["F"]),
                            ('L', keymap["L"]),
                            ('B', keymap["B"]),
                        ] if key in self.pressed_keys
                    ) or "None"
                    self.after(0, self.log, f"{bits}  |  Active: {active}", "sig")
            except Exception as e:
                if self.running:
                    self.after(0, self.log, f"Read error: {e}", "err")
                break

    def _update_keys(self, signal, keymap):
        new_keys = set()
        if signal[0] == "0": new_keys.add(keymap["R"])
        if signal[1] == "0": new_keys.add(keymap["F"])
        if signal[2] == "0": new_keys.add(keymap["L"])
        if signal[3] == "0": new_keys.add(keymap["B"])

        for key in self.pressed_keys - new_keys:
            try: self.keyboard.release(key)
            except Exception: pass
        for key in new_keys - self.pressed_keys:
            try: self.keyboard.press(key)
            except Exception: pass
        self.pressed_keys = new_keys

    # ---------- Run Game ----------
    def run_game(self):
        path = self.game_var.get().strip() or self.cfg.get("game_path", "")
        if not path:
            messagebox.showwarning("No Game", "Please select the game EXE first.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Not Found", f"Game not found:\n{path}")
            return
        try:
            subprocess.Popen([path], cwd=os.path.dirname(path))
            self.cfg["game_path"] = path
            save_config(self.cfg)
            self.log(f"Launched game: {path}", "ok")
        except Exception as e:
            self.log(f"Launch failed: {e}", "err")
            messagebox.showerror("Launch Error", str(e))

    # ---------- Close ----------
    def on_close(self):
        self.stop_controller()
        self.destroy()


if __name__ == "__main__":
    app = SignalTowerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()