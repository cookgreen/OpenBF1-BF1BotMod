import sys
import os
from cx_Freeze import setup, Executable
# No need to import pygame here just for fonts anymore

base = None
if sys.platform == "win32":
    base = "Win32GUI"

# --- Remove the pygame default font finding logic ---
# pygame_default_font = pygame.font.get_default_font()
# pygame_font_path = os.path.dirname(pygame.font.match_font(pygame_default_font)) # THIS CAUSED ERROR
# include_font_files = [(os.path.join(pygame_font_path, pygame_default_font), os.path.basename(pygame_default_font))]

build_exe_options = {
    "packages": ["pygame", "moderngl", "glm", "math", "xml", "numpy"],
    "excludes": ["tkinter"],
    "include_files": [
        ("assets", "assets"),
        ("data", "data"),
        ("fonts", "fonts"),
        ("models", "models"),
        ("music", "music"),
        ("shaders", "shaders"),
        ("sound", "sound"),
        ("textures", "textures"),
    ],
}
app_icon = "app.ico"

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="bf1botmod.exe",
        icon=app_icon
    )
]

setup(
    name="BF1BotMod",
    version="1.0",
    description="Battlefield 1 Bot Mod is a unofficial bot addon for Battlefield 1",
    options={"build_exe": build_exe_options},
    executables=executables
)

print("-" * 40)
print("Setup script finished.")
print("Executable and required files should be in the 'build/exe...' directory.")
print("-" * 40)