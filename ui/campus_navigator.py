"""
ui/campus_navigator.py - Campus Navigator module UI.

Simple project version:
- Uses algorithms/graph.py for graph data and algorithms
- Defines CampusNavigatorFrame for app.py
- Draws building dots and animated algorithm paths on the canvas
- Lets you click the map to discover x, y coordinates
"""

import math
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from algorithms.graph import BUILDINGS, CAMPUS_GRAPH, bfs, dfs, dijkstra, prims_mst


CAMPUS_MAP = Path(__file__).parent.parent / "assets" / "campus_map.png"

CANVAS_WIDTH = 680
CANVAS_HEIGHT = 880

BG_DARK = "#0A1026"
PANEL_BG = "#101A3A"
TEXT = "#FFFFFF"
TEXT_MUTED = "#C7D2FE"
BORDER = "#5146A6"

INITIAL_BUILDING_COLOR = "#3b82f6"
PATH_LINE_COLOR = "#ef4444"
PATH_NODE_COLOR = "#ef4444"
PRIM_LINE_COLOR = "#10b981"
PRIM_PATH_COLOR = "#10b981"
DFS_LINE_COLOR = "#8b5cf6"
DFS_PATH_COLOR = "#8b5cf6"
DISCOVERY_DOT_COLOR = "#facc15"


# Coordinates for the displayed campus map.
# Click the map in the app and send me the printed coordinates to update these.
BUILDING_COORDS = {
    "Bookstore/Titan Shops (B)": (192, 480),
    "Carl's Jr (CJ)": (337, 622),
    "Children's Center (CC)": (150, 272),
    "Clayes Performing Arts Center (CPAC)": (203, 556),
    "College Park (CP)": (357, 719),
    "Computer Science (CS)": (384, 464),
    "Dan Black Hall (DBH)": (245, 631),
    "Eastside Parking Structure (EPS)": (428, 581),
    "Education-Classroom (EC)": (308, 502),
    "Engineering Building (E)": (351, 462),
    "Goodwin Field (GF)": (284, 203),
    "Greenhouse Complex (BGC)": (202, 615),
    "Humanities-Social Sciences (HSS)": (320, 560),
    "Kinesiology & Health (KHS)": (231, 426),
    "Langsdorf Hall (LH)": (308, 646),
    "McCarthy Hall (MH)": (245, 604),
    "Mihaylo Hall (SGMH)": (364, 657),
    "Nutwood Parking Structure (NPS)": (115, 637),
    "Parking & Transportation Services (P)": (81, 283),
    "Pollak Library (PL)": (258, 500),
    "Receiving (R)": (120, 357),
    "Residence Halls (RH)": (426, 281),
    "Ruby Gerontology Center (RGC)": (361, 401),
    "State College Parking Structure (SCPS)": (119, 425),
    "Student Health and Counseling Center (SHCC)": (318, 413),
    "Student Housing (SH)": (406, 393),
    "Student Rec Center (SRC)": (173, 416),
    "Titan House (TH)": (315, 367),
    "Titan Stadium (TS)": (214, 234),
    "Titan Student Union (TSU)": (141, 488),
    "University Hall (UH)": (317, 605),
    "University Police (UP)": (79, 423),
    "Visual Arts (VA)": (130, 539),
}


class CampusNavigatorFrame(tk.Frame):
    """Campus navigator page used by app.py."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._map_photo = None
        self._animation_jobs = []
        self._coord_var = tk.StringVar(value="Click the map to mark a coordinate.")
        self._start_var = tk.StringVar(value=BUILDINGS[0] if BUILDINGS else "")
        self._end_var = tk.StringVar(value=BUILDINGS[1] if len(BUILDINGS) > 1 else "")

        self._build()
        self._load_map()
        self._draw_initial_buildings()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.columnconfigure(0, weight=0, minsize=CANVAS_WIDTH + 20)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_map(body)
        self._build_side_panel(body)

    def _build_map(self, parent):
        map_panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER, highlightthickness=1)
        map_panel.grid(row=0, column=0, sticky="nw", padx=(0, 10))
        map_panel.rowconfigure(1, weight=0)
        map_panel.rowconfigure(2, weight=0)
        map_panel.columnconfigure(0, weight=0)

        tk.Label(
            map_panel,
            text="Map Canvas",
            fg=TEXT,
            bg=PANEL_BG,
            font=("Courier New", 12, "bold"),
            anchor="w",
            padx=10,
            pady=8,
        ).grid(row=0, column=0, sticky="ew")

        self.canvas = tk.Canvas(
            map_panel,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#f8fafc",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=1, column=0, sticky="nw", padx=8, pady=(0, 6))
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        tk.Label(
            map_panel,
            textvariable=self._coord_var,
            fg=TEXT_MUTED,
            bg=PANEL_BG,
            font=("Courier New", 10),
            anchor="w",
            padx=10,
            pady=5,
        ).grid(row=2, column=0, sticky="ew")

    def _build_side_panel(self, parent):
        side = tk.Frame(parent, bg=BG_DARK)
        side.grid(row=0, column=1, sticky="nsew")
        side.rowconfigure(2, weight=1)
        side.columnconfigure(0, weight=1)

        self._build_controls(side)
        self._build_hint(side)
        self._build_results(side)

    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER, highlightthickness=1)
        ctrl.grid(row=0, column=0, sticky="new")
        ctrl.columnconfigure(1, weight=1)

        tk.Label(
            ctrl,
            text="Control Panel",
            fg=TEXT,
            bg=PANEL_BG,
            font=("Courier New", 12, "bold"),
            anchor="w",
            padx=10,
            pady=8,
        ).grid(row=0, column=0, columnspan=2, sticky="ew")

        tk.Label(
            ctrl,
            text="Start Node:",
            font=("Courier New", 10),
            fg=TEXT_MUTED,
            bg=PANEL_BG,
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=(8, 4))
        self._dropdown(ctrl, self._start_var).grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(8, 4))

        tk.Label(
            ctrl,
            text="Destination Node:",
            font=("Courier New", 10),
            fg=TEXT_MUTED,
            bg=PANEL_BG,
        ).grid(row=2, column=0, sticky="w", padx=(12, 8), pady=4)
        self._dropdown(ctrl, self._end_var).grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=4)

        buttons = [
            ("Run Dijkstra's", self._run_dijkstra),
            ("Run BFS", self._run_bfs),
            ("Run DFS", self._run_dfs),
            ("Run Prim's MST", self._run_prims),
            ("Reset Graph", self._reset),
            ("Clear Coordinate Marks", self._clear_coordinate_marks),
        ]
        for row, (label, command) in enumerate(buttons, start=3):
            tk.Button(
                ctrl,
                text=label,
                command=command,
                fg=TEXT,
                bg="#6D28D9",
                activeforeground=TEXT,
                activebackground="#2563EB",
                relief="flat",
                font=("Courier New", 10, "bold"),
                cursor="hand2",
                padx=10,
                pady=7,
            ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=18, pady=4)

    def _build_hint(self, parent):
        hint = tk.Frame(parent, bg="#15104A", highlightbackground=BORDER, highlightthickness=1)
        hint.grid(row=1, column=0, sticky="ew", pady=10)
        tk.Label(
            hint,
            text="Click the map to mark coordinates. Run an algorithm to animate routes.",
            font=("Courier New", 9),
            fg=TEXT_MUTED,
            bg="#15104A",
            justify="left",
            wraplength=390,
            padx=10,
            pady=8,
        ).pack(fill="x")

    def _build_results(self, parent):
        results = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER, highlightthickness=1)
        results.grid(row=2, column=0, sticky="nsew")
        results.rowconfigure(1, weight=0)
        results.rowconfigure(2, weight=1)
        results.columnconfigure(0, weight=1)

        tk.Label(
            results,
            text="Results",
            fg=TEXT,
            bg=PANEL_BG,
            font=("Courier New", 12, "bold"),
            anchor="w",
            padx=10,
            pady=8,
        ).grid(row=0, column=0, sticky="ew")

        columns = ("from", "to", "metric", "status")
        style = ttk.Style()
        style.configure("Navigator.Treeview", rowheight=34, font=("Courier New", 12))
        style.configure("Navigator.Treeview.Heading", font=("Courier New", 11, "bold"))

        self._results = ttk.Treeview(
            results,
            columns=columns,
            show="headings",
            height=4,
            style="Navigator.Treeview",
        )
        for col, title, width in (
            ("from", "From", 180),
            ("to", "To", 180),
            ("metric", "Distance/Cost", 180),
            ("status", "Time/Status", 150),
        ):
            self._results.heading(col, text=title)
            self._results.column(col, width=width, anchor="w", stretch=True)
        self._results.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        details_frame = tk.Frame(results, bg=PANEL_BG)
        details_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)

        self._details = tk.Text(
            details_frame,
            height=12,
            bg="#F8FAFC",
            fg="#0F172A",
            font=("Courier New", 12),
            wrap="word",
            relief="flat",
            bd=6,
            state="disabled",
        )
        details_scroll = tk.Scrollbar(details_frame, command=self._details.yview)
        self._details.configure(yscrollcommand=details_scroll.set)
        self._details.grid(row=0, column=0, sticky="nsew")
        details_scroll.grid(row=0, column=1, sticky="ns")

    def _dropdown(self, parent, variable):
        return ttk.Combobox(
            parent,
            textvariable=variable,
            values=BUILDINGS,
            state="readonly",
            font=("Courier New", 10),
        )

    def _load_map(self):
        self.canvas.delete("all")

        if not CAMPUS_MAP.exists():
            self._draw_fallback_map()
            return

        try:
            from PIL import Image, ImageTk

            image = Image.open(CAMPUS_MAP)
            image.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
            self._map_photo = ImageTk.PhotoImage(image)
            self.canvas.configure(width=self._map_photo.width(), height=self._map_photo.height())
            self.canvas.create_image(0, 0, image=self._map_photo, anchor="nw", tags="map_image")
            return
        except Exception:
            pass

        try:
            self._map_photo = tk.PhotoImage(file=str(CAMPUS_MAP)).subsample(4, 4)
            self.canvas.configure(width=self._map_photo.width(), height=self._map_photo.height())
            self.canvas.create_image(0, 0, image=self._map_photo, anchor="nw", tags="map_image")
            return
        except Exception:
            self._draw_fallback_map()

    def _draw_fallback_map(self):
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#f8fafc", outline="#111827")
        self.canvas.create_text(
            CANVAS_WIDTH // 2,
            24,
            text="Campus map image could not be loaded",
            fill="#111827",
            font=("Courier New", 12, "bold"),
        )

    def _get_coord(self, building_name):
        return BUILDING_COORDS.get(building_name)

    def _on_canvas_click(self, event):
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        coord_text = f"Clicked coordinate: ({x}, {y})"
        self._coord_var.set(coord_text)
        print(coord_text)

        self.canvas.create_oval(
            x - 5,
            y - 5,
            x + 5,
            y + 5,
            fill=DISCOVERY_DOT_COLOR,
            outline="#111827",
            width=2,
            tags=("coord_mark",),
        )
        self.canvas.create_text(
            x + 8,
            y - 8,
            text=f"({x}, {y})",
            fill="#111827",
            font=("Courier New", 8, "bold"),
            anchor="w",
            tags=("coord_mark",),
        )
        self.canvas.tag_raise("coord_mark")

    def _clear_coordinate_marks(self):
        self.canvas.delete("coord_mark")
        self._coord_var.set("Click the map to mark a coordinate.")

    def _short_name(self, building_name):
        if "(" in building_name and ")" in building_name:
            return building_name.split("(")[-1].split(")")[0]
        return building_name

    def _record_result(self, label, metric="", status="", details=""):
        start, end = self._start_var.get(), self._end_var.get()
        self._results.delete(*self._results.get_children())
        self._results.insert(
            "",
            "end",
            values=(self._short_name(start), self._short_name(end or label), metric, status),
        )
        self._write_details(details)

    def _write_details(self, text):
        self._details.configure(state="normal")
        self._details.delete("1.0", "end")
        self._details.insert("end", text)
        self._details.configure(state="disabled")

    def _format_distance(self, distance):
        if distance is None or distance == math.inf:
            return "No Path"
        return f"{distance} units"

    def _format_time(self, minutes):
        if minutes is None or minutes == math.inf:
            return "Failed"
        return f"{minutes} min"

    def _draw_initial_buildings(self):
        self.canvas.delete("initial_building")
        for building, coord in BUILDING_COORDS.items():
            x, y = coord
            self.canvas.create_oval(
                x - 6,
                y - 6,
                x + 6,
                y + 6,
                fill=INITIAL_BUILDING_COLOR,
                outline="white",
                width=2,
                tags="initial_building",
            )
        self.canvas.tag_raise("initial_building")

    def _reset_path_visuals(self):
        self._cancel_animations()
        self.canvas.delete("path_line", "path_node", "mst_edge", "mst_node", "temp_dot")
        self.canvas.tag_raise("initial_building")

    def _cancel_animations(self):
        for job in self._animation_jobs:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._animation_jobs.clear()

    def _draw_path_elements(self, path, line_color, node_color, path_tag):
        self.canvas.delete(f"{path_tag}_line", f"{path_tag}_node")
        if not path:
            return

        self._animate_path(path, line_color, node_color, path_tag)

    def _animate_path(self, path, line_color, node_color, path_tag, segment_index=0):
        if segment_index == 0:
            self._draw_path_node(path[0], node_color, path_tag)

        if segment_index >= len(path) - 1:
            self.canvas.tag_raise("path_line")
            self.canvas.tag_raise("path_node")
            self.canvas.tag_raise("coord_mark")
            return

        start_node = path[segment_index]
        end_node = path[segment_index + 1]
        coord_start = self._get_coord(start_node)
        coord_end = self._get_coord(end_node)

        if not coord_start or not coord_end:
            job = self.after(
                100,
                lambda: self._animate_path(path, line_color, node_color, path_tag, segment_index + 1),
            )
            self._animation_jobs.append(job)
            return

        x1, y1 = coord_start
        x2, y2 = coord_end
        line_id = self.canvas.create_line(
            x1,
            y1,
            x1,
            y1,
            fill=line_color,
            width=5,
            capstyle="round",
            tags=(path_tag, f"{path_tag}_line", "path_line"),
        )
        self._animate_line_step(
            line_id,
            x1,
            y1,
            x2,
            y2,
            12,
            1,
            lambda: self._finish_path_segment(path, line_color, node_color, path_tag, segment_index),
        )

    def _animate_line_step(self, line_id, x1, y1, x2, y2, steps, step, on_done):
        progress = step / steps
        current_x = x1 + (x2 - x1) * progress
        current_y = y1 + (y2 - y1) * progress
        self.canvas.coords(line_id, x1, y1, current_x, current_y)
        self.canvas.tag_raise("path_line")
        self.canvas.tag_raise("path_node")

        if step >= steps:
            on_done()
            return

        job = self.after(
            18,
            lambda: self._animate_line_step(line_id, x1, y1, x2, y2, steps, step + 1, on_done),
        )
        self._animation_jobs.append(job)

    def _finish_path_segment(self, path, line_color, node_color, path_tag, segment_index):
        self._draw_path_node(path[segment_index + 1], node_color, path_tag)
        job = self.after(
            75,
            lambda: self._animate_path(path, line_color, node_color, path_tag, segment_index + 1),
        )
        self._animation_jobs.append(job)

    def _draw_path_node(self, node, node_color, path_tag):
        coord = self._get_coord(node)
        if not coord:
            return

        x, y = coord
        self.canvas.create_oval(
            x - 8,
            y - 8,
            x + 8,
            y + 8,
            fill=node_color,
            outline="white",
            width=2,
            tags=(path_tag, f"{path_tag}_node", "path_node"),
        )
        self.canvas.tag_raise("path_node")

    def _run_dijkstra(self):
        self._reset_path_visuals()
        start, end = self._start_var.get(), self._end_var.get()
        if start == end:
            return self._record_result("Dijkstra", "Start=End", "-", "Dijkstra path:\nStart and end are the same.")

        dist, time, path = dijkstra(CAMPUS_GRAPH, start, end)
        if path:
            details = (
                "Dijkstra shortest path by distance:\n"
                + " -> ".join(path)
                + f"\n\nTotal distance: {self._format_distance(dist)}"
                + f"\nTotal time: {self._format_time(time)}"
            )
            self._record_result("Dijkstra", self._format_distance(dist), self._format_time(time), details)
            self._draw_path_elements(path, PATH_LINE_COLOR, PATH_NODE_COLOR, "Dijkstra")
        else:
            self._record_result("Dijkstra", "No Path", "Failed", "Dijkstra could not find a path.")

    def _run_bfs(self):
        self._reset_path_visuals()
        start, end = self._start_var.get(), self._end_var.get()
        if start == end:
            return self._record_result("BFS", "Start=End", "-", "BFS path:\nStart and end are the same.")

        hops, dist, time, path = bfs(CAMPUS_GRAPH, start, end)
        if path:
            details = (
                "BFS path with fewest hops:\n"
                + " -> ".join(path)
                + f"\n\nHops: {hops}"
                + f"\nTotal distance: {self._format_distance(dist)}"
                + f"\nTotal time: {self._format_time(time)}"
            )
            self._record_result("BFS", f"Hops: {hops} ({dist} units)", self._format_time(time), details)
            self._draw_path_elements(path, PATH_LINE_COLOR, PATH_NODE_COLOR, "BFS")
        else:
            self._record_result("BFS", "No Path", "Failed", "BFS could not find a path.")

    def _run_dfs(self):
        self._reset_path_visuals()
        visited_order, is_connected, status_str = dfs(CAMPUS_GRAPH, self._start_var.get())
        numbered_order = "\n".join(
            f"{index}. {node}" for index, node in enumerate(visited_order, start=1)
        )
        details = f"DFS traversal order:\n{numbered_order}\n\nConnectivity: {status_str}"
        self._record_result("DFS", f"{len(visited_order)} nodes", status_str, details)
        self._draw_path_elements(visited_order, DFS_LINE_COLOR, DFS_PATH_COLOR, "DFS")

    def _run_prims(self):
        self._reset_path_visuals()
        mst_edges, total_dist, total_time = prims_mst(CAMPUS_GRAPH)
        edge_lines = "\n".join(
            f"{index}. {u} -> {v} ({weight} units)"
            for index, (u, v, weight) in enumerate(mst_edges, start=1)
        )
        details = (
            "Prim's MST edges:\n"
            + edge_lines
            + f"\n\nTotal MST distance: {self._format_distance(total_dist)}"
            + f"\nTotal MST time: {self._format_time(total_time)}"
        )
        self._animate_mst_edges(mst_edges)
        self._record_result("Prim's MST", self._format_distance(total_dist), self._format_time(total_time), details)

    def _animate_mst_edges(self, mst_edges, edge_index=0):
        if edge_index >= len(mst_edges):
            self.canvas.tag_raise("path_line")
            self.canvas.tag_raise("path_node")
            self.canvas.tag_raise("coord_mark")
            return

        u, v, weight = mst_edges[edge_index]
        coord_u = self._get_coord(u)
        coord_v = self._get_coord(v)

        if coord_u and coord_v:
            x1, y1 = coord_u
            x2, y2 = coord_v
            line_id = self.canvas.create_line(
                x1,
                y1,
                x1,
                y1,
                fill=PRIM_LINE_COLOR,
                width=4,
                dash=(4, 2),
                tags=("mst_visual", "mst_edge", "path_line"),
            )
            self._draw_mst_node(u)
            self._animate_line_step(
                line_id,
                x1,
                y1,
                x2,
                y2,
                12,
                1,
                lambda: self._finish_mst_edge(v, mst_edges, edge_index),
            )
        else:
            job = self.after(75, lambda: self._animate_mst_edges(mst_edges, edge_index + 1))
            self._animation_jobs.append(job)

    def _finish_mst_edge(self, node, mst_edges, edge_index):
        self._draw_mst_node(node)
        job = self.after(75, lambda: self._animate_mst_edges(mst_edges, edge_index + 1))
        self._animation_jobs.append(job)

    def _draw_mst_node(self, node):
        coord = self._get_coord(node)
        if not coord:
            return

        x, y = coord
        self.canvas.create_oval(
            x - 5,
            y - 5,
            x + 5,
            y + 5,
            fill=PRIM_PATH_COLOR,
            outline="white",
            width=2,
            tags=("mst_visual", "mst_node", "path_node"),
        )
        self.canvas.tag_raise("path_node")

    def _reset(self):
        self._results.delete(*self._results.get_children())
        self._write_details("")
        self._reset_path_visuals()
