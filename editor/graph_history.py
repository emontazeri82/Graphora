from __future__ import annotations

from dataclasses import dataclass

from model.edge import Edge
from model.edge_type import EdgeType
from model.graph import Graph
from model.node import Node


@dataclass(frozen=True)
class NodeHistoryData:
    """
    Immutable snapshot of one node.
    """

    node_id: int
    name: str
    x: float
    y: float
    size: float
    shape: str
    color: tuple[int, int, int, int]

    @classmethod
    def from_node(
        cls,
        node: Node,
    ) -> NodeHistoryData:
        return cls(
            node_id=node.node_id,
            name=node.name,
            x=node.x,
            y=node.y,
            size=node.size,
            shape=node.shape,
            color=node.color,
        )


@dataclass(frozen=True)
class EdgeHistoryData:
    """
    Immutable snapshot of one edge.
    """

    edge_id: int
    source_id: int
    target_id: int
    edge_type: EdgeType
    name: str
    color: tuple[int, int, int, int]
    thickness: float

    @classmethod
    def from_edge(
        cls,
        edge: Edge,
    ) -> EdgeHistoryData:
        return cls(
            edge_id=edge.edge_id,
            source_id=edge.source.node_id,
            target_id=edge.target.node_id,
            edge_type=edge.edge_type,
            name=edge.name,
            color=edge.color,
            thickness=edge.thickness,
        )


@dataclass(frozen=True)
class GraphSnapshot:
    """
    Complete immutable snapshot of Graphora graph state.
    """

    nodes: tuple[NodeHistoryData, ...]
    edges: tuple[EdgeHistoryData, ...]

    next_node_id: int
    next_edge_id: int

    description: str = ""

    @classmethod
    def capture(
        cls,
        graph: Graph,
        next_node_id: int,
        next_edge_id: int,
        description: str = "",
    ) -> GraphSnapshot:
        nodes = tuple(
            NodeHistoryData.from_node(node)
            for node in graph.nodes
        )

        edges = tuple(
            EdgeHistoryData.from_edge(edge)
            for edge in graph.edges
        )

        return cls(
            nodes=nodes,
            edges=edges,
            next_node_id=next_node_id,
            next_edge_id=next_edge_id,
            description=description,
        )

    def restore_graph(
        self,
    ) -> Graph:
        """
        Reconstruct a completely independent Graph.
        """
        graph = Graph()

        node_map: dict[int, Node] = {}

        # ------------------------------------------------------
        # Restore nodes first
        # ------------------------------------------------------

        for data in self.nodes:
            node = Node(
                node_id=data.node_id,
                name=data.name,
                x=data.x,
                y=data.y,
                size=data.size,
                shape=data.shape,
                color=data.color,
            )

            graph.add_node(node)

            node_map[data.node_id] = node

        # ------------------------------------------------------
        # Restore edges after nodes
        # ------------------------------------------------------

        for data in self.edges:
            source = node_map.get(
                data.source_id
            )

            target = node_map.get(
                data.target_id
            )

            if source is None or target is None:
                continue

            edge = Edge(
                edge_id=data.edge_id,
                source=source,
                target=target,
                edge_type=data.edge_type,
                name=data.name,
                color=data.color,
                thickness=data.thickness,
            )

            graph.add_edge(edge)

        return graph


@dataclass
class HistoryResult:
    """
    State returned by Undo or Redo.
    """

    graph: Graph
    next_node_id: int
    next_edge_id: int
    description: str


class GraphHistory:
    """
    Snapshot-based Undo/Redo manager for Graphora.

    GraphHistory itself does not draw anything and does not
    modify GraphEditor directly.

    GraphEditor records states before mutations and installs
    restored states returned by undo()/redo().
    """

    DEFAULT_MAX_HISTORY: int = 100

    def __init__(
        self,
        max_history: int = DEFAULT_MAX_HISTORY,
    ) -> None:
        if max_history < 1:
            raise ValueError(
                "max_history must be at least 1"
            )

        self.max_history = int(
            max_history
        )

        self._undo_stack: list[
            GraphSnapshot
        ] = []

        self._redo_stack: list[
            GraphSnapshot
        ] = []

    # ==========================================================
    # STATE
    # ==========================================================

    @property
    def can_undo(self) -> bool:
        return bool(
            self._undo_stack
        )

    @property
    def can_redo(self) -> bool:
        return bool(
            self._redo_stack
        )

    @property
    def undo_count(self) -> int:
        return len(
            self._undo_stack
        )

    @property
    def redo_count(self) -> int:
        return len(
            self._redo_stack
        )

    @property
    def next_undo_description(
        self,
    ) -> str | None:
        if not self._undo_stack:
            return None

        return self._undo_stack[
            -1
        ].description

    @property
    def next_redo_description(
        self,
    ) -> str | None:
        if not self._redo_stack:
            return None

        return self._redo_stack[
            -1
        ].description

    # ==========================================================
    # RECORD
    # ==========================================================

    def record(
        self,
        graph: Graph,
        next_node_id: int,
        next_edge_id: int,
        description: str = "",
    ) -> None:
        """
        Record the current state BEFORE a mutation.

        Recording a new action invalidates redo history.
        """
        snapshot = GraphSnapshot.capture(
            graph=graph,
            next_node_id=next_node_id,
            next_edge_id=next_edge_id,
            description=description,
        )

        self._undo_stack.append(
            snapshot
        )

        if (
            len(self._undo_stack)
            > self.max_history
        ):
            del self._undo_stack[0]

        self._redo_stack.clear()

    # ==========================================================
    # UNDO
    # ==========================================================

    def undo(
        self,
        current_graph: Graph,
        next_node_id: int,
        next_edge_id: int,
    ) -> HistoryResult | None:
        if not self._undo_stack:
            return None

        target = self._undo_stack.pop()

        current = GraphSnapshot.capture(
            graph=current_graph,
            next_node_id=next_node_id,
            next_edge_id=next_edge_id,
            description=target.description,
        )

        self._redo_stack.append(
            current
        )

        return HistoryResult(
            graph=target.restore_graph(),
            next_node_id=target.next_node_id,
            next_edge_id=target.next_edge_id,
            description=target.description,
        )

    # ==========================================================
    # REDO
    # ==========================================================

    def redo(
        self,
        current_graph: Graph,
        next_node_id: int,
        next_edge_id: int,
    ) -> HistoryResult | None:
        if not self._redo_stack:
            return None

        target = self._redo_stack.pop()

        current = GraphSnapshot.capture(
            graph=current_graph,
            next_node_id=next_node_id,
            next_edge_id=next_edge_id,
            description=target.description,
        )

        self._undo_stack.append(
            current
        )

        return HistoryResult(
            graph=target.restore_graph(),
            next_node_id=target.next_node_id,
            next_edge_id=target.next_edge_id,
            description=target.description,
        )

    # ==========================================================
    # MANAGEMENT
    # ==========================================================

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()