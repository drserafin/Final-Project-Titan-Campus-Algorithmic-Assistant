"""
ui/components/results_panel.py - Algorithm results display widget.

Single responsibility: show algorithm results in a single scrollable text box.
Zero algorithm logic or canvas code lives here.

Usage
-----
    panel = ResultsPanel(parent)
    panel.grid(...)

    panel.update(from_label, to_label, metric, status, details_text)
    panel.clear()
"""

import tkinter as tk

from ui.theme import COLORS

_PANEL_BG = COLORS["bg_panel"]
_TEXT     = COLORS["text_primary"]
_MUTED    = COLORS["text_muted"]
_BORDER   = COLORS["border"]
_ACCENT   = COLORS["accent"]


class ResultsPanel(tk.Frame):
    """Single scrollable text box that shows all result information."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=_PANEL_BG,
                         highlightbackground=_BORDER, highlightthickness=1,
                         **kwargs)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._build()

    # ── Public ────────────────────────────────────────────────────────────────

    def update(
        self,
        from_label: str,
        to_label: str,
        metric: str,
        status: str,
        details: str,
    ):
        """Write a formatted result block into the text box."""
        header = (
            f"  From   : {from_label}\n"
            f"  To     : {to_label}\n"
            f"  Result : {metric}  |  {status}\n"
            f"{'─' * 48}\n"
            f"{details}\n"
        )
        self._set_text(header)

    def clear(self):
        self._set_text("")

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        tk.Label(
            self, text="Results",
            fg=_TEXT, bg=_PANEL_BG,
            font=("Courier New", 14, "bold"),
            anchor="w", padx=10, pady=8,
        ).grid(row=0, column=0, sticky="ew")

        box_frame = tk.Frame(self, bg=_PANEL_BG)
        box_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        box_frame.rowconfigure(0, weight=1)
        box_frame.columnconfigure(0, weight=1)

        self._box = tk.Text(
            box_frame,
            bg=COLORS["bg_dark"],
            fg=_TEXT,
            insertbackground=_ACCENT,
            font=("Courier New", 18),
            wrap="word",
            relief="flat",
            bd=6,
            state="disabled",
            spacing1=2,   # extra px above each line
            spacing3=2,   # extra px below each line
        )
        scrollbar = tk.Scrollbar(box_frame, command=self._box.yview)
        self._box.configure(yscrollcommand=scrollbar.set)
        self._box.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _set_text(self, text: str):
        self._box.configure(state="normal")
        self._box.delete("1.0", "end")
        self._box.insert("end", text)
        self._box.configure(state="disabled")