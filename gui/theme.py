"""
theme.py — Design tokens & color palette untuk Easy Peasy Bot GUI.
Terinspirasi dari TradingView dark mode.
"""

import customtkinter as ctk

# =============================================================================
# GLOBAL CTK APPEARANCE
# =============================================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =============================================================================
# COLOR PALETTE
# =============================================================================
COLORS = {
    # Backgrounds
    "bg_primary":       "#0D1117",
    "bg_secondary":     "#161B22",
    "bg_tertiary":      "#1C2128",
    "bg_card":          "#21262D",
    "bg_hover":         "#2D333B",

    # Sidebar
    "sidebar_bg":       "#0D1117",
    "sidebar_border":   "#30363D",

    # Accents
    "accent_blue":      "#58A6FF",
    "accent_blue_dim":  "#1C3A5C",
    "accent_green":     "#3FB950",
    "accent_green_dim": "#14341E",
    "accent_red":       "#F85149",
    "accent_red_dim":   "#3D1C1B",
    "accent_yellow":    "#D29922",
    "accent_purple":    "#BC8CFF",
    "accent_orange":    "#E3B341",

    # Text
    "text_primary":     "#E6EDF3",
    "text_secondary":   "#8B949E",
    "text_muted":       "#484F58",
    "text_link":        "#58A6FF",

    # Borders
    "border":           "#30363D",
    "border_subtle":    "#21262D",

    # Status
    "status_running":   "#3FB950",
    "status_stopped":   "#F85149",
    "status_warning":   "#D29922",
    "status_neutral":   "#8B949E",
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONTS = {
    "title_xl":     ("Segoe UI", 22, "bold"),
    "title_lg":     ("Segoe UI", 18, "bold"),
    "title_md":     ("Segoe UI", 15, "bold"),
    "title_sm":     ("Segoe UI", 13, "bold"),
    "body_lg":      ("Segoe UI", 13),
    "body_md":      ("Segoe UI", 12),
    "body_sm":      ("Segoe UI", 11),
    "mono_lg":      ("Consolas", 13),
    "mono_md":      ("Consolas", 12),
    "mono_sm":      ("Consolas", 11),
    "label":        ("Segoe UI", 11),
    "label_bold":   ("Segoe UI", 11, "bold"),
    "caption":      ("Segoe UI", 10),
    "nav_item":     ("Segoe UI", 12, "bold"),
    "nav_header":   ("Segoe UI", 10, "bold"),
}

# =============================================================================
# WIDGET DEFAULTS
# =============================================================================

def entry_style():
    return {
        "fg_color": COLORS["bg_card"],
        "border_color": COLORS["border"],
        "text_color": COLORS["text_primary"],
        "border_width": 1,
        "corner_radius": 6,
        "font": FONTS["body_md"],
    }

def button_primary():
    return {
        "fg_color": COLORS["accent_blue"],
        "hover_color": "#4c94e8",
        "text_color": "#FFFFFF",
        "corner_radius": 6,
        "font": FONTS["body_md"],
        "border_width": 0,
    }

def button_success():
    return {
        "fg_color": COLORS["accent_green"],
        "hover_color": "#2ea043",
        "text_color": "#FFFFFF",
        "corner_radius": 8,
        "font": ("Segoe UI", 14, "bold"),
        "border_width": 0,
    }

def button_danger():
    return {
        "fg_color": COLORS["accent_red"],
        "hover_color": "#d73a49",
        "text_color": "#FFFFFF",
        "corner_radius": 8,
        "font": ("Segoe UI", 14, "bold"),
        "border_width": 0,
    }

def button_secondary():
    return {
        "fg_color": COLORS["bg_card"],
        "hover_color": COLORS["bg_hover"],
        "text_color": COLORS["text_primary"],
        "corner_radius": 6,
        "font": FONTS["body_md"],
        "border_width": 1,
        "border_color": COLORS["border"],
    }

def button_ghost():
    return {
        "fg_color": "transparent",
        "hover_color": COLORS["bg_hover"],
        "text_color": COLORS["text_secondary"],
        "corner_radius": 6,
        "font": FONTS["body_md"],
        "border_width": 0,
    }

def frame_card():
    return {
        "fg_color": COLORS["bg_card"],
        "corner_radius": 8,
        "border_width": 1,
        "border_color": COLORS["border"],
    }

def frame_section():
    return {
        "fg_color": COLORS["bg_secondary"],
        "corner_radius": 10,
        "border_width": 1,
        "border_color": COLORS["border_subtle"],
    }

def switch_style():
    return {
        "progress_color": COLORS["accent_green"],
        "button_color": COLORS["text_primary"],
        "button_hover_color": "#FFFFFF",
        "fg_color": COLORS["bg_hover"],
    }

def slider_style():
    return {
        "progress_color": COLORS["accent_blue"],
        "button_color": COLORS["accent_blue"],
        "button_hover_color": "#4c94e8",
        "fg_color": COLORS["bg_hover"],
    }

def dropdown_style():
    return {
        "fg_color": COLORS["bg_card"],
        "button_color": COLORS["bg_hover"],
        "button_hover_color": COLORS["border"],
        "dropdown_fg_color": COLORS["bg_secondary"],
        "text_color": COLORS["text_primary"],
        "dropdown_text_color": COLORS["text_primary"],
        "dropdown_hover_color": COLORS["bg_hover"],
        "border_color": COLORS["border"],
        "border_width": 1,
        "corner_radius": 6,
        "font": FONTS["body_md"],
    }

def label_style(color="primary", font_key="body_md"):
    color_map = {
        "primary": COLORS["text_primary"],
        "secondary": COLORS["text_secondary"],
        "muted": COLORS["text_muted"],
        "green": COLORS["accent_green"],
        "red": COLORS["accent_red"],
        "blue": COLORS["accent_blue"],
        "yellow": COLORS["accent_yellow"],
        "purple": COLORS["accent_purple"],
    }
    return {
        "text_color": color_map.get(color, COLORS["text_primary"]),
        "font": FONTS.get(font_key, FONTS["body_md"]),
    }

# =============================================================================
# SECTION HEADER HELPER
# =============================================================================

def make_section_header(parent, title: str, subtitle: str = "") -> ctk.CTkFrame:
    """Buat section header dengan garis bawah biru."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=(10, 6))

    title_label = ctk.CTkLabel(
        frame,
        text=title,
        font=FONTS["title_sm"],
        text_color=COLORS["accent_blue"],
        anchor="w",
    )
    title_label.pack(side="left")

    sep = ctk.CTkFrame(frame, height=1, fg_color=COLORS["border"])
    sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=(8, 0))

    if subtitle:
        sub_label = ctk.CTkLabel(
            parent,
            text=subtitle,
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        sub_label.pack(fill="x", pady=(0, 4))

    return frame
