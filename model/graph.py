import networkx as nx

from model.edge import Edge
from model.edge_type import EdgeType
from model.node import Node


class Graph:
    def __init__(self) -> None:
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()

        self._edges: dict[int, Edge] = {}

    # ==========================================================
    # NODES
    # ==========================================================

    @property
    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._graph.nodes)

    @property
    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def add_node(
        self,
        node: Node,
    ) -> bool:
        if self.find_node(node.node_id) is not None:
            return False

        self._graph.add_node(node)

        return True

    def find_node(
        self,
        node_id: int,
    ) -> Node | None:
        for node in self._graph.nodes:
            if node.node_id == node_id:
                return node

        return None

    def contains_node(
        self,
        node: Node,
    ) -> bool:
        return self._graph.has_node(node)

    def remove_node(
        self,
        node_id: int,
    ) -> Node | None:
        node = self.find_node(node_id)

        if node is None:
            return None

        edge_ids_to_remove = [
            edge.edge_id
            for edge in self._edges.values()
            if edge.touches(node)
        ]

        for edge_id in edge_ids_to_remove:
            self.remove_edge(edge_id)

        self._graph.remove_node(node)

        return node

    # ==========================================================
    # EDGES
    # ==========================================================

    @property
    def edges(self) -> tuple[Edge, ...]:
        return tuple(self._edges.values())

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def add_edge(
        self,
        edge: Edge,
    ) -> bool:
        if not self.contains_node(edge.source):
            return False

        if not self.contains_node(edge.target):
            return False

        if edge.edge_id in self._edges:
            return False

        self._edges[edge.edge_id] = edge

        self._add_networkx_edge(edge)

        return True

    def _add_networkx_edge(
        self,
        edge: Edge,
    ) -> None:
        self._graph.add_edge(
            edge.source,
            edge.target,
            key=edge.edge_id,
            edge_id=edge.edge_id,
            edge=edge,
            edge_type=edge.edge_type,
        )

        if (
            edge.edge_type == EdgeType.UNDIRECTED
            and edge.source is not edge.target
        ):
            self._graph.add_edge(
                edge.target,
                edge.source,
                key=edge.edge_id,
                edge_id=edge.edge_id,
                edge=edge,
                edge_type=edge.edge_type,
            )

    def find_edge(
        self,
        edge_id: int,
    ) -> Edge | None:
        return self._edges.get(edge_id)

    def remove_edge(
        self,
        edge_id: int,
    ) -> Edge | None:
        edge = self._edges.get(edge_id)

        if edge is None:
            return None

        edges_to_remove: list[
            tuple[Node, Node, int]
        ] = []

        for source, target, key in self._graph.edges(
            keys=True
        ):
            if key == edge_id:
                edges_to_remove.append(
                    (
                        source,
                        target,
                        key,
                    )
                )

        for source, target, key in edges_to_remove:
            self._graph.remove_edge(
                source,
                target,
                key,
            )

        del self._edges[edge_id]

        return edge

    def edges_for_node(
        self,
        node: Node,
    ) -> tuple[Edge, ...]:
        return tuple(
            edge
            for edge in self._edges.values()
            if edge.touches(node)
        )

    def are_connected(
        self,
        node1: Node,
        node2: Node,
    ) -> bool:
        return (
            self._graph.has_edge(node1, node2)
            or self._graph.has_edge(node2, node1)
        )

    def has_edge_from(
        self,
        node1: Node,
        node2: Node,
    ) -> bool:
        return self._graph.has_edge(
            node1,
            node2,
        )

    # ==========================================================
    # NEIGHBORS
    # ==========================================================

    def neighbors(
        self,
        node: Node,
    ) -> set[Node]:
        result: set[Node] = set()

        result.update(
            self._graph.successors(node)
        )

        result.update(
            self._graph.predecessors(node)
        )

        return result

    def out_neighbors(
        self,
        node: Node,
    ) -> set[Node]:
        return set(
            self._graph.successors(node)
        )

    def in_neighbors(
        self,
        node: Node,
    ) -> set[Node]:
        return set(
            self._graph.predecessors(node)
        )

    # ==========================================================
    # DEGREES
    # ==========================================================

    def out_degree(
        self,
        node: Node,
    ) -> int:
        return int(
            self._graph.out_degree(node)
        )

    def in_degree(
        self,
        node: Node,
    ) -> int:
        return int(
            self._graph.in_degree(node)
        )

    def degree(
        self,
        node: Node,
    ) -> int:
        return int(
            self._graph.degree(node)
        )

    # ==========================================================
    # MATRIX
    # ==========================================================

    def adjacency_matrix(self):
        return nx.to_numpy_array(
            self._graph,
            nodelist=list(
                self._graph.nodes
            ),
            dtype=int,
        )

    # ==========================================================
    # CLEAR
    # ==========================================================

    def clear(self) -> None:
        self._graph.clear()
        self._edges.clear()