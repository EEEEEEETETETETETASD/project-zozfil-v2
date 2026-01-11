#!/usr/bin/env python3
"""
Project Zozfil Update Pusher
Generates update packages and pushes them to the update server.
"""

import os
import json
import shutil
import zipfile
import subprocess

# Configuration
UPDATE_DIR = "updates"
VERSION_FILE = "version.json"

# Load current version
with open(VERSION_FILE, "r") as f:
    version_data = json.load(f)
    current_version = version_data.get("version", "1.0.0")

# Generate a new version
new_version_parts = current_version.split(".")
new_version_parts[-1] = str(int(new_version_parts[-1]) + 1)
new_version = ".".join(new_version_parts)

# Create update directory
os.makedirs(UPDATE_DIR, exist_ok=True)

# Update the version file
with open(VERSION_FILE, "w") as f:
    json.dump({"version": new_version}, f)

# Create a latest_version.json file
with open(os.path.join(UPDATE_DIR, "latest_version.json"), "w") as f:
    json.dump({"version": new_version}, f)

# Copy app.exe to updates as the versioned exe
if os.path.exists("dist/app.exe"):
    shutil.copy("dist/app.exe", os.path.join(UPDATE_DIR, f"{new_version}.exe"))
    print(f"Update exe: {os.path.join(UPDATE_DIR, f'{new_version}.exe')}")

# Copy icon.png if it exists
if os.path.exists("icon.png"):
    shutil.copy("icon.png", os.path.join(UPDATE_DIR, "icon.png"))
    print(f"Update icon: {os.path.join(UPDATE_DIR, 'icon.png')}")

print(f"Update {new_version} generated successfully!")
print(f"Latest version file: {os.path.join(UPDATE_DIR, 'latest_version.json')}")

# Automatically commit and push to GitHub
print("Committing and pushing to GitHub...")
try:
    # Find git root
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
    git_root = result.stdout.strip()
    os.chdir(git_root)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Update to version {new_version}"], check=True)
    subprocess.run(["git", "push"], check=True)
except subprocess.CalledProcessError:
    print("Git repository not found or not initialized. Please commit and push manually.")

print("Update pushed to GitHub successfully!")