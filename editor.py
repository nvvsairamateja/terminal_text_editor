import msvcrt
import os

EDITOR_VERSION = "LITE EDITOR 0.0.1"
input_buffer = b'' # Buffer to store the user input
append_buffer = '' # Buffer to store the screen content
Cx, Cy = 0, 0 # Horizontal and vertical coordinate of the cursor (column and row)


def read_keypress() -> bytes:
    """Reads a single keypress from the user, handling special keys."""
    first_char = msvcrt.getch()

    if first_char in {b'\x00', b'\xe0'}:  # Special function key
         if msvcrt.kbhit():  # Check if more bytes are part of the sequence
            second_char = msvcrt.getch()
            return first_char + second_char
         else: return first_char
    else:
        return first_char


def clear_screen():
    """Clears the terminal screen."""
    global append_buffer
    append_buffer += "\x1b[?25l" # Hide cursor
    append_buffer += "\x1b[H" # Move cursor to the top-left corner

def mover_cursor(keypress : bytes):
    """Moves the cursor based on arrow key input."""
    global Cx, Cy
    if keypress == b'\xe0H': # Up arrow
        Cy = max(Cy - 1, 0)
    elif keypress == b'\xe0P': # Down arrow
        Cy = min(Cy + 1, os.get_terminal_size().lines -1 )
    elif keypress == b'\xe0M': # Right arrow
        Cx = min(Cx + 1, os.get_terminal_size().columns - 1)
    elif keypress == b'\xe0K': # Left arrow
        Cx = max(Cx - 1, 0)
    elif keypress == b'\xe0G': # home key
        Cy = 0
    elif keypress == b'\xe0O': # end key
        Cy = os.get_terminal_size().lines -1


def refresh_screen():
    """Clears the screen and redraws the interface."""
    global append_buffer
    clear_screen()
    draw_rows()
    append_buffer += f"\x1b[{Cy+1};{Cx+1}H"
    append_buffer += "\x1b[?25h" # Display the hidden cursor
    print(append_buffer, end="", flush=True)
    append_buffer = ""

def draw_rows():
    """Draws placeholder rows (e.g., tilde '~') on the screen."""
    global append_buffer
    terminal_size = os.get_terminal_size().lines
    for _ in range(terminal_size - 1):
        append_buffer += "~\x1b[K\r\n" # Draw a tilde, clear the rest of the line, and move to the next line
    append_buffer += "~\x1b[K"

def process_keypress():
    """Processes a keypress and updates the screen or exits based on the input."""
    global input_buffer
    keypress = read_keypress()

    if keypress == b'\x11': # CTRL + q
        print("\x1b[2J", end="", flush=True) # Clear screen
        print("\x1b[H", end="", flush=True) # Move cursor to top-left
        print(input_buffer)
        exit(code=0)
    elif keypress == b'\r': # Convert Enter key to newline
        input_buffer += b'\r\n'
    elif keypress in {b'\xe0H', b'\xe0P', b'\xe0M', b'\xe0K', b'\xe0G', b'\xe0O'}:  # Arrow keys, home and end
        mover_cursor(keypress)
    elif keypress in {b'\xe0I', b'\xe0Q'}: # pg up and pg down
        times = os.get_terminal_size().lines
        while times:
            if keypress == b'\xe0I':
                mover_cursor(b'\xe0H')
            else:
                mover_cursor(b'\xe0P')
            times -= 1
    elif keypress == b'\xe0S': # Delete key
        pass
    else:
        input_buffer += keypress
    
    
while True:
    refresh_screen()
    process_keypress()


