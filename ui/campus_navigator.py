"""
ui/campus_navigator.py - Campus Navigator page.

Single responsibility: wire the sub-components together and handle
the algorithm-run callback. No animation code, no layout sub-building,
no data storage — all of that lives in the dedicated modules.

Sub-components
--------------
    ui/map_animator.py              -- canvas animation engine
    ui/graph_view.py                -- abstract graph renderer
    ui/components/control_panel.py  -- dropdowns + buttons
    ui/components/results_panel.py  -- treeview + details box
    algorithms/graph.py             -- graph data + algorithms
"""

import math
import sys
import tkinter as tk
from pathlib import Path

from algorithms.graph import (
    BUILDINGS, BUILDING_COORDS, CAMPUS_GRAPH,
    bfs, dfs, dijkstra, prims_mst,
)
from ui.theme import COLORS

# Use the same platform-safe button as app.py so bg color is respected on macOS
if sys.platform == "darwin":
    from tkmacosx import Button as _Btn
else:
    from tkinter import Button as _Btn
from ui.map_animator import MapAnimator
from ui.graph_view import GraphView
from ui.components.control_panel import ControlPanel
from ui.components.results_panel import ResultsPanel


# ── File paths & canvas geometry ──────────────────────────────────────────────
CAMPUS_MAP    = Path(__file__).parent.parent / "assets" / "campus_map.png"
CANVAS_WIDTH  = 680
CANVAS_HEIGHT = 880

# ── Colours (algorithm-specific) ──────────────────────────────────────────────
_BG_DARK   = COLORS["bg_dark"]
_PANEL_BG  = COLORS["bg_panel"]
_TEXT      = COLORS["text_primary"]
_TEXT_MUTED = COLORS["text_muted"]
_BORDER    = COLORS["border"]

PATH_COLOR      = "#ef4444"   # Dijkstra + BFS
DFS_COLOR       = "#8b5cf6"
PRIM_COLOR      = "#10b981"
MAP_DOT_COLOR   = "#3b82f6"   # initial building dots on map
COORD_DOT_COLOR = "#facc15"   # click-to-mark dots


class CampusNavigatorFrame(tk.Frame):
    """
    Top-level campus navigator page.

    Responsibilities
    ----------------
    - Create the canvas, map image, and coordinate-click feature.
    - Instantiate and grid all sub-components.
    - Implement handle_run(): translate an algorithm name into a call to
      algorithms/graph.py, then feed the result to the animator and results panel.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=_BG_DARK)
        self._map_photo  = None
        self._view_mode  = "map"   # "map" | "graph"
        self._coord_var  = tk.StringVar(value="Click the map to mark a coordinate.")

        self._build_layout()
        self._load_map()
        self._draw_map_dots()

    # ─────────────────────────────────────────
    # Layout assembly
    # ─────────────────────────────────────────

    def _build_layout(self):
        body = tk.Frame(self, bg=_BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.columnconfigure(0, weight=0, minsize=CANVAS_WIDTH + 20)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Left column: map panel ────────────────────────────────────────────
        map_panel = tk.Frame(
            body, bg=_PANEL_BG,
            highlightbackground=_BORDER, highlightthickness=1,
        )
        map_panel.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        self._build_map_header(map_panel)

        self.canvas = tk.Canvas(
            map_panel,
            width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
            bg="#f8fafc", highlightthickness=0, bd=0,
        )
        self.canvas.grid(row=1, column=0, sticky="nw", padx=8, pady=(4, 6))
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        tk.Label(
            map_panel, textvariable=self._coord_var,
            fg=_TEXT_MUTED, bg=_PANEL_BG,
            font=("Courier New", 10), anchor="w", padx=10, pady=5,
        ).grid(row=2, column=0, sticky="ew")

        # ── Sub-systems that need the canvas ─────────────────────────────────
        self._animator = MapAnimator(
            self.canvas, self.after, self.after_cancel,
        )
        self._animator.set_coord_fn(self._get_coord)

        self._graph_view = GraphView(self.canvas, CANVAS_WIDTH, CANVAS_HEIGHT)

        # ── Right column: controls + hint + results ───────────────────────────
        side = tk.Frame(body, bg=_BG_DARK)
        side.grid(row=0, column=1, sticky="nsew")
        side.rowconfigure(2, weight=1)
        side.columnconfigure(0, weight=1)

        self._controls = ControlPanel(
            side,
            buildings=BUILDINGS,
            on_run=self._handle_run,
            on_reset=self._handle_reset,
            on_clear_marks=self._clear_coord_marks,
        )
        self._controls.grid(row=0, column=0, sticky="new")

        self._build_hint(side)

        self._results = ResultsPanel(side)
        self._results.grid(row=2, column=0, sticky="nsew")

    def _build_map_header(self, parent):
        header = tk.Frame(parent, bg=_PANEL_BG)
        header.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))
        header.columnconfigure(0, weight=1)

        self._canvas_title = tk.StringVar(value="Map Canvas")
        tk.Label(
            header, textvariable=self._canvas_title,
            fg=_TEXT, bg=_PANEL_BG,
            font=("Courier New", 12, "bold"),
            anchor="w", padx=4, pady=8,
        ).grid(row=0, column=0, sticky="w")

        toggle = tk.Frame(header, bg=_PANEL_BG)
        toggle.grid(row=0, column=1, sticky="e")

        accent = COLORS.get("accent", "#6D28D9")
        self._btn_map = _Btn(
            toggle, text="🗺  Map View",
            command=lambda: self._switch_view("map"),
            fg=_TEXT, bg=accent, activeforeground=_TEXT,
            activebackground="#2563EB", relief="flat",
            font=("Courier New", 9, "bold"), cursor="hand2", padx=8, pady=4,
        )
        self._btn_map.pack(side="left", padx=(0, 4))

        self._btn_graph = _Btn(
            toggle, text="⬡  Graph View",
            command=lambda: self._switch_view("graph"),
            fg=_TEXT, bg="#334155", activeforeground=_TEXT,
            activebackground="#2563EB", relief="flat",
            font=("Courier New", 9, "bold"), cursor="hand2", padx=8, pady=4,
        )
        self._btn_graph.pack(side="left")

    def _build_hint(self, parent):
        hint = tk.Frame(parent, bg="#15104A",
                        highlightbackground=_BORDER, highlightthickness=1)
        hint.grid(row=1, column=0, sticky="ew", pady=10)
        tk.Label(
            hint,
            text=(
                "Click the map to mark coordinates. "
                "Toggle Graph View to see edges & weights. "
                "Run an algorithm to animate routes."
            ),
            font=("Courier New", 9), fg=_TEXT_MUTED, bg="#15104A",
            justify="left", wraplength=390, padx=10, pady=8,
        ).pack(fill="x")

    # ─────────────────────────────────────────
    # View switching
    # ─────────────────────────────────────────

    def _switch_view(self, mode: str):
        if mode == self._view_mode:
            return

        self._animator.reset()
        self._view_mode = mode
        accent = COLORS.get("accent", "#6D28D9")

        if mode == "map":
            self._canvas_title.set("Map Canvas")
            self._btn_map.configure(bg=accent)
            self._btn_graph.configure(bg="#334155")
            self.canvas.configure(bg="#f8fafc")
            # Restore map-coord resolver and no-op graph hooks
            self._animator.set_coord_fn(self._get_coord)
            self._animator.set_graph_hooks(
                lambda u, v, c: None, lambda n, c: None, lambda: None,
            )
            self._load_map()
            self._draw_map_dots()

        else:  # "graph"
            self._canvas_title.set("Graph View  —  nodes & edge weights")
            self._btn_map.configure(bg="#334155")
            self._btn_graph.configure(bg=accent)
            self._graph_view.render(BUILDINGS, CAMPUS_GRAPH)
            # Switch animator to graph-view coords and highlight hooks
            self._animator.set_coord_fn(self._graph_view.get_coord)
            self._animator.set_graph_hooks(
                self._graph_view.highlight_edge,
                self._graph_view.highlight_node,
                self._graph_view.reset_colors,
            )

    def _get_coord(self, building_name: str) -> tuple[int, int] | None:
        """Map-view coordinate resolver."""
        return BUILDING_COORDS.get(building_name)

    # ─────────────────────────────────────────
    # Map loading + initial dots
    # ─────────────────────────────────────────

    def _load_map(self):
        self.canvas.delete("all")
        if not CAMPUS_MAP.exists():
            self._draw_fallback()
            return
        try:
            from PIL import Image, ImageTk
            img = Image.open(CAMPUS_MAP)
            img.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
            self._map_photo = ImageTk.PhotoImage(img)
            self.canvas.configure(
                width=self._map_photo.width(), height=self._map_photo.height(),
            )
            self.canvas.create_image(0, 0, image=self._map_photo, anchor="nw", tags="map_image")
            return
        except Exception:
            pass
        try:
            self._map_photo = tk.PhotoImage(file=str(CAMPUS_MAP)).subsample(4, 4)
            self.canvas.configure(
                width=self._map_photo.width(), height=self._map_photo.height(),
            )
            self.canvas.create_image(0, 0, image=self._map_photo, anchor="nw", tags="map_image")
        except Exception:
            self._draw_fallback()

    def _draw_fallback(self):
        self.canvas.create_rectangle(
            0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#f8fafc", outline="#111827",
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 24,
            text="Campus map image could not be loaded",
            fill="#111827", font=("Courier New", 12, "bold"),
        )

    def _draw_map_dots(self):
        self.canvas.delete("initial_building")
        for _name, (x, y) in BUILDING_COORDS.items():
            self.canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,
                fill=MAP_DOT_COLOR, outline="white", width=2,
                tags="initial_building",
            )
        self.canvas.tag_raise("initial_building")

    # ─────────────────────────────────────────
    # Canvas click (map view only)
    # ─────────────────────────────────────────

    def _on_canvas_click(self, event):
        if self._view_mode != "map":
            return
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        msg = f"Clicked coordinate: ({x}, {y})"
        self._coord_var.set(msg)
        print(msg)
        self.canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill=COORD_DOT_COLOR, outline="#111827", width=2,
            tags=("coord_mark",),
        )
        self.canvas.create_text(
            x + 8, y - 8, text=f"({x}, {y})",
            fill="#111827", font=("Courier New", 8, "bold"),
            anchor="w", tags=("coord_mark",),
        )
        self.canvas.tag_raise("coord_mark")

    def _clear_coord_marks(self):
        self.canvas.delete("coord_mark")
        self._coord_var.set("Click the map to mark a coordinate.")

    # ─────────────────────────────────────────
    # Algorithm dispatch
    # ─────────────────────────────────────────

    def _handle_run(self, algo: str, start: str, end: str):
        """Called by ControlPanel with the chosen algorithm and nodes."""
        self._animator.reset()
        if self._view_mode == "map":
            self._draw_map_dots()

        dispatch = {
            "dijkstra": self._run_dijkstra,
            "bfs":      self._run_bfs,
            "dfs":      self._run_dfs,
            "prims":    self._run_prims,
        }
        dispatch[algo](start, end)

    def _handle_reset(self):
        self._animator.reset()
        self._results.clear()
        if self._view_mode == "map":
            self._draw_map_dots()

    # ── Individual algorithm runners ──────────────────────────────────────────

    def _run_dijkstra(self, start: str, end: str):
        if start == end:
            return self._results.update(
                self._abbr(start), self._abbr(end),
                "Start=End", "-", "Dijkstra path:\nStart and end are the same.",
            )
        dist, time, path = dijkstra(CAMPUS_GRAPH, start, end)
        if path:
            self._results.update(
                self._abbr(start), self._abbr(end),
                self._fmt_dist(dist), self._fmt_time(time),
                "Dijkstra shortest path by distance:\n"
                + " -> ".join(path)
                + f"\n\nTotal distance: {self._fmt_dist(dist)}"
                + f"\nTotal time: {self._fmt_time(time)}",
            )
            self._animator.draw_path(path, PATH_COLOR, PATH_COLOR, "Dijkstra")
        else:
            self._results.update(
                self._abbr(start), self._abbr(end),
                "No Path", "Failed", "Dijkstra could not find a path.",
            )

    def _run_bfs(self, start: str, end: str):
        if start == end:
            return self._results.update(
                self._abbr(start), self._abbr(end),
                "Start=End", "-", "BFS path:\nStart and end are the same.",
            )
        hops, dist, time, path = bfs(CAMPUS_GRAPH, start, end)
        if path:
            self._results.update(
                self._abbr(start), self._abbr(end),
                f"Hops: {hops} ({dist} units)", self._fmt_time(time),
                "BFS path with fewest hops:\n"
                + " -> ".join(path)
                + f"\n\nHops: {hops}"
                + f"\nTotal distance: {self._fmt_dist(dist)}"
                + f"\nTotal time: {self._fmt_time(time)}",
            )
            self._animator.draw_path(path, PATH_COLOR, PATH_COLOR, "BFS")
        else:
            self._results.update(
                self._abbr(start), self._abbr(end),
                "No Path", "Failed", "BFS could not find a path.",
            )

    def _run_dfs(self, start: str, _end: str):
        visited, _connected, status = dfs(CAMPUS_GRAPH, start)
        numbered = "\n".join(f"{i}. {n}" for i, n in enumerate(visited, 1))
        self._results.update(
            self._abbr(start), "—",
            f"{len(visited)} nodes", status,
            f"DFS traversal order:\n{numbered}\n\nConnectivity: {status}",
        )
        self._animator.draw_path(visited, DFS_COLOR, DFS_COLOR, "DFS")

    def _run_prims(self, _start: str, _end: str):
        mst_edges, total_dist, total_time = prims_mst(CAMPUS_GRAPH)
        edge_lines = "\n".join(
            f"{i}. {u} -> {v} ({w} units)"
            for i, (u, v, w) in enumerate(mst_edges, 1)
        )
        self._results.update(
            "MST", "all nodes",
            self._fmt_dist(total_dist), self._fmt_time(total_time),
            "Prim's MST edges:\n"
            + edge_lines
            + f"\n\nTotal MST distance: {self._fmt_dist(total_dist)}"
            + f"\nTotal MST time: {self._fmt_time(total_time)}",
        )
        self._animator.draw_mst(mst_edges, PRIM_COLOR, PRIM_COLOR)

    # ─────────────────────────────────────────
    # Formatting helpers
    # ─────────────────────────────────────────

    @staticmethod
    def _abbr(name: str) -> str:
        if "(" in name and ")" in name:
            return name.split("(")[-1].split(")")[0]
        return name

    @staticmethod
    def _fmt_dist(d) -> str:
        return "No Path" if d is None or d == math.inf else f"{d} units"

    @staticmethod
    def _fmt_time(t) -> str:
        return "Failed" if t is None or t == math.inf else f"{t} min"