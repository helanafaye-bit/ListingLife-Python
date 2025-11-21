"""
Settings View
Application settings
"""

import tkinter as tk
from tkinter import ttk


class SettingsView:
    """View for application settings"""
    
    def __init__(self, parent, data_manager, main_window):
        self.parent = parent
        self.data_manager = data_manager
        self.main_window = main_window
        
        self.settings = {}
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings view UI - matching HTML layout exactly"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container (matching HTML .container.settings-page with max-width: 960px)
        container = tk.Frame(self.parent, bg="#f3f4f6")
        container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Header (matching HTML .settings-header - centered, white background, rounded)
        header_frame = tk.Frame(
            container,
            bg="white",
            padx=32,
            pady=32
        )
        header_frame.pack(fill=tk.X, pady=(20, 24))
        
        title_label = tk.Label(
            header_frame,
            text="Settings",
            font=("Segoe UI", 32, "bold"),
            bg="white",
            fg="#111827"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Fine-tune how ListingLife behaves across your pages.",
            font=("Segoe UI", 16),
            bg="white",
            fg="#4b5563"
        )
        subtitle_label.pack(pady=(8, 0))
        
        # Content area (matching HTML .settings-content)
        content_frame = tk.Frame(container, bg="#f3f4f6")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings card (matching HTML .settings-card)
        card = tk.Frame(
            content_frame,
            bg="white",
            padx=32,
            pady=28,
            relief=tk.FLAT,
            borderwidth=1
        )
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Card header (matching HTML .settings-card-header)
        card_header = tk.Frame(card, bg="white")
        card_header.pack(fill=tk.X, pady=(0, 18))
        
        currency_title = tk.Label(
            card_header,
            text="Total Sales Currency Unit",
            font=("Segoe UI", 23, "bold"),
            bg="white",
            fg="#111827",
            anchor=tk.W
        )
        currency_title.pack(anchor=tk.W)
        
        currency_desc = tk.Label(
            card_header,
            text="Select the currency used for totals on the Sold Items Trends page.",
            font=("Segoe UI", 15),
            bg="white",
            fg="#4b5563",
            anchor=tk.W
        )
        currency_desc.pack(anchor=tk.W, pady=(6, 0))
        
        # Settings field (matching HTML .settings-field)
        currency_field = tk.Frame(card, bg="white")
        currency_field.pack(fill=tk.X, pady=(0, 12))
        
        currency_label = tk.Label(
            currency_field,
            text="CURRENCY",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#6b7280",
            anchor=tk.W
        )
        currency_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.currency_var = tk.StringVar()
        currency_combo = ttk.Combobox(
            currency_field,
            textvariable=self.currency_var,
            values=[
                "GBP — British Pound (£)",
                "USD — US Dollar ($)",
                "EUR — Euro (€)",
                "AUD — Australian Dollar ($)",
                "CAD — Canadian Dollar ($)"
            ],
            state="readonly",
            font=("Segoe UI", 16),
            width=50
        )
        currency_combo.pack(fill=tk.X, pady=(0, 10))
        currency_combo.bind("<<ComboboxSelected>>", lambda e: self.save_currency())
        self.currency_combo = currency_combo
        
        help_text = tk.Label(
            currency_field,
            text="Updates save automatically and apply the next time you open Sold Items Trends.",
            font=("Segoe UI", 14),
            bg="white",
            fg="#6b7280",
            anchor=tk.W
        )
        help_text.pack(anchor=tk.W)
        
        # Status label (matching HTML .settings-status)
        self.status_label = tk.Label(
            card,
            text="",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#1f2937",
            anchor=tk.W
        )
        self.status_label.pack(anchor=tk.W, pady=(12, 0))
    
    def load_settings(self):
        """Load settings"""
        self.settings = self.data_manager.load_settings()
        currency = self.settings.get('soldCurrency', 'GBP')
        
        currency_map = {
            'GBP': "GBP — British Pound (£)",
            'USD': "USD — US Dollar ($)",
            'EUR': "EUR — Euro (€)",
            'AUD': "AUD — Australian Dollar ($)",
            'CAD': "CAD — Canadian Dollar ($)"
        }
        
        self.currency_var.set(currency_map.get(currency, currency_map['GBP']))
        self.update_status()
    
    def save_currency(self):
        """Save currency setting"""
        value = self.currency_var.get()
        currency_code = value.split(' — ')[0]
        
        self.settings['soldCurrency'] = currency_code
        self.data_manager.save_settings(self.settings)
        self.update_status()
    
    def update_status(self):
        """Update status label"""
        currency = self.settings.get('soldCurrency', 'GBP')
        currency_map = {
            'GBP': '£',
            'USD': '$',
            'EUR': '€',
            'AUD': '$',
            'CAD': '$'
        }
        symbol = currency_map.get(currency, '£')
        self.status_label.config(text=f"• Currently using {currency} ({symbol}).")
    
    def refresh(self):
        """Refresh the view"""
        self.load_settings()

