#!/usr/bin/env python3
"""
Project Zozfil Updater
Checks for updates and downloads them if available.
"""

import os
import json
import requests
import shutil
import sys

# Configuration
# Replace this URL with your own update server URL
# For example: "https://yourwebsite.com/updates/project_zozfil/"
# The server should host the update files and a latest_version.json file
UPDATE_URL = "https://eeeeeeetetetetetasd.github.io/project-zozfil/"
VERSION_FILE = "version.json"
GAME_EXE = "app.exe"

# Load current version
current_version = "1.0.0"

try:
    with open(VERSION_FILE, "r") as f:
        version_data = json.load(f)
        current_version = version_data.get("version", current_version)
except FileNotFoundError:
    pass

# Check for updates
def check_for_updates():
    """Check if an update is available."""
    try:
        response = requests.get(f"{UPDATE_URL}latest_version.json")
        latest_version_data = response.json()
        latest_version = latest_version_data.get("version", current_version)
        
        if latest_version > current_version:
            return latest_version
        else:
            return None
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None

# Download and apply update
def apply_update(latest_version):
    """Download and apply the latest update."""
    try:
        print(f"Downloading update {latest_version}...")
        
        # Download the latest app.exe
        update_response = requests.get(f"{UPDATE_URL}{latest_version}.exe", stream=True)
        update_response.raise_for_status()
        with open("temp_app.exe", "wb") as f:
            for chunk in update_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Replace the old app.exe
        print("Applying update...")
        if os.path.exists(GAME_EXE):
            os.remove(GAME_EXE)
        shutil.move("temp_app.exe", GAME_EXE)
        
        # Update version file
        with open(VERSION_FILE, "w") as f:
            json.dump({"version": latest_version}, f)
        
        print("Update applied successfully!")
        return True
    except Exception as e:
        print(f"Error applying update: {e}")
        return False

# Main updater logic
if __name__ == "__main__":
    print(f"Current version: {current_version}")
    latest_version = check_for_updates()
    
    if latest_version:
        print(f"Update available: {latest_version}")
        apply_update(latest_version)
    else:
        print("No updates available.")