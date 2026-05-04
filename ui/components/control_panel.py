"""
ui/components/control_panel.py - Algorithm control panel widget.

Single responsibility: render the Start/End dropdowns and algorithm buttons,
then fire callbacks when the user acts. Zero algorithm logic lives here.

Usage
-----
    panel = ControlPanel(
        parent,
        buildings=BUILDINGS,
        on_run=handle_run,          # called with (algo_name, start, end)
        on_reset=handle_reset,
        on_clear_marks=handle_clear,
    )
    panel.grid(...)
"""

import tkinter as tk
from tkinter import ttk

from ui.theme import COLORS, accent_button

_PANEL_BG  = COLORS["bg_panel"]
_TEXT      = COLORS["text_primary"]
_TEXT_MUTED = COLORS["text_muted"]
_BORDER    = COLORS["border"]


class ControlPanel(tk.Frame):
    """
    Dropdowns + algorithm run buttons.

    Callbacks
    ---------
    on_run(algo: str, start: str, end: str)
        Fired for Dijkstra, BFS, DFS, Prim's.
        ``algo`` is one of: "dijkstra", "bfs", "dfs", "prims".
    on_reset()
        Fired when "Reset Graph" is clicked.
    on_clear_marks()
        Fired when "Clear Coordinate Marks" is clicked.
    """

    def __init__(
        self,
        parent,
        buildings: list[str],
        on_run,
        on_reset,
        on_clear_marks,
        **kwargs,
    ):
        super().__init__(parent, bg=_PANEL_BG,
                         highlightbackground=_BORDER, highlightthickness=1,
                         **kwargs)
        self._buildings      = buildings
        self._on_run         = on_run
        self._on_reset       = on_reset
        self._on_clear_marks = on_clear_marks

        self._start_var = tk.StringVar(value=buildings[0] if buildings else "")
        self._end_var   = tk.StringVar(value=buildings[1] if len(buildings) > 1 else "")

        self.columnconfigure(1, weight=1)
        self._build()

    # ── Public ────────────────────────────────────────────────────────────────

    @property
    def start(self) -> str:
        return self._start_var.get()

    @property
    def end(self) -> str:
        return self._end_var.get()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        tk.Label(
            self, text="Control Panel",
            fg=_TEXT, bg=_PANEL_BG,
            font=("Courier New", 12, "bold"),
            anchor="w", padx=10, pady=8,
        ).grid(row=0, column=0, columnspan=2, sticky="ew")

        self._labeled_dropdown(row=1, label="Start Node:",       var=self._start_var)
        self._labeled_dropdown(row=2, label="Destination Node:", var=self._end_var)

        buttons = [
            ("Run Dijkstra's",         lambda: self._fire("dijkstra")),
            ("Run BFS",                lambda: self._fire("bfs")),
            ("Run DFS",                lambda: self._fire("dfs")),
            ("Run Prim's MST",         lambda: self._fire("prims")),
            ("Reset Graph",            self._on_reset),
            ("Clear Coordinate Marks", self._on_clear_marks),
        ]
        for row, (label, cmd) in enumerate(buttons, start=3):
            accent_button(self, text=label, command=cmd).grid(
                row=row, column=0, columnspan=2,
                sticky="ew", padx=18, pady=4,
            )

    def _labeled_dropdown(self, row: int, label: str, var: tk.StringVar):
        tk.Label(
            self, text=label,
            font=("Courier New", 10), fg=_TEXT_MUTED, bg=_PANEL_BG,
        ).grid(row=row, column=0, sticky="w", padx=(12, 8), pady=(8 if row == 1 else 4, 4))

        ttk.Combobox(
            self, textvariable=var,
            values=self._buildings,
            state="readonly",
            font=("Courier New", 10),
        ).grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=(8 if row == 1 else 4, 4))

    def _fire(self, algo: str):
        self._on_run(algo, self._start_var.get(), self._end_var.get())
