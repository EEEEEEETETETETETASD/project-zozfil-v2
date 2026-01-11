#!/usr/bin/env python3
"""
Password Guessing Game
A sleek game where users guess a series of randomized passwords.
"""

import pygame
import sys
import random
import string
import json
import os
import ctypes
import requests

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 0)  # Black
WHITE = (255, 255, 255)
FONT_SIZE = 32
UPDATE_URL = "https://EEEEEEETETETETASD.github.io/project-zozfil/password_game/updates/"

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Project Zozfil")

# Font
font = pygame.font.SysFont("Arial", FONT_SIZE)

def scale_font(size):
    """Scale font size based on screen resolution."""
    base_width = 800
    base_height = 600
    scale_factor = min(SCREEN_WIDTH / base_width, SCREEN_HEIGHT / base_height)
    scaled_size = max(12, int(size * scale_factor))  # Ensure minimum readable size
    return pygame.font.SysFont("Arial", scaled_size)

def get_version():
    """Get the current version from version.json."""
    version = "1.0.0"
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
            version = version_data.get("version", version)
    except FileNotFoundError:
        pass
    return version

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

# Game states
MENU = 0
PLAYING = 1
SETTINGS = 2
PAUSED = 3
EXIT = 4
CHANGELOGS = 5

current_state = MENU

# Password generation
def generate_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Game variables
passwords = [generate_password(6) for _ in range(5)]
current_password_index = 0
user_guess = ""
max_guesses = 6
guesses_used = 0
game_over = False
update_available = False
last_guess = ""

# Changelog data
changelog_data = [
    {
        "version": "1.0.5",
        "changes": [
            "Made window resizable by dragging edges",
            "Removed resolution settings, kept fullscreen toggle",
            "Added progressive general hints that reveal more with wrong guesses",
            "Improved hint system with both general clues and Wordle-like feedback"
        ]
    },
    {
        "version": "1.0.4",
        "changes": [
            "Fixed back button navigation from settings during gameplay",
            "Fixed game over enter key handling to prevent negative guesses",
            "Improved last guess display formatting",
            "Made resolution and fullscreen settings functional",
            "Added Changelogs menu with scrollable history",
            "Enhanced UI with better button boxes and theming"
        ]
    },
    {
        "version": "1.0.3",
        "changes": [
            "Fixed update download corruption with streaming",
            "Improved hint system with Wordle-like feedback",
            "Balanced difficulty: 6-char passwords, 6 guesses",
            "Always show password length hint"
        ]
    },
    {
        "version": "1.0.2",
        "changes": [
            "Added progressive hints on incorrect guesses",
            "Fixed update notification bug",
            "Version displayed on all screens",
            "ESC key opens pause menu globally"
        ]
    },
    {
        "version": "1.0.1",
        "changes": [
            "Initial release",
            "Password guessing game with animated background",
            "Settings menu with graphics options",
            "Automatic update system"
        ]
    }
]

scroll_y = 0
prev_state = MENU
current_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
fullscreen = False
available_resolutions = pygame.display.list_modes()
if current_resolution in available_resolutions:
    res_index = available_resolutions.index(current_resolution)
else:
    res_index = 0
    current_resolution = available_resolutions[0] if available_resolutions else (800, 600)

# Animated dots
class Dot:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-1, 1)

dots = [Dot() for _ in range(100)]

def draw_dots():
    """Draw animated dots on the screen."""
    for dot in dots:
        pygame.draw.circle(screen, WHITE, (int(dot.x), int(dot.y)), dot.size)
        dot.x += dot.speed_x
        dot.y += dot.speed_y
        
        # Bounce off edges
        if dot.x <= 0 or dot.x >= SCREEN_WIDTH:
            dot.speed_x *= -1
        if dot.y <= 0 or dot.y >= SCREEN_HEIGHT:
            dot.speed_y *= -1

def draw_menu():
    """Draw the main menu."""
    screen.fill(BACKGROUND_COLOR)
    draw_dots()
    
    scaled_font = scale_font(FONT_SIZE)
    title_text = scaled_font.render("Project Zozfil", True, WHITE)
    play_text = scaled_font.render("Play", True, WHITE)
    settings_text = scaled_font.render("Settings", True, WHITE)
    changelogs_text = scaled_font.render("Changelogs", True, WHITE)
    exit_text = scaled_font.render("Exit", True, WHITE)
    
    version = get_version()
    version_text = scale_font(16).render(f"Version: {version}", True, WHITE)
    
    # Draw button boxes with size based on text
    button_padding = 20
    button_height = play_text.get_height() + 10

    play_rect = pygame.Rect(SCREEN_WIDTH // 2 - (play_text.get_width() + button_padding) // 2, 245, play_text.get_width() + button_padding, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH // 2 - (settings_text.get_width() + button_padding) // 2, 295, settings_text.get_width() + button_padding, button_height)
    changelogs_rect = pygame.Rect(SCREEN_WIDTH // 2 - (changelogs_text.get_width() + button_padding) // 2, 345, changelogs_text.get_width() + button_padding, button_height)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - (exit_text.get_width() + button_padding) // 2, 395, exit_text.get_width() + button_padding, button_height)

    pygame.draw.rect(screen, WHITE, play_rect, 2)
    pygame.draw.rect(screen, WHITE, settings_rect, 2)
    pygame.draw.rect(screen, WHITE, changelogs_rect, 2)
    pygame.draw.rect(screen, WHITE, exit_rect, 2)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
    screen.blit(play_text, (play_rect.centerx - play_text.get_width() // 2, play_rect.centery - play_text.get_height() // 2))
    screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width() // 2, settings_rect.centery - settings_text.get_height() // 2))
    screen.blit(changelogs_text, (changelogs_rect.centerx - changelogs_text.get_width() // 2, changelogs_rect.centery - changelogs_text.get_height() // 2))
    screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))
    screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 30))
    
    if update_available:
        update_text = scaled_font.render("Update Available! Run updater.exe to update.", True, WHITE)
        screen.blit(update_text, (SCREEN_WIDTH // 2 - update_text.get_width() // 2, 450))

def draw_pause_menu():
    """Draw the pause menu."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    resume_text = font.render("Resume", True, WHITE)
    settings_text = font.render("Settings", True, WHITE)
    main_menu_text = font.render("Main Menu", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    button_padding = 20
    button_height = resume_text.get_height() + 10

    resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - (resume_text.get_width() + button_padding) // 2, 245, resume_text.get_width() + button_padding, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH // 2 - (settings_text.get_width() + button_padding) // 2, 295, settings_text.get_width() + button_padding, button_height)
    main_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - (main_menu_text.get_width() + button_padding) // 2, 345, main_menu_text.get_width() + button_padding, button_height)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - (exit_text.get_width() + button_padding) // 2, 395, exit_text.get_width() + button_padding, button_height)

    pygame.draw.rect(screen, WHITE, resume_rect, 2)
    pygame.draw.rect(screen, WHITE, settings_rect, 2)
    pygame.draw.rect(screen, WHITE, main_menu_rect, 2)
    pygame.draw.rect(screen, WHITE, exit_rect, 2)

    screen.blit(resume_text, (resume_rect.centerx - resume_text.get_width() // 2, resume_rect.centery - resume_text.get_height() // 2))
    screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width() // 2, settings_rect.centery - settings_text.get_height() // 2))
    screen.blit(main_menu_text, (main_menu_rect.centerx - main_menu_text.get_width() // 2, main_menu_rect.centery - main_menu_text.get_height() // 2))
    screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))

    # Display version
    version = get_version()
    version_text = scale_font(16).render(f"Version: {version}", True, WHITE)
    screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 30))

def draw_changelogs():
    """Draw the changelogs screen."""
    screen.fill(BACKGROUND_COLOR)
    draw_dots()

    scaled_font = scale_font(FONT_SIZE)
    small_font = scale_font(20)

    title_text = scaled_font.render("Changelogs", True, WHITE)
    back_text = scaled_font.render("Back", True, WHITE)

    # Draw back button box
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 500, back_text.get_width() + 20, back_text.get_height() + 10)
    pygame.draw.rect(screen, WHITE, back_rect, 2)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

    y_offset = 120 - scroll_y
    for entry in changelog_data:
        # Draw box for each changelog
        box_height = 60 + len(entry["changes"]) * 25
        pygame.draw.rect(screen, WHITE, (50, y_offset, SCREEN_WIDTH - 100, box_height), 2)

        version_text = small_font.render(f"Version {entry['version']}", True, WHITE)
        screen.blit(version_text, (70, y_offset + 10))

        change_y = y_offset + 40
        for change in entry["changes"]:
            change_text = small_font.render(f"- {change}", True, WHITE)
            screen.blit(change_text, (90, change_y))
            change_y += 25

        y_offset += box_height + 20

def draw_settings():
    """Draw the settings screen."""
    screen.fill(BACKGROUND_COLOR)
    draw_dots()

    scaled_font = scale_font(FONT_SIZE)
    small_font = scale_font(20)

    # Tab at the top
    graphics_tab = small_font.render("Graphics", True, WHITE)
    screen.blit(graphics_tab, (SCREEN_WIDTH // 2 - graphics_tab.get_width() // 2, 50))

    # Settings content
    fullscreen_text = small_font.render(f"Fullscreen: {'On' if fullscreen else 'Off'}", True, WHITE)
    back_text = scaled_font.render("Back", True, WHITE)

    # Buttons
    toggle_fs = small_font.render("Toggle", True, WHITE)

    # Draw boxes
    toggle_rect = pygame.Rect(SCREEN_WIDTH // 2 - (toggle_fs.get_width() + 20) // 2, 195, toggle_fs.get_width() + 20, toggle_fs.get_height() + 10)
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 495, back_text.get_width() + 20, back_text.get_height() + 10)

    pygame.draw.rect(screen, WHITE, toggle_rect, 2)
    pygame.draw.rect(screen, WHITE, back_rect, 2)

    screen.blit(fullscreen_text, (SCREEN_WIDTH // 2 - fullscreen_text.get_width() // 2, 150))
    screen.blit(toggle_fs, (toggle_rect.centerx - toggle_fs.get_width() // 2, toggle_rect.centery - toggle_fs.get_height() // 2))
    screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

    # Display version
    version = get_version()
    version_text = scale_font(16).render(f"Version: {version}", True, WHITE)
    screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 30))

def get_wordle_hint(guess, password):
    """Generate Wordle-like feedback for the guess."""
    if not guess:
        return ""
    result = []
    for i, c in enumerate(guess):
        if i < len(password) and c == password[i]:
            result.append(f"[{c}]")  # Correct position
        elif c in password:
            result.append(f"({c})")  # Correct char, wrong position
        else:
            result.append(c)  # Wrong
    return ''.join(result)

def get_hint(password, wrong_guesses, last_guess):
    """Generate progressive hints and Wordle feedback."""
    hints = [
        lambda p: f"Length: {len(p)}",
        lambda p: f"Starts with: {p[:2]}",
        lambda p: f"Uppercase letters: {sum(1 for c in p if c.isupper())}",
        lambda p: f"Digits: {sum(1 for c in p if c.isdigit())}",
        lambda p: f"Ends with: {p[-2:]}",
    ]

    available_hints = [hint(password) for hint in hints[:wrong_guesses + 1]]
    if last_guess:
        available_hints.append(f"Last guess: {get_wordle_hint(last_guess, password)}")
    return ", ".join(available_hints)

def draw_game():
    """Draw the game screen."""
    screen.fill(BACKGROUND_COLOR)
    draw_dots()
    
    scaled_font = scale_font(FONT_SIZE)
    small_font = scale_font(20)
    
    password_text = scaled_font.render(f"Password {current_password_index + 1}/5", True, WHITE)
    guess_text = scaled_font.render(f"Guess: {user_guess}", True, WHITE)
    guesses_text = scaled_font.render(f"Guesses left: {max_guesses - guesses_used}", True, WHITE)
    
    # Wrap hint text
    hint_full = f"Hint: {get_hint(passwords[current_password_index], guesses_used, last_guess)}"
    hint_lines = wrap_text(hint_full, small_font, SCREEN_WIDTH - 100)
    
    screen.blit(password_text, (SCREEN_WIDTH // 2 - password_text.get_width() // 2, 100))
    screen.blit(guess_text, (SCREEN_WIDTH // 2 - guess_text.get_width() // 2, 200))
    screen.blit(guesses_text, (SCREEN_WIDTH // 2 - guesses_text.get_width() // 2, 400))

    # Draw wrapped hint text
    y_offset = 300
    for line in hint_lines:
        hint_line_text = small_font.render(line, True, WHITE)
        screen.blit(hint_line_text, (SCREEN_WIDTH // 2 - hint_line_text.get_width() // 2, y_offset))
        y_offset += 30

    if game_over:
        game_over_text = scaled_font.render("Game Over! Press Enter to continue.", True, WHITE)
        back_text = scaled_font.render("Back to Menu", True, WHITE)
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 545, back_text.get_width() + 20, back_text.get_height() + 10)
        pygame.draw.rect(screen, WHITE, back_rect, 2)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 500))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

    # Display version
    version = get_version()
    version_text = scale_font(16).render(f"Version: {version}", True, WHITE)
    screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 30))

def handle_menu_click(pos):
    """Handle menu button clicks."""
    global current_state, prev_state

    scaled_font = scale_font(FONT_SIZE)
    play_text = scaled_font.render("Play", True, WHITE)
    settings_text = scaled_font.render("Settings", True, WHITE)
    changelogs_text = scaled_font.render("Changelogs", True, WHITE)
    exit_text = scaled_font.render("Exit", True, WHITE)

    button_padding = 20
    button_height = play_text.get_height() + 10

    play_rect = pygame.Rect(SCREEN_WIDTH // 2 - (play_text.get_width() + button_padding) // 2, 245, play_text.get_width() + button_padding, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH // 2 - (settings_text.get_width() + button_padding) // 2, 295, settings_text.get_width() + button_padding, button_height)
    changelogs_rect = pygame.Rect(SCREEN_WIDTH // 2 - (changelogs_text.get_width() + button_padding) // 2, 345, changelogs_text.get_width() + button_padding, button_height)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - (exit_text.get_width() + button_padding) // 2, 395, exit_text.get_width() + button_padding, button_height)

    if play_rect.collidepoint(pos):
        current_state = PLAYING
    elif settings_rect.collidepoint(pos):
        prev_state = current_state
        current_state = SETTINGS
    elif changelogs_rect.collidepoint(pos):
        prev_state = current_state
        current_state = CHANGELOGS
    elif exit_rect.collidepoint(pos):
        current_state = EXIT

def handle_changelogs_click(pos):
    """Handle changelogs button clicks."""
    global current_state, prev_state

    scaled_font = scale_font(FONT_SIZE)
    back_text = scaled_font.render("Back", True, WHITE)

    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 500, back_text.get_width() + 20, back_text.get_height() + 10)

    if back_rect.collidepoint(pos):
        current_state = prev_state

def handle_settings_click(pos):
    """Handle settings button clicks."""
    global current_state, prev_state, fullscreen

    small_font = scale_font(20)
    scaled_font = scale_font(FONT_SIZE)
    toggle_fs = small_font.render("Toggle", True, WHITE)
    back_text = scaled_font.render("Back", True, WHITE)

    toggle_rect = pygame.Rect(SCREEN_WIDTH // 2 - (toggle_fs.get_width() + 20) // 2, 195, toggle_fs.get_width() + 20, toggle_fs.get_height() + 10)
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 495, back_text.get_width() + 20, back_text.get_height() + 10)

    if toggle_rect.collidepoint(pos):
        fullscreen = not fullscreen
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else 0))
    elif back_rect.collidepoint(pos):
        current_state = prev_state

def handle_pause_menu_click(pos):
    """Handle pause menu button clicks."""
    global current_state, prev_state

    resume_text = font.render("Resume", True, WHITE)
    settings_text = font.render("Settings", True, WHITE)
    main_menu_text = font.render("Main Menu", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    button_padding = 20
    button_height = resume_text.get_height() + 10

    resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - (resume_text.get_width() + button_padding) // 2, 245, resume_text.get_width() + button_padding, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH // 2 - (settings_text.get_width() + button_padding) // 2, 295, settings_text.get_width() + button_padding, button_height)
    main_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - (main_menu_text.get_width() + button_padding) // 2, 345, main_menu_text.get_width() + button_padding, button_height)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - (exit_text.get_width() + button_padding) // 2, 395, exit_text.get_width() + button_padding, button_height)

    if resume_rect.collidepoint(pos):
        current_state = PLAYING
    elif settings_rect.collidepoint(pos):
        prev_state = current_state
        current_state = SETTINGS
    elif main_menu_rect.collidepoint(pos):
        current_state = MENU
    elif exit_rect.collidepoint(pos):
        current_state = EXIT

def handle_game_input(event):
    """Handle game input."""
    global user_guess, current_password_index, guesses_used, game_over, last_guess

    if event.type == pygame.KEYDOWN:
        if game_over:
            if event.key == pygame.K_RETURN:
                current_password_index = 0
                guesses_used = 0
                game_over = False
                last_guess = ""
                user_guess = ""
            return
        if event.key == pygame.K_RETURN:
            if user_guess == passwords[current_password_index]:
                current_password_index += 1
                guesses_used = 0
                last_guess = ""
                if current_password_index >= len(passwords):
                    # Game won
                    pass
                user_guess = ""
            else:
                last_guess = user_guess
                guesses_used += 1
                if guesses_used >= max_guesses:
                    game_over = True
                user_guess = ""
        elif event.key == pygame.K_BACKSPACE:
            user_guess = user_guess[:-1]
        else:
            user_guess += event.unicode

# Check for updates
def check_for_updates():
    """Check if an update is available."""
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
            current_version = version_data.get("version", "1.0.0")

        response = requests.get(f"{UPDATE_URL}latest_version.json")
        latest_version_data = response.json()
        latest_version = latest_version_data.get("version", current_version)

        if latest_version > current_version:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False

# Main game loop
clock = pygame.time.Clock()
running = True

# Check for updates at startup
update_available = check_for_updates()

# Show Windows notification if update is available
if update_available:
    ctypes.windll.user32.MessageBoxW(0, "An update is available for Project Zozfil. Run updater.exe to update.", "Update Available", 0x40 | 0x0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.size
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else 0))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == MENU:
                handle_menu_click(event.pos)
            elif current_state == PAUSED:
                handle_pause_menu_click(event.pos)
            elif current_state == SETTINGS:
                handle_settings_click(event.pos)
            elif current_state == CHANGELOGS:
                handle_changelogs_click(event.pos)
            elif current_state == PLAYING and game_over:
                scaled_font = scale_font(FONT_SIZE)
                back_text = scaled_font.render("Back to Menu", True, WHITE)
                back_rect = pygame.Rect(SCREEN_WIDTH // 2 - (back_text.get_width() + 20) // 2, 545, back_text.get_width() + 20, back_text.get_height() + 10)
                if back_rect.collidepoint(event.pos):
                    current_password_index = 0
                    guesses_used = 0
                    game_over = False
                    last_guess = ""
                    user_guess = ""
                    current_state = MENU
        elif event.type == pygame.MOUSEWHEEL:
            if current_state == CHANGELOGS:
                scroll_y -= event.y * 20  # Scroll up/down
                scroll_y = max(0, min(scroll_y, 500))  # Limit scroll
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_state in (PLAYING, PAUSED):
                current_state = PAUSED if current_state == PLAYING else PLAYING
            elif current_state == PLAYING:
                handle_game_input(event)
    
    if current_state == MENU:
        draw_menu()
    elif current_state == PLAYING:
        draw_game()
    elif current_state == PAUSED:
        draw_game()
        draw_pause_menu()
    elif current_state == SETTINGS:
        draw_settings()
    elif current_state == CHANGELOGS:
        draw_changelogs()
    elif current_state == EXIT:
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()