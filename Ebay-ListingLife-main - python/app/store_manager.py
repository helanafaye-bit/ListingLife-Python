"""
Store Manager
Handles store/directory management similar to HTML version
"""

import json
import os
from pathlib import Path
from datetime import datetime


class StoreManager:
    """Manages multiple stores/directories"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.config_file = Path.home() / ".listinglife_stores.json"
        self.stores = []
        self.current_store_id = None
        
        self.load_stores()
        self.load_current_store()
    
    def load_stores(self):
        """Load stores from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.stores = config.get('stores', [])
            
            # If no stores exist, create a default store based on current directory
            if not self.stores:
                current_dir = self.data_manager.get_data_directory()
                dir_name = os.path.basename(current_dir) or "Default Store"
                
                default_store = {
                    'id': 'default',
                    'name': dir_name,
                    'directory': current_dir,
                    'createdAt': datetime.now().isoformat()
                }
                self.stores = [default_store]
                self.save_stores()
        except Exception as e:
            print(f"Error loading stores: {e}")
            # Create default store on error
            current_dir = self.data_manager.get_data_directory()
            dir_name = os.path.basename(current_dir) or "Default Store"
            self.stores = [{
                'id': 'default',
                'name': dir_name,
                'directory': current_dir,
                'createdAt': datetime.now().isoformat()
            }]
            self.save_stores()
    
    def save_stores(self):
        """Save stores to config file"""
        try:
            config = {
                'stores': self.stores,
                'currentStoreId': self.current_store_id
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving stores: {e}")
            return False
    
    def load_current_store(self):
        """Load current store from config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_store_id = config.get('currentStoreId')
                    
                    # Verify store still exists
                    if self.current_store_id and not any(s['id'] == self.current_store_id for s in self.stores):
                        self.current_store_id = self.stores[0]['id'] if self.stores else None
                        self.save_stores()
            else:
                # Set first store as current
                if self.stores:
                    self.current_store_id = self.stores[0]['id']
                    self.save_stores()
        except Exception as e:
            print(f"Error loading current store: {e}")
            if self.stores:
                self.current_store_id = self.stores[0]['id']
    
    def get_stores(self):
        """Get all stores"""
        return self.stores.copy()
    
    def get_current_store(self):
        """Get current store"""
        if not self.current_store_id:
            return self.stores[0] if self.stores else None
        
        for store in self.stores:
            if store['id'] == self.current_store_id:
                return store
        return self.stores[0] if self.stores else None
    
    def get_current_store_id(self):
        """Get current store ID"""
        return self.current_store_id or (self.stores[0]['id'] if self.stores else 'default')
    
    def add_store(self, name, directory=None):
        """Add a new store"""
        if not name or not name.strip():
            return False
        
        # Check if name already exists
        if any(s['name'].lower() == name.lower() for s in self.stores):
            return False
        
        # Create directory if not provided
        if not directory:
            base_dir = Path.home() / "ListingLife" / name
            directory = str(base_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
        
        new_store = {
            'id': f"store-{int(datetime.now().timestamp() * 1000)}",
            'name': name.strip(),
            'directory': directory,
            'createdAt': datetime.now().isoformat()
        }
        
        self.stores.append(new_store)
        return self.save_stores()
    
    def update_store(self, store_id, name=None, directory=None):
        """Update an existing store"""
        store = next((s for s in self.stores if s['id'] == store_id), None)
        if not store:
            return False
        
        if name:
            # Check if name already exists (excluding current store)
            if any(s['id'] != store_id and s['name'].lower() == name.lower() for s in self.stores):
                return False
            store['name'] = name.strip()
        
        if directory:
            store['directory'] = directory
        
        store['updatedAt'] = datetime.now().isoformat()
        return self.save_stores()
    
    def delete_store(self, store_id):
        """Delete a store"""
        if len(self.stores) <= 1:
            return False  # Can't delete the only store
        
        # Remove store from list
        self.stores = [s for s in self.stores if s['id'] != store_id]
        
        # If deleted store was current, switch to first available
        if self.current_store_id == store_id:
            self.current_store_id = self.stores[0]['id'] if self.stores else None
        
        return self.save_stores()
    
    def switch_store(self, store_id):
        """Switch to a different store"""
        store = next((s for s in self.stores if s['id'] == store_id), None)
        if not store:
            return False
        
        self.current_store_id = store_id
        return self.save_stores()
    
    def switch_store_by_name(self, name):
        """Switch store by name"""
        store = next((s for s in self.stores if s['name'] == name), None)
        if store:
            return self.switch_store(store['id'])
        return False
    
    def get_store_directory(self, store_id=None):
        """Get directory path for a store"""
        if not store_id:
            store_id = self.get_current_store_id()
        
        store = next((s for s in self.stores if s['id'] == store_id), None)
        if store:
            return store.get('directory')
        return None


