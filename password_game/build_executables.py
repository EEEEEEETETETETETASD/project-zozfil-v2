#!/usr/bin/env python3
"""
Build Executables for Project Zozfil
Converts Python scripts into standalone executables using PyInstaller.
"""

import os
import subprocess
import shutil

# Build the game executable
print("Building app.exe...")
subprocess.run([
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--name=app",
    "main.py"
], check=True)

# Build the updater executable
print("Building updater.exe...")
subprocess.run([
    "pyinstaller",
    "--onefile",
    "--name=updater",
    "updater.py"
], check=True)

# Move executables to the project directory
if os.path.exists("dist"):
    for file in os.listdir("dist"):
        if file.endswith(".exe"):
            shutil.move(f"dist/{file}", ".")
    shutil.rmtree("dist")

if os.path.exists("build"):
    shutil.rmtree("build")

if os.path.exists("app.spec"):
    os.remove("app.spec")

if os.path.exists("updater.spec"):
    os.remove("updater.spec")

print("Executables built successfully!")