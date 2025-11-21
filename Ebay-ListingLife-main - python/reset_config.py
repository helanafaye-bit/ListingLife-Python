"""
Reset Configuration - Delete saved directory config
Run this if the app won't start and you want to reset directory selection
"""

from pathlib import Path
import json

config_file = Path.home() / ".listinglife_config.json"

if config_file.exists():
    print(f"Found config file at: {config_file}")
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            print(f"Current directory: {config.get('data_directory', 'Not set')}")
    except Exception as e:
        print(f"Error reading config: {e}")
    
    response = input("Delete this config file? (y/n): ")
    if response.lower() == 'y':
        config_file.unlink()
        print("Config file deleted. App will ask for directory again on next run.")
    else:
        print("Config file not deleted.")
else:
    print("No config file found. App will ask for directory on next run.")





