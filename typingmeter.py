import time
import random
import curses
from curses import wrapper
import os
from datetime import datetime

# Sample text passages for typing tests
typing_samples = [
    "The quick brown fox jumps over the lazy dog. ",
    "This sentence contains all the letters in the English alphabet.",
    "Programming is the process of creating a set of instructions that tell a computer how to perform a task.",
    "Python is a high-level, interpreted programming language known for its readability and versatility.",
    "Learning to type quickly and accurately is an essential skill in today's digital world.",
    "Practice makes perfect when it comes to improving your typing speed and accuracy.",
    "The best way to learn programming is by writing code and building projects that interest you.",
    "Typing tests measure both your speed in words per minute and your accuracy percentage.",
    "Focus on accuracy first, then gradually work on increasing your typing speed over time.",
    "Regular practice for just a few minutes each day can significantly improve your typing skills.",
    "Touch typing means typing without looking at the keyboard, using muscle memory instead."
]

# Global variables to store results
test_results = []

def get_text():
    """Return a random text passage for typing test"""
    return random.choice(typing_samples)

def display_text(stdscr, target_text, current_text, wpm=0, accuracy=100, time_elapsed=0):
    """Display the target text and user's progress on the screen"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Display title and instructions
    title = "TYPING SPEED TEST"
    instructions = "Type the text below. Press Esc to exit."
    stdscr.addstr(0, w//2 - len(title)//2, title, curses.A_BOLD)
    stdscr.addstr(1, w//2 - len(instructions)//2, instructions)
    
    # Display target text
    start_y = 3
    wrapped_text = []
    current_line = ""
    
    # Word wrap the target text
    words = target_text.split()
    for word in words:
        if len(current_line + word) + 1 <= w - 4:  # -4 for margin
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            wrapped_text.append(current_line)
            current_line = word
    
    if current_line:
        wrapped_text.append(current_line)
    
    # Display wrapped text
    for i, line in enumerate(wrapped_text):
        stdscr.addstr(start_y + i, 2, line)
    
    # Display user's input
    start_y += len(wrapped_text) + 2
    stdscr.addstr(start_y, 2, "Your input:")
    
    # Prepare to show the user's text with correct/incorrect highlighting
    for i, char in enumerate(current_text):
        # Calculate position in the wrapped text
        total_chars = 0
        line_idx = 0
        char_idx = 0
        
        for line in wrapped_text:
            if total_chars + len(line) > i:
                char_idx = i - total_chars
                break
            total_chars += len(line) + 1  # +1 for newline
            line_idx += 1
        
        # Check if the character is correct and highlight accordingly
        correct_char = target_text[i] if i < len(target_text) else None
        
        if char == correct_char:
            color = curses.A_NORMAL
        else:
            color = curses.A_REVERSE
        
        try:
            if line_idx < len(wrapped_text):
                stdscr.addch(start_y - len(wrapped_text) + line_idx, 2 + char_idx, char, color)
        except curses.error:
            pass  # Ignore errors from writing to bottom-right corner
    
    # Display statistics
    stats = f"WPM: {wpm} | Accuracy: {accuracy:.1f}% | Time: {time_elapsed:.1f}s"
    stdscr.addstr(start_y + 2, 2, stats)
    
    stdscr.refresh()

def calculate_wpm(text, elapsed_time):
    """Calculate words per minute based on standard 5 characters per word"""
    if elapsed_time == 0:
        return 0
    # Standard definition: 5 keypresses = 1 word
    word_count = len(text) / 5
    minutes = elapsed_time / 60
    return int(word_count / minutes)

def calculate_accuracy(target_text, current_text):
    """Calculate typing accuracy percentage"""
    correct_chars = 0
    compared_length = min(len(target_text), len(current_text))
    
    if compared_length == 0:
        return 100.0
    
    for i in range(compared_length):
        if target_text[i] == current_text[i]:
            correct_chars += 1
    
    return (correct_chars / compared_length) * 100

def main(stdscr):
    """Main function to run the typing test"""
    global test_results
    
    # Set up colors
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(0)  # Hide cursor
    
    stdscr.clear()
    
    while True:
        target_text = get_text()
        current_text = ""
        typing_started = False
        start_time = time.time()
        
        while True:
            time_elapsed = time.time() - start_time if typing_started else 0
            wpm = calculate_wpm(current_text, time_elapsed)
            accuracy = calculate_accuracy(target_text[:len(current_text)], current_text)
            
            display_text(stdscr, target_text, current_text, wpm, accuracy, time_elapsed)
            
            # Get key input
            try:
                key = stdscr.getch()
            except:
                continue
            
            # Exit on Escape key
            if key == 27:  # ESC
                return
            
            # Handle backspace
            elif key in (8, 127, curses.KEY_BACKSPACE):
                if current_text:
                    current_text = current_text[:-1]
            
            # Handle regular key inputs
            elif 32 <= key <= 126:  # Printable ASCII characters
                if not typing_started:
                    typing_started = True
                    start_time = time.time()
                current_text += chr(key)
            
            # Check if the test is complete
            if len(current_text) >= len(target_text):
                break
        
        # Calculate final results
        final_time = time.time() - start_time
        final_wpm = calculate_wpm(current_text, final_time)
        final_accuracy = calculate_accuracy(target_text, current_text)
        
        # Store results in global variable
        test_results.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'wpm': final_wpm,
            'accuracy': final_accuracy,
            'time': final_time,
            'text_length': len(target_text)
        })
        
        # Display final results
        stdscr.clear()
        stdscr.addstr(5, 2, "Test completed!")
        stdscr.addstr(7, 2, f"Your typing speed: {final_wpm} WPM")
        stdscr.addstr(8, 2, f"Your accuracy: {final_accuracy:.1f}%")
        stdscr.addstr(9, 2, f"Total time: {final_time:.1f} seconds")
        stdscr.addstr(10, 2, f"Text length: {len(target_text)} characters")
        stdscr.addstr(12, 2, "Press any key to try again, or ESC to exit.")
        stdscr.refresh()
        
        # Wait for user input to continue or exit
        key = stdscr.getch()
        if key == 27:  # ESC
            break

if __name__ == "__main__":
    try:
        # Run the program with curses wrapper
        wrapper(main)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        # Make sure terminal is reset properly
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix/Linux/Mac
            os.system('clear')
        
        # Print results to console after exiting the curses interface
        print("\n===== TYPING TEST RESULTS =====")
        if test_results:
            for i, result in enumerate(test_results, 1):
                print(f"\nTest #{i} - {result['timestamp']}")
                print(f"WPM: {result['wpm']}")
                print(f"Accuracy: {result['accuracy']:.1f}%")
                print(f"Time: {result['time']:.1f} seconds")
                print(f"Text length: {result['text_length']} characters")
            
            # Print average results if multiple tests were taken
            if len(test_results) > 1:
                avg_wpm = sum(r['wpm'] for r in test_results) / len(test_results)
                avg_acc = sum(r['accuracy'] for r in test_results) / len(test_results)
                print("\n===== AVERAGE RESULTS =====")
                print(f"Average WPM: {avg_wpm:.1f}")
                print(f"Average Accuracy: {avg_acc:.1f}%")
                print(f"Total tests: {len(test_results)}")
        else:
            print("No tests completed.")
        
        print("\nThanks for practicing! Keep typing to improve your skills.")