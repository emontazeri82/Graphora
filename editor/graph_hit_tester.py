from __future__ import annotations

import math
from typing import TYPE_CHECKING

from model.edge import Edge
from model.node import Node

if TYPE_CHECKING:
    from editor.graph_editor import GraphEditor


class GraphHitTester:
    """
    Handles Graphora geometry and hit testing.

    Responsibilities:
    - Find nodes at a graph position.
    - Find edges at a graph position.
    - Test whether a point is inside a node.
    - Test whether a point is near an edge.
    - Calculate edge endpoints at node boundaries.
    """

    def __init__(
        self,
        editor: GraphEditor,
    ) -> None:
        self.editor = editor

    # ==========================================================
    # NODE HIT TESTING
    # ==========================================================

    def find_node_at(
        self,
        x: float,
        y: float,
    ) -> Node | None:
        for node in reversed(
            self.editor.graph.nodes
        ):
            if self.point_inside_node(
                node,
                x,
                y,
            ):
                return node

        return None

    @staticmethod
    def point_inside_node(
        node: Node,
        x: float,
        y: float,
    ) -> bool:
        dx = x - node.x
        dy = y - node.y

        if node.shape == "Circle":
            return (
                dx * dx + dy * dy
                <= node.radius * node.radius
            )

        if node.shape == "Square":
            half_size = node.size / 2.0

            return (
                abs(dx) <= half_size
                and abs(dy) <= half_size
            )

        if node.shape == "Rectangle":
            half_width = node.size / 2.0
            half_height = node.size / 3.0

            return (
                abs(dx) <= half_width
                and abs(dy) <= half_height
            )

        return False

    # ==========================================================
    # EDGE GEOMETRY
    # ==========================================================

    def get_edge_endpoints(
        self,
        edge: Edge,
    ) -> tuple[
        tuple[float, float],
        tuple[float, float],
    ]:
        source = edge.source
        target = edge.target

        dx = target.x - source.x
        dy = target.y - source.y

        distance = math.hypot(
            dx,
            dy,
        )

        if distance == 0:
            return (
                source.position,
                target.position,
            )

        unit_x = dx / distance
        unit_y = dy / distance

        source_radius = (
            self.get_node_connection_radius(
                source,
                unit_x,
                unit_y,
            )
        )

        target_radius = (
            self.get_node_connection_radius(
                target,
                -unit_x,
                -unit_y,
            )
        )

        start = (
            source.x
            + unit_x * source_radius,
            source.y
            + unit_y * source_radius,
        )

        end = (
            target.x
            - unit_x * target_radius,
            target.y
            - unit_y * target_radius,
        )

        return start, end

    @staticmethod
    def get_node_connection_radius(
        node: Node,
        unit_x: float,
        unit_y: float,
    ) -> float:
        if node.shape == "Circle":
            return node.radius

        if node.shape == "Square":
            half = node.size / 2.0

            divisor = max(
                abs(unit_x),
                abs(unit_y),
                0.0001,
            )

            return half / divisor

        if node.shape == "Rectangle":
            half_width = node.size / 2.0
            half_height = node.size / 3.0

            tx = (
                half_width / abs(unit_x)
                if abs(unit_x) > 0.0001
                else float("inf")
            )

            ty = (
                half_height / abs(unit_y)
                if abs(unit_y) > 0.0001
                else float("inf")
            )

            return min(
                tx,
                ty,
            )

        return node.radius

    # ==========================================================
    # EDGE HIT TESTING
    # ==========================================================

    def find_edge_at(
        self,
        x: float,
        y: float,
    ) -> Edge | None:
        for edge in reversed(
            self.editor.graph.edges
        ):
            if edge.is_self_loop:
                if self.point_near_self_loop(
                    edge,
                    x,
                    y,
                ):
                    return edge

            else:
                if self.point_near_edge(
                    edge,
                    x,
                    y,
                ):
                    return edge

        return None

    def point_near_edge(
        self,
        edge: Edge,
        x: float,
        y: float,
    ) -> bool:
        start, end = self.get_edge_endpoints(
            edge
        )

        distance = self.distance_to_segment(
            x,
            y,
            start[0],
            start[1],
            end[0],
            end[1],
        )

        tolerance = max(
            7.0,
            edge.thickness + 5.0,
        )

        return distance <= tolerance

    @staticmethod
    def point_near_self_loop(
        edge: Edge,
        x: float,
        y: float,
    ) -> bool:
        node = edge.source

        loop_radius = max(
            18.0,
            node.radius * 0.65,
        )

        center_x = node.x

        center_y = (
            node.y
            - node.radius
            - loop_radius
            + 5.0
        )

        distance = math.hypot(
            x - center_x,
            y - center_y,
        )

        tolerance = max(
            7.0,
            edge.thickness + 5.0,
        )

        return (
            abs(
                distance - loop_radius
            )
            <= tolerance
        )

    @staticmethod
    def distance_to_segment(
        px: float,
        py: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        dx = x2 - x1
        dy = y2 - y1

        length_squared = (
            dx * dx
            + dy * dy
        )

        if length_squared == 0:
            return math.hypot(
                px - x1,
                py - y1,
            )

        t = (
            (
                (px - x1) * dx
                + (py - y1) * dy
            )
            / length_squared
        )

        t = max(
            0.0,
            min(
                1.0,
                t,
            ),
        )

        closest_x = (
            x1 + t * dx
        )

        closest_y = (
            y1 + t * dy
        )

        return math.hypot(
            px - closest_x,
            py - closest_y,
        )