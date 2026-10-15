from model.edge_type import EdgeType
from model.node import Node


class Edge:
    def __init__(
        self,
        edge_id: int,
        source: Node,
        target: Node,
        edge_type: EdgeType,
        name: str = "",
        color: tuple[int, int, int, int] = (180, 190, 220, 255),
        thickness: float = 2.0,
    ) -> None:
        self._edge_id: int = edge_id
        self._source: Node = source
        self._target: Node = target
        self._edge_type: EdgeType = edge_type

        if name.strip():
            self._name: str = name.strip()
        else:
            self._name = f"Edge {edge_id}"

        self._color: tuple[int, int, int, int] = color
        self._thickness: float = thickness

    @property
    def edge_id(self) -> int:
        return self._edge_id

    @property
    def source(self) -> Node:
        return self._source

    @property
    def target(self) -> Node:
        return self._target

    @property
    def edge_type(self) -> EdgeType:
        return self._edge_type

    @edge_type.setter
    def edge_type(
        self,
        value: EdgeType,
    ) -> None:
        self._edge_type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        value = value.strip()

        if value:
            self._name = value

    @property
    def color(self) -> tuple[int, int, int, int]:
        return self._color

    @color.setter
    def color(
        self,
        value: tuple[int, int, int, int],
    ) -> None:
        self._color = value

    @property
    def thickness(self) -> float:
        return self._thickness

    @thickness.setter
    def thickness(
        self,
        value: float,
    ) -> None:
        if value >= 1.0:
            self._thickness = float(value)

    @property
    def is_directed(self) -> bool:
        return self._edge_type == EdgeType.DIRECTED

    @property
    def is_undirected(self) -> bool:
        return self._edge_type == EdgeType.UNDIRECTED

    @property
    def is_self_loop(self) -> bool:
        return self._source is self._target

    def touches(
        self,
        node: Node,
    ) -> bool:
        return (
            self._source is node
            or self._target is node
        )

    def __str__(self) -> str:
        return (
            f"Edge("
            f"id={self._edge_id}, "
            f"name={self._name}, "
            f"source={self._source.node_id}, "
            f"target={self._target.node_id}, "
            f"type={self._edge_type.value}"
            f")"
        )

    def __repr__(self) -> str:
        return self.__str__()