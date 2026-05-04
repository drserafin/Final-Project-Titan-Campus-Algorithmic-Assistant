"""
ui/graph_view.py - Graph View canvas renderer.

Single responsibility: draw the abstract graph (nodes, edges, weight labels)
on a dark canvas and expose highlight hooks for the animator to call.

Public API
----------
    gv = GraphView(canvas)
    gv.render(buildings, campus_graph)   -- draw everything from scratch
    gv.reset_colors()                    -- restore default node/edge colors
    gv.highlight_edge(u, v, color)
    gv.highlight_node(node, color)
    gv.get_coord(building_name) -> (x, y) | None
"""

from algorithms.graph import BUILDING_COORDS, SHORT_LABELS

# ── Visual constants ──────────────────────────────────────────────────────────
GRAPH_BG           = "#0d1117"
GRAPH_NODE_FILL    = "#1e40af"
GRAPH_NODE_OUTLINE = "#3b82f6"
GRAPH_EDGE_COLOR   = "#334155"
GRAPH_WEIGHT_COLOR = "#64748b"
GRAPH_LABEL_COLOR  = "#94a3b8"
_NODE_RADIUS       = 9
_GRID_STEP         = 40


class GraphView:
    """
    Renders and manages the abstract graph canvas.

    Parameters
    ----------
    canvas : tk.Canvas
        The canvas to draw on (already created by the layout layer).
    canvas_width, canvas_height : int
        Dimensions of that canvas.
    margin : int
        Padding kept clear around the edges.
    """

    def __init__(self, canvas, canvas_width: int, canvas_height: int, margin: int = 55):
        self._canvas = canvas
        self._W      = canvas_width
        self._H      = canvas_height
        self._margin = margin

        # building name -> canvas item id
        self._node_items:   dict[str, int] = {}
        self._edge_items:   dict[tuple, int] = {}   # keyed (u, v) AND (v, u)
        self._label_items:  dict[str, int] = {}
        self._weight_items: dict[tuple, int] = {}

        # Normalised pixel positions for this canvas
        self._positions: dict[str, tuple[float, float]] = {}

    # ── Public ────────────────────────────────────────────────────────────────

    def render(self, buildings: list[str], campus_graph: dict):
        """Clear the canvas and draw the full graph."""
        self._canvas.configure(bg=GRAPH_BG)
        self._canvas.delete("all")
        self._node_items.clear()
        self._edge_items.clear()
        self._label_items.clear()
        self._weight_items.clear()
        self._positions.clear()

        self._compute_positions(buildings)
        self._draw_grid()
        self._draw_edges(campus_graph)
        self._draw_nodes(buildings)

    def reset_colors(self):
        """Restore all nodes and edges to their default (unvisited) colors."""
        for line_id in set(self._edge_items.values()):
            self._canvas.itemconfigure(line_id, fill=GRAPH_EDGE_COLOR, width=1.5)
        for oval_id in self._node_items.values():
            self._canvas.itemconfigure(
                oval_id, fill=GRAPH_NODE_FILL, outline=GRAPH_NODE_OUTLINE, width=2,
            )

    def highlight_edge(self, u: str, v: str, color: str):
        line_id = self._edge_items.get((u, v))
        if line_id:
            self._canvas.itemconfigure(line_id, fill=color, width=3)

    def highlight_node(self, node: str, color: str):
        oval_id = self._node_items.get(node)
        if oval_id:
            self._canvas.itemconfigure(oval_id, fill=color, outline="white", width=2)

    def get_coord(self, building: str) -> tuple[float, float] | None:
        return self._positions.get(building)

    # ── Private ───────────────────────────────────────────────────────────────

    def _compute_positions(self, buildings: list[str]):
        """Normalise BUILDING_COORDS map pixels to fit this canvas."""
        coords = {b: BUILDING_COORDS[b] for b in buildings if b in BUILDING_COORDS}
        if not coords:
            return

        xs = [c[0] for c in coords.values()]
        ys = [c[1] for c in coords.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        usable_w = self._W - 2 * self._margin
        usable_h = self._H - 2 * self._margin

        for b in buildings:
            if b in BUILDING_COORDS:
                ox, oy = BUILDING_COORDS[b]
                self._positions[b] = (
                    self._margin + (ox - min_x) / span_x * usable_w,
                    self._margin + (oy - min_y) / span_y * usable_h,
                )
            else:
                self._positions[b] = (self._W / 2, self._H / 2)

    def _draw_grid(self):
        for i in range(0, self._W, _GRID_STEP):
            self._canvas.create_line(i, 0, i, self._H, fill="#161d2b", width=1)
        for j in range(0, self._H, _GRID_STEP):
            self._canvas.create_line(0, j, self._W, j, fill="#161d2b", width=1)

    def _draw_edges(self, campus_graph: dict):
        drawn: set[tuple] = set()
        for node, neighbors in campus_graph.items():
            pos_u = self._positions.get(node)
            if not pos_u:
                continue
            for neighbor, attrs in neighbors.items():
                key = tuple(sorted((node, neighbor)))
                if key in drawn:
                    continue
                drawn.add(key)
                pos_v = self._positions.get(neighbor)
                if not pos_v:
                    continue

                x1, y1 = pos_u
                x2, y2 = pos_v
                line_id = self._canvas.create_line(
                    x1, y1, x2, y2,
                    fill=GRAPH_EDGE_COLOR, width=1.5,
                    tags=("graph_edge",),
                )
                self._edge_items[(node, neighbor)] = line_id
                self._edge_items[(neighbor, node)] = line_id

                # Weight label at midpoint
                wt_id = self._canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(attrs["distance"]),
                    fill=GRAPH_WEIGHT_COLOR,
                    font=("Courier New", 7),
                    tags=("graph_weight",),
                )
                self._weight_items[(node, neighbor)] = wt_id
                self._weight_items[(neighbor, node)] = wt_id

    def _draw_nodes(self, buildings: list[str]):
        r = _NODE_RADIUS
        for building in buildings:
            pos = self._positions.get(building)
            if not pos:
                continue
            x, y = pos
            oval_id = self._canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=GRAPH_NODE_FILL, outline=GRAPH_NODE_OUTLINE, width=2,
                tags=("graph_node",),
            )
            self._node_items[building] = oval_id

            label = SHORT_LABELS.get(building, building[:4])
            self._canvas.create_text(
                x, y + r + 8, text=label,
                fill=GRAPH_LABEL_COLOR,
                font=("Courier New", 7, "bold"),
                tags=("graph_label",),
            )
