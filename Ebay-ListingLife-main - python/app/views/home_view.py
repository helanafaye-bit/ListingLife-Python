"""
Home View
Welcome screen for the application - matches HTML exactly
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path


class HomeView:
    """Home/welcome view"""
    
    def __init__(self, parent, data_manager, main_window):
        self.parent = parent
        self.data_manager = data_manager
        self.main_window = main_window
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the home view UI - matching HTML landing page"""
        # Clear any existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container (matching HTML .landing-container)
        container = tk.Frame(self.parent, bg="#F4F3F2")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=60)
        
        # Hero section (matching HTML .landing-hero)
        hero_frame = tk.Frame(container, bg="white", relief=tk.RAISED, borderwidth=1)
        hero_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Hero content (matching HTML structure)
        hero_content = tk.Frame(hero_frame, bg="white")
        hero_content.pack(expand=True, fill=tk.BOTH, padx=60, pady=60)
        
        # Title (matching HTML h1)
        title_label = tk.Label(
            hero_content,
            text="Welcome to ListingLife",
            font=("Segoe UI", 36, "bold"),
            bg="white",
            fg="#0f172a"
        )
        title_label.pack(pady=(0, 20))
        
        # Logo graphic below title (matching HTML .landing-hero-graphic)
        logo_path = Path(__file__).parent.parent / "assets" / "listinglife-logo.png"
        
        try:
            if logo_path.exists():
                logo_image = tk.PhotoImage(file=str(logo_path))
                # Resize logo to a reasonable size for the hero section
                logo_width = 300
                original_width = logo_image.width()
                original_height = logo_image.height()
                aspect_ratio = original_width / original_height
                logo_height = int(logo_width / aspect_ratio)
                
                logo_image = logo_image.subsample(
                    max(1, original_width // logo_width),
                    max(1, original_height // logo_height)
                )
                
                logo_label = tk.Label(
                    hero_content,
                    image=logo_image,
                    bg="white"
                )
                logo_label.pack(pady=(0, 20))
                logo_label.image = logo_image  # Keep a reference
        except Exception as e:
            print(f"Error loading logo in home view: {e}")
            # Continue without logo if loading fails
        
        # Description (matching HTML p)
        desc_text = (
            "A simple interface for your active listings, split into categories. "
            "Each item shows an end date so you know when to remove it from your "
            "eBay/shop and refresh with new stock. You can also use it to track "
            "which categories or items sell most often."
        )
        desc_label = tk.Label(
            hero_content,
            text=desc_text,
            font=("Segoe UI", 14),
            bg="white",
            fg="#1f2937",
            wraplength=800,
            justify=tk.LEFT
        )
        desc_label.pack(pady=(0, 30))
        
        # Get Started button (matching HTML button)
        get_started_btn = tk.Button(
            hero_content,
            text="Get Started",
            command=self.main_window.show_listings,
            font=("Segoe UI", 14, "bold"),
            bg="#86b817",
            fg="white",
            padx=32,
            pady=14,
            cursor="hand2",
            relief=tk.FLAT,
            borderwidth=0
        )
        get_started_btn.pack()
    
    def refresh(self):
        """Refresh the view"""
        pass
