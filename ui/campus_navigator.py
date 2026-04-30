"""
ui/campus_navigator.py - Campus Navigator module UI.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from algorithms.graph import BUILDINGS
from ui.theme import (
    COLORS,
    FONT_BODY,
    FONT_SMALL,
    FONT_SUBHEAD,
    accent_button,
    card,
    ghost_button,
    panel_title,
    write_output,
)

CAMPUS_MAP = Path(__file__).parent.parent / "assets" / "campus_map.png"


class CampusNavigatorFrame(tk.Frame):
    """Module 1 - BFS, DFS, Dijkstra, and Prim's MST."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self._map_photo = None
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=COLORS["bg_dark"])
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.columnconfigure(0, weight=3, minsize=540)
        body.columnconfigure(1, weight=2, minsize=360)
        body.rowconfigure(0, weight=1)

        self._build_map(body)
        self._build_side_panel(body)

    def _build_map(self, parent):
        map_card = card(parent)
        map_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        map_card.rowconfigure(1, weight=1)
        map_card.columnconfigure(0, weight=1)

        panel_title(map_card, "Map Canvas").grid(row=0, column=0, sticky="ew")
        tk.Frame(map_card, bg=COLORS["border"], height=1).grid(row=1, column=0, sticky="new")

        self._map_label = tk.Label(
            map_card,
            bg=COLORS["bg_panel"],
            fg=COLORS["text_secondary"],
            text="",
            anchor="center",
        )
        self._map_label.grid(row=1, column=0, sticky="nsew", padx=8, pady=(9, 8))
        self._load_map()
        map_card.bind("<Configure>", self._on_map_resize)

    def _build_side_panel(self, parent):
        side = tk.Frame(parent, bg=COLORS["bg_dark"])
        side.grid(row=0, column=1, sticky="nsew")
        side.rowconfigure(0, weight=0)
        side.rowconfigure(1, weight=0)
        side.rowconfigure(2, weight=1)
        side.columnconfigure(0, weight=1)

        self._build_controls(side)
        self._build_hint(side)
        self._build_results(side)

    def _build_controls(self, parent):
        ctrl = card(parent)
        ctrl.grid(row=0, column=0, sticky="new")
        ctrl.columnconfigure(1, weight=1)

        panel_title(ctrl, "Control Panel").grid(row=0, column=0, columnspan=2, sticky="ew")

        tk.Label(
            ctrl,
            text="Start Node:",
            font=FONT_BODY,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_panel"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=(8, 4))
        self._start_var = tk.StringVar(value=BUILDINGS[0] if BUILDINGS else "")
        self._start_dd = self._dropdown(ctrl, self._start_var)
        self._start_dd.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(8, 4))

        tk.Label(
            ctrl,
            text="Destination Node:",
            font=FONT_BODY,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_panel"],
            anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=(12, 8), pady=4)
        end_value = BUILDINGS[1] if len(BUILDINGS) > 1 else (BUILDINGS[0] if BUILDINGS else "")
        self._end_var = tk.StringVar(value=end_value)
        self._end_dd = self._dropdown(ctrl, self._end_var)
        self._end_dd.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=4)

        tk.Frame(ctrl, bg=COLORS["border"], height=1).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 8)
        )

        tk.Label(
            ctrl,
            text="Algorithm Options",
            font=FONT_SUBHEAD,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_panel"],
            anchor="w",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 4))

        algos = [
            ("Run Dijkstra's (Shortest Path)", self._run_dijkstra),
            ("Run BFS (Fewest Hops)", self._run_bfs),
            ("Run DFS (Connectivity)", self._run_dfs),
            ("Run Prim's MST", self._run_prims),
        ]
        for row, (label, command) in enumerate(algos, start=5):
            accent_button(ctrl, label, command=command).grid(
                row=row,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=18,
                pady=4,
            )

        ghost_button(ctrl, "Reset Graph", command=self._reset).grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=18,
            pady=(8, 12),
        )

    def _build_hint(self, parent):
        hint = card(parent, bg=COLORS["bg_panel_alt"])
        hint.grid(row=1, column=0, sticky="ew", pady=10)
        tk.Label(
            hint,
            text=(
                "Click an algorithm to run. Dijkstra and Prim's are heap-based. "
                "BFS is fewest hops, DFS checks connectivity."
            ),
            font=FONT_SMALL,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_panel_alt"],
            justify="left",
            wraplength=390,
            padx=10,
            pady=8,
        ).pack(fill="x")

    def _build_results(self, parent):
        results = card(parent)
        results.grid(row=2, column=0, sticky="nsew")
        results.rowconfigure(1, weight=1)
        results.columnconfigure(0, weight=1)

        panel_title(results, "ttk.Treeview").grid(row=0, column=0, sticky="ew")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Purple.Treeview",
            background="#F8FAFC",
            foreground="#172554",
            fieldbackground="#F8FAFC",
            rowheight=24,
            font=FONT_BODY,
        )
        style.configure(
            "Purple.Treeview.Heading",
            background="#EDE9FE",
            foreground="#312E81",
            font=FONT_SMALL,
        )
        style.map("Purple.Treeview", background=[("selected", COLORS["accent_dim"])])

        columns = ("from", "to", "distance", "time")
        self._results = ttk.Treeview(
            results,
            columns=columns,
            show="headings",
            height=6,
            style="Purple.Treeview",
        )
        for col, title, width in (
            ("from", "From", 90),
            ("to", "To", 110),
            ("distance", "Total Distance", 120),
            ("time", "Total Time", 100),
        ):
            self._results.heading(col, text=title)
            self._results.column(col, width=width, anchor="w", stretch=True)
        self._results.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _load_map(self):
        if not CAMPUS_MAP.exists():
            self._map_label.configure(
                text="[ campus_map.png not found in assets/ ]",
                fg=COLORS["text_secondary"],
                font=FONT_BODY,
            )
            self._map_source = None
            return
        try:
            from PIL import Image, ImageTk

            self._pil_image = Image.open(CAMPUS_MAP)
            self._map_source = "pil"
            self._render_pil(680, 520)
        except ImportError:
            try:
                self._map_photo = tk.PhotoImage(file=str(CAMPUS_MAP))
                self._map_label.configure(image=self._map_photo, text="")
                self._map_source = "tk"
            except Exception as exc:
                self._map_label.configure(text=f"[ Map load error: {exc} ]", fg=COLORS["error"], font=FONT_BODY)
                self._map_source = None

    def _render_pil(self, w: int, h: int):
        from PIL import ImageTk

        img = self._pil_image.copy()
        img.thumbnail((max(w - 18, 10), max(h - 18, 10)))
        self._map_photo = ImageTk.PhotoImage(img)
        self._map_label.configure(image=self._map_photo, text="")

    def _on_map_resize(self, event):
        if not hasattr(self, "_map_source") or self._map_source != "pil":
            return
        if event.width > 10 and event.height > 10:
            self._render_pil(event.width, event.height)

    def _record_result(self, label: str, distance: str = "", time: str = ""):
        start, end = self._start_var.get(), self._end_var.get()
        self._results.delete(*self._results.get_children())
        self._results.insert("", "end", values=(start, end if end else label, distance, time))

    def _run_bfs(self):
        self._record_result("BFS", "Fewest hops", "Calculated")

    def _run_dfs(self):
        self._record_result("DFS", "Connectivity", "Calculated")

    def _run_dijkstra(self):
        self._record_result("Dijkstra", "Shortest path", "Calculated")

    def _run_prims(self):
        self._record_result("Prim's MST", "Campus MST", "Calculated")

    def _reset(self):
        self._results.delete(*self._results.get_children())

    def _dropdown(self, parent, variable) -> ttk.Combobox:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground="#F8FAFC",
            background="#DDD6FE",
            foreground="#172554",
            selectbackground=COLORS["accent_dim"],
            selectforeground=COLORS["text_primary"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["accent_2_dim"],
        )
        return ttk.Combobox(
            parent,
            textvariable=variable,
            values=BUILDINGS,
            state="readonly",
            style="Dark.TCombobox",
            font=FONT_BODY,
        )
