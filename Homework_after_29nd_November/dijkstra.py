import os
import bisect

from collections import defaultdict
from typing import List, Tuple, Optional, Set, Dict, Iterable


INF = float("inf")

VertexType = str
EdgeType = List[Tuple[str, str, int]]
DistanceDict = Dict[VertexType, float]
PathInfo = Dict[VertexType, str]


def read_graph(file_path: str) -> List[Tuple[str, str, int]]:
    res = []
    with open(file_path, "r") as file_pointer:
        for line in file_pointer:
            if line.startswith("#"):
                continue
            begin, end = line.strip().split("\t")
            res.append((begin, end, 1))
    return res


def add_element(que, priority, key):
    index = bisect.bisect_right(que, (priority, "A"))
    que.insert(index, (priority, key))


def initialize_que(vertices: Iterable[str], begin: str):
    return [(0, begin)] + [(INF, v) for v in vertices if v != begin]


def get_visited(dist: DistanceDict) -> Set[VertexType]:
    return {k for k, v in dist.items() if v != INF}


def get_farthest_vertexes(dist: DistanceDict):
    max_dist = max((x for x in dist.values() if x != INF))
    for k, v in dist.items():
        if v == max_dist:
            yield k


def get_path(
    distance_dict: DistanceDict, previous_vertex: PathInfo, max_dist: float
) -> List[VertexType]:
    for key, dist in distance_dict.items():
        if dist == max_dist:
            diameter_path = [key]
            while previous_vertex[key] != None:
                key = previous_vertex[key]
                diameter_path.append(key)
            break
    else:
        raise ValueError("Vertex not found")
    return diameter_path[::-1]


def calc_connected_component_diameter(
    graph_edges: EdgeType, current_diameter: float, start: str
):
    distance_dict, previous_vertex = dijkstra(graph_edges, start)
    max_dist = max((x for x in distance_dict.values() if x != INF))
    if max_dist <= current_diameter:
        return current_diameter, [], set()
    max_path = get_path(distance_dict, previous_vertex, max_dist)
    visited = get_visited(distance_dict)
    for vertex in get_farthest_vertexes(distance_dict):
        dist, path, _ = calc_connected_component_diameter(graph_edges, max_dist, vertex)
        if dist > max_dist:
            max_dist = dist
            max_path = path
    return max_dist, max_path, visited


def main(file_path: Optional[str] = None):
    if file_path is None:
        file_path = os.path.join(os.path.dirname(__file__), "com-amazon.ungraph.txt")
    graph_edges = read_graph(file_path)
    vertex_to_visit = set()
    for begin, end, _dist in graph_edges:
        vertex_to_visit.add(begin)
        vertex_to_visit.add(end)

    res = []
    while vertex_to_visit:
        print(f"step {len(res)}")
        max_dist, max_path, visited = calc_connected_component_diameter(
            graph_edges, 0, vertex_to_visit.pop()
        )
        res.append((max_dist, max_path))
        vertex_to_visit.difference_update(visited)

    print(f"Graph has {len(res)} connected components")
    print(f"longest diameter of any components is {max(res)[0]}")


def dijkstra(graph_edges: EdgeType, start: str) -> Tuple[DistanceDict, PathInfo]:
    neighbourhood: Dict[str, Set[Tuple[str, float]]] = defaultdict(set)
    for begin, end, dist in graph_edges:
        neighbourhood[begin].add((end, dist))
        neighbourhood[end].add((begin, dist))
    previous_vertex = {x: None for x in neighbourhood}
    distance_dict = {x: INF for x in neighbourhood}
    distance_dict[start] = 0
    que = [(0, start)]
    count = 0
    while que:
        count += 1
        dist, vertex = que.pop(0)
        for neigh_v, edge_len in neighbourhood[vertex]:
            if distance_dict[neigh_v] > dist + edge_len:
                distance_dict[neigh_v] = dist + edge_len
                add_element(que, distance_dict[neigh_v], neigh_v)
                previous_vertex[neigh_v] = vertex

    return distance_dict, previous_vertex


if __name__ == "__main__":
    main()
