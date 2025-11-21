# Data Sharing and Collaboration Guide

## How Data Storage Works

Each user selects their own data directory when first running the application. The data is stored locally in JSON files:
- `categories.json`
- `items.json`
- `sold_trends.json`
- `settings.json`

## Git Repository vs Data Files

**Important:** When you upload this project to Git:
- ✅ **Source code** (Python files) will be shared with everyone
- ❌ **Data files** (your listings) will NOT be automatically shared

Each person who clones the repository will:
1. Run the application
2. Select their own data directory
3. Start with empty data files

## How to Share Data with Team Members

### Option 1: Shared Directory (Recommended for Collaboration)

1. **Set up a shared directory:**
   - Use Dropbox, Google Drive, OneDrive, or a network drive
   - All team members should have access to this folder

2. **Everyone selects the same shared directory:**
   - When running the app, all team members select the same shared folder
   - Example: `C:\Users\Team\Dropbox\ListingLife` or `\\server\shared\ListingLife`

3. **Automatic synchronization:**
   - Cloud storage services (Dropbox, OneDrive) will sync changes automatically
   - All team members will see the same data
   - ⚠️ **Warning:** Be careful about simultaneous edits - last save wins!

### Option 2: Manual File Sharing

1. Export your data files from your data directory
2. Share the JSON files via email, file sharing, etc.
3. Team members place the files in their own data directory
4. ⚠️ This is manual and requires re-sharing each time data changes

### Option 3: Version Control (Not Recommended)

**⚠️ DO NOT commit data files to Git unless:**
- Everyone wants the same initial data
- You understand Git merge conflicts will occur
- You're okay with frequent conflicts when multiple people edit

If you want to commit sample/initial data:
1. Create an `initial_data/` folder in the repository
2. Add sample JSON files there
3. Document that users can copy these to their data directory
4. Add `*.json` to `.gitignore` (except in `initial_data/`)

## Best Practice for Teams

**For collaboration, use Option 1 (Shared Directory):**
- Most seamless experience
- Automatic synchronization
- Everyone sees the same data in real-time
- Just ensure everyone selects the same folder path

**Example Setup:**
```
Team Dropbox Folder Structure:
📁 Dropbox/
  └── 📁 TeamProjects/
      └── 📁 ListingLife/          ← Everyone selects this folder
          ├── categories.json       ← Shared across team
          ├── items.json            ← Shared across team
          ├── sold_trends.json      ← Shared across team
          └── settings.json         ← Each user can have own settings
```

## Adding .gitignore (Recommended)

Create a `.gitignore` file in your repository root:

```
# Data files (user-specific, don't commit to git)
*.json
!initial_data/*.json

# Python cache
__pycache__/
*.pyc
*.pyo

# Config files (may contain local paths)
.listinglife_config.json

# OS files
.DS_Store
Thumbs.db
```

This ensures data files won't accidentally be committed to Git.

## Summary

- **Git = Code sharing** (source code, UI, features)
- **Shared Directory = Data sharing** (actual listings, categories)
- Each person selects where to store their data
- For collaboration, everyone should point to the same shared folder





