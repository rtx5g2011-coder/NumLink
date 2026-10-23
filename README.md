<img width="1917" height="1078" alt="Screenshot 2026-10-23 172553" src="https://github.com/user-attachments/assets/3713381c-08a9-4020-b838-8c150b3b74b0" />
<img width="605" height="1280" alt="WhatsApp Image 2026-10-23 at 5 02 33 1 PM" src="https://github.com/user-attachments/assets/6a593b4d-191a-4f11-bb4b-5bbc378dca9f" />
# NumLink 🎮
A 3-Chance Number Guessing Game built with the Raspberry Pi Pico and MicroPython. 

NumLink is a pocket-sized arcade game where players must guess a hidden number between 0 and 9 using capacitive touch pads and a 7-segment display. The game features a custom sound engine, input debouncing, and a secret Easter egg system with non-volatile memory saving.

## ✨ Features
* **Capacitive Touch Controls:** Uses a custom "hold-to-confirm" software filter to debounce touch inputs for snappy, reliable gameplay without accidental double-taps.
* **Crisp Sound Engine:** Features a custom PWM staccato sound profile (80% tone, 20% hard cutoff) for clean UI clicks and multi-note melodies (Win, Lose, Start, Cheat).
* **Smart Display:** Uses a single 7-segment display to show the current guess, remaining lives, and Higher (`H`) / Lower (`L`) hints.
* **Secret Cheat Codes:** A sliding-window array constantly tracks the last 5 button presses to intercept the main game loop if a cheat code is entered.
* **Non-Volatile Memory (Edit Mode):** Players can record their own custom 5-pad cheat codes, which are written directly to `secret.txt` on the Pico's internal flash storage so they survive a reboot.

## 🛠️ Hardware Requirements
* **Microcontroller:** Raspberry Pi Pico
* **Display:** 1-Digit 10-Pin 7-Segment Display
* **Input:** 4-Pad Capacitive Touch Sensor (e.g., TTP224)
* **Audio:** Active Buzzer
* **Visual:** 1x Status LED (with resistor)

## 🎮 How to Play
The game randomly selects a secret number from 0 to 9. You have 3 chances to guess it.
* **Pad 1:** Increase Number
* **Pad 2:** Decrease Number
* **Pad 3:** Submit Guess
* **Pad 4:** Check Remaining Lives

If you guess wrong, the display will briefly flash `H` (Go Higher) or `L` (Go Lower) and blink the status LED to show your remaining lives.

## 🤫 Secret Codes
NumLink constantly tracks your last 5 inputs. Try entering these sequences during normal gameplay:
* **9-Lives Cheat:** `Pad 1, Pad 1, Pad 2, Pad 2, Pad 3` (Up, Up, Down, Down, Guess)
* **Revert to Normal:** `Pad 2, Pad 2, Pad 1, Pad 1, Pad 4`
* **Edit Mode:** `Pad 4, Pad 4, Pad 1, Pad 2` (Info, Info, Up, Down)

**Using Edit Mode:**
Once activated, the screen will flash `E`. Tap any 5 pads to record a brand-new cheat code sequence. The game will save this sequence to the Pico's flash storage, and it will become the new permanent code to trigger the 9-lives cheat!

## 🚀 Setup & Installation
1. Flash your Raspberry Pi Pico with the latest MicroPython firmware.
2. Open `main.py` in Thonny.
3. Wire the components according to the pin definitions in the code.
4. Save `main.py` directly to the Raspberry Pi Pico so the game runs automatically on boot.

---
*Built for Hack Club Forge. Next step: Designing a custom PCB!*


## 🛒 Bill of Materials (BOM)
| Component | Quantity | Description |
| :--- | :--- | :--- |
| Raspberry Pi Pico | 1 | Microcontroller |
| 7-Segment Display | 1 | 1-Digit, 10-pin Common Cathode |
| TTP224 Touch Module| 1 | 4-Pad Capacitive Touch Sensor |
| Active Buzzer | 1 | 5V Active Buzzer |
| LED | 1 | Standard 5mm LED |
| Resistor | 1 | 220 ohm (for Status LED) |
| Breadboard & Wires | 1 | Standard breadboard and jumper wires |

## 🔌 Wiring Diagram (Hand-Wired Prototype)
*Since this project is currently hand-wired on a breadboard, here is the exact pinout required to replicate it:*

| Pico Pin | Component Connection |
| :--- | :--- |
| **GP0** | Status LED (Positive leg) |
| **GP10** | Touch Pad 1 (Up) |
| **GP11** | Touch Pad 2 (Down) |
| **GP12** | Touch Pad 3 (Guess) |
| **GP13** | Touch Pad 4 (Info) |
| **GP15** | Active Buzzer (Positive leg) |
| **GP16 - GP22** | 7-Segment Display (A-G segments) |
| **GP26** | 7-Segment Display (DP/Dot) |
| **GND (Pin 38)** | All Component Grounds |
| **3V3 (Pin 36)** | Touch Sensor VCC Power |
