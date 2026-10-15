from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from model.edge import Edge
from model.edge_type import EdgeType
from model.graph import Graph
from model.node import Node


class GraphSerializationError(Exception):
    """
    Raised when a Graphora graph cannot be saved or loaded.
    """

    pass


class GraphSerializer:
    """
    Saves and loads Graphora graphs.

    GraphSerializer only handles graph data and files.
    It does not contain any Dear PyGui UI logic.
    """

    FILE_TYPE: str = "graphora"
    FILE_VERSION: int = 1
    FILE_EXTENSION: str = ".json"

    # ========================================================
    # SAVE
    # ========================================================

    @classmethod
    def save(
        cls,
        graph: Graph,
        file_path: str | Path,
    ) -> Path:
        """
        Save a Graphora graph to a JSON file.

        Returns the final Path used for the saved file.
        """
        path = cls.normalize_save_path(file_path)

        data = cls.graph_to_dict(graph)

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except OSError as error:
            raise GraphSerializationError(
                f"Could not save graph to '{path}'."
            ) from error

        return path

    # ========================================================
    # LOAD
    # ========================================================

    @classmethod
    def load(
        cls,
        file_path: str | Path,
    ) -> Graph:
        """
        Load a Graphora graph from a JSON file.
        """
        path = Path(file_path)

        if not path.exists():
            raise GraphSerializationError(
                f"Graph file does not exist: '{path}'."
            )

        if not path.is_file():
            raise GraphSerializationError(
                f"Graph path is not a file: '{path}'."
            )

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data: Any = json.load(file)

        except json.JSONDecodeError as error:
            raise GraphSerializationError(
                f"Invalid Graphora JSON file: '{path}'."
            ) from error

        except OSError as error:
            raise GraphSerializationError(
                f"Could not open graph file: '{path}'."
            ) from error

        if not isinstance(data, dict):
            raise GraphSerializationError(
                "Graphora file must contain a JSON object."
            )

        cls.validate_file(data)

        return cls.graph_from_dict(data)

    # ========================================================
    # GRAPH -> DICTIONARY
    # ========================================================

    @classmethod
    def graph_to_dict(
        cls,
        graph: Graph,
    ) -> dict[str, Any]:
        """
        Convert a Graph into JSON-compatible data.
        """
        nodes: list[dict[str, Any]] = [
            cls.node_to_dict(node)
            for node in graph.nodes
        ]

        edges: list[dict[str, Any]] = [
            cls.edge_to_dict(edge)
            for edge in graph.edges
        ]

        return {
            "file_type": cls.FILE_TYPE,
            "version": cls.FILE_VERSION,
            "graph": {
                "nodes": nodes,
                "edges": edges,
            },
        }

    # ========================================================
    # DICTIONARY -> GRAPH
    # ========================================================

    @classmethod
    def graph_from_dict(
        cls,
        data: dict[str, Any],
    ) -> Graph:
        """
        Reconstruct a complete Graph from serialized data.
        """
        graph_data = data.get("graph")

        if not isinstance(graph_data, dict):
            raise GraphSerializationError(
                "Missing or invalid 'graph' section."
            )

        nodes_data = graph_data.get("nodes")
        edges_data = graph_data.get("edges")

        if not isinstance(nodes_data, list):
            raise GraphSerializationError(
                "'nodes' must be a list."
            )

        if not isinstance(edges_data, list):
            raise GraphSerializationError(
                "'edges' must be a list."
            )

        graph = Graph()

        # Nodes must be restored first because edges
        # reference nodes by their IDs.
        for node_data in nodes_data:
            node = cls.node_from_dict(node_data)

            if not graph.add_node(node):
                raise GraphSerializationError(
                    f"Could not restore node "
                    f"{node.node_id}."
                )

        # Restore edges after every node exists.
        for edge_data in edges_data:
            edge = cls.edge_from_dict(
                edge_data,
                graph,
            )

            if not graph.add_edge(edge):
                raise GraphSerializationError(
                    f"Could not restore edge "
                    f"{edge.edge_id}."
                )

        return graph

    # ========================================================
    # NODE -> DICTIONARY
    # ========================================================

    @staticmethod
    def node_to_dict(
        node: Node,
    ) -> dict[str, Any]:
        """
        Convert one Node into JSON-compatible data.
        """
        return {
            "id": node.node_id,
            "name": node.name,
            "x": node.x,
            "y": node.y,
            "size": node.size,
            "shape": node.shape,
            "color": list(node.color),
        }

    # ========================================================
    # DICTIONARY -> NODE
    # ========================================================

    @classmethod
    def node_from_dict(
        cls,
        data: Any,
    ) -> Node:
        """
        Reconstruct one Node from serialized data.
        """
        if not isinstance(data, dict):
            raise GraphSerializationError(
                "Invalid node entry."
            )

        node_id = cls.require_int(
            data,
            "id",
        )

        name = cls.require_string(
            data,
            "name",
        )

        x = cls.require_number(
            data,
            "x",
        )

        y = cls.require_number(
            data,
            "y",
        )

        size = cls.require_number(
            data,
            "size",
        )

        shape = cls.require_string(
            data,
            "shape",
        )

        color = cls.require_color(
            data,
            "color",
        )

        try:
            return Node(
                node_id=node_id,
                name=name,
                x=x,
                y=y,
                size=size,
                shape=shape,
                color=color,
            )

        except (TypeError, ValueError) as error:
            raise GraphSerializationError(
                f"Could not create node {node_id}."
            ) from error

    # ========================================================
    # EDGE -> DICTIONARY
    # ========================================================

    @staticmethod
    def edge_to_dict(
        edge: Edge,
    ) -> dict[str, Any]:
        """
        Convert one Edge into JSON-compatible data.
        """
        return {
            "id": edge.edge_id,
            "source": edge.source.node_id,
            "target": edge.target.node_id,
            "edge_type": edge.edge_type.value,
            "name": edge.name,
            "color": list(edge.color),
            "thickness": edge.thickness,
        }

    # ========================================================
    # DICTIONARY -> EDGE
    # ========================================================

    @classmethod
    def edge_from_dict(
        cls,
        data: Any,
        graph: Graph,
    ) -> Edge:
        """
        Reconstruct one Edge from serialized data.
        """
        if not isinstance(data, dict):
            raise GraphSerializationError(
                "Invalid edge entry."
            )

        edge_id = cls.require_int(
            data,
            "id",
        )

        source_id = cls.require_int(
            data,
            "source",
        )

        target_id = cls.require_int(
            data,
            "target",
        )

        edge_type_text = cls.require_string(
            data,
            "edge_type",
        )

        name = cls.require_string(
            data,
            "name",
        )

        color = cls.require_color(
            data,
            "color",
        )

        thickness = cls.require_number(
            data,
            "thickness",
        )

        source = graph.find_node(source_id)

        if source is None:
            raise GraphSerializationError(
                f"Edge {edge_id} references missing "
                f"source node {source_id}."
            )

        target = graph.find_node(target_id)

        if target is None:
            raise GraphSerializationError(
                f"Edge {edge_id} references missing "
                f"target node {target_id}."
            )

        try:
            edge_type = EdgeType(
                edge_type_text
            )

        except ValueError as error:
            raise GraphSerializationError(
                f"Invalid edge type "
                f"'{edge_type_text}' for edge "
                f"{edge_id}."
            ) from error

        try:
            return Edge(
                edge_id=edge_id,
                source=source,
                target=target,
                edge_type=edge_type,
                name=name,
                color=color,
                thickness=thickness,
            )

        except (TypeError, ValueError) as error:
            raise GraphSerializationError(
                f"Could not create edge {edge_id}."
            ) from error

    # ========================================================
    # FILE VALIDATION
    # ========================================================

    @classmethod
    def validate_file(
        cls,
        data: dict[str, Any],
    ) -> None:
        """
        Validate Graphora file metadata and basic structure.
        """
        file_type = data.get("file_type")

        if file_type != cls.FILE_TYPE:
            raise GraphSerializationError(
                "This file is not a Graphora graph file."
            )

        version = data.get("version")

        if (
            isinstance(version, bool)
            or not isinstance(version, int)
        ):
            raise GraphSerializationError(
                "Graphora file version is missing "
                "or invalid."
            )

        if version < 1:
            raise GraphSerializationError(
                f"Unsupported Graphora file version: "
                f"{version}."
            )

        if version > cls.FILE_VERSION:
            raise GraphSerializationError(
                "This graph was created by a newer "
                "version of Graphora."
            )

        graph_data = data.get("graph")

        if not isinstance(graph_data, dict):
            raise GraphSerializationError(
                "Graphora file is missing graph data."
            )

        nodes = graph_data.get("nodes")

        if not isinstance(nodes, list):
            raise GraphSerializationError(
                "Graphora file contains invalid "
                "node data."
            )

        edges = graph_data.get("edges")

        if not isinstance(edges, list):
            raise GraphSerializationError(
                "Graphora file contains invalid "
                "edge data."
            )

    # ========================================================
    # VALUE VALIDATION
    # ========================================================

    @staticmethod
    def require_string(
        data: dict[str, Any],
        key: str,
    ) -> str:
        """
        Read and validate a string value.
        """
        value = data.get(key)

        if not isinstance(value, str):
            raise GraphSerializationError(
                f"'{key}' must be a string."
            )

        return value

    @staticmethod
    def require_int(
        data: dict[str, Any],
        key: str,
    ) -> int:
        """
        Read and validate an integer value.
        """
        value = data.get(key)

        # bool is a subclass of int in Python,
        # so explicitly reject bool.
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
        ):
            raise GraphSerializationError(
                f"'{key}' must be an integer."
            )

        return value

    @staticmethod
    def require_number(
        data: dict[str, Any],
        key: str,
    ) -> float:
        """
        Read and validate a numeric value.
        """
        value = data.get(key)

        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                (int, float),
            )
        ):
            raise GraphSerializationError(
                f"'{key}' must be a number."
            )

        return float(value)

    @staticmethod
    def require_color(
        data: dict[str, Any],
        key: str,
    ) -> tuple[int, int, int, int]:
        """
        Read and validate an RGBA color.
        """
        value = data.get(key)

        if not isinstance(value, list):
            raise GraphSerializationError(
                f"'{key}' must be a color list."
            )

        if len(value) != 4:
            raise GraphSerializationError(
                f"'{key}' must contain exactly "
                f"4 RGBA values."
            )

        channels: list[int] = []

        for channel in value:
            if (
                isinstance(channel, bool)
                or not isinstance(channel, int)
            ):
                raise GraphSerializationError(
                    f"'{key}' contains an invalid "
                    f"color value."
                )

            if not 0 <= channel <= 255:
                raise GraphSerializationError(
                    f"'{key}' color values must be "
                    f"between 0 and 255."
                )

            channels.append(channel)

        return (
            channels[0],
            channels[1],
            channels[2],
            channels[3],
        )

    # ========================================================
    # PATH
    # ========================================================

    @classmethod
    def normalize_save_path(
        cls,
        file_path: str | Path,
    ) -> Path:
        """
        Normalize a path before saving.

        If the user does not provide an extension,
        '.json' is automatically added.
        """
        path = Path(file_path).expanduser()

        if not path.name:
            raise GraphSerializationError(
                "A file name is required."
            )

        if path.suffix == "":
            path = path.with_suffix(
                cls.FILE_EXTENSION
            )

        return path