"""
Sold Trends View
View for tracking sold items trends
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
from app.utils import add_context_menu


class SoldTrendsView:
    """View for sold items trends"""
    
    def __init__(self, parent, data_manager, main_window):
        self.parent = parent
        self.data_manager = data_manager
        self.main_window = main_window
        
        self.periods = []
        self.current_period_id = None
        self.categories = []
        self.settings = {}
        
        self.setup_ui()
        self.load_data()
        self.render_categories()
    
    def setup_ui(self):
        """Setup the sold trends view UI - matching HTML layout exactly"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container (matching HTML .container.trends-page)
        container = tk.Frame(self.parent, bg="#f3f4f6")
        container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Header (matching HTML .trends-page-header)
        header_frame = tk.Frame(container, bg="#f3f4f6")
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        title_label = tk.Label(
            header_frame,
            text="Sold Items Trends",
            font=("Segoe UI", 35, "bold"),
            bg="#f3f4f6",
            fg="#1f2937"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Track how many items have sold across your categories and subcategories.",
            font=("Segoe UI", 16),
            bg="#f3f4f6",
            fg="#4b5563"
        )
        subtitle_label.pack(pady=(10, 0))
        
        # Search container (matching HTML)
        search_container = tk.Frame(container, bg="#f3f4f6")
        search_container.pack(fill=tk.X, pady=(0, 20))
        
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
        
        # Add section buttons (matching HTML)
        add_section = tk.Frame(container, bg="#f3f4f6")
        add_section.pack(fill=tk.X, pady=(0, 20))
        
        add_category_btn = tk.Button(
            add_section,
            text="Add Category",
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
        
        reset_btn = tk.Button(
            add_section,
            text="Reset Data",
            command=self.reset_data,
            font=("Segoe UI", 16, "bold"),
            bg="#f7f7f7",
            fg="#333333",
            padx=24,
            pady=12,
            relief=tk.SOLID,
            borderwidth=1,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Period section (matching HTML .data-period-section)
        period_section = tk.Frame(container, bg="#f3f4f6")
        period_section.pack(fill=tk.X, pady=(0, 30))
        
        # Period toolbar (matching HTML .data-period-toolbar)
        period_toolbar = tk.Frame(period_section, bg="#f3f4f6")
        period_toolbar.pack(fill=tk.X, pady=(0, 12))
        
        # Period header
        period_header = tk.Frame(period_toolbar, bg="#f3f4f6")
        period_header.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        period_title = tk.Label(
            period_header,
            text="Periods Of Data",
            font=("Segoe UI", 23, "bold"),
            bg="#f3f4f6",
            fg="#111827",
            anchor=tk.W
        )
        period_title.pack(anchor=tk.W)
        
        period_subtitle = tk.Label(
            period_header,
            text="Switch between saved periods to compare different timeframes.",
            font=("Segoe UI", 15),
            bg="#f3f4f6",
            fg="#6b7280",
            anchor=tk.W
        )
        period_subtitle.pack(anchor=tk.W, pady=(6, 0))
        
        # Period controls
        period_controls = tk.Frame(period_toolbar, bg="#f3f4f6")
        period_controls.pack(side=tk.RIGHT)
        
        self.period_var = tk.StringVar()
        period_combo = ttk.Combobox(
            period_controls,
            textvariable=self.period_var,
            width=25,
            state="readonly",
            font=("Segoe UI", 15)
        )
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", lambda e: self.set_current_period(self.period_var.get()))
        self.period_combo = period_combo
        
        add_period_btn = tk.Button(
            period_controls,
            text="Add Period",
            command=self.add_period,
            font=("Segoe UI", 12),
            bg="#f7f7f7",
            fg="#333333",
            padx=12,
            pady=6,
            relief=tk.SOLID,
            borderwidth=1,
            cursor="hand2"
        )
        add_period_btn.pack(side=tk.LEFT, padx=5)
        
        remove_period_btn = tk.Button(
            period_controls,
            text="Remove Period",
            command=self.remove_period,
            font=("Segoe UI", 12),
            bg="#e53238",
            fg="white",
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        remove_period_btn.pack(side=tk.LEFT, padx=5)
        self.remove_period_btn = remove_period_btn
        
        # Period display (matching HTML .data-period-display)
        self.period_display = tk.Label(
            period_section,
            text="No period saved yet",
            font=("Segoe UI", 18, "bold"),
            bg="#d1e7fd",
            fg="#0f172a",
            padx=16,
            pady=12,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.period_display.pack(fill=tk.X)
        
        # Trends content wrapper (matching HTML .trends-content-wrapper)
        trends_wrapper = tk.Frame(container, bg="#f3f4f6")
        trends_wrapper.pack(fill=tk.BOTH, expand=True)
        
        # Main content area
        self.content_frame = tk.Frame(trends_wrapper, bg="#f3f4f6")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 24))
        
        # Trending keywords sidebar (matching HTML .trending-keywords-sidebar)
        self.keywords_sidebar = tk.Frame(
            trends_wrapper,
            bg="white",
            padx=20,
            pady=20,
            width=320
        )
        self.keywords_sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.keywords_sidebar.pack_propagate(False)
        
        # Sidebar header
        keywords_header = tk.Frame(self.keywords_sidebar, bg="white")
        keywords_header.pack(fill=tk.X, pady=(0, 20))
        
        keywords_title = tk.Label(
            keywords_header,
            text="Trending Keywords",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg="#1f2937",
            anchor=tk.W
        )
        keywords_title.pack(anchor=tk.W, pady=(0, 6))
        
        keywords_subtitle = tk.Label(
            keywords_header,
            text="Most sold items by keyword",
            font=("Segoe UI", 13),
            bg="white",
            fg="#6b7280",
            anchor=tk.W
        )
        keywords_subtitle.pack(anchor=tk.W)
        
        # Keywords list
        self.keywords_list_frame = tk.Frame(self.keywords_sidebar, bg="white")
        self.keywords_list_frame.pack(fill=tk.BOTH, expand=True)
    
    def update_trending_keywords(self):
        """Update trending keywords sidebar"""
        # Clear existing keywords
        for widget in self.keywords_list_frame.winfo_children():
            widget.destroy()
        
        # Extract all keywords from sold items and count them
        keyword_counts = {}
        
        for category in self.categories:
            for subcategory in category.get('subcategories', []):
                for item in subcategory.get('items', []):
                    name = item.get('name', '')
                    # Split by common delimiters to extract keywords
                    keywords = name.lower().split()
                    for keyword in keywords:
                        # Filter out common words
                        if len(keyword) > 2 and keyword not in ['the', 'and', 'for', 'with']:
                            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by count and get top keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not sorted_keywords:
            empty_label = tk.Label(
                self.keywords_list_frame,
                text="No trending keywords yet",
                font=("Segoe UI", 12),
                bg="white",
                fg="#6b7280"
            )
            empty_label.pack(pady=20)
            return
        
        # Display keywords
        for keyword, count in sorted_keywords:
            keyword_frame = tk.Frame(
                self.keywords_list_frame,
                bg="#f9fafb",
                relief=tk.RAISED,
                borderwidth=1,
                padx=14,
                pady=12
            )
            keyword_frame.pack(fill=tk.X, pady=5)
            
            keyword_label = tk.Label(
                keyword_frame,
                text=keyword.title(),
                font=("Segoe UI", 14, "bold"),
                bg="#f9fafb",
                fg="#1f2937",
                anchor=tk.W
            )
            keyword_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            count_label = tk.Label(
                keyword_frame,
                text=str(count),
                font=("Segoe UI", 13, "bold"),
                bg="#0064d3",
                fg="white",
                padx=10,
                pady=4
            )
            count_label.pack(side=tk.RIGHT)
    
    def search_items(self):
        """Search for sold items"""
        search_term = self.search_var.get().strip().lower()
        # Ignore placeholder text
        if not search_term or search_term == "search items... (e.g., 'glass plate')":
            self.render_categories()
            return
        
        # Filter items matching search term
        matching_items = []
        for category in self.categories:
            for subcategory in category.get('subcategories', []):
                for item in subcategory.get('items', []):
                    if search_term in item.get('name', '').lower():
                        matching_items.append((category, subcategory, item))
        
        # Show search results (similar to listings view)
        # For now, just filter the displayed categories
        self.render_categories(search_term=search_term)
    
    def load_data(self):
        """Load sold trends data"""
        data = self.data_manager.load_sold_trends()
        self.periods = data.get('periods', [])
        self.current_period_id = data.get('currentPeriodId')
        
        if self.periods and not self.current_period_id:
            self.current_period_id = self.periods[0].get('id')
        
        if self.current_period_id:
            period = next((p for p in self.periods if p.get('id') == self.current_period_id), None)
            if period:
                self.categories = period.get('categories', [])
            else:
                self.categories = []
        else:
            self.categories = []
        
        self.settings = self.data_manager.load_settings()
        self.update_period_select()
        self.update_period_display()
        self.update_trending_keywords()
    
    def save_data(self):
        """Save sold trends data"""
        data = {
            'periods': self.periods,
            'currentPeriodId': self.current_period_id
        }
        self.data_manager.save_sold_trends(data)
    
    def update_period_select(self):
        """Update period combobox"""
        values = [f"{p.get('id')}|{p.get('name')}" for p in self.periods]
        self.period_combo['values'] = values
        
        if self.current_period_id:
            for p in self.periods:
                if p.get('id') == self.current_period_id:
                    self.period_var.set(f"{p.get('id')}|{p.get('name')}")
                    break
        
        self.remove_period_btn.config(state=tk.NORMAL if self.periods else tk.DISABLED)
    
    def update_period_display(self):
        """Update period display label"""
        if self.current_period_id:
            period = next((p for p in self.periods if p.get('id') == self.current_period_id), None)
            if period:
                self.period_display.config(text=period.get('name', 'Untitled Period'))
            else:
                self.period_display.config(text="No period saved yet")
        else:
            self.period_display.config(text="No period saved yet")
    
    def set_current_period(self, value):
        """Set current period"""
        if value:
            period_id = value.split('|')[0]
            self.current_period_id = period_id
            period = next((p for p in self.periods if p.get('id') == period_id), None)
            if period:
                self.categories = period.get('categories', [])
            else:
                self.categories = []
            self.save_data()
            self.update_period_display()
            self.render_categories()
    
    def add_period(self):
        """Add a new period"""
        name = simpledialog.askstring("Add Period", "Enter period name (e.g., 2025, October 2025):")
        if name:
            description = simpledialog.askstring("Period Description", "Enter description (optional):", initialvalue="")
            if description is None:
                description = ""
            
            new_period = {
                'id': str(int(datetime.now().timestamp() * 1000)),
                'name': name,
                'description': description or '',
                'categories': [],
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
            self.periods.append(new_period)
            self.current_period_id = new_period['id']
            self.categories = []
            self.save_data()
            self.load_data()
            self.render_categories()
    
    def remove_period(self):
        """Remove current period"""
        if not self.periods or not self.current_period_id:
            return
        
        period = next((p for p in self.periods if p.get('id') == self.current_period_id), None)
        if not period:
            return
        
        if messagebox.askyesno(
            "Remove Period",
            f"Remove the period '{period.get('name')}'?\n"
            "This deletes all categories and sold data saved for it."
        ):
            self.periods = [p for p in self.periods if p.get('id') != self.current_period_id]
            
            if self.periods:
                self.current_period_id = self.periods[0].get('id')
                period = self.periods[0]
                self.categories = period.get('categories', [])
            else:
                self.current_period_id = None
                self.categories = []
            
            self.save_data()
            self.load_data()
            self.render_categories()
    
    def reset_data(self):
        """Reset all sold trends data"""
        if messagebox.askyesno(
            "Reset Sold Trends Data",
            "This will clear all sold trend data. This action cannot be undone."
        ):
            self.periods = []
            self.current_period_id = None
            self.categories = []
            self.save_data()
            self.load_data()
            self.render_categories()
    
    def add_category(self):
        """Add a new sold category"""
        if not self.current_period_id:
            messagebox.showwarning("No Period", "Please add a period first.")
            return
        
        dialog = SoldCategoryDialog(self.parent, self.data_manager, self)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        self.render_categories()
    
    def edit_category(self, category):
        """Edit a sold category"""
        dialog = SoldCategoryDialog(self.parent, self.data_manager, self, category)
        self.parent.wait_window(dialog.dialog)
        self.load_data()
        self.render_categories()
    
    def delete_category(self, category):
        """Delete a sold category"""
        if messagebox.askyesno(
            "Delete Category",
            f"Delete category '{category.get('name')}' and all of its subcategories?"
        ):
            self.categories = [c for c in self.categories if c.get('id') != category.get('id')]
            self.update_current_period_categories()
            self.save_data()
            self.load_data()
            self.render_categories()
    
    def update_current_period_categories(self):
        """Update categories in current period"""
        if self.current_period_id:
            for period in self.periods:
                if period.get('id') == self.current_period_id:
                    period['categories'] = self.categories
                    period['updatedAt'] = datetime.now().isoformat()
                    break
    
    def format_currency(self, value):
        """Format currency value"""
        currency_map = {
            'GBP': {'symbol': '£', 'locale': 'en-GB'},
            'USD': {'symbol': '$', 'locale': 'en-US'},
            'EUR': {'symbol': '€', 'locale': 'de-DE'},
            'AUD': {'symbol': '$', 'locale': 'en-AU'},
            'CAD': {'symbol': '$', 'locale': 'en-CA'}
        }
        
        currency = self.settings.get('soldCurrency', 'GBP')
        config = currency_map.get(currency, currency_map['GBP'])
        
        return f"{config['symbol']}{value:,.2f}"
    
    def render_categories(self):
        """Render sold categories"""
        # Clear display
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if not self.current_period_id:
            empty_label = tk.Label(
                self.content_frame,
                text="No periods yet\nAdd a period to start tracking how many items have sold.",
                font=("Segoe UI", 14),
                bg="#F4F3F2",
                fg="#6c757d"
            )
            empty_label.pack(expand=True)
            return
        
        if not self.categories:
            period = next((p for p in self.periods if p.get('id') == self.current_period_id), None)
            period_name = period.get('name', 'this period') if period else 'this period'
            empty_label = tk.Label(
                self.content_frame,
                text=f"No sold categories yet\nCreate a category for '{period_name}' to start tracking how many items have sold.",
                font=("Segoe UI", 14),
                bg="#F4F3F2",
                fg="#6c757d"
            )
            empty_label.pack(expand=True)
            return
        
        # Scrollable categories
        canvas = tk.Canvas(self.content_frame, bg="#F4F3F2", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
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
        
        for i, category in enumerate(self.categories):
            category_frame = self.create_category_card(categories_frame, category, i)
            category_frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        for i in range(2):
            categories_frame.grid_columnconfigure(i, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_category_card(self, parent, category, index):
        """Create a sold category card"""
        card = tk.Frame(
            parent,
            bg="#f2f3f4",
            relief=tk.RAISED,
            borderwidth=1,
            padx=28,
            pady=32
        )
        
        # Header
        header_frame = tk.Frame(card, bg="#f2f3f4")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        name_label = tk.Label(
            header_frame,
            text=category.get('name', 'Unnamed'),
            font=("Segoe UI", 18, "bold"),
            bg="#f2f3f4",
            fg="#111827"
        )
        name_label.pack()
        
        if category.get('description'):
            desc_label = tk.Label(
                header_frame,
                text=category.get('description'),
                font=("Segoe UI", 11),
                bg="#f2f3f4",
                fg="#4b5563",
                wraplength=300
            )
            desc_label.pack(pady=(5, 0))
        
        # Subcategories
        subcategories = category.get('subcategories', [])
        if subcategories:
            sub_frame = tk.Frame(card, bg="#f2f3f4")
            sub_frame.pack(fill=tk.X, pady=10)
            
            for sub in subcategories:
                sub_item_frame = tk.Frame(sub_frame, bg="#e8e9ea", padx=10, pady=8)
                sub_item_frame.pack(fill=tk.X, pady=2)
                
                sub_name = tk.Label(
                    sub_item_frame,
                    text=sub.get('name', ''),
                    font=("Segoe UI", 11, "bold"),
                    bg="#e8e9ea",
                    fg="#1f2937"
                )
                sub_name.pack(side=tk.LEFT)
                
                items = sub.get('items', [])
                if items:
                    count = len(items)
                    total_price = sum(item.get('price', 0) for item in items)
                    sub_info = tk.Label(
                        sub_item_frame,
                        text=f"{count} items · Total {self.format_currency(total_price)}",
                        font=("Segoe UI", 10),
                        bg="#e8e9ea",
                        fg="#0f172a"
                    )
                    sub_info.pack(side=tk.RIGHT)
                else:
                    count = sub.get('count', 0)
                    price = sub.get('price')
                    if price:
                        sub_info = tk.Label(
                            sub_item_frame,
                            text=f"{count} × {self.format_currency(price)}",
                            font=("Segoe UI", 10),
                            bg="#e8e9ea",
                            fg="#0f172a"
                        )
                        sub_info.pack(side=tk.RIGHT)
                    else:
                        sub_info = tk.Label(
                            sub_item_frame,
                            text=str(count),
                            font=("Segoe UI", 10),
                            bg="#e8e9ea",
                            fg="#0f172a"
                        )
                        sub_info.pack(side=tk.RIGHT)
        else:
            empty_label = tk.Label(
                card,
                text="No subcategories yet. Use Edit to add the first one.",
                font=("Segoe UI", 10),
                bg="#f2f3f4",
                fg="#4b5563"
            )
            empty_label.pack(pady=10)
        
        # Totals
        totals_frame = tk.Frame(card, bg="#f2f3f4")
        totals_frame.pack(fill=tk.X, pady=10)
        
        total_sold = sum(
            len(sub.get('items', [])) if sub.get('items') else sub.get('count', 0)
            for sub in subcategories
        )
        
        total_made = 0
        has_price = False
        for sub in subcategories:
            items = sub.get('items', [])
            if items:
                total_made += sum(item.get('price', 0) for item in items)
                has_price = True
            elif sub.get('price'):
                count = sub.get('count', 0)
                total_made += count * sub.get('price')
                has_price = True
        
        total_sold_label = tk.Label(
            totals_frame,
            text=f"Total sold: {total_sold}",
            font=("Segoe UI", 11, "bold"),
            bg="#f2f3f4",
            fg="#0f172a"
        )
        total_sold_label.pack(side=tk.LEFT)
        
        if has_price:
            total_made_label = tk.Label(
                totals_frame,
                text=f"Total made: {self.format_currency(total_made)}",
                font=("Segoe UI", 11, "bold"),
                bg="#f2f3f4",
                fg="#77d47f"
            )
            total_made_label.pack(side=tk.RIGHT)
        
        # Actions
        actions_frame = tk.Frame(card, bg="#f2f3f4")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        edit_btn = tk.Button(
            actions_frame,
            text="Edit",
            command=lambda c=category: self.edit_category(c),
            font=("Segoe UI", 10),
            bg="#0064d3",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT)
        
        return card
    
    def refresh(self):
        """Refresh the view"""
        self.load_data()
        self.render_categories()


class SoldCategoryDialog:
    """Dialog for adding/editing sold categories"""
    
    def __init__(self, parent, data_manager, view, category=None):
        self.data_manager = data_manager
        self.view = view
        self.category = category
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Sold Category" if not category else "Edit Sold Category")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        parent.update_idletasks()
        x = (parent.winfo_width() // 2) - (800 // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (600 // 2) + parent.winfo_y()
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.subcategories = category.get('subcategories', []) if category else []
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
            text="Add Sold Category" if not self.category else "Edit Sold Category",
            font=("Segoe UI", 18, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Form frame
        form_frame = tk.Frame(scrollable_frame, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        tk.Label(form_frame, text="Category Name", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=self.category.get('name', '') if self.category else '')
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, font=("Segoe UI", 11), width=60)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        add_context_menu(name_entry)
        
        # Description
        tk.Label(form_frame, text="Description (optional)", font=("Segoe UI", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.desc_text = tk.Text(form_frame, font=("Segoe UI", 11), width=60, height=2)
        if self.category:
            self.desc_text.insert('1.0', self.category.get('description', ''))
        self.desc_text.pack(fill=tk.X, pady=(0, 20))
        add_context_menu(self.desc_text)
        
        # Subcategories
        tk.Label(form_frame, text="Subcategories", font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.subcategories_frame = tk.Frame(form_frame)
        self.subcategories_frame.pack(fill=tk.BOTH, expand=True)
        
        add_sub_btn = tk.Button(
            form_frame,
            text="Add Subcategory",
            command=self.add_subcategory,
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="#333333",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        add_sub_btn.pack(anchor=tk.W, pady=10)
        
        # Render existing subcategories
        for sub in self.subcategories:
            self.add_subcategory_row(sub)
        
        if not self.subcategories:
            self.add_subcategory()
        
        # Buttons
        buttons_frame = tk.Frame(scrollable_frame, pady=20)
        buttons_frame.pack()
        
        if self.category:
            delete_btn = tk.Button(
                buttons_frame,
                text="Delete Category",
                command=self.delete_category,
                font=("Segoe UI", 11),
                bg="#e53238",
                fg="white",
                padx=20,
                pady=8
            )
            delete_btn.pack(side=tk.LEFT, padx=10)
        
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
            text="Save Category",
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
    
    def add_subcategory(self):
        """Add a new subcategory row"""
        self.add_subcategory_row()
    
    def add_subcategory_row(self, subcategory=None):
        """Add a subcategory row to the form"""
        row_frame = tk.Frame(self.subcategories_frame, bg="#e8e9ea", padx=10, pady=10)
        row_frame.pack(fill=tk.X, pady=5)
        
        # Name
        name_var = tk.StringVar(value=subcategory.get('name', '') if subcategory else '')
        tk.Label(row_frame, text="Name", font=("Segoe UI", 9)).pack(anchor=tk.W)
        name_entry = tk.Entry(row_frame, textvariable=name_var, font=("Segoe UI", 10), width=30)
        name_entry.pack(side=tk.LEFT, padx=5)
        add_context_menu(name_entry)
        
        # Count
        count_var = tk.StringVar(value=str(subcategory.get('count', 0)) if subcategory else '0')
        tk.Label(row_frame, text="Count", font=("Segoe UI", 9)).pack(anchor=tk.W)
        count_entry = tk.Entry(row_frame, textvariable=count_var, font=("Segoe UI", 10), width=10)
        count_entry.pack(side=tk.LEFT, padx=5)
        add_context_menu(count_entry)
        
        # Price
        price_var = tk.StringVar(value=str(subcategory.get('price', '')) if subcategory and subcategory.get('price') else '')
        tk.Label(row_frame, text="Price", font=("Segoe UI", 9)).pack(anchor=tk.W)
        price_entry = tk.Entry(row_frame, textvariable=price_var, font=("Segoe UI", 10), width=15)
        price_entry.pack(side=tk.LEFT, padx=5)
        add_context_menu(price_entry)
        
        # Remove button
        remove_btn = tk.Button(
            row_frame,
            text="Remove",
            command=lambda: row_frame.destroy(),
            font=("Segoe UI", 9),
            bg="#e53238",
            fg="white",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        remove_btn.pack(side=tk.RIGHT, padx=5)
        
        # Store variables
        row_frame.name_var = name_var
        row_frame.count_var = count_var
        row_frame.price_var = price_var
    
    def save(self):
        """Save category"""
        name = self.name_var.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a category name.")
            return
        
        # Collect subcategories
        subcategories = []
        for row in self.subcategories_frame.winfo_children():
            if isinstance(row, tk.Frame):
                sub_name = row.name_var.get().strip()
                if sub_name:
                    try:
                        count = int(row.count_var.get() or 0)
                        price_str = row.price_var.get().strip()
                        price = float(price_str) if price_str else None
                    except ValueError:
                        messagebox.showerror("Error", "Please enter valid numbers for count and price.")
                        return
                    
                    subcategories.append({
                        'id': str(int(datetime.now().timestamp() * 1000)),
                        'name': sub_name,
                        'count': count,
                        'price': price,
                        'items': []
                    })
        
        categories = self.view.categories
        
        if self.category:
            # Edit existing
            for cat in categories:
                if cat.get('id') == self.category.get('id'):
                    cat['name'] = name
                    cat['description'] = description
                    cat['subcategories'] = subcategories
                    break
        else:
            # Add new
            new_category = {
                'id': str(int(datetime.now().timestamp() * 1000)),
                'name': name,
                'description': description,
                'subcategories': subcategories,
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
            categories.append(new_category)
        
        self.view.categories = categories
        self.view.update_current_period_categories()
        self.view.save_data()
        self.dialog.destroy()
    
    def delete_category(self):
        """Delete category"""
        if messagebox.askyesno(
            "Delete Category",
            f"Delete category '{self.category.get('name')}' and all of its subcategories?"
        ):
            self.view.delete_category(self.category)
            self.dialog.destroy()

