"""
Directory Setup Dialog
Allows users to select where to save their data (local or Dropbox)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from app.data_manager import DataManager


class DirectorySetup:
    """Dialog for selecting data storage directory"""
    
    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Welcome to ListingLife")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 550)
        
        # Center the dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (700 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (600 // 2) + parent.winfo_y()
        self.dialog.geometry(f"700x600+{x}+{y}")
        
        self.selected_directory = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI for directory selection"""
        # Main container with scrollbar capability
        main_container = tk.Frame(self.dialog, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg="#f0f0f0", pady=25)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Welcome to ListingLife",
            font=("Segoe UI", 22, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Choose where to save your data",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            fg="#6c757d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Scrollable content area
        canvas = tk.Canvas(main_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content_frame = tk.Frame(scrollable_frame, padx=40, pady=25)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        info_label = tk.Label(
            content_frame,
            text="Select a directory to store your listing data:",
            font=("Segoe UI", 10, "bold"),
            justify=tk.LEFT,
            fg="#495057",
            bg="#f0f0f0"
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        info_label2 = tk.Label(
            content_frame,
            text="• Local folder on your computer\n"
                 "• Dropbox folder for cloud sync\n"
                 "• Shared network folder",
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            fg="#495057",
            bg="#f0f0f0"
        )
        info_label2.pack(anchor=tk.W, pady=(0, 20))
        
        # Selected directory display
        dir_display_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, borderwidth=2)
        dir_display_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.dir_label = tk.Label(
            dir_display_frame,
            text="No directory selected",
            font=("Segoe UI", 10),
            fg="#6c757d",
            anchor=tk.W,
            wraplength=600,
            bg="white",
            padx=15,
            pady=12
        )
        self.dir_label.pack(fill=tk.X)
        
        # Buttons frame
        buttons_frame = tk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 25))
        
        browse_btn = tk.Button(
            buttons_frame,
            text="📁 Browse for Folder...",
            command=self.browse_directory,
            font=("Segoe UI", 11),
            bg="#0064d3",
            fg="white",
            padx=25,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick access section
        quick_frame = tk.Frame(content_frame, bg="#f0f0f0")
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        quick_label = tk.Label(
            quick_frame,
            text="Quick Access:",
            font=("Segoe UI", 11, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        quick_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Dropbox button
        dropbox_btn = tk.Button(
            quick_frame,
            text="📁 Use Dropbox Folder",
            command=self.select_dropbox,
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            anchor=tk.W,
            width=35
        )
        dropbox_btn.pack(fill=tk.X, pady=(0, 8))
        
        # Local Documents button
        local_btn = tk.Button(
            quick_frame,
            text="📁 Use Local Documents Folder",
            command=self.select_local_documents,
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            anchor=tk.W,
            width=35
        )
        local_btn.pack(fill=tk.X, pady=(0, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom section with action buttons - FIXED AT BOTTOM
        bottom_frame = tk.Frame(self.dialog, bg="#e8e8e8", pady=20, relief=tk.RAISED, borderwidth=2)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status message on left
        self.status_msg = tk.Label(
            bottom_frame,
            text="⚠ Please select a directory above",
            font=("Segoe UI", 10),
            fg="#6c757d",
            bg="#e8e8e8"
        )
        self.status_msg.pack(side=tk.LEFT, padx=25)
        
        # Button container on right
        btn_container = tk.Frame(bottom_frame, bg="#e8e8e8")
        btn_container.pack(side=tk.RIGHT, padx=25)
        
        cancel_btn = tk.Button(
            btn_container,
            text="Cancel",
            command=self.cancel,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=25,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Start App button - ALWAYS VISIBLE at bottom
        self.continue_btn = tk.Button(
            btn_container,
            text="🚀 START APP",
            command=self.continue_setup,
            font=("Segoe UI", 13, "bold"),
            bg="#86b817",
            fg="white",
            padx=40,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=3,
            state=tk.DISABLED
        )
        self.continue_btn.pack(side=tk.LEFT, padx=5)
        
        # Ensure button is visible
        self.dialog.update_idletasks()
    
    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(
            title="Select Data Directory",
            mustexist=False
        )
        if directory:
            self.select_directory(directory)
    
    def select_dropbox(self):
        """Try to find and select Dropbox folder"""
        # Common Dropbox locations
        possible_paths = [
            Path.home() / "Dropbox",
            Path.home() / "Dropbox (Personal)",
            Path("C:/Users") / os.getenv("USERNAME", "") / "Dropbox",
        ]
        
        # Also check for Dropbox path from info file
        try:
            info_file = Path.home() / "AppData/Roaming/Dropbox/info.json"
            if info_file.exists():
                import json
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    if 'personal' in info:
                        possible_paths.insert(0, Path(info['personal']['path']))
        except Exception:
            pass
        
        dropbox_path = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                dropbox_path = path / "ListingLife"
                break
        
        if dropbox_path:
            self.select_directory(str(dropbox_path))
        else:
            # Let user browse to Dropbox
            messagebox.showinfo(
                "Dropbox Not Found",
                "Could not automatically find your Dropbox folder.\n"
                "Please browse to your Dropbox folder manually."
            )
            self.browse_directory()
    
    def select_local_documents(self):
        """Select local Documents folder"""
        documents_path = Path.home() / "Documents" / "ListingLife"
        self.select_directory(str(documents_path))
    
    def select_directory(self, directory):
        """Select and validate directory"""
        try:
            # Create directory if it doesn't exist
            Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = Path(directory) / ".test_write"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                raise Exception(f"Directory is not writable: {e}")
            
            # Success - directory is valid
            self.selected_directory = directory
            
            # Update directory label with checkmark
            self.dir_label.config(
                text=f"✓ SELECTED: {directory}",
                fg="#0064d3",
                font=("Segoe UI", 10, "bold"),
                bg="#e6f3ff"
            )
            
            # CRITICAL: Enable the Start App button
            self.continue_btn.config(
                state=tk.NORMAL,
                cursor="hand2",
                bg="#86b817",
                fg="white",
                activebackground="#95c92b",
                relief=tk.RAISED,
                borderwidth=4
            )
            
            # Update status message
            self.status_msg.config(
                text="✓ Ready! Click 'START APP' →",
                fg="#86b817",
                font=("Segoe UI", 10, "bold")
            )
            
            # Force immediate UI update
            self.dialog.update_idletasks()
            self.dialog.update()
            
            # Focus the button
            self.continue_btn.focus_set()
            
            print(f"DEBUG: Directory selected: {directory}")
            print(f"DEBUG: Button state set to: {self.continue_btn['state']}")
            print(f"DEBUG: Button visible: {self.continue_btn.winfo_viewable()}")
            
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror(
                "Error",
                f"Could not use this directory:\n{error_msg}\n\nPlease select a different location."
            )
            self.selected_directory = None
            self.continue_btn.config(state=tk.DISABLED)
            self.status_msg.config(
                text="❌ Error: Please select a valid directory",
                fg="#e53238"
            )
            print(f"DEBUG: Error selecting directory: {e}")
    
    def continue_setup(self):
        """Continue with selected directory and start the app"""
        print(f"DEBUG: continue_setup called, selected_directory: {self.selected_directory}")
        if self.selected_directory:
            try:
                # Save directory and set it on the app
                self.app.save_data_directory(self.selected_directory)
                self.app.data_directory = self.selected_directory
                print(f"DEBUG: Directory saved: {self.selected_directory}")
                
                # Just close the dialog - main.py will handle the rest
                self.dialog.destroy()
                print("DEBUG: Dialog closed, main.py should now open main window")
            except Exception as e:
                import traceback
                error_msg = f"Error saving directory:\n{str(e)}\n\n{traceback.format_exc()}"
                print(f"DEBUG: {error_msg}")
                messagebox.showerror("Error", error_msg)
        else:
            messagebox.showwarning("No Directory Selected", "Please select a directory first.")
    
    def cancel(self):
        """Cancel directory selection"""
        self.selected_directory = None
        self.dialog.destroy()
