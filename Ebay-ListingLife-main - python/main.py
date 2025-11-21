#!/usr/bin/env python3
"""
ListingLife - eBay Listing Management Application
A Python desktop application for managing eBay listings, categories, and tracking sold items.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Import application modules
from app.directory_setup import DirectorySetup
from app.main_window import MainWindow
from app.data_manager import DataManager


class ListingLifeApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ListingLife")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Data directory path
        self.data_directory = None
        self.data_manager = None
        self.main_window = None
        
        # Check for saved data directory
        self.load_data_directory()
        
        # If no directory is set or doesn't exist, show directory selection dialog
        if not self.data_directory or not os.path.exists(self.data_directory):
            self.show_directory_setup()
            # After dialog closes, reload directory in case it was just saved
            self.load_data_directory()
        
        # Initialize data manager and show main window
        if self.data_directory and os.path.exists(self.data_directory):
            try:
                print(f"DEBUG: Initializing with directory: {self.data_directory}")
                self.data_manager = DataManager(self.data_directory)
                print("DEBUG: Data manager initialized")
                self.show_main_window()
                print("DEBUG: Main window shown")
            except Exception as e:
                import traceback
                error_msg = f"Error initializing application:\n{str(e)}\n\n{traceback.format_exc()}"
                print(error_msg)
                try:
                    messagebox.showerror("Error", error_msg)
                except:
                    pass
                # Reset directory and show setup again
                self.data_directory = None
                self.show_directory_setup()
        else:
            # User cancelled directory selection or directory doesn't exist
            print("DEBUG: No valid directory selected, closing application")
            self.root.quit()
    
    def load_data_directory(self):
        """Load saved data directory from user's home directory"""
        config_file = Path.home() / ".listinglife_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.data_directory = config.get('data_directory')
            except Exception:
                self.data_directory = None
    
    def save_data_directory(self, directory):
        """Save data directory to config file"""
        config_file = Path.home() / ".listinglife_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump({'data_directory': directory}, f)
            self.data_directory = directory
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save directory preference: {e}")
    
    def show_directory_setup(self):
        """Show directory selection dialog"""
        setup = DirectorySetup(self.root, self)
        self.root.wait_window(setup.dialog)
    
    def show_main_window(self):
        """Show the main application window"""
        try:
            # Clear any existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Make sure root window is visible before creating main window
            self.root.deiconify()
            self.root.update_idletasks()
            
            # Create main window
            print("DEBUG: Creating MainWindow object...")
            self.main_window = MainWindow(self.root, self.data_manager)
            print("DEBUG: MainWindow object created")
            
            # Ensure root window is visible and on top
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            print("DEBUG: Main window created and made visible")
        except Exception as e:
            import traceback
            error_msg = f"Error showing main window:\n{str(e)}\n\n{traceback.format_exc()}"
            print(f"DEBUG: {error_msg}")
            try:
                # Create a minimal error window
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror("Error", error_msg)
                error_root.destroy()
            except:
                pass
            # Re-raise or handle as needed
            raise
    
    def run(self):
        """Start the application"""
        try:
            if self.data_directory and self.data_manager:
                print("DEBUG: Starting application main loop")
                self.root.mainloop()
            else:
                print("DEBUG: No valid data directory or manager, not starting main loop")
                self.root.quit()
        except Exception as e:
            import traceback
            error_msg = f"Error running application:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)


def main():
    """Entry point"""
    try:
        app = ListingLifeApp()
        app.run()
    except Exception as e:
        import traceback
        error_msg = f"Fatal error starting application:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # Try to show error in a message box if tkinter is working
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Fatal Error", error_msg)
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

