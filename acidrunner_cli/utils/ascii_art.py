import os
import time
import typer
from colorama import Fore, init
from itertools import cycle

stop_animation = False  # Global flag to stop the animation
logs = []  # List to store log messages

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def move_cursor_up(lines=1):
    # Move the terminal cursor up by 'lines' number of lines
    print(f"\033[{lines}A")

def print_art(frame, loading=False):
    bits = '1101100001'
    toggled_bits = ''.join(b if (frame // 5) % 2 == 0 else ' ' for b in bits)
    hex_value = f"0x{frame % 256:02x}"  # Cycle through 00 to ff
    loot = cycle(["./.", ".-.", ".\\."])

    # Color cycling for funky effects
    colors = cycle([Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE])
    
    if loading:
        # Simulate "pinking" effect by alternating between magenta and red
        color1 = Fore.MAGENTA if frame % 2 == 0 else Fore.RED
        color2 = Fore.MAGENTA if frame % 2 == 1 else Fore.RED
        color3 = Fore.MAGENTA if frame % 3 == 0 else Fore.RED
    else:
        # Regular funky colors
        color1 = next(colors)
        color2 = next(colors)
        color3 = next(colors)

    art = f"""                
                 {color3}  .  .       
     {color1}O       O         Observe
     {color1}O      OOO     /
   {color2}O O    O O O    /
    {color2}O O O    O   --

       {color3}/        \\________
      {color3}/            \\    
     {color3}/              \\        
   {color1}{toggled_bits}     {color2}
   {color1}O{color3}       O         Observe
       {color3}O      OOO     /
                     .  .
       {color3}O       O         
       {color3}O      OOO     /
     {color3}O O    O O O    /_____
      {color2}O O O    O   --\\
       /              \\
         /        \\________
        /            \\
       /              \\
   Loading{loot}     {hex_value} 
    """

    art = f"""                
                 {color3}  .  .       
     {color1}O       O         Observe
     {color1}O      OOO     /
   {color2}O O    O O O    /
    {color2}O O O    O   --

       {color3}/        \\________
      {color3}/            \\    
     {color3}/              \\        
   {color1}{toggled_bits}     {color2}
   {color1}O{color3}       O         Observe
       {color3}O      OOO     /
                     .  .
       {color3}O       O         
       {color3}O      OOO     /
     {color3}O O    O O O    /_____
      {color2}O O O    O   --\\
       /              \\
         /        \\________
        /            \\
       /              \\
   Loading{loot}     {hex_value} 
    """


    print(art)

def animate_art(loading=False, speed=0.137):
    """Function to run the animation in a separate thread."""
    global stop_animation
    frame = 0
    while not stop_animation:
        # Move the cursor back up before printing art to overwrite
        print('\033c', end='')  # Clear the console (works in many terminals)
        print_art(frame, loading)
        time.sleep(speed)
        frame += 1

animate_art(loading=True)
