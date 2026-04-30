"""
algorithms/graph.py — Graph algorithm implementations.

All functions operate on a plain adjacency list (dict of lists/dicts).
Zero GUI / tkinter imports — pure Python only.

Graph format expected:
  Unweighted: { "NodeA": ["NodeB", "NodeC"], ... }
  Weighted:   { "NodeA": {"NodeB": 5, "NodeC": 2}, ... }
"""

import heapq
from collections import deque


# ── Graph definition ─────────────────────────────────────────────────────────
# Real CSUF campus buildings derived from the official campus map.
# Edge weights = approximate walking time in minutes between buildings.
# Graph is undirected — edges are mirrored in both directions.

CAMPUS_GRAPH: dict[str, dict[str, int]] = {
    # Core academic spine
    "Pollak Library (PL)": {
        "Titan Student Union (TSU)": 3,
        "Dan Black Hall (DBH)":      4,
        "Education-Classroom (EC)":  3,
        "Humanities (H)":            4,
        "Commons":                   2,
    },
    "Titan Student Union (TSU)": {
        "Pollak Library (PL)":           3,
        "Bookstore / Titan Shops (B)":   2,
        "Student Rec Center (SRC)":      4,
        "Visual Arts (VA)":              5,
        "Commons":                       3,
    },
    "Dan Black Hall (DBH)": {
        "Pollak Library (PL)":           4,
        "Mihaylo Hall (MH)":             2,
        "Langsdorf Hall (LH)":           3,
        "Education-Classroom (EC)":      4,
    },
    "Engineering (E)": {
        "Computer Science (CS)":         2,
        "Eng & CS Complex (ECS)":        2,
        "Kinesiology & Health (KHS)":    4,
        "Student Health (SHCC)":         3,
    },
    "Computer Science (CS)": {
        "Engineering (E)":               2,
        "Eng & CS Complex (ECS)":        1,
        "Student Health (SHCC)":         3,
    },
    "Eng & CS Complex (ECS)": {
        "Engineering (E)":               2,
        "Computer Science (CS)":         1,
        "Kinesiology & Health (KHS)":    3,
    },
    "Humanities (H)": {
        "Pollak Library (PL)":           4,
        "Quad":                          2,
        "Education-Classroom (EC)":      3,
        "Clayes Performing Arts (CPAC)": 3,
    },
    "Kinesiology & Health (KHS)": {
        "Engineering (E)":               4,
        "Eng & CS Complex (ECS)":        3,
        "Titan Gymnasium (TG)":          2,
        "Student Rec Center (SRC)":      3,
        "Student Health (SHCC)":         2,
    },
    "Student Rec Center (SRC)": {
        "Titan Student Union (TSU)":     4,
        "Kinesiology & Health (KHS)":    3,
        "State College Parking (SCPS)":  2,
        "Titan Gymnasium (TG)":          2,
    },
    "Titan Gymnasium (TG)": {
        "Student Rec Center (SRC)":      2,
        "Kinesiology & Health (KHS)":    2,
        "Titan House (TH)":              3,
    },
    "Langsdorf Hall (LH)": {
        "Dan Black Hall (DBH)":          3,
        "Mihaylo Hall (MH)":             2,
        "Sgmh (SGMH)":                   2,
        "University Hall (UH)":          3,
    },
    "Mihaylo Hall (MH)": {
        "Dan Black Hall (DBH)":          2,
        "Langsdorf Hall (LH)":           2,
        "Sgmh (SGMH)":                   3,
        "Bookstore / Titan Shops (B)":   4,
    },
    "Sgmh (SGMH)": {
        "Langsdorf Hall (LH)":           2,
        "Mihaylo Hall (MH)":             3,
        "University Hall (UH)":          2,
    },
    "University Hall (UH)": {
        "Langsdorf Hall (LH)":           3,
        "Sgmh (SGMH)":                   2,
        "Carl's Jr. (CJ)":               2,
    },
    "Education-Classroom (EC)": {
        "Pollak Library (PL)":           3,
        "Dan Black Hall (DBH)":          4,
        "Humanities (H)":                3,
        "Quad":                          2,
    },
    "Quad": {
        "Humanities (H)":                2,
        "Education-Classroom (EC)":      2,
        "Clayes Performing Arts (CPAC)": 2,
        "Ruby Gerontology (RGC)":        4,
    },
    "Clayes Performing Arts (CPAC)": {
        "Humanities (H)":                3,
        "Quad":                          2,
        "Visual Arts (VA)":              3,
        "Mihaylo Hall (MH)":             4,
    },
    "Visual Arts (VA)": {
        "Titan Student Union (TSU)":     5,
        "Clayes Performing Arts (CPAC)": 3,
        "Bookstore / Titan Shops (B)":   3,
    },
    "Bookstore / Titan Shops (B)": {
        "Titan Student Union (TSU)":     2,
        "Visual Arts (VA)":              3,
        "Mihaylo Hall (MH)":             4,
        "Commons":                       3,
    },
    "Commons": {
        "Pollak Library (PL)":           2,
        "Titan Student Union (TSU)":     3,
        "Bookstore / Titan Shops (B)":   3,
    },
    "Student Health (SHCC)": {
        "Engineering (E)":               3,
        "Computer Science (CS)":         3,
        "Kinesiology & Health (KHS)":    2,
        "Ruby Gerontology (RGC)":        3,
    },
    "Ruby Gerontology (RGC)": {
        "Student Health (SHCC)":         3,
        "Quad":                          4,
        "Titan House (TH)":              4,
    },
    "Titan House (TH)": {
        "Titan Gymnasium (TG)":          3,
        "Ruby Gerontology (RGC)":        4,
        "Residence Halls (RH)":          3,
    },
    "Residence Halls (RH)": {
        "Titan House (TH)":              3,
        "Student Health (SHCC)":         5,
    },
    "State College Parking (SCPS)": {
        "Student Rec Center (SRC)":      2,
        "University Police (UP)":        2,
    },
    "University Police (UP)": {
        "State College Parking (SCPS)":  2,
        "Student Rec Center (SRC)":      3,
    },
    "Carl's Jr. (CJ)": {
        "University Hall (UH)":          2,
        "Sgmh (SGMH)":                   3,
    },
    "Becker Amphitheater (BA)": {
        "Titan Student Union (TSU)":     3,
        "Visual Arts (VA)":              2,
    },
    "Eastside Parking (EPS)": {
        "Quad":                          4,
        "Clayes Performing Arts (CPAC)": 4,
        "Ruby Gerontology (RGC)":        3,
    },
}

# Flat list of all building names (for dropdowns)
BUILDINGS: list[str] = sorted(CAMPUS_GRAPH.keys())


# ── BFS ──────────────────────────────────────────────────────────────────────

def bfs(graph: dict, start: str, end: str) -> dict:
    """
    Breadth-First Search — finds the path with the fewest hops.

    Returns:
        {
          "path":    list[str] | None,
          "hops":    int,
          "visited": list[str],   # BFS visit order
        }

    Time:  O(V + E)
    Space: O(V)
    """
    # TODO: implement BFS
    raise NotImplementedError("BFS not yet implemented — see algorithms/graph.py")


# ── DFS ──────────────────────────────────────────────────────────────────────

def dfs(graph: dict, start: str) -> dict:
    """
    Depth-First Search — full traversal from start node.

    Returns:
        {
          "order":      list[str],   # DFS visit order
          "components": int,         # connected component count
        }

    Time:  O(V + E)
    Space: O(V)
    """
    # TODO: implement DFS
    raise NotImplementedError("DFS not yet implemented — see algorithms/graph.py")


# ── Dijkstra ─────────────────────────────────────────────────────────────────

def dijkstra(graph: dict, start: str, end: str) -> dict:
    """
    Dijkstra's shortest path algorithm (min-heap based).

    Returns:
        {
          "path":      list[str] | None,
          "distance":  int | float,
          "all_dists": dict[str, int|float],
        }

    Time:  O((V + E) log V)
    Space: O(V)
    """
    # TODO: implement Dijkstra using heapq
    raise NotImplementedError("Dijkstra not yet implemented — see algorithms/graph.py")


# ── Prim's MST ───────────────────────────────────────────────────────────────

def prims_mst(graph: dict) -> dict:
    """
    Prim's Minimum Spanning Tree algorithm (min-heap based).

    Returns:
        {
          "edges":       list[tuple[str, str, int]],  # (u, v, weight)
          "total_weight": int,
        }

    Time:  O((V + E) log V)
    Space: O(V)
    """
    # TODO: implement Prim's MST using heapq
    raise NotImplementedError("Prim's MST not yet implemented — see algorithms/graph.py")