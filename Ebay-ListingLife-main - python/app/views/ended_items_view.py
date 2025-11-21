"""
Ended Items View
View for items that have ended
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class EndedItemsView:
    """View for ended items"""
    
    def __init__(self, parent, data_manager, main_window):
        self.parent = parent
        self.data_manager = data_manager
        self.main_window = main_window
        
        self.categories = []
        self.items = []
        
        self.setup_ui()
        self.load_data()
        self.render_ended_items()
    
    def setup_ui(self):
        """Setup the ended items view UI"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        container = tk.Frame(self.parent, bg="#F4F3F2")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(container, bg="white", padx=30, pady=20)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Items Ended (0 Days Left)",
            font=("Segoe UI", 28, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
        
        back_btn = tk.Button(
            header_frame,
            text="← Back to Categories",
            command=self.main_window.show_listings,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        back_btn.pack(side=tk.RIGHT)
        
        # Content area
        self.content_frame = tk.Frame(container, bg="#F4F3F2", padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Load categories and items"""
        self.categories = self.data_manager.load_categories()
        self.items = self.data_manager.load_items()
    
    def calculate_days_left(self, item):
        """Calculate days remaining for an item"""
        if item.get('manuallyEnded'):
            return 0
        
        date_added = item.get('dateAdded')
        duration = item.get('duration', 30)
        
        if not date_added:
            return 0
        
        try:
            added_date = datetime.strptime(date_added, '%Y-%m-%d')
            end_date = added_date + timedelta(days=duration)
            days_left = (end_date - datetime.now()).days
            return days_left
        except Exception:
            return 0
    
    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return 'Unknown'
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            return date.strftime('%b %d, %Y')
        except Exception:
            return date_string
    
    def render_ended_items(self):
        """Render ended items list"""
        # Clear display
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Filter ended items
        ended_items = [
            item for item in self.items
            if self.calculate_days_left(item) <= 0
        ]
        
        if not ended_items:
            empty_label = tk.Label(
                self.content_frame,
                text="No ended items\nAll your items are still active!",
                font=("Segoe UI", 14),
                bg="#F4F3F2",
                fg="#6c757d"
            )
            empty_label.pack(expand=True)
            return
        
        # Scrollable items list
        canvas = tk.Canvas(self.content_frame, bg="#F4F3F2", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F4F3F2")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for item in ended_items:
            item_frame = self.create_item_card(scrollable_frame, item)
            item_frame.pack(fill=tk.X, padx=10, pady=5)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_item_card(self, parent, item):
        """Create an item card widget"""
        card = tk.Frame(
            parent,
            bg="#f8f9fa",
            relief=tk.RAISED,
            borderwidth=1,
            padx=20,
            pady=15
        )
        
        # Left side - info
        info_frame = tk.Frame(card, bg="#f8f9fa")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Item name
        name_label = tk.Label(
            info_frame,
            text=item.get('name', 'Unnamed'),
            font=("Segoe UI", 16, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50",
            anchor=tk.W
        )
        name_label.pack(fill=tk.X, pady=(0, 5))
        
        # Category
        category = next((c for c in self.categories if c.get('id') == item.get('categoryId')), None)
        category_name = category.get('name', 'Unknown') if category else 'Unknown'
        category_label = tk.Label(
            info_frame,
            text=f"Category: {category_name} | Added: {self.format_date(item.get('dateAdded', ''))}",
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            fg="#6c757d",
            anchor=tk.W
        )
        category_label.pack(fill=tk.X, pady=(0, 5))
        
        # Status
        status_text = "Manually Ended" if item.get('manuallyEnded') else "Ended"
        status_label = tk.Label(
            info_frame,
            text=status_text,
            font=("Segoe UI", 11, "bold"),
            bg="#f8f9fa",
            fg="#6b7280",
            anchor=tk.W
        )
        status_label.pack(fill=tk.X)
        
        # Right side - actions
        actions_frame = tk.Frame(card, bg="#f8f9fa")
        actions_frame.pack(side=tk.RIGHT)
        
        edit_btn = tk.Button(
            actions_frame,
            text="Edit",
            command=lambda i=item: self.edit_item(i),
            font=("Segoe UI", 10),
            bg="#0064d3",
            fg="white",
            padx=12,
            pady=5,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(
            actions_frame,
            text="Delete",
            command=lambda i=item: self.delete_item(i),
            font=("Segoe UI", 10),
            bg="#e53238",
            fg="white",
            padx=12,
            pady=5,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        return card
    
    def edit_item(self, item):
        """Edit an item (opens in listings view)"""
        from app.views.listings_view import ItemDialog
        dialog = ItemDialog(self.parent, self.data_manager, self.main_window.views["listings"], item)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        self.render_ended_items()
    
    def delete_item(self, item):
        """Delete an item"""
        if messagebox.askyesno(
            "Delete Item",
            f"Are you sure you want to delete '{item.get('name')}'?"
        ):
            items = self.data_manager.load_items()
            items = [i for i in items if i.get('id') != item.get('id')]
            self.data_manager.save_items(items)
            self.load_data()
            self.render_ended_items()
    
    def refresh(self):
        """Refresh the view"""
        self.load_data()
        self.render_ended_items()

