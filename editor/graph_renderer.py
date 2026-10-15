from __future__ import annotations

import math
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from model.edge import Edge
from model.node import Node

if TYPE_CHECKING:
    from editor.graph_editor import GraphEditor


class GraphRenderer:
    """
    Handles drawing Graphora nodes and edges.

    GraphRenderer is responsible only for visual rendering.
    GraphEditor remains responsible for editor state and
    graph operations.
    """

    DEFAULT_NODE_OUTLINE: tuple[int, int, int, int] = (
        180,
        200,
        255,
        255,
    )

    SELECTED_COLOR: tuple[int, int, int, int] = (
        255,
        220,
        100,
        255,
    )

    LABEL_COLOR: tuple[int, int, int, int] = (
        255,
        255,
        255,
        255,
    )

    def __init__(
        self,
        editor: GraphEditor,
    ) -> None:
        self.editor = editor

    # ==========================================================
    # NODE DRAWING
    # ==========================================================

    def draw_node(
        self,
        node: Node,
    ) -> None:
        self.delete_node_drawing(node)

        if self.editor.selected_node is node:
            outline_color = self.SELECTED_COLOR
            thickness = 4
        else:
            outline_color = self.DEFAULT_NODE_OUTLINE
            thickness = 2

        tag = self.node_tag(node)

        if node.shape == "Circle":
            dpg.draw_circle(
                center=(
                    node.x,
                    node.y,
                ),
                radius=node.radius,
                color=outline_color,
                fill=node.color,
                thickness=thickness,
                parent="canvas_layer",
                tag=tag,
            )

        elif node.shape == "Square":
            half_size = node.size / 2.0

            dpg.draw_rectangle(
                pmin=(
                    node.x - half_size,
                    node.y - half_size,
                ),
                pmax=(
                    node.x + half_size,
                    node.y + half_size,
                ),
                color=outline_color,
                fill=node.color,
                thickness=thickness,
                parent="canvas_layer",
                tag=tag,
            )

        elif node.shape == "Rectangle":
            half_width = node.size / 2.0
            half_height = node.size / 3.0

            dpg.draw_rectangle(
                pmin=(
                    node.x - half_width,
                    node.y - half_height,
                ),
                pmax=(
                    node.x + half_width,
                    node.y + half_height,
                ),
                color=outline_color,
                fill=node.color,
                thickness=thickness,
                parent="canvas_layer",
                tag=tag,
            )

        self.draw_node_label(node)

    def draw_node_label(
        self,
        node: Node,
    ) -> None:
        tag = self.node_label_tag(node)

        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        display_text, base_font_size = (
            self.get_fitted_node_label(node)
        )

        font_size = max(
            6.0,
            base_font_size * self.editor.zoom,
        )

        text_width, text_height = self.get_text_size(
            display_text
        )

        size_ratio = base_font_size / 14.0

        text_width *= size_ratio
        text_height *= size_ratio

        dpg.draw_text(
            pos=(
                node.x - text_width / 2.0,
                node.y - text_height / 2.0,
            ),
            text=display_text,
            color=self.LABEL_COLOR,
            size=font_size,
            parent="canvas_layer",
            tag=tag,
        )

    def get_fitted_node_label(
        self,
        node: Node,
    ) -> tuple[str, float]:
        text = node.name

        normal_font_size = 14.0
        min_font_size = 9.0

        max_width = self.get_node_label_max_width(node)

        text_width, _ = self.get_text_size(text)

        if text_width <= max_width:
            return text, normal_font_size

        font_size = (
            normal_font_size
            * max_width
            / max(text_width, 1.0)
        )

        if font_size >= min_font_size:
            return text, font_size

        font_size = min_font_size

        available_width = (
            max_width
            * normal_font_size
            / font_size
        )

        ellipsis = "..."
        fitted_text = text

        while fitted_text:
            candidate = fitted_text + ellipsis

            candidate_width, _ = self.get_text_size(
                candidate
            )

            if candidate_width <= available_width:
                return candidate, font_size

            fitted_text = fitted_text[:-1]

        return ellipsis, font_size

    @staticmethod
    def get_node_label_max_width(
        node: Node,
    ) -> float:
        padding = 10.0

        if node.shape == "Circle":
            return max(
                10.0,
                node.size * 0.72,
            )

        if node.shape == "Square":
            return max(
                10.0,
                node.size - padding * 2.0,
            )

        if node.shape == "Rectangle":
            return max(
                10.0,
                node.size - padding * 2.0,
            )

        return max(
            10.0,
            node.size - padding * 2.0,
        )

    def delete_node_drawing(
        self,
        node: Node,
    ) -> None:
        tags = (
            self.node_tag(node),
            self.node_label_tag(node),
        )

        for tag in tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)

    # ==========================================================
    # EDGE DRAWING
    # ==========================================================

    def draw_edge(
        self,
        edge: Edge,
    ) -> None:
        self.delete_edge_drawing(edge)

        if self.editor.selected_edge is edge:
            color = self.SELECTED_COLOR
            thickness = edge.thickness + 2.0
        else:
            color = edge.color
            thickness = edge.thickness

        if edge.is_self_loop:
            self.draw_self_loop(
                edge,
                color,
                thickness,
            )
        else:
            self.draw_regular_edge(
                edge,
                color,
                thickness,
            )

    def draw_regular_edge(
        self,
        edge: Edge,
        color: tuple[int, int, int, int],
        thickness: float,
    ) -> None:
        start, end = (
            self.editor.get_edge_endpoints(edge)
        )

        dpg.draw_line(
            p1=start,
            p2=end,
            color=color,
            thickness=thickness,
            parent="canvas_layer",
            tag=self.edge_line_tag(edge),
        )

        if edge.is_directed:
            self.draw_arrowhead(
                edge,
                start,
                end,
                color,
            )

    def draw_arrowhead(
        self,
        edge: Edge,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int, int],
    ) -> None:
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        angle = math.atan2(
            dy,
            dx,
        )

        arrow_length = 14.0
        arrow_angle = math.radians(28.0)

        left = (
            end[0]
            - arrow_length
            * math.cos(
                angle - arrow_angle
            ),
            end[1]
            - arrow_length
            * math.sin(
                angle - arrow_angle
            ),
        )

        right = (
            end[0]
            - arrow_length
            * math.cos(
                angle + arrow_angle
            ),
            end[1]
            - arrow_length
            * math.sin(
                angle + arrow_angle
            ),
        )

        dpg.draw_triangle(
            p1=end,
            p2=left,
            p3=right,
            color=color,
            fill=color,
            parent="canvas_layer",
            tag=self.edge_arrow_tag(edge),
        )

    def draw_self_loop(
        self,
        edge: Edge,
        color: tuple[int, int, int, int],
        thickness: float,
    ) -> None:
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

        dpg.draw_circle(
            center=(
                center_x,
                center_y,
            ),
            radius=loop_radius,
            color=color,
            fill=(0, 0, 0, 0),
            thickness=thickness,
            parent="canvas_layer",
            tag=self.edge_line_tag(edge),
        )

        if edge.is_directed:
            arrow_x = center_x + loop_radius
            arrow_y = center_y

            dpg.draw_triangle(
                p1=(
                    arrow_x,
                    arrow_y,
                ),
                p2=(
                    arrow_x - 12,
                    arrow_y - 6,
                ),
                p3=(
                    arrow_x - 12,
                    arrow_y + 6,
                ),
                color=color,
                fill=color,
                parent="canvas_layer",
                tag=self.edge_arrow_tag(edge),
            )

    def delete_edge_drawing(
        self,
        edge: Edge,
    ) -> None:
        tags = (
            self.edge_line_tag(edge),
            self.edge_arrow_tag(edge),
        )

        for tag in tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)

    # ==========================================================
    # REDRAWING
    # ==========================================================

    def redraw_edges_for_node(
        self,
        node: Node,
    ) -> None:
        for edge in self.editor.graph.edges_for_node(
            node
        ):
            self.draw_edge(edge)

    def redraw_node_on_top(
        self,
        node: Node,
    ) -> None:
        self.draw_node(node)

    def redraw_all(self) -> None:
        for edge in self.editor.graph.edges:
            self.draw_edge(edge)

        for node in self.editor.graph.nodes:
            self.draw_node(node)

    def redraw_node_labels(self) -> None:
        for node in self.editor.graph.nodes:
            self.draw_node_label(node)

    # ==========================================================
    # TAGS
    # ==========================================================

    @staticmethod
    def node_tag(
        node: Node,
    ) -> str:
        return f"node_{node.node_id}"

    @staticmethod
    def node_label_tag(
        node: Node,
    ) -> str:
        return f"node_label_{node.node_id}"

    @staticmethod
    def edge_line_tag(
        edge: Edge,
    ) -> str:
        return f"edge_{edge.edge_id}"

    @staticmethod
    def edge_arrow_tag(
        edge: Edge,
    ) -> str:
        return f"edge_arrow_{edge.edge_id}"

    # ==========================================================
    # TEXT
    # ==========================================================

    @staticmethod
    def get_text_size(
        text: str,
    ) -> tuple[float, float]:
        size = dpg.get_text_size(text)

        if size is None:
            return (
                float(len(text) * 7),
                14.0,
            )

        return (
            float(size[0]),
            float(size[1]),
        )