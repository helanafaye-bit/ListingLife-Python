"""
Utility functions for the application
"""

import tkinter as tk


def add_context_menu(widget):
    """
    Add right-click context menu (Copy, Cut, Paste) to Entry or Text widgets
    """
    def show_context_menu(event):
        """Show context menu on right click"""
        menu = tk.Menu(widget, tearoff=0)
        
        # Get clipboard content
        try:
            clipboard_content = widget.clipboard_get()
            has_clipboard = True
        except tk.TclError:
            has_clipboard = False
        
        # Check if there's selection
        try:
            if isinstance(widget, tk.Text):
                has_selection = bool(widget.tag_ranges(tk.SEL))
            else:  # Entry widget
                has_selection = bool(widget.selection_get())
        except tk.TclError:
            has_selection = False
        
        # Copy
        menu.add_command(
            label="Copy",
            command=lambda: copy_text(widget),
            state=tk.NORMAL if has_selection else tk.DISABLED
        )
        
        # Cut
        menu.add_command(
            label="Cut",
            command=lambda: cut_text(widget),
            state=tk.NORMAL if has_selection else tk.DISABLED
        )
        
        # Paste
        menu.add_command(
            label="Paste",
            command=lambda: paste_text(widget),
            state=tk.NORMAL if has_clipboard else tk.DISABLED
        )
        
        menu.add_separator()
        
        # Select All
        menu.add_command(
            label="Select All",
            command=lambda: select_all(widget)
        )
        
        # Show menu at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def copy_text(widget):
        """Copy selected text to clipboard"""
        try:
            if isinstance(widget, tk.Text):
                text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            else:  # Entry widget
                text = widget.selection_get()
            widget.clipboard_clear()
            widget.clipboard_append(text)
        except tk.TclError:
            pass
    
    def cut_text(widget):
        """Cut selected text to clipboard"""
        try:
            if isinstance(widget, tk.Text):
                text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:  # Entry widget
                text = widget.selection_get()
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            widget.clipboard_clear()
            widget.clipboard_append(text)
        except tk.TclError:
            pass
    
    def paste_text(widget):
        """Paste text from clipboard"""
        try:
            clipboard_content = widget.clipboard_get()
            if isinstance(widget, tk.Text):
                # Delete selected text if any
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass
                # Insert at cursor position
                widget.insert(tk.INSERT, clipboard_content)
            else:  # Entry widget
                # Delete selected text if any
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass
                # Insert at cursor position
                widget.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            pass
    
    def select_all(widget):
        """Select all text in widget"""
        if isinstance(widget, tk.Text):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        else:  # Entry widget
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
    
    # Bind right-click button
    widget.bind("<Button-3>", show_context_menu)  # Button-3 is right-click on Windows/Linux
    widget.bind("<Button-2>", show_context_menu)  # Button-2 is right-click on macOS (fallback)


