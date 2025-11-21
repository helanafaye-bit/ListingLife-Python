"""
Listings View
Main view for managing categories and items - matching HTML version exactly
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
from app.utils import add_context_menu


class ListingsView:
    """View for managing listings"""
    
    def __init__(self, parent, data_manager, main_window):
        self.parent = parent
        self.data_manager = data_manager
        self.main_window = main_window
        
        self.categories = []
        self.items = []
        self.current_view_mode = "categories"  # "categories" or "items"
        self.selected_category_id = None
        self.sidebar_mode = "recent"  # "recent" or "ending"
        self.sort_var = tk.StringVar(value="newest")
        self.floating_add_btn = None
        
        self.setup_ui()
        self.load_data()
        self.render_categories()
    
    def setup_ui(self):
        """Setup the listings view UI - matching HTML layout exactly"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container (matching HTML .container)
        container = tk.Frame(self.parent, bg="#F4F3F2")
        container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Header (matching HTML header with search)
        header_frame = tk.Frame(
            container,
            bg="white",
            padx=30,
            pady=30
        )
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="ListingLife",
            font=("Segoe UI", 40, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack()
        
        # Search container (centered, matching HTML)
        search_container = tk.Frame(header_frame, bg="white")
        search_container.pack(pady=(20, 0))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=("Segoe UI", 16),
            width=35,
            relief=tk.SOLID,
            borderwidth=2
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.insert(0, "Search items... (e.g., 'Glass plate')")
        search_entry.config(fg="gray")
        search_entry.bind("<Return>", lambda e: self.search_items())
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search items... (e.g., 'Glass plate')" else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search items... (e.g., 'Glass plate')") if not search_entry.get() else None)
        add_context_menu(search_entry)
        
        search_btn = tk.Button(
            search_container,
            text="Search",
            command=self.search_items,
            font=("Segoe UI", 16, "bold"),
            bg="#0064d3",
            fg="white",
            padx=24,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        search_btn.pack(side=tk.LEFT)
        
        # Main layout (matching HTML .main-layout)
        self.main_layout = tk.Frame(container, bg="#F4F3F2")
        self.main_layout.pack(fill=tk.BOTH, expand=True)
        
        # Main content area (matching HTML .main-content)
        self.display_frame = tk.Frame(self.main_layout, bg="#F4F3F2")
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Add section buttons (matching HTML .add-section)
        add_section = tk.Frame(self.display_frame, bg="#F4F3F2")
        add_section.pack(fill=tk.X, pady=(0, 20))
        
        add_category_btn = tk.Button(
            add_section,
            text="Add New Category",
            command=self.add_category,
            font=("Segoe UI", 16, "bold"),
            bg="#0064d3",
            fg="white",
            padx=24,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_category_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        add_item_btn = tk.Button(
            add_section,
            text="Add New Item",
            command=self.add_item,
            font=("Segoe UI", 16, "bold"),
            bg="#f7f7f7",
            fg="#333333",
            padx=24,
            pady=12,
            relief=tk.SOLID,
            borderwidth=1,
            cursor="hand2"
        )
        add_item_btn.pack(side=tk.LEFT)
        
        # Sidebar (matching HTML .sidebar)
        self.sidebar_frame = tk.Frame(
            self.main_layout,
            bg="white",
            padx=20,
            pady=20,
            width=320
        )
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar_frame, bg="white")
        sidebar_header.pack(fill=tk.X, pady=(0, 15))
        
        self.sidebar_title = tk.Label(
            sidebar_header,
            text="Recently Added Items",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#1f2937",
            anchor=tk.W
        )
        self.sidebar_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Sidebar toggle buttons (matching HTML .sidebar-toggle)
        toggle_frame = tk.Frame(sidebar_header, bg="white")
        toggle_frame.pack(fill=tk.X)
        
        self.recent_toggle = tk.Button(
            toggle_frame,
            text="Recent",
            command=lambda: self.set_sidebar_mode("recent"),
            font=("Segoe UI", 12),
            bg="#0064d3",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.recent_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.ending_toggle = tk.Button(
            toggle_frame,
            text="Ending Soon",
            command=lambda: self.set_sidebar_mode("ending"),
            font=("Segoe UI", 12),
            bg="#f8f9fa",
            fg="#333333",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.ending_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Urgent items list
        self.urgent_items_frame = tk.Frame(self.sidebar_frame, bg="white")
        self.urgent_items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update urgent items
        self.update_urgent_items()
    
    def load_data(self):
        """Load categories and items"""
        self.categories = self.data_manager.load_categories()
        self.items = self.data_manager.load_items()
    
    def save_data(self):
        """Save categories and items"""
        self.data_manager.save_categories(self.categories)
        self.data_manager.save_items(self.items)
    
    def render_categories(self):
        """Render categories grid"""
        self.current_view_mode = "categories"
        self.selected_category_id = None
        
        # Hide floating button when viewing categories
        self.hide_floating_add_button()
        
        # Clear display
        for widget in self.display_frame.winfo_children():
            if widget not in [self.display_frame.winfo_children()[0]]:  # Keep add section
                widget.destroy()
        
        # Create display frame for categories
        categories_display = tk.Frame(self.display_frame, bg="#F4F3F2")
        categories_display.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame
        canvas = tk.Canvas(categories_display, bg="#F4F3F2", highlightthickness=0)
        scrollbar = ttk.Scrollbar(categories_display, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F4F3F2")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Categories grid
        categories_frame = tk.Frame(scrollable_frame, bg="#F4F3F2")
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if not self.categories:
            empty_label = tk.Label(
                categories_frame,
                text="No categories yet\nCreate your first category to start managing your items!",
                font=("Segoe UI", 14),
                bg="#F4F3F2",
                fg="#6c757d"
            )
            empty_label.pack(expand=True)
        else:
            for i, category in enumerate(self.categories):
                category_frame = self.create_category_card(categories_frame, category, i)
                category_frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            
            # Configure grid weights
            for i in range(3):
                categories_frame.grid_columnconfigure(i, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_category_card(self, parent, category, index):
        """Create a category card widget"""
        card = tk.Frame(
            parent,
            bg="#f2f3f4",
            relief=tk.RAISED,
            borderwidth=2,
            padx=25,
            pady=25,
            cursor="hand2"
        )
        
        # Count active items
        active_items = [item for item in self.items 
                       if item.get('categoryId') == category.get('id') 
                       and not item.get('manuallyEnded', False)]
        item_count = len(active_items)
        
        # Category name
        name_label = tk.Label(
            card,
            text=category.get('name', 'Unnamed'),
            font=("Segoe UI", 18, "bold"),
            bg="#f2f3f4",
            fg="#2c3e50"
        )
        name_label.pack(pady=(0, 10))
        
        # Item count
        count_label = tk.Label(
            card,
            text=f"{item_count} item{'s' if item_count != 1 else ''}",
            font=("Segoe UI", 12),
            bg="#f2f3f4",
            fg="#6c757d"
        )
        count_label.pack(pady=(0, 10))
        
        # Description
        if category.get('description'):
            desc_label = tk.Label(
                card,
                text=category.get('description'),
                font=("Segoe UI", 10),
                bg="#f2f3f4",
                fg="#495057",
                wraplength=200
            )
            desc_label.pack(pady=(0, 15))
        
        # Buttons
        buttons_frame = tk.Frame(card, bg="#f2f3f4")
        buttons_frame.pack()
        
        edit_btn = tk.Button(
            buttons_frame,
            text="Edit",
            command=lambda c=category: self.edit_category(c),
            font=("Segoe UI", 10),
            bg="#0064d3",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = tk.Button(
            buttons_frame,
            text="Delete",
            command=lambda c=category: self.delete_category(c),
            font=("Segoe UI", 10),
            bg="#e53238",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT)
        
        # Click handler to view items
        def on_click(event):
            self.show_category_items(category.get('id'))
        
        card.bind("<Button-1>", on_click)
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda e, c=card: on_click(e))
        
        return card
    
    def show_category_items(self, category_id):
        """Show items for a category"""
        self.current_view_mode = "items"
        self.selected_category_id = category_id
        
        # Clear display
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        category = next((c for c in self.categories if c.get('id') == category_id), None)
        if not category:
            return
        
        # Header
        header_frame = tk.Frame(self.display_frame, bg="#F4F3F2")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_btn = tk.Button(
            header_frame,
            text="← Back to Categories",
            command=self.render_categories,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        back_btn.pack(side=tk.LEFT)
        
        # Category title section with sort dropdown (matching HTML)
        title_section = tk.Frame(header_frame, bg="#F4F3F2")
        title_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            title_section,
            text=category.get('name', 'Category'),
            font=("Segoe UI", 24, "bold"),
            bg="#F4F3F2",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Sort dropdown (matching HTML)
        sort_frame = tk.Frame(title_section, bg="#F4F3F2")
        sort_frame.pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar(value="newest|Newest First")
        sort_labels = {
            "newest": "Newest First",
            "oldest": "Oldest First",
            "lowest-days": "Lowest Days Left",
            "highest-days": "Highest Days Left"
        }
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=[f"{val}|{sort_labels[val]}" for val in sort_labels.keys()],
            state="readonly",
            font=("Segoe UI", 11),
            width=18
        )
        sort_combo.pack(side=tk.LEFT, padx=10)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.handle_sort_change())
        
        # Average days display
        avg_days = category.get('averageDays', 30)
        avg_label = tk.Label(
            header_frame,
            text=f"Average: {avg_days} days",
            font=("Segoe UI", 12, "bold"),
            bg="#0064d3",
            fg="white",
            padx=16,
            pady=8,
            cursor="hand2"
        )
        avg_label.pack(side=tk.RIGHT)
        avg_label.bind("<Button-1>", lambda e: self.edit_average_days(category))
        
        # Items list
        category_items = [item for item in self.items 
                          if item.get('categoryId') == category_id 
                          and not item.get('manuallyEnded', False)]
        
        # Create content area for items (or empty message) - leave bottom padding for button
        items_content = tk.Frame(self.display_frame, bg="#F4F3F2")
        items_content.pack(fill=tk.BOTH, expand=True, pady=(0, 80))  # Bottom padding for floating button
        
        if not category_items:
            empty_label = tk.Label(
                items_content,
                text="No active items in this category yet\nAdd your first item to this category!",
                font=("Segoe UI", 14),
                bg="#F4F3F2",
                fg="#6c757d"
            )
            empty_label.pack(expand=True)
        else:
            # Sort items based on current sort selection
            sorted_items = self.sort_items(category_items)
            
            # Scrollable items list
            canvas = tk.Canvas(items_content, bg="#F4F3F2", highlightthickness=0)
            scrollbar = ttk.Scrollbar(items_content, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#F4F3F2")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for item in sorted_items:
                item_frame = self.create_item_card(scrollable_frame, item)
                item_frame.pack(fill=tk.X, padx=10, pady=5)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Force layout update before creating button
        self.display_frame.update_idletasks()
        
        # Create or update floating Add Item button (fixed at bottom center) - after all content
        self.show_floating_add_button()
    
    def show_floating_add_button(self):
        """Show floating Add Item button at bottom center (only when viewing items)"""
        # Hide existing button if any
        self.hide_floating_add_button()
        
        # Only show if we're viewing items within a category
        if self.current_view_mode != "items" or not self.selected_category_id:
            return
        
        # Create floating button (green, white text, fixed at bottom center)
        # Place on display_frame so it's positioned relative to the content area
        self.floating_add_btn = tk.Button(
            self.display_frame,
            text="Add Item",
            command=self.add_item,
            font=("Segoe UI", 16, "bold"),
            bg="#10b981",  # Green color
            fg="white",
            padx=32,
            pady=16,
            relief=tk.FLAT,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0
        )
        
        # Force layout update to get correct dimensions
        self.display_frame.update_idletasks()
        
        # Get display_frame dimensions for positioning
        display_width = self.display_frame.winfo_width()
        display_height = self.display_frame.winfo_height()
        
        # Position at bottom center using place (fixed position)
        # Calculate center X position and bottom Y position
        if display_width > 1 and display_height > 1:
            center_x = display_width / 2
            bottom_y = display_height - 20
            self.floating_add_btn.place(x=center_x, y=bottom_y, anchor=tk.S)
        else:
            # Fallback to relative positioning
            self.floating_add_btn.place(relx=0.5, rely=1.0, anchor=tk.S, y=-20)
        
        # Bring button to front - lift it multiple times to ensure it's visible above all other widgets
        self.floating_add_btn.lift()
        self.floating_add_btn.lift(self.display_frame.winfo_children()[-1] if self.display_frame.winfo_children() else None)
        
        # Update position when display_frame is resized
        def update_button_position(event=None):
            if self.floating_add_btn and self.floating_add_btn.winfo_exists():
                self.floating_add_btn.place(relx=0.5, rely=1.0, anchor=tk.S, y=-20)
                # Keep it on top
                self.floating_add_btn.lift()
        
        # Remove any existing bind to avoid duplicates
        try:
            if hasattr(self, '_button_config_handler'):
                self.display_frame.unbind('<Configure>', self._button_config_handler)
        except:
            pass
        
        # Store handler reference
        self._button_config_handler = update_button_position
        self.display_frame.bind('<Configure>', update_button_position)
        
        # Force the button to be visible by lifting it again after a short delay
        self.display_frame.after(100, lambda: self.floating_add_btn.lift() if self.floating_add_btn else None)
    
    def hide_floating_add_button(self):
        """Hide floating Add Item button"""
        if self.floating_add_btn:
            self.floating_add_btn.destroy()
            self.floating_add_btn = None
    
    def create_item_card(self, parent, item):
        """Create an item card widget - matching HTML layout with photo"""
        card = tk.Frame(
            parent,
            bg="#f8f9fa",
            relief=tk.RAISED,
            borderwidth=1,
            padx=20,
            pady=15,
            cursor="hand2"
        )
        
        # Item photo (matching HTML .item-photo)
        photo_frame = tk.Frame(card, bg="#f8f9fa", width=80, height=80)
        photo_frame.pack(side=tk.LEFT, padx=(0, 15))
        photo_frame.pack_propagate(False)
        
        item_photo = item.get('photo', '')
        if item_photo:
            try:
                # Try to load and display image
                from PIL import Image, ImageTk
                import urllib.request
                import io
                
                # Download image
                with urllib.request.urlopen(item_photo) as response:
                    img_data = response.read()
                
                # Open and resize image
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                
                photo_label = tk.Label(
                    photo_frame,
                    image=photo_img,
                    bg="#f8f9fa"
                )
                photo_label.image = photo_img  # Keep a reference
                photo_label.pack()
            except Exception:
                # Fallback to placeholder if image fails to load
                photo_placeholder = tk.Label(
                    photo_frame,
                    text="📷",
                    font=("Segoe UI", 24),
                    bg="#f8f9fa",
                    fg="#6c757d"
                )
                photo_placeholder.pack(expand=True)
        else:
            # No photo placeholder (matching HTML .item-photo.no-photo)
            photo_placeholder = tk.Label(
                photo_frame,
                text="📷",
                font=("Segoe UI", 24),
                bg="#f8f9fa",
                fg="#6c757d"
            )
            photo_placeholder.pack(expand=True)
        
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
        
        # Date added
        date_added = item.get('dateAdded', '')
        date_label = tk.Label(
            info_frame,
            text=f"Added: {self.format_date(date_added)}",
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            fg="#6c757d",
            anchor=tk.W
        )
        date_label.pack(fill=tk.X, pady=(0, 5))
        
        # Note preview
        note = item.get('note', '')
        if note:
            note_preview = note[:50] + '...' if len(note) > 50 else note
            note_label = tk.Label(
                info_frame,
                text=note_preview,
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#6c757d",
                anchor=tk.W
            )
            note_label.pack(fill=tk.X, pady=(0, 5))
        
        # Days left
        days_left = self.calculate_days_left(item)
        days_text = f"{days_left} days left" if days_left > 0 else "Ended"
        urgency_class = self.get_urgency_class(days_left)
        
        days_label = tk.Label(
            info_frame,
            text=days_text,
            font=("Segoe UI", 11, "bold"),
            bg="#f8f9fa",
            fg=self.get_urgency_color(urgency_class),
            anchor=tk.W
        )
        days_label.pack(fill=tk.X)
        
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
        
        # Mark as Sold button (matching HTML)
        sold_btn = tk.Button(
            actions_frame,
            text="Sold",
            command=lambda i=item: self.mark_as_sold(i),
            font=("Segoe UI", 10),
            bg="#28a745",
            fg="white",
            padx=12,
            pady=5,
            cursor="hand2"
        )
        sold_btn.pack(side=tk.LEFT, padx=2)
        
        end_btn = tk.Button(
            actions_frame,
            text="End",
            command=lambda i=item: self.end_item(i),
            font=("Segoe UI", 10),
            bg="#F5AF02",
            fg="#1f2937",
            padx=12,
            pady=5,
            cursor="hand2"
        )
        end_btn.pack(side=tk.LEFT, padx=2)
        
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
        
        # Click handler to view item
        def on_click(event):
            self.view_item(item)
        
        card.bind("<Button-1>", on_click)
        
        return card
    
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
            return max(0, days_left)
        except Exception:
            return 0
    
    def get_urgency_class(self, days_left):
        """Get urgency class based on days left"""
        if days_left <= 0:
            return 'ended'
        elif days_left <= 3:
            return 'danger'
        elif days_left <= 7:
            return 'warning'
        else:
            return 'normal'
    
    def get_urgency_color(self, urgency_class):
        """Get color for urgency class"""
        colors = {
            'ended': '#6b7280',
            'danger': '#dc2626',
            'warning': '#d97706',
            'normal': '#2563eb'
        }
        return colors.get(urgency_class, '#495057')
    
    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return 'Unknown'
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            return date.strftime('%b %d, %Y')
        except Exception:
            return date_string
    
    def handle_sort_change(self):
        """Handle sort dropdown change"""
        if self.current_view_mode == "items" and self.selected_category_id:
            # Re-render items with new sort order
            self.show_category_items(self.selected_category_id)
    
    def sort_items(self, items):
        """Sort items based on current sort selection"""
        sort_value = self.sort_var.get()
        # Extract sort key from combo value format "newest|Newest First"
        if "|" in sort_value:
            sort_key = sort_value.split("|")[0]
        else:
            sort_key = sort_value
        
        sorted_items = items.copy()
        
        if sort_key == "newest":
            sorted_items.sort(key=lambda x: x.get('dateAdded', ''), reverse=True)
        elif sort_key == "oldest":
            sorted_items.sort(key=lambda x: x.get('dateAdded', ''), reverse=False)
        elif sort_key == "lowest-days":
            sorted_items.sort(key=lambda x: self.calculate_days_left(x))
        elif sort_key == "highest-days":
            sorted_items.sort(key=lambda x: self.calculate_days_left(x), reverse=True)
        else:
            # Default to newest
            sorted_items.sort(key=lambda x: x.get('dateAdded', ''), reverse=True)
        
        return sorted_items
    
    def search_items(self):
        """Search items"""
        search_term = self.search_var.get().strip()
        if search_term and search_term != "Search items... (e.g., 'Glass plate')":
            # Simple search implementation - show matching items
            matching_items = [item for item in self.items 
                             if search_term.lower() in item.get('name', '').lower()
                             or search_term.lower() in item.get('description', '').lower()
                             or search_term.lower() in item.get('note', '').lower()
                             and not item.get('manuallyEnded', False)]
            
            if matching_items:
                # Show search results
                messagebox.showinfo("Search Results", f"Found {len(matching_items)} matching items.")
                # TODO: Display search results
            else:
                messagebox.showinfo("Search Results", "No items found matching your search.")
    
    def set_sidebar_mode(self, mode):
        """Set sidebar mode (recent or ending)"""
        self.sidebar_mode = mode
        if mode == "recent":
            self.recent_toggle.config(bg="#0064d3", fg="white")
            self.ending_toggle.config(bg="#f8f9fa", fg="#333333")
            self.sidebar_title.config(text="Recently Added Items")
        else:
            self.recent_toggle.config(bg="#f8f9fa", fg="#333333")
            self.ending_toggle.config(bg="#0064d3", fg="white")
            self.sidebar_title.config(text="Items Ending Soon")
        self.update_urgent_items()
    
    def update_urgent_items(self):
        """Update urgent items sidebar"""
        # Clear existing items
        for widget in self.urgent_items_frame.winfo_children():
            widget.destroy()
        
        if self.sidebar_mode == "recent":
            # Show items added in the last 7 days (excluding ended items)
            recent_items = sorted(
                [item for item in self.items 
                 if not item.get('manuallyEnded', False)
                 and item.get('dateAdded')],
                key=lambda x: x.get('dateAdded', ''),
                reverse=True
            )[:10]
            
            if not recent_items:
                empty_label = tk.Label(
                    self.urgent_items_frame,
                    text="No recent items",
                    font=("Segoe UI", 12),
                    bg="white",
                    fg="#6c757d"
                )
                empty_label.pack(pady=20)
                return
            
            for item in recent_items:
                item_frame = self.create_urgent_item_card(self.urgent_items_frame, item)
                item_frame.pack(fill=tk.X, pady=5)
        else:
            # Show items ending within 14 days
            ending_items = []
            for item in self.items:
                if not item.get('manuallyEnded', False):
                    days_left = self.calculate_days_left(item)
                    if 0 < days_left <= 14:
                        ending_items.append((item, days_left))
            
            ending_items.sort(key=lambda x: x[1])  # Sort by days left
            ending_items = [item for item, days in ending_items[:10]]
            
            if not ending_items:
                empty_label = tk.Label(
                    self.urgent_items_frame,
                    text="No items ending soon",
                    font=("Segoe UI", 12),
                    bg="white",
                    fg="#6c757d"
                )
                empty_label.pack(pady=20)
                return
            
            for item in ending_items:
                item_frame = self.create_urgent_item_card(self.urgent_items_frame, item)
                item_frame.pack(fill=tk.X, pady=5)
    
    def create_urgent_item_card(self, parent, item):
        """Create an urgent item card for sidebar"""
        item_frame = tk.Frame(parent, bg="#f8f9fa", relief=tk.SOLID, borderwidth=1, padx=10, pady=8)
        
        # Item name
        name_label = tk.Label(
            item_frame,
            text=item.get('name', 'Unnamed'),
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50",
            anchor=tk.W
        )
        name_label.pack(fill=tk.X, pady=(0, 3))
        
        # Days left or date added
        if self.sidebar_mode == "ending":
            days_left = self.calculate_days_left(item)
            info_text = f"{days_left} days left"
        else:
            info_text = f"Added: {self.format_date(item.get('dateAdded', ''))}"
        
        info_label = tk.Label(
            item_frame,
            text=info_text,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            fg="#6c757d",
            anchor=tk.W
        )
        info_label.pack(fill=tk.X)
        
        return item_frame
    
    def add_category(self):
        """Add a new category"""
        dialog = CategoryDialog(self.parent, self.data_manager, self)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        self.render_categories()
    
    def edit_category(self, category):
        """Edit an existing category"""
        dialog = CategoryDialog(self.parent, self.data_manager, self, category)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        if self.current_view_mode == "categories":
            self.render_categories()
        else:
            self.show_category_items(self.selected_category_id)
    
    def delete_category(self, category):
        """Delete a category"""
        if messagebox.askyesno(
            "Delete Category",
            f"Are you sure you want to delete '{category.get('name')}'?\n"
            "All items in this category will also be deleted."
        ):
            # Remove category
            self.categories = [c for c in self.categories if c.get('id') != category.get('id')]
            
            # Remove items in this category
            self.items = [i for i in self.items if i.get('categoryId') != category.get('id')]
            
            self.save_data()
            self.load_data()
            self.render_categories()
    
    def add_item(self):
        """Add a new item"""
        dialog = ItemDialog(self.parent, self.data_manager, self)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        if self.current_view_mode == "items" and self.selected_category_id:
            self.show_category_items(self.selected_category_id)
        else:
            self.render_categories()
        self.update_urgent_items()
    
    def edit_item(self, item):
        """Edit an existing item"""
        dialog = ItemDialog(self.parent, self.data_manager, self, item)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        if self.current_view_mode == "items" and self.selected_category_id:
            self.show_category_items(self.selected_category_id)
        else:
            self.render_categories()
        self.update_urgent_items()
    
    def end_item(self, item):
        """End an item (mark as manually ended)"""
        if messagebox.askyesno(
            "End Item",
            f"Are you sure you want to end '{item.get('name')}'?\n"
            "This will move the item to the 'Items Ended' list."
        ):
            item['manuallyEnded'] = True
            item['endedDate'] = datetime.now().strftime('%Y-%m-%d')
            self.save_data()
            self.load_data()
            if self.current_view_mode == "items" and self.selected_category_id:
                self.show_category_items(self.selected_category_id)
            else:
                self.render_categories()
            self.update_urgent_items()
    
    def delete_item(self, item):
        """Delete an item"""
        if messagebox.askyesno(
            "Delete Item",
            f"Are you sure you want to delete '{item.get('name')}'?"
        ):
            self.items = [i for i in self.items if i.get('id') != item.get('id')]
            self.save_data()
            self.load_data()
            if self.current_view_mode == "items" and self.selected_category_id:
                self.show_category_items(self.selected_category_id)
            else:
                self.render_categories()
            self.update_urgent_items()
    
    def mark_as_sold(self, item):
        """Mark an item as sold and add it to sold trends"""
        dialog = SoldItemDialog(self.parent, self.data_manager, item, self.categories)
        self.parent.wait_window(dialog.dialog)
        # Refresh the view after marking as sold
        self.load_data()
        if self.current_view_mode == "items" and self.selected_category_id:
            self.show_category_items(self.selected_category_id)
        else:
            self.render_categories()
        self.update_urgent_items()
    
    def view_item(self, item):
        """View item details"""
        dialog = ItemViewDialog(self.parent, item, self.categories)
        self.parent.wait_window(dialog.dialog)
    
    def edit_average_days(self, category):
        """Edit average days for a category"""
        new_avg = simpledialog.askinteger(
            "Edit Average Days",
            f"Enter new average days for '{category.get('name')}':",
            initialvalue=category.get('averageDays', 30),
            minvalue=1
        )
        if new_avg:
            category['averageDays'] = new_avg
            self.save_data()
            self.load_data()
            if self.current_view_mode == "items" and self.selected_category_id:
                self.show_category_items(self.selected_category_id)
            else:
                self.render_categories()
    
    def refresh(self):
        """Refresh the view"""
        self.load_data()
        self.update_urgent_items()
        if self.current_view_mode == "items" and self.selected_category_id:
            self.show_category_items(self.selected_category_id)
        else:
            self.render_categories()


# Dialog classes for adding/editing categories and items
class CategoryDialog:
    """Dialog for adding/editing categories"""
    
    def __init__(self, parent, data_manager, view, category=None):
        self.data_manager = data_manager
        self.view = view
        self.category = category
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Category" if not category else "Edit Category")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (500 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (450 // 2) + parent.winfo_y()
        self.dialog.geometry(f"500x450+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="Add New Category" if not self.category else "Edit Category",
            font=("Segoe UI", 18, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Form frame - don't expand to fill, let it size naturally
        form_frame = tk.Frame(self.dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.X)
        
        # Name
        tk.Label(form_frame, text="Title", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=self.category.get('name', '') if self.category else '')
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, font=("Segoe UI", 11), width=40)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(name_entry)
        
        # Description
        tk.Label(form_frame, text="Description", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.desc_text = tk.Text(form_frame, font=("Segoe UI", 11), width=40, height=3)
        if self.category:
            self.desc_text.insert('1.0', self.category.get('description', ''))
        self.desc_text.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(self.desc_text)
        
        # Average days
        tk.Label(form_frame, text="Average Days", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.avg_days_var = tk.StringVar(value=str(self.category.get('averageDays', 30)) if self.category else '30')
        avg_days_entry = tk.Entry(form_frame, textvariable=self.avg_days_var, font=("Segoe UI", 11), width=40)
        avg_days_entry.pack(fill=tk.X, pady=(0, 20))
        add_context_menu(avg_days_entry)
        
        # Buttons frame - pack at bottom
        buttons_frame = tk.Frame(self.dialog, pady=20)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Save Category",
            command=self.save,
            font=("Segoe UI", 11, "bold"),
            bg="#0064d3",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """Save category"""
        name = self.name_var.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        try:
            avg_days = int(self.avg_days_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for average days.")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter a category name.")
            return
        
        if avg_days < 1:
            messagebox.showerror("Error", "Average days must be at least 1.")
            return
        
        categories = self.data_manager.load_categories()
        
        if self.category:
            # Edit existing
            for cat in categories:
                if cat.get('id') == self.category.get('id'):
                    cat['name'] = name
                    cat['description'] = description
                    cat['averageDays'] = avg_days
                    break
        else:
            # Add new
            new_category = {
                'id': str(int(datetime.now().timestamp() * 1000)),
                'name': name,
                'description': description,
                'averageDays': avg_days,
                'createdAt': datetime.now().isoformat()
            }
            categories.append(new_category)
        
        self.data_manager.save_categories(categories)
        self.dialog.destroy()


class ItemDialog:
    """Dialog for adding/editing items"""
    
    def __init__(self, parent, data_manager, view, item=None):
        self.data_manager = data_manager
        self.view = view
        self.item = item
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Item" if not item else "Edit Item")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (600 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (700 // 2) + parent.winfo_y()
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Scrollable frame
        canvas = tk.Canvas(self.dialog, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Add New Item" if not self.item else "Edit Item",
            font=("Segoe UI", 18, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Form frame
        form_frame = tk.Frame(scrollable_frame, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category
        tk.Label(form_frame, text="Select Category", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        categories = self.data_manager.load_categories()
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, font=("Segoe UI", 11), width=50)
        # Show only category names in dropdown
        category_combo['values'] = [c.get('name') for c in categories]
        if self.item:
            item_cat_id = self.item.get('categoryId')
            for c in categories:
                if c.get('id') == item_cat_id:
                    category_combo.set(c.get('name'))  # Set only name
                    break
        elif self.view.selected_category_id:
            for c in categories:
                if c.get('id') == self.view.selected_category_id:
                    category_combo.set(c.get('name'))  # Set only name
                    break
        category_combo.pack(fill=tk.X, pady=(0, 15))
        category_combo.bind("<<ComboboxSelected>>", lambda e: self.on_category_change(categories))
        self.category_combo = category_combo
        self.categories = categories
        
        # Name
        tk.Label(form_frame, text="Item Name", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=self.item.get('name', '') if self.item else '')
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, font=("Segoe UI", 11), width=50)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(name_entry)
        
        # Description
        tk.Label(form_frame, text="Description", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.desc_text = tk.Text(form_frame, font=("Segoe UI", 11), width=50, height=3)
        if self.item:
            self.desc_text.insert('1.0', self.item.get('description', ''))
        self.desc_text.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(self.desc_text)
        
        # Note
        tk.Label(form_frame, text="Note", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.note_text = tk.Text(form_frame, font=("Segoe UI", 11), width=50, height=2)
        if self.item:
            self.note_text.insert('1.0', self.item.get('note', ''))
        self.note_text.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(self.note_text)
        
        # Date added
        tk.Label(form_frame, text="Date Added", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        date_added = self.item.get('dateAdded', '') if self.item else datetime.now().strftime('%Y-%m-%d')
        self.date_added_var = tk.StringVar(value=date_added)
        date_added_entry = tk.Entry(form_frame, textvariable=self.date_added_var, font=("Segoe UI", 11), width=50)
        date_added_entry.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(date_added_entry)
        
        # End date with suggestion
        tk.Label(form_frame, text="End Date", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        if self.item:
            date_added = self.item.get('dateAdded', '')
            duration = self.item.get('duration', 30)
            if date_added:
                try:
                    added_date = datetime.strptime(date_added, '%Y-%m-%d')
                    end_date = (added_date + timedelta(days=duration)).strftime('%Y-%m-%d')
                except:
                    end_date = ''
            else:
                end_date = ''
        else:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.end_date_var = tk.StringVar(value=end_date)
        end_date_entry = tk.Entry(form_frame, textvariable=self.end_date_var, font=("Segoe UI", 11), width=50)
        end_date_entry.pack(fill=tk.X, pady=(0, 5))
        add_context_menu(end_date_entry)
        
        # End date suggestion hint
        self.end_date_hint = tk.Label(
            form_frame,
            text="",
            font=("Segoe UI", 9),
            fg="#6c757d",
            anchor=tk.W
        )
        self.end_date_hint.pack(anchor=tk.W, pady=(0, 15))
        
        # Photo URL
        tk.Label(form_frame, text="Image URL", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.photo_var = tk.StringVar(value=self.item.get('photo', '') if self.item else '')
        photo_entry = tk.Entry(form_frame, textvariable=self.photo_var, font=("Segoe UI", 11), width=50)
        photo_entry.pack(fill=tk.X, pady=(0, 15))
        photo_entry.bind("<KeyRelease>", lambda e: self.preview_image())
        add_context_menu(photo_entry)
        
        # Image preview
        self.preview_frame = tk.Frame(form_frame, bg="#f8f9fa", relief=tk.SOLID, borderwidth=1, width=200, height=150)
        self.preview_frame.pack(fill=tk.X, pady=(0, 15))
        self.preview_frame.pack_propagate(False)
        self.preview_label = None
        
        # Buttons
        buttons_frame = tk.Frame(scrollable_frame, pady=20)
        buttons_frame.pack()
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Save Item",
            command=self.save,
            font=("Segoe UI", 11, "bold"),
            bg="#0064d3",
            fg="white",
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_category_change(self, categories):
        """Handle category change to suggest end date"""
        category_name = self.category_var.get()
        if category_name and not self.item:
            # Find category by name (since dropdown now shows only names)
            category = next((c for c in categories if c.get('name') == category_name), None)
            if category:
                avg_days = category.get('averageDays', 30)
                date_added = self.date_added_var.get()
                if date_added:
                    try:
                        added_date = datetime.strptime(date_added, '%Y-%m-%d')
                        suggested_end = (added_date + timedelta(days=avg_days)).strftime('%Y-%m-%d')
                        self.end_date_var.set(suggested_end)
                        self.end_date_hint.config(text=f"Suggested end date based on category average ({avg_days} days)")
                    except:
                        pass
    
    def preview_image(self):
        """Preview image from URL"""
        url = self.photo_var.get().strip()
        if url:
            try:
                from PIL import Image, ImageTk
                import urllib.request
                import io
                
                with urllib.request.urlopen(url) as response:
                    img_data = response.read()
                
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                
                # Clear existing preview
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                
                self.preview_label = tk.Label(self.preview_frame, image=photo_img, bg="#f8f9fa")
                self.preview_label.image = photo_img  # Keep reference
                self.preview_label.pack()
            except Exception:
                # Clear preview on error
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                error_label = tk.Label(self.preview_frame, text="Invalid image URL", font=("Segoe UI", 10), fg="#dc2626", bg="#f8f9fa")
                error_label.pack()
    
    def save(self):
        """Save item"""
        category_name = self.category_var.get()
        if not category_name:
            messagebox.showerror("Error", "Please select a category.")
            return
        
        # Find category ID by name (since dropdown now shows only names)
        category = next((c for c in self.categories if c.get('name') == category_name), None)
        if not category:
            messagebox.showerror("Error", "Selected category not found.")
            return
        
        category_id = category.get('id')
        name = self.name_var.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        note = self.note_text.get('1.0', tk.END).strip()
        date_added = self.date_added_var.get().strip()
        end_date = self.end_date_var.get().strip()
        photo = self.photo_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter an item name.")
            return
        
        if not date_added:
            messagebox.showerror("Error", "Please select a date added.")
            return
        
        if not end_date:
            messagebox.showerror("Error", "Please select an end date.")
            return
        
        # Calculate duration
        try:
            added_date = datetime.strptime(date_added, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            duration = max(1, (end_date_obj - added_date).days)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
        
        items = self.data_manager.load_items()
        
        if self.item:
            # Edit existing
            for it in items:
                if it.get('id') == self.item.get('id'):
                    it['categoryId'] = category_id
                    it['name'] = name
                    it['description'] = description
                    it['note'] = note
                    it['dateAdded'] = date_added
                    it['duration'] = duration
                    it['photo'] = photo
                    if it.get('manuallyEnded') and duration > 0:
                        it['manuallyEnded'] = False
                        if 'endedDate' in it:
                            del it['endedDate']
                    break
        else:
            # Add new
            new_item = {
                'id': str(int(datetime.now().timestamp() * 1000)),
                'categoryId': category_id,
                'name': name,
                'description': description,
                'note': note,
                'dateAdded': date_added,
                'duration': duration,
                'photo': photo,
                'createdAt': datetime.now().isoformat()
            }
            items.append(new_item)
        
        self.data_manager.save_items(items)
        self.dialog.destroy()


class ItemViewDialog:
    """Dialog for viewing item details (matching HTML view modal)"""
    
    def __init__(self, parent, item, categories):
        self.item = item
        self.categories = categories
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Item Details")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (700 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (600 // 2) + parent.winfo_y()
        self.dialog.geometry(f"700x600+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI - matching HTML view modal layout"""
        # Title
        title_frame = tk.Frame(self.dialog)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="Item Details",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        close_btn = tk.Button(
            title_frame,
            text="×",
            command=self.dialog.destroy,
            font=("Segoe UI", 24),
            bg="white",
            fg="#333",
            borderwidth=0,
            cursor="hand2",
            width=3
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Main content area (matching HTML .view-content)
        content_frame = tk.Frame(self.dialog, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Photo section (matching HTML .view-photo-section)
        photo_frame = tk.Frame(content_frame, bg="#f8f9fa", width=250, height=300)
        photo_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        photo_frame.pack_propagate(False)
        
        item_photo = self.item.get('photo', '')
        if item_photo:
            try:
                from PIL import Image, ImageTk
                import urllib.request
                import io
                
                # Download and display image
                with urllib.request.urlopen(item_photo) as response:
                    img_data = response.read()
                
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((250, 300), Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                
                photo_label = tk.Label(
                    photo_frame,
                    image=photo_img,
                    bg="#f8f9fa"
                )
                photo_label.image = photo_img  # Keep a reference
                photo_label.pack(expand=True)
            except Exception:
                # Fallback to placeholder
                no_photo = tk.Label(
                    photo_frame,
                    text="📷\nNo photo available",
                    font=("Segoe UI", 16),
                    bg="#f8f9fa",
                    fg="#6c757d"
                )
                no_photo.pack(expand=True)
        else:
            # No photo placeholder (matching HTML .no-photo-placeholder)
            no_photo = tk.Label(
                photo_frame,
                text="📷\nNo photo available",
                font=("Segoe UI", 16),
                bg="#f8f9fa",
                fg="#6c757d"
            )
            no_photo.pack(expand=True)
        
        # Info section (matching HTML .view-info-section)
        info_frame = tk.Frame(content_frame, bg="#f8f9fa")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Item name
        field_frame = tk.Frame(info_frame, bg="#f8f9fa")
        field_frame.pack(fill=tk.X, pady=10)
        tk.Label(field_frame, text="Item Name:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        tk.Label(field_frame, text=self.item.get('name', 'Unnamed'), font=("Segoe UI", 11), bg="#f8f9fa", anchor=tk.W).pack(anchor=tk.W, pady=(5, 0))
        
        # Category
        category = next((c for c in self.categories if c.get('id') == self.item.get('categoryId')), None)
        category_name = category.get('name', 'Unknown') if category else 'Unknown'
        field_frame = tk.Frame(info_frame, bg="#f8f9fa")
        field_frame.pack(fill=tk.X, pady=10)
        tk.Label(field_frame, text="Category:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        tk.Label(field_frame, text=category_name, font=("Segoe UI", 11), bg="#f8f9fa", anchor=tk.W).pack(anchor=tk.W, pady=(5, 0))
        
        # Description
        field_frame = tk.Frame(info_frame, bg="#f8f9fa")
        field_frame.pack(fill=tk.X, pady=10)
        tk.Label(field_frame, text="Description:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        desc_text = self.item.get('description', '') or 'No description available'
        desc_label = tk.Label(field_frame, text=desc_text, font=("Segoe UI", 11), bg="#f8f9fa", wraplength=400, justify=tk.LEFT, anchor=tk.W)
        desc_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Note
        field_frame = tk.Frame(info_frame, bg="#f8f9fa")
        field_frame.pack(fill=tk.X, pady=10)
        tk.Label(field_frame, text="Notes:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        note_text = self.item.get('note', '') or 'No notes'
        note_label = tk.Label(field_frame, text=note_text, font=("Segoe UI", 11), bg="#f8f9fa", wraplength=400, justify=tk.LEFT, anchor=tk.W)
        note_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Date added
        date_added = self.item.get('dateAdded', '')
        if date_added:
            try:
                date_obj = datetime.strptime(date_added, '%Y-%m-%d')
                date_display = date_obj.strftime('%b %d, %Y')
            except:
                date_display = date_added
        else:
            date_display = 'Unknown'
        
        field_frame = tk.Frame(info_frame, bg="#f8f9fa")
        field_frame.pack(fill=tk.X, pady=10)
        tk.Label(field_frame, text="Date Added:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack(anchor=tk.W)
        tk.Label(field_frame, text=date_display, font=("Segoe UI", 11), bg="#f8f9fa", anchor=tk.W).pack(anchor=tk.W, pady=(5, 0))
        
        # Close button
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        close_btn.pack()



class SoldItemDialog:
    """Dialog for marking an item as sold"""
    
    def __init__(self, parent, data_manager, item, categories):
        self.data_manager = data_manager
        self.item = item
        self.categories = categories
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Mark Item as Sold")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (600 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (500 // 2) + parent.winfo_y()
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.new_category_mode = False
        self.new_subcategory_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="Mark Item as Sold",
            font=("Segoe UI", 18, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Form frame
        form_frame = tk.Frame(self.dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category
        cat_frame = tk.Frame(form_frame)
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(cat_frame, text="Select Category", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        
        cat_select_frame = tk.Frame(cat_frame)
        cat_select_frame.pack(fill=tk.X)
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(cat_select_frame, textvariable=self.category_var, font=("Segoe UI", 11), width=40)
        self.update_category_options()
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        create_cat_btn = tk.Button(
            cat_select_frame,
            text="Create New",
            command=self.toggle_new_category,
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="#333333",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        create_cat_btn.pack(side=tk.LEFT)
        
        # New category fields
        self.new_cat_frame = tk.Frame(form_frame)
        tk.Label(self.new_cat_frame, text="New Category Name", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.new_cat_name_var = tk.StringVar()
        new_cat_entry = tk.Entry(self.new_cat_frame, textvariable=self.new_cat_name_var, font=("Segoe UI", 11))
        new_cat_entry.pack(fill=tk.X, pady=(0, 10))
        add_context_menu(new_cat_entry)
        
        tk.Label(self.new_cat_frame, text="Description (optional)", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.new_cat_desc_text = tk.Text(self.new_cat_frame, font=("Segoe UI", 11), width=50, height=2)
        self.new_cat_desc_text.pack(fill=tk.X, pady=(0, 10))
        add_context_menu(self.new_cat_desc_text)
        
        # Subcategory
        tk.Label(form_frame, text="Select Subcategory", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(10, 5))
        
        subcat_frame = tk.Frame(form_frame)
        subcat_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(subcat_frame, textvariable=self.subcategory_var, font=("Segoe UI", 11), width=40)
        self.subcategory_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.subcategory_combo.bind("<<ComboboxSelected>>", self.on_subcategory_change)
        
        create_subcat_btn = tk.Button(
            subcat_frame,
            text="Create New",
            command=self.toggle_new_subcategory,
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="#333333",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        create_subcat_btn.pack(side=tk.LEFT)
        
        # New subcategory fields
        self.new_subcat_frame = tk.Frame(form_frame)
        tk.Label(self.new_subcat_frame, text="New Subcategory Name", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.new_subcat_name_var = tk.StringVar()
        new_subcat_entry = tk.Entry(self.new_subcat_frame, textvariable=self.new_subcat_name_var, font=("Segoe UI", 11))
        new_subcat_entry.pack(fill=tk.X, pady=(0, 10))
        add_context_menu(new_subcat_entry)
        
        # Price
        tk.Label(form_frame, text="Price Sold At", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(10, 5))
        self.price_var = tk.StringVar()
        price_entry = tk.Entry(form_frame, textvariable=self.price_var, font=("Segoe UI", 11), width=50)
        price_entry.pack(fill=tk.X, pady=(0, 20))
        add_context_menu(price_entry)
        
        # Buttons
        buttons_frame = tk.Frame(self.dialog, pady=20)
        buttons_frame.pack()
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Segoe UI", 11),
            bg="#f7f7f7",
            fg="#333333",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Mark as Sold",
            command=self.save,
            font=("Segoe UI", 11, "bold"),
            bg="#0064d3",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
    
    def update_category_options(self):
        """Update category dropdown options from sold trends"""
        sold_data = self.data_manager.load_sold_trends()
        periods = sold_data.get('periods', [])
        current_period_id = sold_data.get('currentPeriodId')
        
        # Find current period or use first period
        current_period = None
        if current_period_id:
            current_period = next((p for p in periods if p.get('id') == current_period_id), None)
        if not current_period and periods:
            current_period = periods[0]
        
        options = []
        if current_period:
            categories = current_period.get('categories', [])
            # Show only category names in dropdown
            options = [cat.get('name') for cat in categories]
        
        self.category_combo['values'] = options
    
    def on_category_change(self, event=None):
        """Handle category selection change"""
        self.update_subcategory_options()
        if self.new_category_mode:
            self.new_category_mode = False
            self.new_cat_frame.pack_forget()
    
    def update_subcategory_options(self):
        """Update subcategory dropdown based on selected category"""
        category_name = self.category_var.get()
        if not category_name:
            self.subcategory_combo['values'] = []
            return
        
        # Find category by name (since dropdown now shows only names)
        sold_data = self.data_manager.load_sold_trends()
        periods = sold_data.get('periods', [])
        current_period_id = sold_data.get('currentPeriodId')
        
        current_period = None
        if current_period_id:
            current_period = next((p for p in periods if p.get('id') == current_period_id), None)
        if not current_period and periods:
            current_period = periods[0]
        
        if current_period:
            categories = current_period.get('categories', [])
            category = next((c for c in categories if c.get('name') == category_name), None)
            if category:
                subcategories = category.get('subcategories', [])
                # Show only subcategory names in dropdown
                options = [sub.get('name') for sub in subcategories]
                self.subcategory_combo['values'] = options
                return
        
        self.subcategory_combo['values'] = []
    
    def on_subcategory_change(self, event=None):
        """Handle subcategory selection change"""
        if self.new_subcategory_mode:
            self.new_subcategory_mode = False
            self.new_subcat_frame.pack_forget()
    
    def toggle_new_category(self):
        """Toggle new category input fields"""
        self.new_category_mode = not self.new_category_mode
        if self.new_category_mode:
            # Pack new category frame in form_frame (parent)
            form_frame = self.dialog.winfo_children()[1]
            # Find subcategory label to pack before it
            subcat_label = None
            for widget in form_frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('text') == 'Select Subcategory':
                    subcat_label = widget
                    break
            if subcat_label:
                self.new_cat_frame.pack(fill=tk.X, pady=(0, 10), before=subcat_label)
            else:
                self.new_cat_frame.pack(fill=tk.X, pady=(0, 10))
            self.category_combo.set('')
        else:
            self.new_cat_frame.pack_forget()
    
    def toggle_new_subcategory(self):
        """Toggle new subcategory input fields"""
        self.new_subcategory_mode = not self.new_subcategory_mode
        if self.new_subcategory_mode:
            self.new_subcat_frame.pack(fill=tk.X, pady=(0, 10), after=self.subcategory_combo.master)
            self.subcategory_combo.set('')
        else:
            self.new_subcat_frame.pack_forget()
    
    def save(self):
        """Save sold item"""
        from datetime import datetime
        import json
        
        # Get price
        try:
            price = float(self.price_var.get())
            if price < 0:
                messagebox.showerror("Error", "Price must be 0 or greater.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price.")
            return
        
        # Load sold trends data
        sold_data = self.data_manager.load_sold_trends()
        periods = sold_data.get('periods', [])
        current_period_id = sold_data.get('currentPeriodId')
        
        # Find or create current period
        current_period = None
        if current_period_id:
            current_period = next((p for p in periods if p.get('id') == current_period_id), None)
        
        if not current_period:
            # Create default period
            timestamp = datetime.now().isoformat()
            current_period = {
                'id': f"period-{int(datetime.now().timestamp() * 1000)}",
                'name': 'Default Period',
                'description': '',
                'categories': [],
                'createdAt': timestamp,
                'updatedAt': timestamp
            }
            periods.append(current_period)
            current_period_id = current_period['id']
            sold_data['currentPeriodId'] = current_period_id
        
        # Handle category
        category_id = None
        is_new_category = self.new_category_mode
        new_category_name = self.new_cat_name_var.get().strip()
        new_category_desc = self.new_cat_desc_text.get('1.0', tk.END).strip()
        
        if is_new_category:
            if not new_category_name:
                messagebox.showerror("Error", "Please enter a name for the new category.")
                return
            # Create new category
            timestamp = datetime.now().isoformat()
            new_category = {
                'id': f"cat-{int(datetime.now().timestamp() * 1000)}",
                'name': new_category_name,
                'description': new_category_desc,
                'subcategories': [],
                'createdAt': timestamp,
                'updatedAt': timestamp
            }
            if 'categories' not in current_period:
                current_period['categories'] = []
            current_period['categories'].append(new_category)
            category_id = new_category['id']
            category = new_category
        else:
            category_name = self.category_var.get()
            if not category_name:
                messagebox.showerror("Error", "Please select a category or create a new one.")
                return
            # Find category by name (since dropdown now shows only names)
            category = next((c for c in current_period.get('categories', []) if c.get('name') == category_name), None)
            if not category:
                messagebox.showerror("Error", "Category not found.")
                return
            category_id = category.get('id')
            if not category:
                messagebox.showerror("Error", "Category not found.")
                return
        
        # Handle subcategory
        subcategory_id = None
        is_new_subcategory = self.new_subcategory_mode
        new_subcategory_name = self.new_subcat_name_var.get().strip()
        
        if is_new_category or is_new_subcategory:
            if not new_subcategory_name:
                messagebox.showerror("Error", "Please enter a name for the new subcategory.")
                return
            # Create new subcategory
            timestamp = datetime.now().isoformat()
            new_subcategory = {
                'id': f"sub-{int(datetime.now().timestamp() * 1000)}",
                'name': new_subcategory_name,
                'count': 0,
                'price': None,
                'items': [],
                'createdAt': timestamp,
                'updatedAt': timestamp
            }
            if 'subcategories' not in category:
                category['subcategories'] = []
            category['subcategories'].append(new_subcategory)
            subcategory_id = new_subcategory['id']
            subcategory = new_subcategory
        else:
            subcategory_name = self.subcategory_var.get()
            if not subcategory_name:
                messagebox.showerror("Error", "Please select a subcategory or create a new one.")
                return
            # Find subcategory by name (since dropdown now shows only names)
            subcategory = next((s for s in category.get('subcategories', []) if s.get('name') == subcategory_name), None)
            if not subcategory:
                messagebox.showerror("Error", "Subcategory not found.")
                return
            subcategory_id = subcategory.get('id')
            if not subcategory:
                messagebox.showerror("Error", "Subcategory not found.")
                return
        
        # Add item to subcategory
        timestamp = datetime.now().isoformat()
        sold_item = {
            'id': f"solditem-{int(datetime.now().timestamp() * 1000)}",
            'label': self.item.get('name', 'Unnamed'),
            'price': price,
            'photo': self.item.get('photo') or None,
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        
        if 'items' not in subcategory:
            subcategory['items'] = []
        subcategory['items'].append(sold_item)
        
        # Update subcategory count
        subcategory['count'] = len(subcategory['items'])
        subcategory['updatedAt'] = timestamp
        
        # Update category and period
        category['updatedAt'] = timestamp
        current_period['updatedAt'] = timestamp
        
        # Save sold trends
        sold_data['periods'] = periods
        self.data_manager.save_sold_trends(sold_data)
        
        # Mark item as sold (ended)
        items = self.data_manager.load_items()
        for it in items:
            if it.get('id') == self.item.get('id'):
                it['manuallyEnded'] = True
                it['endedDate'] = datetime.now().strftime('%Y-%m-%d')
                it['soldDate'] = timestamp
                it['soldPrice'] = price
                break
        
        self.data_manager.save_items(items)
        
        messagebox.showinfo("Success", f"Item '{self.item.get('name')}' has been marked as sold and added to Sold Items Trends.")
        self.dialog.destroy()
