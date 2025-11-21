"""
Main Window
The primary application interface - matches HTML layout exactly
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from pathlib import Path
from app.views.home_view import HomeView
from app.views.listings_view import ListingsView
from app.views.ended_items_view import EndedItemsView
from app.views.sold_trends_view import SoldTrendsView
from app.views.settings_view import SettingsView
from app.utils import add_context_menu


class MainWindow:
    """Main application window"""
    
    def __init__(self, root, data_manager):
        self.root = root
        self.data_manager = data_manager
        
        # Current view name
        self.current_view_name = None
        self.views = {}
        self.view_frames = {}  # Store frame containers for each view
        
        self.setup_ui()
        self.show_home()
    
    def setup_ui(self):
        """Setup the main UI - matching HTML structure"""
        # Create top border with logo and beta banner (like HTML)
        top_border = tk.Frame(self.root, bg="white", height=96)
        top_border.pack(fill=tk.X, side=tk.TOP)
        top_border.pack_propagate(False)
        
        # Left spacer for flexbox-like layout
        left_spacer = tk.Frame(top_border, bg="white")
        left_spacer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Logo (centered) - load logo image
        logo_path = Path(__file__).parent / "assets" / "listinglife-logo.png"
        
        # Try to load logo image, fallback to text if not found
        try:
            if logo_path.exists():
                self.logo_image = tk.PhotoImage(file=str(logo_path))
                # Resize logo to fit top border height (keeping aspect ratio)
                logo_height = 68  # Matching HTML max-height
                original_width = self.logo_image.width()
                original_height = self.logo_image.height()
                aspect_ratio = original_width / original_height
                logo_width = int(logo_height * aspect_ratio)
                
                self.logo_image = self.logo_image.subsample(
                    max(1, original_width // logo_width),
                    max(1, original_height // logo_height)
                )
                
                logo_label = tk.Label(
                    top_border,
                    image=self.logo_image,
                    bg="white",
                    cursor="hand2"
                )
                logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                logo_label.bind("<Button-1>", lambda e: self.show_home())
                logo_label.image = self.logo_image  # Keep a reference
            else:
                # Fallback to text if logo not found
                logo_label = tk.Label(
                    top_border,
                    text="ListingLife",
                    font=("Segoe UI", 20, "bold"),
                    bg="white",
                    fg="#2c3e50",
                    cursor="hand2"
                )
                logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                logo_label.bind("<Button-1>", lambda e: self.show_home())
        except Exception as e:
            # Fallback to text if image loading fails
            print(f"Error loading logo: {e}")
            logo_label = tk.Label(
                top_border,
                text="ListingLife",
                font=("Segoe UI", 20, "bold"),
                bg="white",
                fg="#2c3e50",
                cursor="hand2"
            )
            logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            logo_label.bind("<Button-1>", lambda e: self.show_home())
        
        # Beta banner (right side)
        beta_label = tk.Label(
            top_border,
            text="Early Access",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#dc2626",
            justify=tk.RIGHT
        )
        beta_label.pack(side=tk.RIGHT, padx=12, pady=12)
        
        # Main container
        main_container = tk.Frame(self.root, bg="#F4F3F2")
        main_container.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # Sidebar navigation (fixed on left, like HTML) - expanded by 5% for better text visibility
        self.sidebar = tk.Frame(main_container, bg="#d4d2d2", width=168)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Add padding at top for logo space (96px matching HTML)
        top_spacer = tk.Frame(self.sidebar, bg="#d4d2d2", height=96)
        top_spacer.pack(fill=tk.X, side=tk.TOP)
        top_spacer.pack_propagate(False)
        
        # Sidebar buttons container
        sidebar_buttons = tk.Frame(self.sidebar, bg="#d4d2d2")
        sidebar_buttons.pack(fill=tk.X, padx=20, pady=32)
        
        # Navigation buttons - matching HTML exactly
        nav_configs = [
            ("Home", "home"),
            ("ListingLife", "listings"),
            ("Items Ended", "ended"),
            ("Sold Items Trends", "sold"),
            ("Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for i, (text, view_name) in enumerate(nav_configs):
            # Add separator between buttons (like HTML)
            if i > 0:
                separator = tk.Frame(sidebar_buttons, bg="#b0b0b0", height=1)
                separator.pack(fill=tk.X, pady=(12, 0))
            
            btn = tk.Button(
                sidebar_buttons,
                text=text.upper(),
                command=self._create_nav_command(view_name),
                font=("Segoe UI", 15, "bold"),
                bg="#d4d2d2",
                fg="#1f2937",
                activebackground="#a4a2a2",
                activeforeground="#111827",
                relief=tk.FLAT,
                anchor=tk.W,
                padx=0,
                pady=4,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=0)
            self.nav_buttons[view_name] = btn
        
        # Store selector section at bottom of sidebar (matching HTML)
        store_selector_frame = tk.Frame(self.sidebar, bg="#d4d2d2")
        store_selector_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(20, 32))
        
        # Store label
        store_label = tk.Label(
            store_selector_frame,
            text="Store",
            font=("Segoe UI", 10),
            bg="#d4d2d2",
            fg="#4b5563"
        )
        store_label.pack(anchor=tk.W, pady=(0, 4))
        
        # Store dropdown
        self.store_var = tk.StringVar()
        self.store_dropdown = ttk.Combobox(
            store_selector_frame,
            textvariable=self.store_var,
            font=("Segoe UI", 11),
            state="readonly",
            width=18
        )
        self.store_dropdown.pack(fill=tk.X, pady=(0, 8))
        self.store_dropdown.bind("<<ComboboxSelected>>", self.on_store_change)
        
        # Manage button
        manage_store_btn = tk.Button(
            store_selector_frame,
            text="Manage",
            command=self.show_store_management,
            font=("Segoe UI", 10),
            bg="#0064d3",
            fg="white",
            padx=12,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT
        )
        manage_store_btn.pack(fill=tk.X)
        
        # Content area (right side, like HTML)
        self.content_area = tk.Frame(main_container, bg="#F4F3F2")
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create view frames (but don't show them yet)
        self.view_frames["home"] = tk.Frame(self.content_area, bg="#F4F3F2")
        self.view_frames["listings"] = tk.Frame(self.content_area, bg="#F4F3F2")
        self.view_frames["ended"] = tk.Frame(self.content_area, bg="#F4F3F2")
        self.view_frames["sold"] = tk.Frame(self.content_area, bg="#F4F3F2")
        self.view_frames["settings"] = tk.Frame(self.content_area, bg="#F4F3F2")
        
        # Initialize views with their frames
        self.views["home"] = HomeView(self.view_frames["home"], self.data_manager, self)
        self.views["listings"] = ListingsView(self.view_frames["listings"], self.data_manager, self)
        self.views["ended"] = EndedItemsView(self.view_frames["ended"], self.data_manager, self)
        self.views["sold"] = SoldTrendsView(self.view_frames["sold"], self.data_manager, self)
        self.views["settings"] = SettingsView(self.view_frames["settings"], self.data_manager, self)
        
        # Initialize store management
        self.initialize_store_manager()
    
    def _create_nav_command(self, view_name):
        """Create a proper closure for navigation button commands"""
        def nav_command():
            self.switch_view(view_name)
        return nav_command
    
    def switch_view(self, view_name):
        """Switch to a different view - only one visible at a time"""
        print(f"DEBUG: Switching to view: {view_name}")
        
        # Hide ALL views first
        for name, frame in self.view_frames.items():
            frame.pack_forget()
        
        # Update navigation button states
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.config(bg="#a4a2a2", fg="#111827")
            else:
                btn.config(bg="#d4d2d2", fg="#1f2937")
        
        # Show the selected view
        if view_name in self.view_frames:
            self.view_frames[view_name].pack(fill=tk.BOTH, expand=True)
            self.current_view_name = view_name
            
            # Refresh view data if needed
            if view_name in self.views:
                view = self.views[view_name]
                if hasattr(view, 'refresh'):
                    view.refresh()
            
            print(f"DEBUG: View '{view_name}' is now visible")
        else:
            print(f"DEBUG: ERROR - View '{view_name}' not found!")
    
    def show_home(self):
        """Show home view"""
        self.switch_view("home")
    
    def show_listings(self):
        """Show listings view"""
        self.switch_view("listings")
    
    def show_ended(self):
        """Show ended items view"""
        self.switch_view("ended")
    
    def show_sold_trends(self):
        """Show sold trends view"""
        self.switch_view("sold")
    
    def show_settings(self):
        """Show settings view"""
        self.switch_view("settings")
    
    def update_shop_dropdown(self):
        """Update the shop/directory dropdown with available directories"""
        # For now, just show the current directory
        # In the future, you could scan for multiple shop directories
        if self.data_manager:
            current_dir = self.data_manager.get_data_directory()
            dir_name = current_dir.split('\\')[-1] if '\\' in current_dir else current_dir.split('/')[-1]
            if not dir_name:
                dir_name = current_dir
            
            shops = [dir_name]
            self.shop_dropdown['values'] = shops
            self.shop_var.set(dir_name)
    
    def initialize_store_manager(self):
        """Initialize store manager and load stores"""
        from app.store_manager import StoreManager
        self.store_manager = StoreManager(self.data_manager)
        self.update_store_dropdown()
    
    def update_store_dropdown(self):
        """Update the store dropdown with available stores"""
        if hasattr(self, 'store_dropdown') and hasattr(self, 'store_manager'):
            stores = self.store_manager.get_stores()
            store_names = [s['name'] for s in stores]
            self.store_dropdown['values'] = store_names
            
            current_store = self.store_manager.get_current_store()
            if current_store:
                self.store_var.set(current_store['name'])
    
    def on_store_change(self, event=None):
        """Handle store change"""
        selected_name = self.store_var.get()
        if selected_name:
            self.store_manager.switch_store_by_name(selected_name)
            # Refresh all views
            for view_name, view in self.views.items():
                if hasattr(view, 'refresh'):
                    view.refresh()
    
    def show_store_management(self):
        """Show store management modal"""
        StoreManagementDialog(self.root, self.store_manager, self)


class StoreManagementDialog:
    """Dialog for managing stores"""
    
    def __init__(self, parent, store_manager, main_window):
        self.parent = parent
        self.store_manager = store_manager
        self.main_window = main_window
        self.editing_store_id = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage Stores")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (500 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (500 // 2) + parent.winfo_y()
        self.dialog.geometry(f"500x500+{x}+{y}")
        
        self.setup_ui()
        self.render_stores_list()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="Manage Stores",
            font=("Segoe UI", 18, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Stores list frame with scrollbar
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stores_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            yscrollcommand=scrollbar.set
        )
        self.stores_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stores_listbox.yview)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.dialog, pady=20)
        buttons_frame.pack()
        
        add_btn = tk.Button(
            buttons_frame,
            text="Add Store",
            command=self.open_store_form,
            font=("Segoe UI", 11),
            bg="#0064d3",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(
            buttons_frame,
            text="Edit",
            command=self.edit_selected_store,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def render_stores_list(self):
        """Render list of stores"""
        self.stores_listbox.delete(0, tk.END)
        stores = self.store_manager.get_stores()
        
        for store in stores:
            current_marker = " (Current)" if store['id'] == self.store_manager.get_current_store_id() else ""
            self.stores_listbox.insert(tk.END, f"{store['name']}{current_marker}")
    
    def open_store_form(self, store_id=None):
        """Open store form dialog"""
        StoreFormDialog(self.dialog, self.store_manager, self.main_window, self, store_id)
    
    def edit_selected_store(self):
        """Edit selected store"""
        selection = self.stores_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a store to edit.")
            return
        
        index = selection[0]
        stores = self.store_manager.get_stores()
        if index < len(stores):
            store_id = stores[index]['id']
            self.open_store_form(store_id)


class StoreFormDialog:
    """Dialog for adding/editing a store"""
    
    def __init__(self, parent, store_manager, main_window, management_dialog=None, store_id=None):
        self.parent = parent
        self.store_manager = store_manager
        self.main_window = main_window
        self.management_dialog = management_dialog
        self.store_id = store_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Store" if not store_id else "Edit Store")
        self.dialog.geometry("450x280")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (450 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (280 // 2) + parent.winfo_y()
        self.dialog.geometry(f"450x280+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title_text = "Add Store" if not self.store_id else "Edit Store"
        title_label = tk.Label(
            self.dialog,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            pady=15
        )
        title_label.pack()
        
        # Form frame
        form_frame = tk.Frame(self.dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store name
        tk.Label(form_frame, text="Store Name", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        
        if self.store_id:
            store = next((s for s in self.store_manager.get_stores() if s['id'] == self.store_id), None)
            if store:
                self.name_var.set(store['name'])
        
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, font=("Segoe UI", 11), width=40)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        add_context_menu(name_entry)
        
        # Buttons
        buttons_frame = tk.Frame(self.dialog, pady=15)
        buttons_frame.pack()
        
        if self.store_id and len(self.store_manager.get_stores()) > 1:
            delete_btn = tk.Button(
                buttons_frame,
                text="Delete",
                command=self.delete_store,
                font=("Segoe UI", 11),
                bg="#e53238",
                fg="white",
                padx=15,
                pady=6,
                cursor="hand2"
            )
            delete_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Save",
            command=self.save_store,
            font=("Segoe UI", 11, "bold"),
            bg="#0064d3",
            fg="white",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
    
    def save_store(self):
        """Save store"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a store name.")
            return
        
        if self.store_id:
            # Update existing store
            if not self.store_manager.update_store(self.store_id, name=name):
                messagebox.showerror("Error", "A store with this name already exists.")
                return
            messagebox.showinfo("Success", "Store updated successfully.")
        else:
            # Add new store
            if not self.store_manager.add_store(name):
                messagebox.showerror("Error", "A store with this name already exists.")
                return
            messagebox.showinfo("Success", "Store created successfully.")
        
        # Refresh dropdown and management dialog
        if self.main_window:
            self.main_window.update_store_dropdown()
        if self.management_dialog:
            self.management_dialog.render_stores_list()
        
        self.dialog.destroy()
    
    def delete_store(self):
        """Delete store"""
        if not self.store_id:
            return
        
        if len(self.store_manager.get_stores()) <= 1:
            messagebox.showwarning("Cannot Delete", "Cannot delete the only store. Please create another store first.")
            return
        
        store = next((s for s in self.store_manager.get_stores() if s['id'] == self.store_id), None)
        if not store:
            return
        
        if not messagebox.askyesno(
            "Delete Store",
            f'Are you sure you want to delete "{store["name"]}"?\n\n'
            'This will permanently delete all data for this store including listings, '
            'ended items, sold trends, and settings.'
        ):
            return
        
        if not self.store_manager.delete_store(self.store_id):
            messagebox.showerror("Error", "Failed to delete store.")
            return
        
        messagebox.showinfo("Success", "Store deleted successfully.")
        
        # Refresh dropdown and close management dialog if open
        if self.main_window:
            self.main_window.update_store_dropdown()
        if self.management_dialog:
            self.management_dialog.render_stores_list()
        
        self.dialog.destroy()
