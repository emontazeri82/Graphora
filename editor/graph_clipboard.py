from __future__ import annotations

from dataclasses import dataclass

from model.edge import Edge
from model.edge_type import EdgeType
from model.node import Node


@dataclass(frozen=True)
class NodeClipboardData:
    """
    Immutable snapshot of one copied node.
    """

    original_id: int
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
    ) -> NodeClipboardData:
        return cls(
            original_id=node.node_id,
            name=node.name,
            x=node.x,
            y=node.y,
            size=node.size,
            shape=node.shape,
            color=node.color,
        )


@dataclass(frozen=True)
class EdgeClipboardData:
    """
    Immutable snapshot of one copied edge.

    source_id and target_id refer to the IDs of the
    original copied nodes.
    """

    original_id: int
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
    ) -> EdgeClipboardData:
        return cls(
            original_id=edge.edge_id,
            source_id=edge.source.node_id,
            target_id=edge.target.node_id,
            edge_type=edge.edge_type,
            name=edge.name,
            color=edge.color,
            thickness=edge.thickness,
        )


@dataclass
class PasteResult:
    """
    Result returned after a paste operation.
    """

    nodes: list[Node]
    edges: list[Edge]
    next_node_id: int
    next_edge_id: int


class GraphClipboard:
    """
    Internal clipboard for Graphora.

    Supports:
    - Copying one node
    - Copying multiple nodes
    - Copying edges whose endpoints are copied
    - Copying a self-loop with its node
    - Pasting independent copies
    - Repeated paste with increasing offset
    - Clearing clipboard data

    This is an application clipboard, not the operating
    system text clipboard.
    """

    DEFAULT_PASTE_OFFSET: float = 30.0

    def __init__(
        self,
        paste_offset: float = DEFAULT_PASTE_OFFSET,
    ) -> None:
        self._nodes: list[NodeClipboardData] = []
        self._edges: list[EdgeClipboardData] = []

        self._paste_offset: float = float(
            paste_offset
        )

        self._paste_count: int = 0

    # ==========================================================
    # STATE
    # ==========================================================

    @property
    def is_empty(self) -> bool:
        return not self._nodes

    @property
    def has_nodes(self) -> bool:
        return bool(self._nodes)

    @property
    def has_edges(self) -> bool:
        return bool(self._edges)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    @property
    def paste_count(self) -> int:
        return self._paste_count

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
        self._paste_count = 0

    # ==========================================================
    # COPY
    # ==========================================================

    def copy_node(
        self,
        node: Node,
        connected_edges: tuple[Edge, ...] = (),
    ) -> None:
        """
        Copy one node.

        Self-loops may be copied because both endpoints
        belong to the copied node.

        Edges connecting the node to nodes outside the
        clipboard are ignored.
        """
        self.copy(
            nodes=(node,),
            edges=connected_edges,
        )

    def copy(
        self,
        nodes: tuple[Node, ...] | list[Node],
        edges: tuple[Edge, ...] | list[Edge] = (),
    ) -> None:
        """
        Replace the current clipboard contents.

        Only edges whose source AND target are among the
        copied nodes are stored.
        """
        self.clear()

        unique_nodes: dict[int, Node] = {}

        for node in nodes:
            unique_nodes[node.node_id] = node

        if not unique_nodes:
            return

        copied_node_ids = set(
            unique_nodes.keys()
        )

        self._nodes = [
            NodeClipboardData.from_node(node)
            for node in unique_nodes.values()
        ]

        unique_edges: dict[int, Edge] = {}

        for edge in edges:
            if (
                edge.source.node_id
                in copied_node_ids
                and edge.target.node_id
                in copied_node_ids
            ):
                unique_edges[edge.edge_id] = edge

        self._edges = [
            EdgeClipboardData.from_edge(edge)
            for edge in unique_edges.values()
        ]

        self._paste_count = 0

    # ==========================================================
    # PASTE
    # ==========================================================

    def paste(
        self,
        next_node_id: int,
        next_edge_id: int,
    ) -> PasteResult:
        """
        Create new Node and Edge objects from clipboard data.

        This method does NOT add them to Graph automatically.
        GraphEditor will do that during integration.
        """
        if self.is_empty:
            return PasteResult(
                nodes=[],
                edges=[],
                next_node_id=next_node_id,
                next_edge_id=next_edge_id,
            )

        self._paste_count += 1

        offset = (
            self._paste_offset
            * self._paste_count
        )

        new_nodes: list[Node] = []
        new_edges: list[Edge] = []

        node_map: dict[int, Node] = {}

        current_node_id = next_node_id
        current_edge_id = next_edge_id

        # ------------------------------------------------------
        # Recreate nodes
        # ------------------------------------------------------

        for data in self._nodes:
            node = Node(
                node_id=current_node_id,
                name=data.name,
                x=data.x + offset,
                y=data.y + offset,
                size=data.size,
                shape=data.shape,
                color=data.color,
            )

            node_map[data.original_id] = node

            new_nodes.append(node)

            current_node_id += 1

        # ------------------------------------------------------
        # Recreate edges
        # ------------------------------------------------------

        for data in self._edges:
            source = node_map.get(
                data.source_id
            )

            target = node_map.get(
                data.target_id
            )

            if source is None or target is None:
                continue

            edge = Edge(
                edge_id=current_edge_id,
                source=source,
                target=target,
                edge_type=data.edge_type,
                name=data.name,
                color=data.color,
                thickness=data.thickness,
            )

            new_edges.append(edge)

            current_edge_id += 1

        return PasteResult(
            nodes=new_nodes,
            edges=new_edges,
            next_node_id=current_node_id,
            next_edge_id=current_edge_id,
        )

    # ==========================================================
    # INSPECTION
    # ==========================================================

    def copied_nodes(
        self,
    ) -> tuple[NodeClipboardData, ...]:
        return tuple(self._nodes)

    def copied_edges(
        self,
    ) -> tuple[EdgeClipboardData, ...]:
        return tuple(self._edges)