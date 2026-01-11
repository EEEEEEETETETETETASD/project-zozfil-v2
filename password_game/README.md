# Project Zozfil - Update Instructions

## Pushing Updates

To release a new update for Project Zozfil:

### Step 1: Build the Executables
Run the build script to create the latest `app.exe` and `updater.exe`:
```
python build_executables.py
```

### Step 2: Generate and Push the Update
Run the update pusher to increment the version, package the update, and push to GitHub:
```
python push_update.py
```
This will:
- Increment the version number (e.g., 1.0.2 → 1.0.3)
- Copy the new `app.exe` to `updates/{version}.exe`
- Create/update `updates/latest_version.json`
- Commit all changes to Git
- Push the commit to the GitHub repository

### Step 3: Verify the Update
- The update files are now live on GitHub (if using GitHub Pages or direct access)
- Users can run `updater.exe` to check for and download updates
- The updater downloads the new `app.exe` and replaces the old one

## Setting Up the Repository
- Ensure Git is initialized: `git init`
- Set your Git identity: `git config --global user.name "Your Name"` and `git config --global user.email "your@email.com"`
- Add the remote: `git remote add origin https://github.com/yourusername/yourrepo.git`
- For automatic pushing, ensure the repository is connected

## Testing Updates Locally
- Run `python update_server.py` to serve updates from `updates/` on `http://localhost:8000`
- Temporarily set `UPDATE_URL` in `updater.py` and `main.py` to `"http://localhost:8000/"`
- Run `updater.exe` to test the update process

## Notes
- Always build executables before pushing updates
- The updater replaces `app.exe` in the same directory
- Version is read from `version.json` and displayed in the game