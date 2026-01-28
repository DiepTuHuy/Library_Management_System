# Theme Configuration for CustomTkinter
import customtkinter as ctk

# Color Palette
COLORS = {
    # Primary Colors
    "primary": "#2563EB",      # Blue
    "primary_light": "#3B82F6",
    "primary_dark": "#1E40AF",
    
    # Accent Colors
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Red
    "info": "#06B6D4",         # Cyan
    
    # Backgrounds
    "bg_dark": "#0F172A",
    "bg_primary": "#1E293B",
    "bg_secondary": "#334155",
    "bg_light": "#F8FAFC",
    
    # Text Colors
    "text_primary": "#FFFFFF",
    "text_secondary": "#CBD5E1",
    "text_dark": "#0F172A",
    
    # Neutral
    "border": "#475569",
    "disabled": "#64748B",
}

# Fonts
FONTS = {
    "title": ("Segoe UI", 32, "bold"),
    "heading": ("Segoe UI", 24, "bold"),
    "subheading": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 14, "normal"),
    "body_small": ("Segoe UI", 12, "normal"),
    "label": ("Segoe UI", 13, "normal"),
    "button": ("Segoe UI", 13, "bold"),
}

# Sizes
SIZES = {
    "padding_xs": 5,
    "padding_sm": 10,
    "padding_md": 15,
    "padding_lg": 20,
    "padding_xl": 30,
    
    "button_height": 40,
    "input_height": 40,
    "row_height": 50,
}

def setup_theme():
    """Setup CustomTkinter theme"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    return COLORS, FONTS, SIZES
