"""
algorithms/graph.py - Graph data and algorithm implementations.

Campus graph rules:
- Nodes are CSUF campus map locations.
- Edges are walkable paths between nearby locations.
- distance is a normalized map-based weight, not real-world feet.
  1-3  = very close
  4-7  = medium
  8-12 = far
- time is derived from distance so it stays consistent with the weight.

Also owns all campus spatial data (BUILDING_COORDS, SHORT_LABELS)
so the UI never needs to store map data.

This module has no GUI or tkinter imports.
"""

import heapq
from collections import deque


# ─────────────────────────────────────────
# Campus spatial data
# ─────────────────────────────────────────

# Pixel coordinates on the displayed campus map image.
# Click the map in the app and use the printed coordinates to update these.
BUILDING_COORDS: dict[str, tuple[int, int]] = {
    "Bookstore/Titan Shops (B)":                   (192, 480),
    "Carl's Jr (CJ)":                              (337, 622),
    "Children's Center (CC)":                      (150, 272),
    "Clayes Performing Arts Center (CPAC)":        (203, 556),
    "College Park (CP)":                           (357, 719),
    "Computer Science (CS)":                       (384, 464),
    "Dan Black Hall (DBH)":                        (245, 631),
    "Eastside Parking Structure (EPS)":            (428, 581),
    "Education-Classroom (EC)":                    (308, 502),
    "Engineering Building (E)":                    (351, 462),
    "Goodwin Field (GF)":                          (284, 203),
    "Greenhouse Complex (BGC)":                    (202, 615),
    "Humanities-Social Sciences (HSS)":            (320, 560),
    "Kinesiology & Health (KHS)":                  (231, 426),
    "Langsdorf Hall (LH)":                         (308, 646),
    "McCarthy Hall (MH)":                          (245, 604),
    "Mihaylo Hall (SGMH)":                         (364, 657),
    "Nutwood Parking Structure (NPS)":             (115, 637),
    "Parking & Transportation Services (P)":       (81,  283),
    "Pollak Library (PL)":                         (258, 500),
    "Receiving (R)":                               (120, 357),
    "Residence Halls (RH)":                        (426, 281),
    "Ruby Gerontology Center (RGC)":               (361, 401),
    "State College Parking Structure (SCPS)":      (119, 425),
    "Student Health and Counseling Center (SHCC)": (318, 413),
    "Student Housing (SH)":                        (406, 393),
    "Student Rec Center (SRC)":                    (173, 416),
    "Titan House (TH)":                            (315, 367),
    "Titan Stadium (TS)":                          (214, 234),
    "Titan Student Union (TSU)":                   (141, 488),
    "University Hall (UH)":                        (317, 605),
    "University Police (UP)":                      (79,  423),
    "Visual Arts (VA)":                            (130, 539),
}

# Short abbreviation shown on the Graph View canvas.
SHORT_LABELS: dict[str, str] = {
    name: (name.split("(")[-1].split(")")[0] if "(" in name else name[:4])
    for name in BUILDING_COORDS
}


# ─────────────────────────────────────────
# Graph construction helpers
# ─────────────────────────────────────────

def _time_from_distance(distance: int) -> int:
    """Convert normalized distance units into a simple walking-time estimate."""
    return max(1, (distance + 1) // 2)


def _edge(distance: int, accessible: bool = True) -> dict[str, int | bool]:
    if distance < 1 or distance > 12:
        raise ValueError(f"distance must be between 1 and 12, got {distance}")
    return {
        "distance": distance,
        "time": _time_from_distance(distance),
        "accessible": accessible,
    }


def _add_edge(
    graph: dict[str, dict[str, dict[str, int | bool]]],
    a: str,
    b: str,
    distance: int,
    accessible: bool = True,
):
    """Add an undirected weighted edge."""
    graph[a][b] = _edge(distance, accessible)
    graph[b][a] = _edge(distance, accessible)


# ─────────────────────────────────────────
# Campus graph
# ─────────────────────────────────────────

CAMPUS_GRAPH: dict[str, dict[str, dict[str, int | bool]]] = {
    building: {} for building in BUILDING_COORDS
}

# North / athletic area
_add_edge(CAMPUS_GRAPH, "Goodwin Field (GF)",    "Titan Stadium (TS)",     2)
_add_edge(CAMPUS_GRAPH, "Goodwin Field (GF)",    "Children's Center (CC)", 4)
_add_edge(CAMPUS_GRAPH, "Goodwin Field (GF)",    "Titan House (TH)",       5)
_add_edge(CAMPUS_GRAPH, "Goodwin Field (GF)",    "Residence Halls (RH)",   6)
_add_edge(CAMPUS_GRAPH, "Titan Stadium (TS)",    "Children's Center (CC)", 4)
_add_edge(CAMPUS_GRAPH, "Titan Stadium (TS)",    "Titan House (TH)",       7)
_add_edge(CAMPUS_GRAPH, "Titan House (TH)",      "Residence Halls (RH)",   5)
_add_edge(CAMPUS_GRAPH, "Kinesiology & Health (KHS)", "Titan House (TH)", 4)

# East side / engineering corridor
_add_edge(CAMPUS_GRAPH, "Residence Halls (RH)",                        "Student Housing (SH)",                        4)
_add_edge(CAMPUS_GRAPH, "Residence Halls (RH)",                        "Eastside Parking Structure (EPS)",            6)
_add_edge(CAMPUS_GRAPH, "Student Housing (SH)",                        "Ruby Gerontology Center (RGC)",               2)
_add_edge(CAMPUS_GRAPH, "Student Housing (SH)",                        "Student Health and Counseling Center (SHCC)", 3)
_add_edge(CAMPUS_GRAPH, "Student Housing (SH)",                        "Eastside Parking Structure (EPS)",            5)
_add_edge(CAMPUS_GRAPH, "Ruby Gerontology Center (RGC)",               "Student Health and Counseling Center (SHCC)", 2)
_add_edge(CAMPUS_GRAPH, "Ruby Gerontology Center (RGC)",               "Engineering Building (E)",                    3)
_add_edge(CAMPUS_GRAPH, "Ruby Gerontology Center (RGC)",               "Computer Science (CS)",                       3)
_add_edge(CAMPUS_GRAPH, "Ruby Gerontology Center (RGC)",               "Eastside Parking Structure (EPS)",            4)
_add_edge(CAMPUS_GRAPH, "Student Health and Counseling Center (SHCC)", "Engineering Building (E)",                    3)
_add_edge(CAMPUS_GRAPH, "Student Health and Counseling Center (SHCC)", "Computer Science (CS)",                       4)
_add_edge(CAMPUS_GRAPH, "Student Health and Counseling Center (SHCC)", "Kinesiology & Health (KHS)",                  3)
_add_edge(CAMPUS_GRAPH, "Engineering Building (E)",                    "Computer Science (CS)",                       1)
_add_edge(CAMPUS_GRAPH, "Engineering Building (E)",                    "Education-Classroom (EC)",                    4)
_add_edge(CAMPUS_GRAPH, "Engineering Building (E)",                    "Eastside Parking Structure (EPS)",            5)
_add_edge(CAMPUS_GRAPH, "Computer Science (CS)",                       "Education-Classroom (EC)",                    3)
_add_edge(CAMPUS_GRAPH, "Computer Science (CS)",                       "Eastside Parking Structure (EPS)",            4)

# Central academic core
_add_edge(CAMPUS_GRAPH, "Education-Classroom (EC)",         "Pollak Library (PL)",                    3)
_add_edge(CAMPUS_GRAPH, "Education-Classroom (EC)",         "Humanities-Social Sciences (HSS)",        3)
_add_edge(CAMPUS_GRAPH, "Education-Classroom (EC)",         "University Hall (UH)",                    5)
_add_edge(CAMPUS_GRAPH, "Education-Classroom (EC)",         "Mihaylo Hall (SGMH)",                     7)
_add_edge(CAMPUS_GRAPH, "Pollak Library (PL)",              "Humanities-Social Sciences (HSS)",        2)
_add_edge(CAMPUS_GRAPH, "Pollak Library (PL)",              "Bookstore/Titan Shops (B)",               2)
_add_edge(CAMPUS_GRAPH, "Pollak Library (PL)",              "Titan Student Union (TSU)",               4)
_add_edge(CAMPUS_GRAPH, "Pollak Library (PL)",              "Clayes Performing Arts Center (CPAC)",    5)
_add_edge(CAMPUS_GRAPH, "Humanities-Social Sciences (HSS)", "University Hall (UH)",                    1)
_add_edge(CAMPUS_GRAPH, "Humanities-Social Sciences (HSS)", "Kinesiology & Health (KHS)",              5)
_add_edge(CAMPUS_GRAPH, "University Hall (UH)",             "McCarthy Hall (MH)",                      2)
_add_edge(CAMPUS_GRAPH, "University Hall (UH)",             "Dan Black Hall (DBH)",                    2)
_add_edge(CAMPUS_GRAPH, "University Hall (UH)",             "Carl's Jr (CJ)",                          2)
_add_edge(CAMPUS_GRAPH, "Carl's Jr (CJ)",                   "Langsdorf Hall (LH)",                     2)
_add_edge(CAMPUS_GRAPH, "Carl's Jr (CJ)",                   "Mihaylo Hall (SGMH)",                     3)

# West side / student-life area
_add_edge(CAMPUS_GRAPH, "Titan Student Union (TSU)",              "Bookstore/Titan Shops (B)",                   1)
_add_edge(CAMPUS_GRAPH, "Titan Student Union (TSU)",              "Student Rec Center (SRC)",                    5)
_add_edge(CAMPUS_GRAPH, "Titan Student Union (TSU)",              "Visual Arts (VA)",                            3)
_add_edge(CAMPUS_GRAPH, "Titan Student Union (TSU)",              "Clayes Performing Arts Center (CPAC)",        5)
_add_edge(CAMPUS_GRAPH, "Titan Student Union (TSU)",              "University Police (UP)",                      5)
_add_edge(CAMPUS_GRAPH, "Bookstore/Titan Shops (B)",              "Student Rec Center (SRC)",                    3)
_add_edge(CAMPUS_GRAPH, "Student Rec Center (SRC)",               "Kinesiology & Health (KHS)",                  3)
_add_edge(CAMPUS_GRAPH, "Student Rec Center (SRC)",               "Receiving (R)",                               3)
_add_edge(CAMPUS_GRAPH, "Student Rec Center (SRC)",               "State College Parking Structure (SCPS)",      4)
_add_edge(CAMPUS_GRAPH, "Student Rec Center (SRC)",               "Children's Center (CC)",                      5)
_add_edge(CAMPUS_GRAPH, "State College Parking Structure (SCPS)", "University Police (UP)",                      2)
_add_edge(CAMPUS_GRAPH, "State College Parking Structure (SCPS)", "Receiving (R)",                               2)
_add_edge(CAMPUS_GRAPH, "State College Parking Structure (SCPS)", "Parking & Transportation Services (P)",       4)
_add_edge(CAMPUS_GRAPH, "University Police (UP)",                 "Receiving (R)",                               3)
_add_edge(CAMPUS_GRAPH, "University Police (UP)",                 "Visual Arts (VA)",                            6)
_add_edge(CAMPUS_GRAPH, "University Police (UP)",                 "Parking & Transportation Services (P)",       5)
_add_edge(CAMPUS_GRAPH, "Receiving (R)",                          "Visual Arts (VA)",                            4)
_add_edge(CAMPUS_GRAPH, "Receiving (R)",                          "Parking & Transportation Services (P)",       4)
_add_edge(CAMPUS_GRAPH, "Children's Center (CC)",                 "Parking & Transportation Services (P)",       4)
_add_edge(CAMPUS_GRAPH, "Children's Center (CC)",                 "State College Parking Structure (SCPS)",      4)

# South campus
_add_edge(CAMPUS_GRAPH, "Visual Arts (VA)",                      "Clayes Performing Arts Center (CPAC)", 3)
_add_edge(CAMPUS_GRAPH, "Visual Arts (VA)",                      "Nutwood Parking Structure (NPS)",      4)
_add_edge(CAMPUS_GRAPH, "Clayes Performing Arts Center (CPAC)",  "Greenhouse Complex (BGC)",             2)
_add_edge(CAMPUS_GRAPH, "Clayes Performing Arts Center (CPAC)",  "McCarthy Hall (MH)",                   4)
_add_edge(CAMPUS_GRAPH, "Clayes Performing Arts Center (CPAC)",  "Nutwood Parking Structure (NPS)",      5)
_add_edge(CAMPUS_GRAPH, "Nutwood Parking Structure (NPS)",       "Greenhouse Complex (BGC)",             3)
_add_edge(CAMPUS_GRAPH, "Greenhouse Complex (BGC)",              "McCarthy Hall (MH)",                   2)
_add_edge(CAMPUS_GRAPH, "Greenhouse Complex (BGC)",              "Dan Black Hall (DBH)",                 2)
_add_edge(CAMPUS_GRAPH, "McCarthy Hall (MH)",                    "Dan Black Hall (DBH)",                 1)
_add_edge(CAMPUS_GRAPH, "McCarthy Hall (MH)",                    "Langsdorf Hall (LH)",                  4)
_add_edge(CAMPUS_GRAPH, "McCarthy Hall (MH)",                    "Carl's Jr (CJ)",                       2)
_add_edge(CAMPUS_GRAPH, "Dan Black Hall (DBH)",                  "Langsdorf Hall (LH)",                  3)
_add_edge(CAMPUS_GRAPH, "Langsdorf Hall (LH)",                   "Mihaylo Hall (SGMH)",                  2)
_add_edge(CAMPUS_GRAPH, "Langsdorf Hall (LH)",                   "College Park (CP)",                    5)
_add_edge(CAMPUS_GRAPH, "Mihaylo Hall (SGMH)",                   "College Park (CP)",                    3)
_add_edge(CAMPUS_GRAPH, "Mihaylo Hall (SGMH)",                   "Eastside Parking Structure (EPS)",     6)


BUILDINGS: list[str] = sorted(CAMPUS_GRAPH.keys())


# ─────────────────────────────────────────
# Algorithms
# ─────────────────────────────────────────

def dijkstra(graph, start, end):
    """
    Heap-based Dijkstra's shortest path algorithm. Optimizes for distance.
    Returns: (total_distance, total_time, path_list) or (inf, inf, None).
    """
    if not graph:
        return float("inf"), float("inf"), None

    pq = [(0, 0, start, [start])]
    visited = set()

    while pq:
        dist, time, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        if current == end:
            return dist, time, path
        for neighbor, attrs in graph.get(current, {}).items():
            if neighbor not in visited:
                heapq.heappush(pq, (
                    dist + attrs["distance"],
                    time + attrs["time"],
                    neighbor,
                    path + [neighbor],
                ))

    return float("inf"), float("inf"), None


def bfs(graph, start, end):
    """
    Breadth-first search — path with fewest hops.
    Returns: (hops, total_distance, total_time, path_list) or (inf, inf, inf, None).
    """
    if not graph:
        return float("inf"), float("inf"), float("inf"), None

    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current == end:
            total_dist = sum(graph[path[i]][path[i + 1]]["distance"] for i in range(len(path) - 1))
            total_time = sum(graph[path[i]][path[i + 1]]["time"]     for i in range(len(path) - 1))
            return len(path) - 1, total_dist, total_time, path
        if current not in visited:
            visited.add(current)
            for neighbor in graph.get(current, {}):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return float("inf"), float("inf"), float("inf"), None


def dfs(graph, start):
    """
    Depth-first search full traversal from a start node.
    Returns: (visit_order, is_connected, status_string).
    """
    if not graph:
        return [], False, "Graph is empty"

    visited_order = []
    stack = [start]
    seen = set()

    while stack:
        current = stack.pop()
        if current not in seen:
            seen.add(current)
            visited_order.append(current)
            for neighbor in sorted(graph.get(current, {}), reverse=True):
                if neighbor not in seen:
                    stack.append(neighbor)

    is_connected = len(seen) == len(graph)
    status_str = f"Graph {'is' if is_connected else 'is NOT'} fully connected."
    return visited_order, is_connected, status_str


def prims_mst(graph):
    """
    Heap-based Prim's minimum spanning tree algorithm. Optimizes for distance.
    Returns: (list of (u, v, distance), total_distance, total_time).
    """
    if not graph:
        return [], 0, 0

    start_node = next(iter(graph))
    pq = []
    for neighbor, attrs in graph[start_node].items():
        heapq.heappush(pq, (attrs["distance"], attrs["time"], start_node, neighbor))

    mst_edges = []
    visited = {start_node}
    total_dist = total_time = 0

    while pq and len(visited) < len(graph):
        edge_dist, edge_time, u, v = heapq.heappop(pq)
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, edge_dist))
            total_dist += edge_dist
            total_time += edge_time
            for next_neighbor, attrs in graph.get(v, {}).items():
                if next_neighbor not in visited:
                    heapq.heappush(pq, (attrs["distance"], attrs["time"], v, next_neighbor))

    return mst_edges, total_dist, total_time
