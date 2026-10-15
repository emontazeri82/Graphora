from __future__ import annotations

from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from editor.graph_editor import GraphEditor


class GraphView:
    """
    Handles Graphora canvas view state.

    Responsibilities:
    - Zoom
    - Pan offsets
    - Mouse coordinate conversion
    - Reset view
    - Fit graph to visible canvas
    - Apply Dear PyGui canvas transforms
    """

    def __init__(
        self,
        editor: GraphEditor,
    ) -> None:
        self.editor = editor

        self.zoom: float = 1.0

        self.pan_x: float = 0.0
        self.pan_y: float = 0.0

        self.min_zoom: float = 0.25
        self.max_zoom: float = 3.0
        self.zoom_step: float = 0.1

    # ==========================================================
    # COORDINATES
    # ==========================================================

    def get_canvas_mouse_position(
        self,
    ) -> tuple[float, float]:
        mouse_x, mouse_y = dpg.get_mouse_pos(
            local=False
        )

        canvas_x, canvas_y = (
            dpg.get_item_rect_min(
                "graph_canvas"
            )
        )

        screen_x = float(
            mouse_x - canvas_x
        )

        screen_y = float(
            mouse_y - canvas_y
        )

        graph_x = (
            screen_x - self.pan_x
        ) / self.zoom

        graph_y = (
            screen_y - self.pan_y
        ) / self.zoom

        return (
            graph_x,
            graph_y,
        )

    # ==========================================================
    # TRANSFORM
    # ==========================================================

    def apply_view_transform(
        self,
    ) -> None:
        scale_matrix = dpg.create_scale_matrix(
            [
                self.zoom,
                self.zoom,
            ]
        )

        translation_matrix = (
            dpg.create_translation_matrix(
                [
                    self.pan_x,
                    self.pan_y,
                ]
            )
        )

        transform = (
            translation_matrix
            * scale_matrix
        )

        dpg.apply_transform(
            "canvas_layer",
            transform,
        )

        zoom_text = (
            f"{self.zoom * 100:.0f}%"
        )

        if dpg.does_item_exist(
            "zoom_display"
        ):
            dpg.configure_item(
                "zoom_display",
                label=zoom_text,
            )

        if dpg.does_item_exist(
            "status_zoom"
        ):
            dpg.set_value(
                "status_zoom",
                zoom_text,
            )

    # ==========================================================
    # ZOOM
    # ==========================================================

    def zoom_in(
        self,
    ) -> None:
        self.zoom = min(
            self.max_zoom,
            self.zoom + self.zoom_step,
        )

        self.editor.redraw_node_labels()
        self.apply_view_transform()

    def zoom_out(
        self,
    ) -> None:
        self.zoom = max(
            self.min_zoom,
            self.zoom - self.zoom_step,
        )

        self.editor.redraw_node_labels()
        self.apply_view_transform()

    # ==========================================================
    # RESET
    # ==========================================================

    def reset_view(
        self,
    ) -> None:
        self.zoom = 1.0

        self.pan_x = 0.0
        self.pan_y = 0.0

        self.editor.redraw_node_labels()
        self.apply_view_transform()

        if dpg.does_item_exist(
            "status_text"
        ):
            dpg.set_value(
                "status_text",
                "View reset to 100%",
            )

    # ==========================================================
    # FIT
    # ==========================================================

    def fit_view(
        self,
    ) -> None:
        nodes = self.editor.graph.nodes

        if not nodes:
            self.reset_view()
            return

        canvas_width, canvas_height = (
            dpg.get_item_rect_size(
                "canvas_container"
            )
        )

        if canvas_width <= 0:
            return

        if canvas_height <= 0:
            return

        padding = 80.0

        min_x = min(
            node.x - node.size / 2.0
            for node in nodes
        )

        max_x = max(
            node.x + node.size / 2.0
            for node in nodes
        )

        min_y = min(
            node.y - node.size / 2.0
            for node in nodes
        )

        max_y = max(
            node.y + node.size / 2.0
            for node in nodes
        )

        graph_width = max(
            1.0,
            max_x - min_x,
        )

        graph_height = max(
            1.0,
            max_y - min_y,
        )

        available_width = max(
            1.0,
            canvas_width - padding * 2.0,
        )

        available_height = max(
            1.0,
            canvas_height - padding * 2.0,
        )

        zoom_x = (
            available_width
            / graph_width
        )

        zoom_y = (
            available_height
            / graph_height
        )

        self.zoom = max(
            self.min_zoom,
            min(
                self.max_zoom,
                zoom_x,
                zoom_y,
            ),
        )

        graph_center_x = (
            min_x + max_x
        ) / 2.0

        graph_center_y = (
            min_y + max_y
        ) / 2.0

        canvas_center_x = (
            canvas_width / 2.0
        )

        canvas_center_y = (
            canvas_height / 2.0
        )

        self.pan_x = (
            canvas_center_x
            - graph_center_x * self.zoom
        )

        self.pan_y = (
            canvas_center_y
            - graph_center_y * self.zoom
        )

        self.editor.redraw_node_labels()
        self.apply_view_transform()

        if dpg.does_item_exist(
            "status_text"
        ):
            dpg.set_value(
                "status_text",
                "Graph fitted to view",
            )