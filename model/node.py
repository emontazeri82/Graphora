class Node:
    def __init__(
        self,
        node_id: int,
        name: str,
        x: float = 0.0,
        y: float = 0.0,
        size: float = 50.0,
        shape: str = "Circle",
        color: tuple[int, int, int, int] = (70, 110, 220, 255),
    ) -> None:
        self._node_id: int = node_id
        self._name: str = name

        self._x: float = x
        self._y: float = y

        self._size: float = size
        self._shape: str = shape

        self._color: tuple[int, int, int, int] = color

    @property
    def node_id(self) -> int:
        return self._node_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(
        self,
        new_name: str,
    ) -> None:
        new_name = new_name.strip()

        if new_name:
            self._name = new_name

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(
        self,
        value: float,
    ) -> None:
        self._x = float(value)

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(
        self,
        value: float,
    ) -> None:
        self._y = float(value)

    @property
    def position(
        self,
    ) -> tuple[float, float]:
        return self._x, self._y

    def set_position(
        self,
        x: float,
        y: float,
    ) -> None:
        self._x = float(x)
        self._y = float(y)

    @property
    def size(self) -> float:
        return self._size

    @size.setter
    def size(
        self,
        value: float,
    ) -> None:
        if value >= 20:
            self._size = float(value)

    @property
    def radius(self) -> float:
        return self._size / 2.0

    @property
    def shape(self) -> str:
        return self._shape

    @shape.setter
    def shape(
        self,
        value: str,
    ) -> None:
        if value in {
            "Circle",
            "Rectangle",
            "Square",
        }:
            self._shape = value

    @property
    def color(
        self,
    ) -> tuple[int, int, int, int]:
        return self._color

    @color.setter
    def color(
        self,
        value: tuple[int, int, int, int],
    ) -> None:
        self._color = value

    def __str__(self) -> str:
        return (
            f"Node("
            f"id={self._node_id}, "
            f"name={self._name}, "
            f"x={self._x}, "
            f"y={self._y}"
            f")"
        )

    def __repr__(self) -> str:
        return self.__str__()