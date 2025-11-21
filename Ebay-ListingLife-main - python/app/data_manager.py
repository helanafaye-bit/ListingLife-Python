"""
Data Manager
Handles all data persistence operations
"""

import json
import os
from pathlib import Path
from datetime import datetime


class DataManager:
    """Manages data storage and retrieval"""
    
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Data file paths
        self.categories_file = self.data_directory / "categories.json"
        self.items_file = self.data_directory / "items.json"
        self.sold_trends_file = self.data_directory / "sold_trends.json"
        self.settings_file = self.data_directory / "settings.json"
        
        # Initialize data files if they don't exist
        self.initialize_data_files()
    
    def initialize_data_files(self):
        """Create empty data files if they don't exist"""
        if not self.categories_file.exists():
            self.save_categories([])
        
        if not self.items_file.exists():
            self.save_items([])
        
        if not self.sold_trends_file.exists():
            self.save_sold_trends({"periods": [], "currentPeriodId": None})
        
        if not self.settings_file.exists():
            self.save_settings({"soldCurrency": "GBP"})
    
    # Categories operations
    def load_categories(self):
        """Load categories from file"""
        try:
            if self.categories_file.exists():
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading categories: {e}")
        return []
    
    def save_categories(self, categories):
        """Save categories to file"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving categories: {e}")
            return False
    
    # Items operations
    def load_items(self):
        """Load items from file"""
        try:
            if self.items_file.exists():
                with open(self.items_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading items: {e}")
        return []
    
    def save_items(self, items):
        """Save items to file"""
        try:
            with open(self.items_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving items: {e}")
            return False
    
    # Sold trends operations
    def load_sold_trends(self):
        """Load sold trends from file"""
        try:
            if self.sold_trends_file.exists():
                with open(self.sold_trends_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading sold trends: {e}")
        return {"periods": [], "currentPeriodId": None}
    
    def save_sold_trends(self, data):
        """Save sold trends to file"""
        try:
            with open(self.sold_trends_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving sold trends: {e}")
            return False
    
    # Settings operations
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {"soldCurrency": "GBP"}
    
    def save_settings(self, settings):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_data_directory(self):
        """Get the data directory path"""
        return str(self.data_directory)





