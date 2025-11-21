# ListingLife - Python Desktop Application

A Python desktop application for managing eBay listings, categories, and tracking sold items. This application helps you organize your active listings, track when items should be removed, and analyze which categories or items sell most often.

## Features

- **Category Management**: Organize your listings into categories with custom average days
- **Item Management**: Track individual items with dates, photos, notes, and descriptions
- **Ended Items Tracking**: View items that have ended or been manually ended
- **Sold Items Trends**: Track how many items have sold across categories and subcategories
- **Currency Settings**: Configure currency for sold items totals
- **Directory Selection**: Choose where to save your data (local, Dropbox, or shared folders)
- **Collaboration Ready**: Save data to shared directories (like Dropbox) for team collaboration

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)

### Installing tkinter (if needed)

**Windows**: tkinter is included with Python installations

**Linux**: 
```bash
sudo apt-get install python3-tk
```

**macOS**: tkinter is included with Python installations

## Installation

1. Clone or download this repository
2. Ensure Python 3.7+ is installed
3. No additional packages required - uses only Python standard library!

## Usage

### First Run

When you first launch the application, you'll be prompted to select a directory where your data will be stored. You can choose:

- **Local Folder**: Save to a folder on your computer (e.g., Documents/ListingLife)
- **Dropbox Folder**: Save to Dropbox for cloud sync and collaboration
- **Shared Network Folder**: Save to any shared network location

The selected directory will be remembered for future sessions.

### Running the Application

```bash
python main.py
```

Or on some systems:

```bash
python3 main.py
```

## Data Storage

All data is stored as JSON files in your selected directory:

- `categories.json` - Category definitions
- `items.json` - Item listings
- `sold_trends.json` - Sold items trends data
- `settings.json` - Application settings

These files can be easily backed up, shared, or synchronized via cloud storage services.

## Features Overview

### Home
Welcome screen with application overview and quick start button.

### ListingLife
Main view for managing categories and items:
- View all categories in a grid
- Click a category to see its items
- Add, edit, or delete categories
- Add, edit, end, or delete items
- Search for items across all categories
- View item details

### Items Ended
View all items that have ended (either automatically or manually):
- See all ended items in one place
- Edit or delete ended items
- Items are automatically moved here when their end date passes

### Sold Items Trends
Track sales performance:
- Create data periods (e.g., "2025", "October 2025")
- Add categories with subcategories
- Track sold counts and prices
- View totals for each category
- Switch between different time periods

### Settings
Configure application behavior:
- Set currency for sold items totals (GBP, USD, EUR, AUD, CAD)
- Settings are saved automatically

## Collaboration

To collaborate with others:

1. Select a shared directory (like Dropbox) when setting up the application
2. All team members should point to the same directory
3. Data files are JSON format, so they can be easily shared and synchronized
4. Note: Be careful when multiple people edit simultaneously - consider using file synchronization tools

## Keyboard Shortcuts

- **Enter** in search box: Perform search
- **Escape**: Close dialogs (where applicable)

## Troubleshooting

### Application won't start
- Ensure Python 3.7+ is installed
- Check that tkinter is available: `python -c "import tkinter"`

### Can't select directory
- Ensure you have write permissions to the selected directory
- Try creating the directory manually first

### Data not saving
- Check that the data directory is writable
- Ensure sufficient disk space
- Check for file permission issues

## License

This application is provided as-is for personal and commercial use.

## Support

For issues or questions, please check the code comments or file an issue in the repository.

## Version History

- **1.0.0** - Initial Python port from web application
  - Full feature parity with web version
  - Directory selection on startup
  - JSON-based data storage
  - Cross-platform support (Windows, macOS, Linux)



