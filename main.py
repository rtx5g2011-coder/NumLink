import time
import random
from machine import Pin, PWM

# ==========================================
# 1. HARDWARE PIN SETUP
# ==========================================

# 7-Segment Display Pins:
segment_pins = [18, 19, 22, 21, 20, 17, 16]
segments = [Pin(pin, Pin.OUT) for pin in segment_pins]
dot = Pin(26, Pin.OUT)

# Status LED
status_led = Pin(0, Pin.OUT)

# Active Buzzer (on GP15)
buzzer = PWM(Pin(15))
buzzer.duty_u16(0) 

# 4-Pad Touch Sensor Module (Active HIGH with PULL_DOWN)
touch_up    = Pin(10, Pin.IN, Pin.PULL_DOWN) # Pad 1: Number Up
touch_down  = Pin(11, Pin.IN, Pin.PULL_DOWN) # Pad 2: Number Down
touch_guess = Pin(12, Pin.IN, Pin.PULL_DOWN) # Pad 3: Submit Guess
touch_info  = Pin(13, Pin.IN, Pin.PULL_DOWN) # Pad 4: Check Lives

# ==========================================
# 2. DISPLAY PATTERNS & MUSIC NOTES
# ==========================================

digits = {
    9: [1, 1, 1, 1, 0, 1, 1], 8: [1, 1, 1, 1, 1, 1, 1], 7: [1, 1, 1, 0, 0, 0, 0],
    6: [1, 0, 1, 1, 1, 1, 1], 5: [1, 0, 1, 1, 0, 1, 1], 4: [0, 1, 1, 0, 0, 1, 1],
    3: [1, 1, 1, 1, 0, 0, 1], 2: [1, 1, 0, 1, 1, 0, 1], 1: [0, 1, 1, 0, 0, 0, 0],
    0: [1, 1, 1, 1, 1, 1, 0]
}

letters = {
    'H':   [0, 1, 1, 0, 1, 1, 1], # Go Higher
    'L':   [0, 0, 0, 1, 1, 1, 0], # Go Lower
    'E':   [1, 0, 0, 1, 1, 1, 1], # End / Game Over
    'OFF': [0, 0, 0, 0, 0, 0, 0]  # Blank Screen
}

# Musical Note Frequencies (Hz)
NOTE_C4 = 261; NOTE_D4 = 294; NOTE_E4 = 330; NOTE_G4 = 392; NOTE_C5 = 523
NOTE_D5 = 587; NOTE_E5 = 659; NOTE_G5 = 784; NOTE_C6 = 1047
NOTE_G3 = 196; NOTE_F3 = 175; NOTE_E3 = 165

# Melodies stored as (Frequency, Total Duration)
MELODY_START = [(NOTE_C4, 0.15), (NOTE_E4, 0.15), (NOTE_G4, 0.2)]
MELODY_WIN   = [(NOTE_C4, 0.15), (NOTE_E4, 0.15), (NOTE_G4, 0.15), (NOTE_C5, 0.5)]
MELODY_LOSE  = [(NOTE_G3, 0.3), (NOTE_F3, 0.3), (NOTE_E3, 0.6)]
MELODY_CHEAT = [(NOTE_E4, 0.1), (NOTE_G4, 0.1), (NOTE_E5, 0.1), (NOTE_C6, 0.1), (NOTE_D5, 0.1), (NOTE_G5, 0.3)]
MELODY_REV   = [(NOTE_G5, 0.1), (NOTE_D5, 0.1), (NOTE_C5, 0.1), (NOTE_G4, 0.4)]

# ==========================================
# 3. SECRET CODES & INPUT TRACKING
# ==========================================

max_chances = 3
input_history = []
secret_code = [1, 1, 2, 2, 3]  # Up, Up, Down, Down, Guess (9 Lives)
reverse_code = [2, 2, 1, 1, 4] # Down, Down, Up, Up, Info (3 Lives)
edit_code = [1, 2, 2, 2]       # Info, Info, Up, Down (Edit Mode)

def check_secret_codes(pad_pressed):
    global max_chances, input_history, secret_code
    
    input_history.append(pad_pressed)
    if len(input_history) > 5:
        input_history.pop(0) 
        
    if input_history == secret_code:
        print("\n>>> SECRET CODE ACTIVATED!")
        input_history.clear()
        max_chances = 9
        play_melody(MELODY_CHEAT)
        start_new_game()
        return True # Tells the game a code fired
        
    elif input_history == reverse_code:
        print("\n>>> CHEAT REVERSED!")
        input_history.clear()
        max_chances = 3
        play_melody(MELODY_REV)
        start_new_game()
        return True 
        
    elif input_history[-4:] == edit_code:
        enter_edit_mode()
        return True 
        
    return False # No code triggered yet

def enter_edit_mode():
    global secret_code, input_history
    input_history.clear()
    print("\n>>> EDIT MODE: Tap 5 buttons to save a new Easter Egg code.")
    play_melody([(NOTE_C5, 0.1), (NOTE_G5, 0.2)])
    
    new_code = []
    while len(new_code) < 5:
        show_pattern(letters['E'])
        dot.toggle()
        
        while touch_up.value() or touch_down.value() or touch_guess.value() or touch_info.value():
            time.sleep(0.01)
            
        pressed = 0
        while pressed == 0:
            if is_firmly_pressed(touch_up): pressed = 1
            elif is_firmly_pressed(touch_down): pressed = 2
            elif is_firmly_pressed(touch_guess): pressed = 3
            elif is_firmly_pressed(touch_info): pressed = 4
            time.sleep(0.01)
            
        new_code.append(pressed)
        play_tone(1500, 0.1) 
        print(f"Recorded pad {pressed}... ({len(new_code)}/5)")
        
        while touch_up.value() or touch_down.value() or touch_guess.value() or touch_info.value():
            time.sleep(0.01)
            
    secret_code = new_code.copy()
    print(">>> NEW SECRET CODE SAVED:", secret_code)
    play_melody([(NOTE_G5, 0.1), (NOTE_C6, 0.3)])
    start_new_game()

# ==========================================
# 4. SOUND & HELPER FUNCTIONS
# ==========================================

def play_tone(freq, duration):
    """Plays a sharp, staccato tone to prevent buzzer ringing/bleeding."""
    if freq > 0:
        buzzer.freq(freq)
        buzzer.duty_u16(32768) 
        time.sleep(duration * 0.8)
        buzzer.duty_u16(0)
        time.sleep(duration * 0.2) 
    else:
        buzzer.duty_u16(0)
        time.sleep(duration)

def play_melody(melody):
    """Loops through a list of notes and plays them cleanly."""
    for note, duration in melody:
        play_tone(note, duration)

HOLD_THRESHOLD = 3 

def is_firmly_pressed(pin):
    if pin.value() == 0: return False
    for _ in range(HOLD_THRESHOLD):
        if pin.value() == 0: return False
        time.sleep(0.01)
    return True

def wait_for_release(pin):
    while pin.value() == 1:
        time.sleep(0.02)
    time.sleep(0.08)

def wait_for_any_press():
    print("\n--- Press ANY pad to play again ---")
    time.sleep(0.5) 
    while True:
        if touch_up.value() or touch_down.value() or touch_guess.value() or touch_info.value():
            while touch_up.value() or touch_down.value() or touch_guess.value() or touch_info.value():
                time.sleep(0.05)
            time.sleep(0.1)
            break
        dot.toggle()
        time.sleep(0.2)

def show_pattern(pattern):
    for i in range(7):
        segments[i].value(pattern[i])

def spin_animation(loops=2):
    show_pattern(letters['OFF'])
    for _ in range(loops):
        for i in range(6):
            segments[i].value(1)
            status_led.toggle()
            time.sleep(0.06)
            segments[i].value(0)

def blink_lives(lives):
    status_led.value(0)
    time.sleep(0.2)
    delay = 0.1 if lives <= 3 else 0.05
    for _ in range(lives):
        status_led.value(1)
        play_tone(1500, delay) 
        time.sleep(delay)
        status_led.value(0)
        time.sleep(delay * 1.5)
    status_led.value(1)

def start_new_game():
    global secret_number, current_guess, chances_left
    secret_number = random.randint(0, 9)
    current_guess = 0
    chances_left = max_chances
    dot.value(0)
    
    spin_animation(2)
    show_pattern(digits[max_chances])
    dot.value(1)
    
    play_melody(MELODY_START)
    blink_lives(max_chances)
    dot.value(0)
    
    show_pattern(digits[current_guess])
    print(f"\n==========================================")
    print(f"NEW GAME STARTED! ({max_chances} Chances)")
    print(f"==========================================")

# ==========================================
# 5. MAIN GAME LOOP
# ==========================================

start_new_game()

while True:
    # --- PAD 1: Increase Guess ---
    if is_firmly_pressed(touch_up):
        play_tone(1000, 0.08) 
        current_guess = (current_guess + 1) % 10
        show_pattern(digits[current_guess])
        if check_secret_codes(1): continue 
        wait_for_release(touch_up)
        
    # --- PAD 2: Decrease Guess ---
    elif is_firmly_pressed(touch_down):
        play_tone(800, 0.08) 
        current_guess = (current_guess - 1) % 10
        show_pattern(digits[current_guess])
        if check_secret_codes(2): continue
        wait_for_release(touch_down)
        
    # --- PAD 3: Submit Guess ---
    elif is_firmly_pressed(touch_guess):
        if check_secret_codes(3): continue
        wait_for_release(touch_guess)
        chances_left -= 1
        
        # 1. PLAYER WINS
        if current_guess == secret_number:
            print(">>> YOU WIN!")
            show_pattern(digits[current_guess])
            play_melody(MELODY_WIN)
            for _ in range(4):
                show_pattern(letters['OFF'])
                time.sleep(0.15)
                show_pattern(digits[current_guess])
                time.sleep(0.15)
            wait_for_any_press()
            start_new_game()
            
        # 2. OUT OF CHANCES (GAME OVER)
        elif chances_left == 0:
            print(f">>> GAME OVER! Secret was {secret_number}.")
            show_pattern(letters['E'])
            play_melody(MELODY_LOSE)
            time.sleep(1)
            show_pattern(digits[secret_number])
            wait_for_any_press()
            start_new_game()
            
        # 3. WRONG GUESS, SHOW HINT
        else:
            play_tone(250, 0.2) 
            if current_guess < secret_number:
                show_pattern(letters['H'])
                dot.value(1)
            else:
                show_pattern(letters['L'])
                dot.value(0)
            time.sleep(0.9)
            show_pattern(digits[chances_left])
            blink_lives(chances_left)
            show_pattern(digits[current_guess])

    # --- PAD 4: Check Lives ---
    elif is_firmly_pressed(touch_info):
        play_tone(1200, 0.08) 
        show_pattern(digits[chances_left])
        blink_lives(chances_left)
        show_pattern(digits[current_guess])
        if check_secret_codes(4): continue
        wait_for_release(touch_info)
        
    time.sleep(0.01)
