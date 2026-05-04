"""
ui/theme.py - Design tokens and shared UI helpers.

Import from here anywhere you need colors, fonts, or reusable widgets.
Do not scatter hex codes across files.
"""

import sys
import tkinter as tk

# -- Cross-Platform Button Fix -----------------------------------------------
if sys.platform == "darwin":
    from tkmacosx import Button as CustomButton
else:
    from tkinter import Button as CustomButton


# -- Color Palette -----------------------------------------------------------
COLORS = {
    "bg_dark": "#0A1026",
    "bg_panel": "#101A3A",
    "bg_panel_alt": "#15104A",
    "bg_hover": "#1B2C65",
    "accent": "#38BDF8",
    "accent_dim": "#2563EB",
    "accent_2": "#A855F7",
    "accent_2_dim": "#6D28D9",
    "text_primary": "#F8FAFC",
    "text_secondary": "#C7D2FE",
    "text_muted": "#94A3B8",
    "border": "#5146A6",
    "nav_bg": "#061633",
    "success": "#22C55E",
    "warning": "#FBBF24",
    "error": "#FB7185",
}

GRADIENT_STOPS = ("#0E4C8A", "#28136B", "#7C136F")

# -- Typography --------------------------------------------------------------
FONT_HEADING = ("Courier New", 22, "bold")
FONT_SUBHEAD = ("Courier New", 12, "bold")
FONT_BODY = ("Courier New", 10)
FONT_MONO = ("Courier New", 10)
FONT_NAV = ("Courier New", 11, "bold")
FONT_LOGO = ("Courier New", 16, "bold")
FONT_SMALL = ("Courier New", 9)


def gradient_bar(parent: tk.Widget, height: int = 4) -> tk.Canvas:
    """A lightweight blue-to-purple accent strip."""
    canvas = tk.Canvas(parent, height=height, bd=0, highlightthickness=0)
    canvas.pack(fill="x", side="top")

    def paint(event=None):
        canvas.delete("grad")
        width = max(canvas.winfo_width(), 1)
        stops = GRADIENT_STOPS
        segments = len(stops) - 1
        for x in range(width):
            segment = min(int(x / width * segments), segments - 1)
            local = (x - (width * segment / segments)) / (width / segments)
            c1 = _hex_to_rgb(stops[segment])
            c2 = _hex_to_rgb(stops[segment + 1])
            color = _rgb_to_hex(tuple(int(c1[i] + (c2[i] - c1[i]) * local) for i in range(3)))
            canvas.create_line(x, 0, x, height, fill=color, tags="grad")

    canvas.bind("<Configure>", paint)
    return canvas


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def section_header(parent: tk.Widget, title: str, subtitle: str = "") -> tk.Frame:
    """Renders a consistent section heading at the top of every module."""
    header = tk.Frame(parent, bg=COLORS["bg_dark"])
    header.pack(fill="x", padx=16, pady=(12, 8))

    tk.Label(
        header,
        text=title,
        font=FONT_HEADING,
        fg=COLORS["text_primary"],
        bg=COLORS["bg_dark"],
        anchor="w",
    ).pack(fill="x")

    tk.Frame(header, bg=COLORS["accent_2"], height=2).pack(fill="x", pady=(4, 0))

    if subtitle:
        tk.Label(
            header,
            text=subtitle,
            font=FONT_BODY,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"],
            anchor="w",
        ).pack(fill="x", pady=(6, 0))

    return header


def card(parent: tk.Widget, **kwargs) -> tk.Frame:
    """A panel card with consistent border and background."""
    defaults = dict(
        bg=COLORS["bg_panel"],
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        highlightthickness=1,
    )
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def panel_title(parent: tk.Widget, text: str) -> tk.Label:
    """Shared title label for framed panels."""
    return tk.Label(
        parent,
        text=text,
        font=FONT_SUBHEAD,
        fg=COLORS["text_primary"],
        bg=COLORS["bg_panel"],
        anchor="w",
        padx=10,
        pady=6,
    )


def accent_button(parent: tk.Widget, text: str, command=None, **kwargs):
    """Primary CTA button styled with the blue/purple accent."""
    defaults = dict(
        text=text,
        font=FONT_SUBHEAD,
        fg=COLORS["text_primary"],
        bg=COLORS["accent_2_dim"],
        activebackground=COLORS["accent_dim"],
        activeforeground=COLORS["text_primary"],
        relief="flat",
        bd=0,
        padx=14,
        pady=7,
        cursor="hand2",
        command=command,
    )
    defaults.update(kwargs)
    return CustomButton(parent, **defaults)


def ghost_button(parent: tk.Widget, text: str, command=None, **kwargs):
    """Secondary button style."""
    defaults = dict(
        text=text,
        font=FONT_BODY,
        fg=COLORS["text_secondary"],
        bg=COLORS["bg_panel_alt"],
        activebackground=COLORS["bg_hover"],
        activeforeground=COLORS["text_primary"],
        relief="flat",
        bd=0,
        padx=10,
        pady=5,
        cursor="hand2",
        command=command,
    )
    defaults.update(kwargs)
    return CustomButton(parent, **defaults)


def labeled_entry(parent: tk.Widget, label: str, width: int = 20) -> tuple[tk.Frame, tk.Entry]:
    """Returns (row_frame, entry_widget). Pack or grid the row_frame yourself."""
    row = tk.Frame(parent, bg=COLORS["bg_panel"])
    tk.Label(
        row,
        text=label,
        font=FONT_BODY,
        fg=COLORS["text_secondary"],
        bg=COLORS["bg_panel"],
        width=18,
        anchor="w",
    ).pack(side="left", padx=(8, 4), pady=4)
    entry = tk.Entry(
        row,
        font=FONT_MONO,
        width=width,
        bg=COLORS["bg_hover"],
        fg=COLORS["text_primary"],
        insertbackground=COLORS["accent"],
        relief="flat",
        bd=4,
    )
    entry.pack(side="left", padx=(0, 8), pady=4)
    return row, entry


def output_box(parent: tk.Widget, height: int = 12) -> tk.Text:
    """A read-only monospaced output text widget."""
    box = tk.Text(
        parent,
        font=FONT_MONO,
        bg=COLORS["bg_dark"],
        fg=COLORS["text_primary"],
        insertbackground=COLORS["accent"],
        selectbackground=COLORS["accent_2_dim"],
        relief="flat",
        bd=0,
        height=height,
        wrap="word",
        state="disabled",
    )
    sb = tk.Scrollbar(parent, command=box.yview, bg=COLORS["bg_panel"], troughcolor=COLORS["bg_dark"])
    box.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    box.pack(fill="both", expand=True, padx=(8, 0), pady=8)
    return box


def write_output(box: tk.Text, text: str, clear: bool = True):
    """Helper to write text into a read-only output_box."""
    box.configure(state="normal")
    if clear:
        box.delete("1.0", "end")
    box.insert("end", text)
    box.configure(state="disabled")
    box.see("end")