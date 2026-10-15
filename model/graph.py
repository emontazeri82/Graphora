import networkx as nx

from model.edge_type import EdgeType
from model.node import Node


class Graph:
    def __init__(self) -> None:
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()

    @property
    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._graph.nodes)

    @property
    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        edge_ids: set[int] = set()

        for _, _, data in self._graph.edges(data=True):
            edge_ids.add(data["edge_id"])

        return len(edge_ids)

    def add_node(self, node: Node) -> None:
        if self.find_node(node.node_id) is not None:
            return

        self._graph.add_node(node)

    def find_node(self, node_id: int) -> Node | None:
        for node in self._graph.nodes:
            if node.node_id == node_id:
                return node

        return None

    def contains_node(self, node: Node) -> bool:
        return self._graph.has_node(node)

    def remove_node(self, node_id: int) -> Node | None:
        node = self.find_node(node_id)

        if node is None:
            return None

        self._graph.remove_node(node)
        return node

    def add_edge(
        self,
        edge_id: int,
        source: Node,
        target: Node,
        edge_type: EdgeType,
    ) -> None:
        if source not in self._graph or target not in self._graph:
            return

        if self.find_edge(edge_id) is not None:
            return

        self._graph.add_edge(
            source,
            target,
            key=edge_id,
            edge_id=edge_id,
            edge_type=edge_type,
        )

        if edge_type == EdgeType.UNDIRECTED and source != target:
            self._graph.add_edge(
                target,
                source,
                key=edge_id,
                edge_id=edge_id,
                edge_type=edge_type,
            )

    def find_edge(
        self,
        edge_id: int,
    ) -> tuple[Node, Node, dict[str, object]] | None:
        for source, target, key, data in self._graph.edges(
            keys=True,
            data=True,
        ):
            if key == edge_id:
                return source, target, data

        return None

    def remove_edge(self, edge_id: int) -> bool:
        edges_to_remove: list[tuple[Node, Node, int]] = []

        for source, target, key in self._graph.edges(keys=True):
            if key == edge_id:
                edges_to_remove.append((source, target, key))

        if not edges_to_remove:
            return False

        for source, target, key in edges_to_remove:
            self._graph.remove_edge(source, target, key)

        return True

    def are_connected(self, node1: Node, node2: Node) -> bool:
        return (
            self._graph.has_edge(node1, node2)
            or self._graph.has_edge(node2, node1)
        )

    def has_edge_from(self, node1: Node, node2: Node) -> bool:
        return self._graph.has_edge(node1, node2)

    def neighbors(self, node: Node) -> set[Node]:
        neighbors: set[Node] = set()

        neighbors.update(self._graph.successors(node))
        neighbors.update(self._graph.predecessors(node))

        return neighbors

    def out_neighbors(self, node: Node) -> set[Node]:
        return set(self._graph.successors(node))

    def in_neighbors(self, node: Node) -> set[Node]:
        return set(self._graph.predecessors(node))

    def out_degree(self, node: Node) -> int:
        return int(self._graph.out_degree(node))

    def in_degree(self, node: Node) -> int:
        return int(self._graph.in_degree(node))

    def degree(self, node: Node) -> int:
        return int(self._graph.degree(node))

    def adjacency_matrix(self):
        return nx.to_numpy_array(
            self._graph,
            nodelist=list(self._graph.nodes),
            dtype=int,
        )

    def clear(self) -> None:
        self._graph.clear()