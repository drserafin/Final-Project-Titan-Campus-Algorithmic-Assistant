"""
ui/algorithm_info.py — Algorithm Info / About module UI.

Shows Big-O complexity table for all implemented algorithms
and a P vs NP reflection section.  No algorithm calls needed here.
"""

import tkinter as tk
from ui.theme import (COLORS, FONT_BODY, FONT_SUBHEAD, FONT_MONO, FONT_SMALL,
                      section_header, card)


# Full complexity reference
COMPLEXITY_TABLE = [
    # (Algorithm,            Time Complexity,      Space,      Class,      Module)
    ("BFS",                  "O(V + E)",           "O(V)",     "P",        "Navigator"),
    ("DFS",                  "O(V + E)",           "O(V)",     "P",        "Navigator"),
    ("Dijkstra",             "O((V+E) log V)",     "O(V)",     "P",        "Navigator"),
    ("Prim's MST",           "O((V+E) log V)",     "O(V)",     "P",        "Navigator"),
    ("Greedy Scheduler",     "O(n log n)",         "O(n)",     "P",        "Planner"),
    ("0/1 Knapsack DP",      "O(n · W)",           "O(n · W)", "NP-Hard",  "Planner"),
    ("Naive Search",         "O(n · m)",           "O(1)",     "P",        "Search"),
    ("Rabin–Karp",           "O(n + m) avg",       "O(1)",     "P",        "Search"),
    ("KMP",                  "O(n + m)",           "O(m)",     "P",        "Search"),
]

PNP_TEXT = """\
P  (Polynomial time)
  Problems that can be SOLVED efficiently by a deterministic algorithm.
  Every algorithm in this project except 0/1 Knapsack lives here.
  Examples: BFS, Dijkstra, KMP.

NP  (Non-deterministic Polynomial time)
  Problems whose solutions can be VERIFIED in polynomial time,
  but no known efficient algorithm exists to FIND them.
  The 0/1 Knapsack is NP-Hard in its general unbounded form.

NP-Hard
  At least as difficult as the hardest NP problems.
  Our DP Knapsack runs in pseudo-polynomial time O(n·W) — efficient
  enough when W (capacity) is small, but not truly polynomial.

The Open Question — P = NP?
  If P = NP, every problem whose solution can be checked quickly
  could also be solved quickly.  This would break most modern
  cryptography and revolutionize computing.  As of 2025, unsolved."""


class AlgorithmInfoFrame(tk.Frame):
    """Module 4 — Complexity table + P vs NP reflection"""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self._build()

    def _build(self):
        section_header(self,
                        "⚙  Algorithm Info",
                        "Big-O complexity reference · P vs NP discussion")

        # Scrollable canvas for the whole content
        canvas = tk.Canvas(self, bg=COLORS["bg_dark"],
                           highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
        win_id = canvas.create_window((0, 0), window=inner,
                                      anchor="nw", width=0)

        def _on_resize(e):
            canvas.itemconfigure(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))

        self._build_table(inner)
        self._build_pnp(inner)
        self._build_legend(inner)

    # ── Big-O table ──────────────────────────────────────────────────────────

    def _build_table(self, parent):
        tcard = tk.Frame(parent, bg=COLORS["bg_panel"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        tcard.pack(fill="x", pady=(0, 16))

        tk.Label(tcard, text="Complexity Reference Table",
                 font=FONT_SUBHEAD, fg=COLORS["accent"],
                 bg=COLORS["bg_panel"], anchor="w",
                 padx=12, pady=8).pack(fill="x")
        tk.Frame(tcard, bg=COLORS["border"], height=1).pack(fill="x")

        headers = ["Algorithm", "Time Complexity", "Space", "Class", "Module"]
        widths   = [22, 22, 12, 10, 12]

        # Header row
        hrow = tk.Frame(tcard, bg=COLORS["accent_dim"])
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            tk.Label(hrow, text=h, font=FONT_SUBHEAD,
                     fg=COLORS["accent"], bg=COLORS["accent_dim"],
                     width=w, anchor="w", padx=8, pady=5).pack(side="left")

        # Data rows
        for idx, row in enumerate(COMPLEXITY_TABLE):
            bg = COLORS["bg_panel"] if idx % 2 == 0 else COLORS["bg_hover"]
            r  = tk.Frame(tcard, bg=bg)
            r.pack(fill="x")
            for i, (cell, w) in enumerate(zip(row, widths)):
                color = COLORS["error"]   if cell == "NP-Hard" \
                   else COLORS["success"] if cell == "P" \
                   else COLORS["text_primary"]
                tk.Label(r, text=cell, font=FONT_MONO,
                         fg=color, bg=bg,
                         width=w, anchor="w",
                         padx=8, pady=4).pack(side="left")

    # ── P vs NP ──────────────────────────────────────────────────────────────

    def _build_pnp(self, parent):
        pcard = tk.Frame(parent, bg=COLORS["bg_panel"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        pcard.pack(fill="x", pady=(0, 16))

        tk.Label(pcard, text="P vs NP — Reflection",
                 font=FONT_SUBHEAD, fg=COLORS["accent"],
                 bg=COLORS["bg_panel"], anchor="w",
                 padx=12, pady=8).pack(fill="x")
        tk.Frame(pcard, bg=COLORS["border"], height=1).pack(fill="x")

        tk.Label(pcard, text=PNP_TEXT, font=FONT_BODY,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 justify="left", anchor="nw",
                 padx=16, pady=12, wraplength=900).pack(fill="x")

    # ── Legend ───────────────────────────────────────────────────────────────

    def _build_legend(self, parent):
        lcard = tk.Frame(parent, bg=COLORS["bg_panel"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        lcard.pack(fill="x", pady=(0, 16))

        tk.Label(lcard, text="Variables",
                 font=FONT_SUBHEAD, fg=COLORS["accent"],
                 bg=COLORS["bg_panel"], anchor="w",
                 padx=12, pady=8).pack(fill="x")
        tk.Frame(lcard, bg=COLORS["border"], height=1).pack(fill="x")

        legend_text = (
            "V = number of vertices (buildings)   "
            "E = number of edges (paths)   "
            "n = input size   "
            "m = pattern length   "
            "W = knapsack capacity"
        )
        tk.Label(lcard, text=legend_text, font=FONT_SMALL,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12, pady=8).pack(fill="x")
