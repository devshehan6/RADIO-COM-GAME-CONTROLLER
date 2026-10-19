# 📡 Dev Shehan — Signal Tower

> **RC Signal Tower → PC Game Controller**
>
> A hybrid Arduino + Python project that turns an RC car receiver/transmitter pair into a fully working PC game controller. Point the RC controller at the tower, and the tower relays the input over USB serial to a Python GUI that presses real keyboard keys inside any game.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Hardware Requirements](#-hardware-requirements)
- [Wiring / Schematic](#-wiring--schematic)
- [Software Requirements](#-software-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [How to Use](#-how-to-use)
- [Serial Protocol](#-serial-protocol)
- [🎬 Media & Demos](#-media--demos)
- [Troubleshooting](#-troubleshooting)
- [Credits](#-credits)
- [License](#-license)

---

## 🧭 Overview

This project takes the **receiver (RX) of an RC car** and uses its 4 output channels as digital inputs into an Arduino board. The Arduino then:

1. **Reads** the 4 channel signals (A, B, C, D)
2. **Displays** them as filled/hollow balls on a 128×64 OLED
3. **Drives** a 4-bulb "signal tower" animation (like a real traffic tower)
4. **Streams** the 4-bit state to the PC over USB Serial (`115200` baud)

On the PC side, a **CustomTkinter GUI (Python)**:

- Reads the serial stream
- Maps the bits to keyboard keys (**WASD** or **Arrow keys**)
- Presses/releases them via `pynput`, so **any game** responds
- Can **launch the game EXE** directly
- Saves everything to a `config.json`

The result: **drive a PC game with an RC car controller.** 🎮🚗

---

## ⚙️ How It Works

```
 RC Controller ──2.4GHz──▶ RC Receiver ──▶ Arduino GPIO (A,B,C,D)
                                              │
                                              ├─▶ OLED (status UI)
                                              ├─▶ 4 Bulbs (tower animation)
                                              └─▶ USB Serial ──▶ Python GUI
                                                                     │
                                                                     ├─▶ pynput (W/A/S/D or arrows)
                                                                     └─▶ Game EXE
```

1. The RC transmitter sends stick/trigger input to the RC receiver.
2. The receiver's PWM outputs are read on Arduino pins **21, 20, 10, 9** (A, B, C, D).
3. Arduino serializes the 4 values as a 4-character `0/1` string every **50 ms**.
4. The Python GUI (`pynput`) simulates key presses — the focused game reacts instantly.
5. `1` state = **not pressed**, `0` state = **pressed** (inverted logic in the firmware).

---

## 📁 Project Structure

```
radioCom/
├── data/
│   ├── connectAndLoadGame.mp4     # Demo: connecting & loading the game
│   ├── diagram.drawio             # Editable circuit diagram (draw.io)
│   ├── playGame.mp4               # Demo: playing a game with the tower
│   ├── signelToverDiagram.png     # Circuit / schematic image
│   └── tower.mp4                  # Demo: tower effect & OLED
├── controller_gui.py              # Python CustomTkinter GUI (main app)
├── signal_tower.ino               # Arduino firmware
├── config.json                    # Auto-generated config (port, baud, keys)
└── README.md
```

> Rename your files as needed — the above mirrors the original `data/` directory listing.

---

## 🔌 Hardware Requirements

| Component | Qty | Notes |
|---|---|---|
| Arduino board (ESP32 / Uno / Nano) | 1 | Code uses pins 0–3 for bulbs, 21/20/10/9 for inputs — matches **ESP32** |
| SSD1306 OLED (128×64, I²C) | 1 | Address `0x3C` |
| 4× LED / bulb module | 1 | Driven with `analogWrite` (PWM) |
| RC car receiver (RX) | 1 | Outputs 4 channels |
| RC transmitter (TX) | 1 | The "remote" |
| Jumper wires + breadboard | — |  |
| USB cable | 1 | For serial to PC |

---

## 🗺️ Wiring / Schematic

**OLED (I²C)** — ESP32 pins:
| OLED | Arduino |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | **GPIO 8** |
| SCL | **GPIO 7** |

**Bulbs (PWM):** `GPIO 0, 1, 2, 3`

**RC Receiver → Arduino:**
| RC Channel | Arduino GPIO |
|---|---|
| A | **21** |
| B | **20** |
| C | **10** |
| D | **9** | 

### 📷 Circuit Diagram (Live Preview)

![Signal Tower Circuit Diagram](data/signelToverDiagram.png)

📥 **Downloads:**
- 🖼️ **Circuit image:** [`data/signelToverDiagram.png`](data/signelToverDiagram.png)
- ✏️ **Editable draw.io source:** [`data/diagram.drawio`](data/diagram.drawio) — [**Open in draw.io**](data/diagram.drawio)

> ⚠️ If you use a 3.3V Arduino (ESP32), connect the RC receiver signal pins directly. For 5V boards, use a **voltage divider** on the receiver signal lines.

---

## 💻 Software Requirements

### Python (PC side)
- Python **3.9+**
- Packages:
  ```bash
  pip install pyserial customtkinter pynput
  ```

### Arduino.
- **Arduino IDE** (or PlatformIO)
- Libraries (install via Library Manager):
  - `Adafruit GFX Library`
  - `Adafruit SSD1306`

---

## 🛠️ Installation

### 1. Flash the Arduino
1. Open `signal_tower.ino` in Arduino IDE.
2. Select your board (ESP32 Dev Module / Uno / etc.).
3. Install `Adafruit GFX` + `Adafruit SSD1306` if prompted.
4. Upload.

### 2. Set up the Python GUI
```bash
git clone https://github.com/devshehan6/RADIO-COM-GAME-CONTROLLER
cd radioCom
pip install pyserial customtkinter pynput
python controller_gui.py
```

### 3. Connect the hardware
- Plug the Arduino into your PC via USB.
- Power the RC receiver and pair it with the RC transmitter.
- Open the GUI → click **⟳ Refresh** to detect the COM port.

---

## ⚙️ Configuration

On first run, `config.json` is auto-generated in the same folder as `controller_gui.py`:

```json
{
  "port": "COM6",
  "baud_rate": 115200,
  "controller_type": "wasd",
  "game_path": ""
}
```

| Key | Description |
|---|---|
| `port` | Serial port (e.g. `COM6` on Windows, `/dev/ttyUSB0` on Linux). Numeric values like `"6"` are auto-normalized to `"COM6"`. |
| `baud_rate` | Must match Arduino (`115200`). |
| `controller_type` | `"wasd"` or `"arrow"` — maps bits to W/A/S/D or arrow keys. |
| `game_path` | Full path to a game `.exe` (optional; enables the **🎮 Run Game** button). |

> You can also edit these in the GUI and click **💾 Save Config**.

---

## 🎮 How to Use

1. **Launch** `controller_gui.py`.
2. **Select** the COM port and baud rate (default `115200`).
3. **Choose** controller type: **WASD** or **Arrow Keys**.
4. *(Optional)* **Browse** and pick a game `.exe` → enables one-click launch.
5. Click **▶ Start Controller**.
6. **Focus your game window** (click into it) — the GUI logs incoming signals.
7. Move the RC sticks → the game character moves.
8. Click **■ Stop Controller** to stop and release all keys.

**Status indicators**
- 🟢 Green dot = controller running
- ⚪ Grey dot = idle
- Live log shows the 4-bit signal + currently active keys

---

## 📡 Serial Protocol

Every **50 ms**, Arduino sends a single line:

```
<B><C><A><D>\n
```

Example:

| Serial | Active Keys (WASD mode) |
|---|---|
| `1111` | none |
| `0111` | **W** (forward) |
| `1011` | **A** (left) |
| `1101` | **D** (right) |
| `1110` | **S** (back) |
| `0000` | W + A + D + S (all) |

> **Logic:** `0` = key **pressed**, `1` = key **released**.
> The GUI replaces `,` and spaces, so `1,1,1,1` and `1111` are equivalent.

---

## 🎬 Media & Demos

### 🎥 Watch the Demos

| Demo | Preview / Play |
|---|---|
| **Tower Build & OLED** | [![Tower Demo](https://img.shields.io/badge/▶_Watch-tower.mp4-00e0b0?style=for-the-badge&logo=video)](https://github.com/devshehan6/radioCom/raw/main/data/tower.mp4) |
| **Connect & Load Game** | [![Connect Demo](https://img.shields.io/badge/▶_Watch-connectAndLoadGame.mp4-8be9fd?style=for-the-badge&logo=video)](https://github.com/devshehan6/radioCom/raw/main/data/connectAndLoadGame.mp4) |
| **Playing a Game** | [![Play Demo](https://img.shields.io/badge/▶_Watch-playGame.mp4-f39c12?style=for-the-badge&logo=video)](https://github.com/devshehan6/radioCom/raw/main/data/playGame.mp4) |

> **💡 Tip:** GitHub **cannot play `.mp4` files inline** inside a README. The buttons above open/download the video directly. To preview them inside the repo, simply **click the file** in the `data/` folder — GitHub will then show the built-in video player.

### 📁 Direct File Links

| File | Description | Link |
|---|---|---|
| `tower.mp4` | The physical tower build & OLED effect | [▶ Open](data/tower.mp4) |
| `connectAndLoadGame.mp4` | How to connect the tower and load a game | [▶ Open](data/connectAndLoadGame.mp4) |
| `playGame.mp4` | Playing a game using the signal tower | [▶ Open](data/playGame.mp4) |
| `signelToverDiagram.png` | Circuit diagram | [🖼 View](data/signelToverDiagram.png) |
| `diagram.drawio` | Editable draw.io schematic | [✏ Open in draw.io](data/diagram.drawio) |

### 🖼 Diagram Preview

![Signal Tower Diagram](data/signelToverDiagram.png)

---

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| **Port not detected** | Click **⟳ Refresh**. Check USB cable/drivers. On Linux use `/dev/ttyUSB0`. |
| **GUI shows `Read error`** | Wrong baud rate, or another program has the port open. Close Arduino Serial Monitor. |
| **Keys not working in game** | Make sure the **game window has focus**. Run the GUI as **Administrator** (Windows) — some games ignore simulated input otherwise. |
| **Stuck key** | Click **■ Stop Controller** — it releases all keys. |
| **OLED blank** | Verify SDA=8 / SCL=7 and address `0x3C`. Run an I²C scanner. |
| **Bulbs not animating** | Confirm bulbs on GPIO `0,1,2,3` and PWM-capable pins. |
| **Wrong direction mapping** | Swap keys by editing `build_keymap()` in the GUI, or change the bit order in Arduino's `Serial.print` block. |
| **Videos won't play** | GitHub README cannot stream `.mp4` inline. Open the file directly in the `data/` folder (click it on GitHub) — GitHub has a built-in player for that view. |

---

## 🏆 Credits

- **Project by:** [devshehan6](https://github.com/devshehan6)
- **GUI design:** CustomTkinter
- **Key injection:** [`pynput`](https://pypi.org/project/pynput/)
- **OLED:** Adafruit GFX + SSD1306 libraries
- **Inspiration:** RC car receivers reused as HID input devices

---

## 📜 License

This project is provided for **educational & hobbyist use**.
If you plan to redistribute, please keep the credits and add an `MIT` (or your preferred) license file.
