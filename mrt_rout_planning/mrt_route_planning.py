from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Set
import math
import heapq
from collections import deque
from time import perf_counter
import json

# Types
Station = str
Line = str

BaseEdge = Tuple[Station, int, Line]     # (neighbor, baseline_minutes, line)
BaseGraph = Dict[Station, List[BaseEdge]]

Node = Tuple[Station, Line]              # (station, line)
Edge = Tuple[Node, float] # (neighbor_node, edge_cost_minutes_or_transfer)
Graph = Dict[Node, List[Edge]]


# Cost Model

TRANSFER_PENALTY_MIN = 3
MAJOR_INTERCHANGES_FUTURE = {"Tanah Merah", "Changi Terminal 5"}

CROWDING_TODAY: Dict[Station, int] = {
    "City Hall": 3,
    "Bugis": 3,
    "Raffles Place": 3,
    "Marina Bay": 2,
    "Promenade": 2,
    "Paya Lebar": 1,
    "Tanah Merah": 1,
    "Outram Park": 1,
    "HarbourFront": 1,
    "Orchard": 1,
    "Tampines": 1,
    "Expo": 1,
    "Sungei Bedok": 1,
}

CROWDING_FUTURE: Dict[Station, int] = {
    **CROWDING_TODAY,
    "Tanah Merah": 3,
    "Expo": 2,
    "Sungei Bedok": 2,
    "Changi Terminal 5": 3,
}

IS_FUTURE_MODE = False

def crowd_value(station: Station) -> int:
    return (CROWDING_FUTURE if IS_FUTURE_MODE else CROWDING_TODAY).get(station, 0)

def transfer_penalty(station: Station) -> int:
    if IS_FUTURE_MODE and station in MAJOR_INTERCHANGES_FUTURE:
        return 6
    return TRANSFER_PENALTY_MIN


# Graph helpers

def add_undirected_edge(g: BaseGraph, a: Station, b: Station, minutes: int, line: Line) -> None:
    g.setdefault(a, []).append((b, minutes, line))
    g.setdefault(b, []).append((a, minutes, line))


# Graph Building (Today / Future)  

def build_today_base_graph() -> BaseGraph:
    g: BaseGraph = {}

    # Airport branch (today: EWL label)
    add_undirected_edge(g, "Tanah Merah", "Expo", 5, "EWL")
    add_undirected_edge(g, "Expo", "Changi Airport", 4, "EWL")

    # EWL east/spine
    add_undirected_edge(g, "Tanah Merah", "Simei", 3, "EWL")
    add_undirected_edge(g, "Simei", "Tampines", 3, "EWL")

    add_undirected_edge(g, "Tanah Merah", "Bedok", 4, "EWL")
    add_undirected_edge(g, "Bedok", "Kembangan", 2, "EWL")
    add_undirected_edge(g, "Kembangan", "Eunos", 2, "EWL")
    add_undirected_edge(g, "Eunos", "Paya Lebar", 2, "EWL")
    add_undirected_edge(g, "Paya Lebar", "Aljunied", 2, "EWL")
    add_undirected_edge(g, "Aljunied", "Kallang", 2, "EWL")
    add_undirected_edge(g, "Kallang", "Lavender", 2, "EWL")
    add_undirected_edge(g, "Lavender", "Bugis", 2, "EWL")
    add_undirected_edge(g, "Bugis", "City Hall", 2, "EWL")

    add_undirected_edge(g, "City Hall", "Raffles Place", 2, "EWL")
    add_undirected_edge(g, "Raffles Place", "Tanjong Pagar", 2, "EWL")
    add_undirected_edge(g, "Tanjong Pagar", "Outram Park", 2, "EWL")

    # NSL
    add_undirected_edge(g, "City Hall", "Dhoby Ghaut", 2, "NSL")
    add_undirected_edge(g, "Dhoby Ghaut", "Somerset", 2, "NSL")
    add_undirected_edge(g, "Somerset", "Orchard", 2, "NSL")
    add_undirected_edge(g, "Orchard", "Newton", 3, "NSL")
    add_undirected_edge(g, "Newton", "Novena", 2, "NSL")
    add_undirected_edge(g, "Novena", "Toa Payoh", 3, "NSL")
    add_undirected_edge(g, "Toa Payoh", "Braddell", 2, "NSL")
    add_undirected_edge(g, "Braddell", "Bishan", 2, "NSL")

    add_undirected_edge(g, "Raffles Place", "Marina Bay", 2, "NSL")

    # NEL + HarbourFront
    add_undirected_edge(g, "Outram Park", "HarbourFront", 5, "NEL")
    add_undirected_edge(g, "Outram Park", "Chinatown", 2, "NEL")
    add_undirected_edge(g, "Chinatown", "Clarke Quay", 2, "NEL")
    add_undirected_edge(g, "Clarke Quay", "Dhoby Ghaut", 2, "NEL")
    add_undirected_edge(g, "Dhoby Ghaut", "Serangoon", 2, "NEL")

    # DTL East arm
    add_undirected_edge(g, "Expo", "Upper Changi", 2, "DTL")
    add_undirected_edge(g, "Upper Changi", "Tampines East", 2, "DTL")
    add_undirected_edge(g, "Tampines East", "Tampines", 2, "DTL")

    # DTL to Sungei Bedok
    add_undirected_edge(g, "Expo", "Xilin", 2, "DTL")
    add_undirected_edge(g, "Xilin", "Sungei Bedok", 2, "DTL")

    # DTL West/core
    add_undirected_edge(g, "Tampines", "Tampines West", 2, "DTL")
    add_undirected_edge(g, "Tampines West", "Bedok Reservoir", 2, "DTL")
    add_undirected_edge(g, "Bedok Reservoir", "Bedok North", 2, "DTL")
    add_undirected_edge(g, "Bedok North", "Kaki Bukit", 2, "DTL")
    add_undirected_edge(g, "Kaki Bukit", "Ubi", 2, "DTL")
    add_undirected_edge(g, "Ubi", "MacPherson", 2, "DTL")

    add_undirected_edge(g, "MacPherson", "Mattar", 2, "DTL")
    add_undirected_edge(g, "Mattar", "Geylang Bahru", 2, "DTL")
    add_undirected_edge(g, "Geylang Bahru", "Bendemeer", 2, "DTL")
    add_undirected_edge(g, "Bendemeer", "Jalan Besar", 2, "DTL")
    add_undirected_edge(g, "Jalan Besar", "Bencoolen", 2, "DTL")
    add_undirected_edge(g, "Bencoolen", "Fort Canning", 2, "DTL")
    add_undirected_edge(g, "Fort Canning", "Chinatown", 2, "DTL")
    add_undirected_edge(g, "Chinatown", "Telok Ayer", 2, "DTL")
    add_undirected_edge(g, "Telok Ayer", "Downtown", 2, "DTL")
    add_undirected_edge(g, "Downtown", "Bayfront", 2, "DTL")
    add_undirected_edge(g, "Bayfront", "Promenade", 2, "DTL")
    add_undirected_edge(g, "Promenade", "Bugis", 2, "DTL")
    add_undirected_edge(g, "Bugis", "Rochor", 2, "DTL")
    add_undirected_edge(g, "Rochor", "Little India", 2, "DTL")
    add_undirected_edge(g, "Little India", "Newton", 2, "DTL")

    # CCL segment
    add_undirected_edge(g, "Paya Lebar", "Dakota", 2, "CCL")
    add_undirected_edge(g, "Dakota", "Mountbatten", 2, "CCL")
    add_undirected_edge(g, "Mountbatten", "Stadium", 2, "CCL")
    add_undirected_edge(g, "Stadium", "Nicoll Highway", 2, "CCL")
    add_undirected_edge(g, "Nicoll Highway", "Promenade", 2, "CCL")
    add_undirected_edge(g, "Promenade", "Bayfront", 2, "CCL")
    add_undirected_edge(g, "Bayfront", "Marina Bay", 2, "CCL")
    add_undirected_edge(g, "MacPherson", "Paya Lebar", 2, "CCL")

    # CCL to Bishan
    add_undirected_edge(g, "MacPherson", "Tai Seng", 2, "CCL")
    add_undirected_edge(g, "Tai Seng", "Bartley", 2, "CCL")
    add_undirected_edge(g, "Bartley", "Serangoon", 2, "CCL")
    add_undirected_edge(g, "Serangoon", "Lorong Chuan", 2, "CCL")
    add_undirected_edge(g, "Lorong Chuan", "Bishan", 2, "CCL")

    # TEL East Coast to Gardens by the Bay
    add_undirected_edge(g, "Sungei Bedok", "Bedok South", 2, "TEL")
    add_undirected_edge(g, "Bedok South", "Bayshore", 2, "TEL")
    add_undirected_edge(g, "Bayshore", "Siglap", 2, "TEL")
    add_undirected_edge(g, "Siglap", "Marine Terrace", 2, "TEL")
    add_undirected_edge(g, "Marine Terrace", "Marine Parade", 2, "TEL")
    add_undirected_edge(g, "Marine Parade", "Tanjong Katong", 2, "TEL")
    add_undirected_edge(g, "Tanjong Katong", "Katong Park", 2, "TEL")
    add_undirected_edge(g, "Katong Park", "Tanjong Rhu", 2, "TEL")
    add_undirected_edge(g, "Tanjong Rhu", "Gardens by the Bay", 2, "TEL")
    add_undirected_edge(g, "Gardens by the Bay", "Marina Bay", 2, "TEL")

    # Make HarbourFront a better interchange via CCL 
    add_undirected_edge(g, "HarbourFront", "Keppel", 2, "CCL")
    add_undirected_edge(g, "Keppel", "Cantonment", 2, "CCL")
    add_undirected_edge(g, "Cantonment", "Outram Park", 2, "CCL")

    # Extend EWL to Pasir Ris
    add_undirected_edge(g, "Tampines", "Pasir Ris", 4, "EWL")

    return g

def build_future_base_graph() -> BaseGraph:
    g = build_today_base_graph()

    # TELe: Sungei Bedok -> T5 -> Tanah Merah (TEL)
    add_undirected_edge(g, "Sungei Bedok", "Changi Terminal 5", 4, "TEL")  
    add_undirected_edge(g, "Changi Terminal 5", "Tanah Merah", 4, "TEL")   

    # CRL extension to T5 
    add_undirected_edge(g, "Pasir Ris", "Pasir Ris East", 2, "CRL")
    add_undirected_edge(g, "Pasir Ris East", "Loyang", 3, "CRL")
    add_undirected_edge(g, "Loyang", "Aviation Park", 3, "CRL")
    add_undirected_edge(g, "Aviation Park", "Changi Terminal 5", 4, "CRL")

    # Small CRL connection towards Tampines North 
    add_undirected_edge(g, "Pasir Ris", "Tampines North", 5, "CRL")
    add_undirected_edge(g, "Tampines North", "Tampines", 6, "CRL") 

    # Convert Tanah Merah - Expo - Changi Airport to TEL systems 
    def relabel_edge(u: Station, v: Station, new_line: Line) -> None:
        g[u] = [(nbr, mins, new_line if nbr == v else line) for nbr, mins, line in g[u]]
        g[v] = [(nbr, mins, new_line if nbr == u else line) for nbr, mins, line in g[v]]

    relabel_edge("Tanah Merah", "Expo", "TEL")
    relabel_edge("Expo", "Changi Airport", "TEL")

    return g

# Expand BaseGraph -> StateGraph (station,line) + transfers

def stations_and_lines(base: BaseGraph) -> Dict[Station, Set[Line]]:
    sl: Dict[Station, Set[Line]] = {}
    for u, edges in base.items():
        sl.setdefault(u, set())
        for v, _, line in edges:
            sl.setdefault(v, set())
            sl[u].add(line)
            sl[v].add(line)
    return sl

def build_state_graph(base: BaseGraph, *, start: Station, goal: Station) -> Tuple[Graph, Set[Node], Set[Node]]:
    sl = stations_and_lines(base)
    interchanges = {st for st, lines in sl.items() if len(lines) >= 2}
    # Debug: check unexpected interchanges
    # print("Interchanges:", sorted(interchanges))


    tmp: Dict[Node, Dict[Node, float]] = {}

    # 1) ride edges: baseline time only
    for u, edges in base.items():
        for v, mins, line in edges:
            a = (u, line)
            b = (v, line)
            cost = float(mins)
            tmp.setdefault(a, {})
            if b not in tmp[a] or cost < tmp[a][b]:
                tmp[a][b] = cost

    # 2) transfer edges: transfer penalty + crowd at that station
    for st in interchanges:
        lines = sorted(sl[st])
        for l1 in lines:
            for l2 in lines:
                if l1 == l2:
                    continue
                a = (st, l1)
                b = (st, l2)
                cost = float(transfer_penalty(st) + crowd_value(st))
                tmp.setdefault(a, {})
                if b not in tmp[a] or cost < tmp[a][b]:
                    tmp[a][b] = cost

    # 3) super nodes: pay crowd only when boarding + alighting
    SUPER_START: Node = ("__START__", "__START__")
    SUPER_GOAL: Node  = ("__GOAL__", "__GOAL__")

    # boarding: SUPER_START -> (start, each line)
    for line_name in sl.get(start, set()):
        a = SUPER_START
        b = (start, line_name)
        cost = float(crowd_value(start))
        tmp.setdefault(a, {})
        if b not in tmp[a] or cost < tmp[a][b]:
            tmp[a][b] = cost

    # alighting: (goal, each line) -> SUPER_GOAL
    for line_name in sl.get(goal, set()):
        a = (goal, line_name)
        b = SUPER_GOAL
        cost = float(crowd_value(goal))
        tmp.setdefault(a, {})
        if b not in tmp[a] or cost < tmp[a][b]:
            tmp[a][b] = cost

    g: Graph = {u: [(v, c) for v, c in nbrs.items()] for u, nbrs in tmp.items()}
    return g, {SUPER_START}, {SUPER_GOAL}


# Coordinates + Heuristic (time-based)

COORDS_XY: Dict[Station, Tuple[float, float]] = {}
HEURISTIC_SCALE_MIN_PER_KM = 0.0

import os

def load_coords_from_json(json_path: str) -> Dict[Station, Tuple[float, float]]:
   
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, json_path)

    with open(full_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    coords: Dict[Station, Tuple[float, float]] = {}
    for r in rows:
        name = r["station_name"].strip()
        lat = float(r["latitude"])
        lon = float(r["longitude"])
        coords[name] = (lat, lon)

    
    if "Changi Aiport" in coords and "Changi Airport" not in coords:
        coords["Changi Airport"] = coords.pop("Changi Aiport")

    return coords


def latlon_to_xy_km(lat: float, lon: float, ref_lat: float) -> Tuple[float, float]:
    """
    Equirectangular approximation:
      1 deg latitude  ~ 111.32 km
      1 deg longitude ~ 111.32 * cos(ref_lat) km
    """
    y = lat * 111.32
    x = lon * 111.32 * math.cos(math.radians(ref_lat))
    return x, y

def build_xy_coords(coords_latlon: Dict[Station, Tuple[float, float]]) -> Dict[Station, Tuple[float, float]]:
    if not coords_latlon:
        return {}
    ref_lat = sum(lat for lat, _ in coords_latlon.values()) / len(coords_latlon)
    return {st: latlon_to_xy_km(lat, lon, ref_lat) for st, (lat, lon) in coords_latlon.items()}
def check_missing_coords(base: BaseGraph, coords_xy: Dict[Station, Tuple[float, float]]) -> None:
    """Debug helper: prints stations that exist in the graph but have no coordinates."""
    stations = set(base.keys())
    for u, edges in base.items():
        for v, _, _ in edges:
            stations.add(v)

    missing = sorted([s for s in stations if s not in coords_xy])
    if missing:
        print("Missing COORDS:", missing)
    else:
        print("Missing COORDS: none ")

def compute_safe_minutes_per_km(base: BaseGraph, safety: float = 0.9) -> float:
    """
    Convert distance (km) -> time (min) using ONLY your graph data:

      minutes_per_km = min_over_edges( edge_minutes / euclid_km )

    Using min() keeps it conservative (underestimates time).
    safety (<1) makes it even more conservative.
    """
    ratios: List[float] = []
    for u, edges in base.items():
        for v, mins, _ in edges:
            if u in COORDS_XY and v in COORDS_XY:
                ux, uy = COORDS_XY[u]
                vx, vy = COORDS_XY[v]
                d = math.hypot(ux - vx, uy - vy)
                if d > 1e-6:
                    ratios.append(mins / d)

    if not ratios:
        return 0.0
    return safety * min(ratios)

def h_station(a: Station, b: Station) -> float:
    """Heuristic in minutes (straight-line lower bound)."""
    if a not in COORDS_XY or b not in COORDS_XY:
        return 0.0
    ax, ay = COORDS_XY[a]
    bx, by = COORDS_XY[b]
    d_km = math.hypot(ax - bx, ay - by)
    return HEURISTIC_SCALE_MIN_PER_KM * d_km


def h_node(n: Node, goal_station: Station, start_station: Station) -> float:
    st, _ = n
    if st == "__START__":
        return h_station(start_station, goal_station)
    if st == "__GOAL__":
        return 0.0
    return h_station(st, goal_station)

# Path utilities

def reconstruct(parent: Dict[Node, Optional[Node]], goal: Node) -> List[Node]:
    out: List[Node] = []
    cur: Optional[Node] = goal
    while cur is not None:
        out.append(cur)
        cur = parent[cur]
    out.reverse()
    return out

def collapse_station_path(node_path: List[Node]) -> List[Station]:
    out: List[Station] = []
    for st, _ln in node_path:
        if st in {"__START__", "__GOAL__"}:
            continue
        if not out or out[-1] != st:
            out.append(st)
    return out


def path_cost(graph: Graph, node_path: List[Node]) -> float:
    """Sum of edge costs along node_path (graph already includes crowding + penalties)."""
    if not node_path:
        return float("inf")

    total = 0.0
    for i in range(len(node_path) - 1):
        u = node_path[i]
        v = node_path[i + 1]

        edge_cost = None
        for nbr, c in graph.get(u, []):
            if nbr == v:
                edge_cost = c
                break
        if edge_cost is None:
            return float("inf")

        total += edge_cost

    return total

# Count the number of hops in the path 
def hop_count_stations(stations: List[Station]) -> int:
    return max(0, len(stations) - 1)
def hop_count_nodes(node_path: List[Node]) -> int:
    return max(0, len(node_path) - 1)



# Search Algorithms

def bfs(graph: Graph, starts: List[Node], goals: Set[Node]) -> Tuple[Optional[List[Node]], int]:
    q = deque(starts)
    parent: Dict[Node, Optional[Node]] = {s: None for s in starts}
    visited = set(starts)
    expanded = 0

    while q:
        u = q.popleft()
        expanded += 1
        if u in goals:
            return reconstruct(parent, u), expanded

        for v, _ in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                q.append(v)

    return None, expanded

def dfs(graph: Graph, starts: List[Node], goals: Set[Node]) -> Tuple[Optional[List[Node]], int]:
    stack = list(starts)
    parent: Dict[Node, Optional[Node]] = {s: None for s in starts}
    discovered: Set[Node] = set(starts)
    expanded = 0

    while stack:
        u = stack.pop()
        expanded += 1

        if u in goals:
            return reconstruct(parent, u), expanded

        for v, _ in reversed(graph.get(u, [])):
            if v not in discovered:
                discovered.add(v)
                parent[v] = u
                stack.append(v)

    return None, expanded


def gbfs(graph: Graph, starts: List[Node], goals: Set[Node],
         goal_station: Station, start_station: Station) -> Tuple[Optional[List[Node]], int]:

    def key(n: Node) -> float:
        return h_node(n, goal_station, start_station)



    pq: List[Tuple[float, Node]] = [(key(s), s) for s in starts]
    heapq.heapify(pq)

    parent: Dict[Node, Optional[Node]] = {s: None for s in starts}
    visited: Set[Node] = set()
    expanded = 0

    while pq:
        _, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        expanded += 1

        if u in goals:
            return reconstruct(parent, u), expanded

        for v, _ in graph.get(u, []):
            if v in visited:
                continue
            if v not in parent:
                parent[v] = u
            heapq.heappush(pq, (key(v), v))

    return None, expanded

def astar(graph: Graph, starts: List[Node], goals: Set[Node],
          goal_station: Station, start_station: Station) -> Tuple[Optional[List[Node]], float, int]:

    def h(n: Node) -> float:
        return h_node(n, goal_station, start_station)



    pq: List[Tuple[float, float, Node]] = []
    best_g: Dict[Node, float] = {}
    parent: Dict[Node, Optional[Node]] = {}

    for s in starts:
        best_g[s] = 0.0
        parent[s] = None
        heapq.heappush(pq, (h(s), 0.0, s))

    expanded = 0

    while pq:
        _f, gcur, u = heapq.heappop(pq)
        if gcur != best_g.get(u, float("inf")):
            continue

        expanded += 1
        if u in goals:
            return reconstruct(parent, u), gcur, expanded

        for v, edge_cost in graph.get(u, []):
            new_g = gcur + edge_cost
            if new_g < best_g.get(v, float("inf")):
                best_g[v] = new_g
                parent[v] = u
                heapq.heappush(pq, (new_g + h(v), new_g, v))

    return None, float("inf"), expanded

#Transfer Count

def transfer_count(node_path: List[Node]) -> int:
    c = 0
    for i in range(len(node_path)-1):
        (s1,l1) = node_path[i]
        (s2,l2) = node_path[i+1]
        if s1 == s2 and l1 != l2:
            c += 1
    return c

# Experiment Runner

def validate_station_path(stations: List[Station], start: Station, goal: Station) -> None:
    if stations and stations[0] != start:
        raise RuntimeError(f"Path does not start at origin! expected {start}, got {stations[0]}: {stations}")
    if stations and stations[-1] != goal:
        raise RuntimeError(f"Path does not end at destination! expected {goal}, got {stations[-1]}: {stations}")

def run_algorithm(fn, *args):
    t0 = perf_counter()
    out = fn(*args)
    t1 = perf_counter()
    return out, (t1 - t0)

def run_one(base: BaseGraph, start_station: Station, goal_station: Station) -> None:
    sg, start_nodes_set, goal_nodes = build_state_graph(base, start=start_station, goal=goal_station)

    if not start_nodes_set or not goal_nodes:
        print("  NO PATH (start/goal lines missing)")
        return

    starts = sorted(list(start_nodes_set))

    

   
    # BFS
   
    (p, expanded), dt = run_algorithm(bfs, sg, starts, goal_nodes)
    if p:
        stations = collapse_station_path(p)
        validate_station_path(stations, start_station, goal_station)

        station_hops = hop_count_stations(stations)
        state_hops = hop_count_nodes(p)
        transfers = transfer_count(p)
        cost = path_cost(sg, p)

        print(
            f"  BFS : expanded={expanded:4d} | time={dt*1000:8.3f} ms"
            f" | station_hops={station_hops:3d} | state_hops={state_hops:3d}"
            f" | transfers={transfers:2d} | cost={cost:7.1f} | {stations}"
        )
    else:
        print(f"  BFS : expanded={expanded:4d} | time={dt*1000:8.3f} ms | NO PATH")

   
    # DFS

    (p, expanded), dt = run_algorithm(dfs, sg, starts, goal_nodes)
    if p:
        stations = collapse_station_path(p)
        validate_station_path(stations, start_station, goal_station)

        station_hops = hop_count_stations(stations)
        state_hops = hop_count_nodes(p)
        transfers = transfer_count(p)
        cost = path_cost(sg, p)

        print(
            f"  DFS : expanded={expanded:4d} | time={dt*1000:8.3f} ms"
            f" | station_hops={station_hops:3d} | state_hops={state_hops:3d}"
            f" | transfers={transfers:2d} | cost={cost:7.1f} | {stations}"
        )
    else:
        print(f"  DFS : expanded={expanded:4d} | time={dt*1000:8.3f} ms | NO PATH")

  
    # GBFS
    
    (p, expanded), dt = run_algorithm(gbfs, sg, starts, goal_nodes, goal_station, start_station)
    if p:
        stations = collapse_station_path(p)
        validate_station_path(stations, start_station, goal_station)

        station_hops = hop_count_stations(stations)
        state_hops = hop_count_nodes(p)
        transfers = transfer_count(p)
        cost = path_cost(sg, p)

        print(
            f"  GBFS: expanded={expanded:4d} | time={dt*1000:8.3f} ms"
            f" | station_hops={station_hops:3d} | state_hops={state_hops:3d}"
            f" | transfers={transfers:2d} | cost={cost:7.1f} | {stations}"
        )
    else:
        print(f"  GBFS: expanded={expanded:4d} | time={dt*1000:8.3f} ms | NO PATH")

   
    # A*
   
    (p, acost, expanded), dt = run_algorithm(astar, sg, starts, goal_nodes, goal_station, start_station)
    if p:
        stations = collapse_station_path(p)
        validate_station_path(stations, start_station, goal_station)

        station_hops = hop_count_stations(stations)
        state_hops = hop_count_nodes(p)
        transfers = transfer_count(p)
        posthoc = path_cost(sg, p)

        print(
            f"  A*  : expanded={expanded:4d} | time={dt*1000:8.3f} ms"
            f" | station_hops={station_hops:3d} | state_hops={state_hops:3d}"
            f" | transfers={transfers:2d} | cost={acost:7.1f} | posthoc={posthoc:7.1f} | {stations}"
        )
    else:
        print(f"  A*  : expanded={expanded:4d} | time={dt*1000:8.3f} ms | NO PATH")




def run_suite(base: BaseGraph, title: str, tests: List[Tuple[Station, Station]]) -> None:
    print(f"\n=== {title} ===")
    for s, g in tests:
        print(f"\n{s} -> {g}")
        run_one(base, s, g)

# Tests (>=5 per mode)

TESTS_TODAY = [
    ("Changi Airport", "City Hall"),
    ("Changi Airport", "Orchard"),
    ("Changi Airport", "Gardens by the Bay"),
   
]

TESTS_FUTURE = [
    ("Paya Lebar", "Changi Terminal 5"),
    ("HarbourFront", "Changi Terminal 5"),
    ("Bishan", "Changi Terminal 5"),
    ("Tampines", "Changi Terminal 5"),
    
]


# Main

def main() -> None:
    global IS_FUTURE_MODE, COORDS_XY, HEURISTIC_SCALE_MIN_PER_KM

    
    # TODAY MODE
    
    IS_FUTURE_MODE = False
    today_base = build_today_base_graph()

    coords_today = load_coords_from_json("mrt_today_coordinates.json")
    COORDS_XY = build_xy_coords(coords_today)

    HEURISTIC_SCALE_MIN_PER_KM = compute_safe_minutes_per_km(today_base)
    run_suite(today_base, "TODAY MODE", TESTS_TODAY)

    
    # FUTURE MODE
    # IMPORTANT: future graph contains today stations too,
    # so I  merged coords: today + future (future overrides duplicates)
    
    IS_FUTURE_MODE = True
    future_base = build_future_base_graph()

    coords_future_only = load_coords_from_json("mrt_future_coordinates.json")
    coords_future_all = dict(coords_today)
    coords_future_all.update(coords_future_only)

    COORDS_XY = build_xy_coords(coords_future_all)
    check_missing_coords(future_base, COORDS_XY)

    HEURISTIC_SCALE_MIN_PER_KM = compute_safe_minutes_per_km(future_base)
    run_suite(future_base, "FUTURE MODE", TESTS_FUTURE)

if __name__ == "__main__":
    main()
