class Node:
    def __init__(self, node_id: int, name: str) -> None:
        self._node_id: int = node_id
        self._name: str = name

    @property
    def node_id(self) -> int:
        return self._node_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        new_name = new_name.strip()

        if new_name:
            self._name = new_name

    def __str__(self) -> str:
        return f"Node(id={self._node_id}, name={self._name})"

    def __repr__(self) -> str:
        return self.__str__()