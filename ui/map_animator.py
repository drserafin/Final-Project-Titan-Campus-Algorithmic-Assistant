"""
ui/map_animator.py - Canvas animation engine for the campus navigator.

Single responsibility: draw and animate paths, nodes, and MST edges on a
tkinter Canvas. Knows nothing about UI layout, algorithm logic, or data.

Public API
----------
    animator.draw_path(path, line_color, node_color, tag)
    animator.draw_mst(mst_edges, line_color, node_color)
    animator.reset()
    animator.set_coord_fn(fn)   -- inject coordinate resolver
    animator.set_graph_hooks(highlight_edge_fn, highlight_node_fn, reset_fn)
"""

import tkinter as tk


# ── Animation tuning ──────────────────────────────────────────────────────────
_LINE_STEPS      = 14    # substeps per line segment
_LINE_STEP_MS    = 16    # ms between substeps  (~60 fps)
_PULSE_FRAMES    = 8     # frames for the expanding ring
_PULSE_FRAME_MS  = 40    # ms between pulse frames
_HOP_PAUSE_MS    = 60    # pause between arriving at a node and moving to next


def _ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


class MapAnimator:
    """
    Drives all canvas visuals for the campus navigator.

    Parameters
    ----------
    canvas : tk.Canvas
        The canvas to draw on.
    after_fn : callable
        Pass ``widget.after`` so the animator can schedule callbacks without
        holding a reference to the full widget.
    after_cancel_fn : callable
        Pass ``widget.after_cancel``.
    """

    def __init__(self, canvas: tk.Canvas, after_fn, after_cancel_fn):
        self._canvas          = canvas
        self._after           = after_fn
        self._after_cancel    = after_cancel_fn
        self._jobs: list[str] = []

        # Injected from the outside — keeps this class data-agnostic
        self._coord_fn = lambda name: None           # building name -> (x, y) | None
        self._highlight_edge_fn  = lambda u, v, c: None
        self._highlight_node_fn  = lambda n, c: None
        self._reset_graph_colors = lambda: None

    # ── Dependency injection ──────────────────────────────────────────────────

    def set_coord_fn(self, fn):
        """Supply a callable that maps a building name to (x, y) on the canvas."""
        self._coord_fn = fn

    def set_graph_hooks(self, highlight_edge_fn, highlight_node_fn, reset_fn):
        """
        Optional hooks called when the Graph View is active.
        If Map View is active the hooks are no-ops — just don't set them.
        """
        self._highlight_edge_fn  = highlight_edge_fn
        self._highlight_node_fn  = highlight_node_fn
        self._reset_graph_colors = reset_fn

    # ── Public draw methods ───────────────────────────────────────────────────

    def draw_path(self, path: list[str], line_color: str, node_color: str, tag: str):
        """Animate a sequence of nodes as a travelling path."""
        self._canvas.delete(f"{tag}_line", f"{tag}_node")
        if not path:
            return
        self._animate_path(path, line_color, node_color, tag, segment_index=0)

    def draw_mst(self, mst_edges: list[tuple], line_color: str, node_color: str):
        """Animate a list of MST edges (u, v, weight) one at a time."""
        self._animate_mst_edges(mst_edges, line_color, node_color, edge_index=0)

    def reset(self):
        """Cancel all running animations and delete all path/node canvas items."""
        self._cancel_all()
        self._canvas.delete(
            "path_line", "path_node",
            "mst_edge",  "mst_node",
            "temp_dot",
        )
        self._reset_graph_colors()

    # ── Internal: path animation ──────────────────────────────────────────────

    def _animate_path(self, path, line_color, node_color, tag, segment_index):
        if segment_index == 0:
            self._pulse_node(path[0], node_color, tag)

        if segment_index >= len(path) - 1:
            self._raise_path_layers()
            return

        u = path[segment_index]
        v = path[segment_index + 1]
        cu = self._coord_fn(u)
        cv = self._coord_fn(v)

        if not cu or not cv:
            job = self._after(
                100,
                lambda: self._animate_path(path, line_color, node_color, tag, segment_index + 1),
            )
            self._jobs.append(job)
            return

        x1, y1 = cu
        x2, y2 = cv

        self._highlight_edge_fn(u, v, line_color)

        line_id = self._canvas.create_line(
            x1, y1, x1, y1,
            fill=line_color, width=5, capstyle="round",
            tags=(tag, f"{tag}_line", "path_line"),
        )
        self._animate_line(
            line_id, x1, y1, x2, y2, _LINE_STEPS, 1,
            on_done=lambda: self._finish_segment(path, line_color, node_color, tag, segment_index),
        )

    def _finish_segment(self, path, line_color, node_color, tag, segment_index):
        next_node = path[segment_index + 1]
        self._highlight_edge_fn(path[segment_index], next_node, line_color)

        def _continue():
            job = self._after(
                _HOP_PAUSE_MS,
                lambda: self._animate_path(path, line_color, node_color, tag, segment_index + 1),
            )
            self._jobs.append(job)

        self._pulse_node(next_node, node_color, tag, on_done=_continue)

    # ── Internal: MST animation ───────────────────────────────────────────────

    def _animate_mst_edges(self, mst_edges, line_color, node_color, edge_index):
        if edge_index >= len(mst_edges):
            self._raise_path_layers()
            return

        u, v, _weight = mst_edges[edge_index]
        cu = self._coord_fn(u)
        cv = self._coord_fn(v)

        if not cu or not cv:
            job = self._after(
                75,
                lambda: self._animate_mst_edges(mst_edges, line_color, node_color, edge_index + 1),
            )
            self._jobs.append(job)
            return

        x1, y1 = cu
        x2, y2 = cv

        self._highlight_edge_fn(u, v, line_color)
        self._highlight_node_fn(u, node_color)
        self._draw_mst_dot(u, node_color)

        line_id = self._canvas.create_line(
            x1, y1, x1, y1,
            fill=line_color, width=4, dash=(4, 2),
            tags=("mst_visual", "mst_edge", "path_line"),
        )

        def _on_edge_done():
            self._highlight_node_fn(v, node_color)
            self._draw_mst_dot(v, node_color)
            job = self._after(
                75,
                lambda: self._animate_mst_edges(mst_edges, line_color, node_color, edge_index + 1),
            )
            self._jobs.append(job)

        self._animate_line(line_id, x1, y1, x2, y2, _LINE_STEPS, 1, on_done=_on_edge_done)

    def _draw_mst_dot(self, node, color):
        coord = self._coord_fn(node)
        if not coord:
            return
        x, y = coord
        self._canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill=color, outline="white", width=2,
            tags=("mst_visual", "mst_node", "path_node"),
        )
        self._canvas.tag_raise("path_node")

    # ── Internal: primitives ──────────────────────────────────────────────────

    def _animate_line(self, line_id, x1, y1, x2, y2, steps, step, on_done):
        t = _ease_out_cubic(step / steps)
        self._canvas.coords(line_id, x1, y1, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        self._canvas.tag_raise("path_line")
        self._canvas.tag_raise("path_node")

        if step >= steps:
            on_done()
            return

        job = self._after(
            _LINE_STEP_MS,
            lambda: self._animate_line(line_id, x1, y1, x2, y2, steps, step + 1, on_done),
        )
        self._jobs.append(job)

    def _pulse_node(self, node: str, color: str, tag: str, frame: int = 0, on_done=None):
        coord = self._coord_fn(node)
        if not coord:
            if on_done:
                on_done()
            return

        x, y = coord
        self._highlight_node_fn(node, color)

        # Draw the permanent filled dot on frame 0
        if frame == 0:
            self._canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                fill=color, outline="white", width=2,
                tags=(tag, f"{tag}_node", "path_node"),
            )

        # Expanding ring that fades by shrinking its width
        ring_r    = 8 + _ease_out_cubic(frame / _PULSE_FRAMES) * 14
        ring_w    = max(1, int(3 * (1 - frame / _PULSE_FRAMES)))
        ring_id   = self._canvas.create_oval(
            x - ring_r, y - ring_r, x + ring_r, y + ring_r,
            outline=color, width=ring_w,
            tags=(tag, "path_node", "pulse_ring"),
        )
        self._canvas.tag_raise("path_node")

        def _delete_ring(rid=ring_id):
            try:
                self._canvas.delete(rid)
            except Exception:
                pass

        if frame < _PULSE_FRAMES - 1:
            job = self._after(
                _PULSE_FRAME_MS,
                lambda: self._pulse_node(node, color, tag, frame + 1, on_done),
            )
            self._jobs.append(job)
            cleanup = self._after(_PULSE_FRAME_MS * (_PULSE_FRAMES - frame) + 80, _delete_ring)
            self._jobs.append(cleanup)
        else:
            _delete_ring()
            if on_done:
                on_done()

    def _raise_path_layers(self):
        self._canvas.tag_raise("path_line")
        self._canvas.tag_raise("path_node")
        self._canvas.tag_raise("coord_mark")

    def _cancel_all(self):
        for job in self._jobs:
            try:
                self._after_cancel(job)
            except tk.TclError:
                pass
        self._jobs.clear()
