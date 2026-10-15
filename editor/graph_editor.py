import math

import dearpygui.dearpygui as dpg

from model.edge import Edge
from model.edge_type import EdgeType
from model.graph import Graph
from model.node import Node


class GraphEditor:
    DEFAULT_NODE_COLOR: tuple[int, int, int, int] = (
        70,
        110,
        220,
        255,
    )

    DEFAULT_NODE_OUTLINE: tuple[int, int, int, int] = (
        180,
        200,
        255,
        255,
    )

    DEFAULT_EDGE_COLOR: tuple[int, int, int, int] = (
        180,
        190,
        220,
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

    def __init__(self) -> None:
        self.graph: Graph = Graph()

        self.current_mode: str = "Select"

        self.next_node_id: int = 1
        self.next_edge_id: int = 1

        self.selected_node: Node | None = None
        self.selected_edge: Edge | None = None

        self.pending_edge_source: Node | None = None

        self.dragging_node: Node | None = None

        self.drag_offset_x: float = 0.0
        self.drag_offset_y: float = 0.0

        # Canvas view
        self.zoom: float = 1.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0

        self.min_zoom: float = 0.25
        self.max_zoom: float = 3.0
        self.zoom_step: float = 0.1

    # ==========================================================
    # MODE
    # ==========================================================

    def change_mode(
        self,
        sender: int | str,
        app_data: object,
        user_data: str,
    ) -> None:
        self.current_mode = user_data

        self.pending_edge_source = None
        self.dragging_node = None

        dpg.set_value(
            "current_mode",
            self.current_mode,
        )

        dpg.set_value(
            "status_mode",
            self.current_mode,
        )

        if self.current_mode == "Directed Edge":
            message = (
                "Directed Edge mode: "
                "click the source node"
            )

        elif self.current_mode == "Undirected Edge":
            message = (
                "Undirected Edge mode: "
                "click the first node"
            )

        elif self.current_mode == "Node":
            message = (
                "Node mode: click the canvas "
                "to create a node"
            )

        else:
            message = (
                "Select mode"
            )

        dpg.set_value(
            "status_text",
            message,
        )

    # ==========================================================
    # COORDINATES
    # ==========================================================

    def get_canvas_mouse_position(
    self,
    ) -> tuple[float, float]:
        mouse_x, mouse_y = dpg.get_mouse_pos(
            local=False
        )

        canvas_x, canvas_y = dpg.get_item_rect_min(
            "graph_canvas"
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
    # CANVAS CLICK
    # ==========================================================

    def handle_canvas_click(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        if not dpg.is_item_hovered(
            "graph_canvas"
        ):
            return

        x, y = self.get_canvas_mouse_position()

        if self.current_mode == "Node":
            self.create_node_at(
                x,
                y,
            )
            return

        if self.current_mode == "Directed Edge":
            self.handle_edge_mode_click(
                x,
                y,
                EdgeType.DIRECTED,
            )
            return

        if self.current_mode == "Undirected Edge":
            self.handle_edge_mode_click(
                x,
                y,
                EdgeType.UNDIRECTED,
            )
            return

        if self.current_mode == "Select":
            self.handle_select_click(
                x,
                y,
            )

    # ==========================================================
    # SELECT CLICK
    # ==========================================================

    def handle_select_click(
        self,
        x: float,
        y: float,
    ) -> None:
        node = self.find_node_at(
            x,
            y,
        )

        if node is not None:
            self.select_node(node)

            self.dragging_node = node

            self.drag_offset_x = (
                x - node.x
            )

            self.drag_offset_y = (
                y - node.y
            )

            return

        edge = self.find_edge_at(
            x,
            y,
        )

        if edge is not None:
            self.select_edge(edge)
            return

        self.clear_selection()

    # ==========================================================
    # NODE CREATION
    # ==========================================================

    def create_node_at(
        self,
        x: float,
        y: float,
    ) -> None:
        node = Node(
            node_id=self.next_node_id,
            name=f"Node {self.next_node_id}",
            x=x,
            y=y,
            size=50.0,
            shape="Circle",
            color=self.DEFAULT_NODE_COLOR,
        )

        added = self.graph.add_node(node)

        if not added:
            return

        self.next_node_id += 1

        self.draw_node(node)

        self.update_graph_counters()

        dpg.set_value(
            "status_text",
            f"Created {node.name}",
        )

    # ==========================================================
    # NODE DRAWING
    # ==========================================================

    def draw_node(
        self,
        node: Node,
    ) -> None:
        self.delete_node_drawing(node)

        if self.selected_node is node:
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

        text_width, text_height = (
            self.get_text_size(node.name)
        )

        dpg.draw_text(
            pos=(
                node.x - text_width / 2.0,
                node.y - text_height / 2.0,
            ),
            text=node.name,
            color=self.LABEL_COLOR,
            size=14,
            parent="canvas_layer",
            tag=tag,
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

    # ==========================================================
    # NODE HIT TESTING
    # ==========================================================

    def find_node_at(
        self,
        x: float,
        y: float,
    ) -> Node | None:
        for node in reversed(
            self.graph.nodes
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
    # NODE SELECTION
    # ==========================================================

    def select_node(
        self,
        node: Node,
    ) -> None:
        previous_node = self.selected_node
        previous_edge = self.selected_edge

        self.selected_edge = None

        if previous_edge is not None:
            self.draw_edge(previous_edge)

        if (
            previous_node is not None
            and previous_node is not node
        ):
            self.selected_node = None
            self.draw_node(previous_node)

        self.selected_node = node

        self.draw_node(node)

        self.update_node_properties_panel()

        dpg.set_value(
            "status_text",
            f"Selected {node.name}",
        )

    # ==========================================================
    # DRAGGING
    # ==========================================================

    def handle_mouse_drag(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        if self.current_mode != "Select":
            return

        node = self.dragging_node

        if node is None:
            return

        x, y = self.get_canvas_mouse_position()

        node.x = (
            x - self.drag_offset_x
        )

        node.y = (
            y - self.drag_offset_y
        )

        self.redraw_edges_for_node(node)

        self.draw_node(node)

        self.update_node_properties_panel()

        dpg.set_value(
            "status_text",
            (
                f"Moving {node.name}: "
                f"({int(node.x)}, {int(node.y)})"
            ),
        )

    def handle_mouse_release(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        if self.dragging_node is None:
            return

        node = self.dragging_node

        self.dragging_node = None

        dpg.set_value(
            "status_text",
            (
                f"Moved {node.name} to "
                f"({int(node.x)}, {int(node.y)})"
            ),
        )

    # ==========================================================
    # EDGE CREATION
    # ==========================================================

    def handle_edge_mode_click(
        self,
        x: float,
        y: float,
        edge_type: EdgeType,
    ) -> None:
        node = self.find_node_at(
            x,
            y,
        )

        if node is None:
            self.pending_edge_source = None

            dpg.set_value(
                "status_text",
                "Edge cancelled",
            )

            return

        if self.pending_edge_source is None:
            self.pending_edge_source = node

            dpg.set_value(
                "status_text",
                (
                    f"Source: {node.name}. "
                    f"Click target node."
                ),
            )

            return

        source = self.pending_edge_source
        target = node

        self.pending_edge_source = None

        self.create_edge(
            source,
            target,
            edge_type,
        )

    def create_edge(
        self,
        source: Node,
        target: Node,
        edge_type: EdgeType,
    ) -> None:
        edge = Edge(
            edge_id=self.next_edge_id,
            source=source,
            target=target,
            edge_type=edge_type,
            color=self.DEFAULT_EDGE_COLOR,
            thickness=2.0,
        )

        added = self.graph.add_edge(edge)

        if not added:
            return

        self.next_edge_id += 1

        self.draw_edge(edge)

        self.redraw_node_on_top(source)

        if target is not source:
            self.redraw_node_on_top(target)

        self.update_graph_counters()

        arrow = (
            "->"
            if edge_type == EdgeType.DIRECTED
            else "--"
        )

        dpg.set_value(
            "status_text",
            (
                f"Created {source.name} "
                f"{arrow} {target.name}"
            ),
        )

    # ==========================================================
    # EDGE DRAWING
    # ==========================================================

    def draw_edge(
        self,
        edge: Edge,
    ) -> None:
        self.delete_edge_drawing(edge)

        if self.selected_edge is edge:
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
        start, end = self.get_edge_endpoints(
            edge
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
            arrow_x = (
                center_x + loop_radius
            )

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
            self.graph.edges
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

        distance = (
            self.distance_to_segment(
                x,
                y,
                start[0],
                start[1],
                end[0],
                end[1],
            )
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

    # ==========================================================
    # EDGE SELECTION
    # ==========================================================

    def select_edge(
        self,
        edge: Edge,
    ) -> None:
        previous_node = self.selected_node
        previous_edge = self.selected_edge

        self.selected_node = None

        if previous_node is not None:
            self.draw_node(previous_node)

        if (
            previous_edge is not None
            and previous_edge is not edge
        ):
            self.selected_edge = None
            self.draw_edge(previous_edge)

        self.selected_edge = edge

        self.draw_edge(edge)

        self.update_edge_properties_panel()

        dpg.set_value(
            "status_text",
            f"Selected {edge.name}",
        )

    # ==========================================================
    # EDGE REDRAWING
    # ==========================================================

    def redraw_edges_for_node(
        self,
        node: Node,
    ) -> None:
        for edge in self.graph.edges_for_node(
            node
        ):
            self.draw_edge(edge)

    def redraw_node_on_top(
        self,
        node: Node,
    ) -> None:
        self.draw_node(node)

    def redraw_all(
        self,
    ) -> None:
        for edge in self.graph.edges:
            self.draw_edge(edge)

        for node in self.graph.nodes:
            self.draw_node(node)

    # ==========================================================
    # EDGE DRAWING TAGS
    # ==========================================================

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
    # CLEAR SELECTION
    # ==========================================================

    def clear_selection(
        self,
    ) -> None:
        old_node = self.selected_node
        old_edge = self.selected_edge

        self.selected_node = None
        self.selected_edge = None

        if old_edge is not None:
            self.draw_edge(old_edge)

        if old_node is not None:
            self.draw_node(old_node)

        self.clear_properties_panel()

        dpg.set_value(
            "status_text",
            "Nothing selected",
        )

    # ==========================================================
    # NODE PROPERTIES
    # ==========================================================

    def update_node_properties_panel(
        self,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        dpg.set_value(
            "selected_object",
            node.name,
        )

        dpg.set_value(
            "property_page_title",
            "NODE",
        )

        dpg.configure_item(
            "node_properties",
            show=True,
        )

        dpg.configure_item(
            "edge_properties",
            show=False,
        )

        dpg.set_value(
            "node_id",
            str(node.node_id),
        )

        dpg.set_value(
            "node_label",
            node.name,
        )

        dpg.set_value(
            "node_x",
            int(round(node.x)),
        )

        dpg.set_value(
            "node_y",
            int(round(node.y)),
        )

        dpg.set_value(
            "node_size",
            int(round(node.size)),
        )

        dpg.set_value(
            "node_shape",
            node.shape,
        )

        dpg.set_value(
            "node_color",
            node.color,
        )

    # Compatibility with previous version.
    def update_properties_panel(
        self,
    ) -> None:
        if self.selected_node is not None:
            self.update_node_properties_panel()

        elif self.selected_edge is not None:
            self.update_edge_properties_panel()

    # ==========================================================
    # EDGE PROPERTIES
    # ==========================================================

    def update_edge_properties_panel(
        self,
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        dpg.set_value(
            "selected_object",
            edge.name,
        )

        dpg.set_value(
            "property_page_title",
            "EDGE",
        )

        dpg.configure_item(
            "node_properties",
            show=False,
        )

        dpg.configure_item(
            "edge_properties",
            show=True,
        )

        self.set_value_if_exists(
            "edge_id",
            str(edge.edge_id),
        )

        self.set_value_if_exists(
            "edge_label",
            edge.name,
        )

        self.set_value_if_exists(
            "edge_source",
            edge.source.name,
        )

        self.set_value_if_exists(
            "edge_target",
            edge.target.name,
        )

        self.set_value_if_exists(
            "edge_type",
            (
                "Directed"
                if edge.is_directed
                else "Undirected"
            ),
        )

        self.set_value_if_exists(
            "edge_thickness",
            int(edge.thickness),
        )

        self.set_value_if_exists(
            "edge_color",
            edge.color,
        )

    # ==========================================================
    # CLEAR PROPERTIES
    # ==========================================================

    def clear_properties_panel(
        self,
    ) -> None:
        dpg.set_value(
            "selected_object",
            "Nothing selected",
        )

        dpg.set_value(
            "property_page_title",
            "PROPERTIES",
        )

        dpg.configure_item(
            "node_properties",
            show=False,
        )

        dpg.configure_item(
            "edge_properties",
            show=False,
        )

    # ==========================================================
    # NODE PROPERTY CALLBACKS
    # ==========================================================

    def update_selected_node_name(
        self,
        sender: int | str,
        app_data: str,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        new_name = app_data.strip()

        if not new_name:
            dpg.set_value(
                "node_label",
                node.name,
            )
            return

        node.name = new_name

        self.redraw_edges_for_node(node)

        self.draw_node(node)

        self.update_node_properties_panel()

        dpg.set_value(
            "status_text",
            f"Renamed node to {node.name}",
        )

    def update_selected_node_x(
        self,
        sender: int | str,
        app_data: int,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node.x = float(app_data)

        self.redraw_edges_for_node(node)
        self.draw_node(node)

    def update_selected_node_y(
        self,
        sender: int | str,
        app_data: int,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node.y = float(app_data)

        self.redraw_edges_for_node(node)
        self.draw_node(node)

    def update_selected_node_size(
        self,
        sender: int | str,
        app_data: int,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node.size = float(app_data)

        self.redraw_edges_for_node(node)
        self.draw_node(node)

    def update_selected_node_shape(
        self,
        sender: int | str,
        app_data: str,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node.shape = app_data

        self.redraw_edges_for_node(node)
        self.draw_node(node)

    def update_selected_node_color(
        self,
        sender: int | str,
        app_data: list[float],
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node.color = self.normalize_color(
            app_data
        )

        self.draw_node(node)

    # ==========================================================
    # EDGE PROPERTY CALLBACKS
    # ==========================================================

    def update_selected_edge_name(
        self,
        sender: int | str,
        app_data: str,
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        new_name = app_data.strip()

        if not new_name:
            self.set_value_if_exists(
                "edge_label",
                edge.name,
            )
            return

        edge.name = new_name

        self.update_edge_properties_panel()

        dpg.set_value(
            "status_text",
            f"Renamed edge to {edge.name}",
        )

    def update_selected_edge_thickness(
        self,
        sender: int | str,
        app_data: int,
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        edge.thickness = float(
            app_data
        )

        self.draw_edge(edge)

    def update_selected_edge_color(
        self,
        sender: int | str,
        app_data: list[float],
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        edge.color = self.normalize_color(
            app_data
        )

        self.draw_edge(edge)

    # ==========================================================
    # DELETE
    # ==========================================================

    def handle_delete_key(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        self.delete_selected()

    def delete_selected(
        self,
    ) -> None:
        if self.selected_node is not None:
            self.delete_selected_node()
            return

        if self.selected_edge is not None:
            self.delete_selected_edge()

    def delete_selected_node(
        self,
    ) -> None:
        node = self.selected_node

        if node is None:
            return

        node_name = node.name

        connected_edges = (
            self.graph.edges_for_node(node)
        )

        for edge in connected_edges:
            self.delete_edge_drawing(edge)

        self.delete_node_drawing(node)

        self.graph.remove_node(
            node.node_id
        )

        self.selected_node = None
        self.dragging_node = None

        if self.pending_edge_source is node:
            self.pending_edge_source = None

        self.clear_properties_panel()

        self.update_graph_counters()

        dpg.set_value(
            "status_text",
            f"Deleted {node_name}",
        )

    def delete_selected_edge(
        self,
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        edge_name = edge.name

        self.delete_edge_drawing(edge)

        self.graph.remove_edge(
            edge.edge_id
        )

        self.selected_edge = None

        self.clear_properties_panel()

        self.update_graph_counters()

        dpg.set_value(
            "status_text",
            f"Deleted {edge_name}",
        )

    # ==========================================================
    # COUNTERS
    # ==========================================================

    def update_graph_counters(
        self,
    ) -> None:
        node_count = self.graph.node_count
        edge_count = self.graph.edge_count

        dpg.set_value(
            "node_count",
            str(node_count),
        )

        dpg.set_value(
            "edge_count",
            str(edge_count),
        )

        dpg.set_value(
            "status_nodes",
            str(node_count),
        )

        dpg.set_value(
            "status_edges",
            str(edge_count),
        )

    # Compatibility with previous version.
    def update_node_counters(
        self,
    ) -> None:
        self.update_graph_counters()
    
    # ==========================================================
    # CANVAS VIEW
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

        translation_matrix = dpg.create_translation_matrix(
            [
                self.pan_x,
                self.pan_y,
            ]
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


    def zoom_in(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.zoom = min(
            self.max_zoom,
            self.zoom + self.zoom_step,
        )

        self.apply_view_transform()


    def zoom_out(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.zoom = max(
            self.min_zoom,
            self.zoom - self.zoom_step,
        )

        self.apply_view_transform()


    def reset_view(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.apply_view_transform()

        dpg.set_value(
            "status_text",
            "View reset to 100%",
        )


    def fit_view(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        nodes = self.graph.nodes

        if not nodes:
            self.reset_view()
            return

        canvas_width, canvas_height = dpg.get_item_rect_size(
            "canvas_container"
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

        self.apply_view_transform()

        dpg.set_value(
            "status_text",
            "Graph fitted to view",
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def get_text_size(
        text: str,
    ) -> tuple[float, float]:
        size = dpg.get_text_size(
            text
        )

        if size is None:
            return (
                float(len(text) * 7),
                14.0,
            )

        return (
            float(size[0]),
            float(size[1]),
        )

    @staticmethod
    def normalize_color(
        color: list[float],
    ) -> tuple[int, int, int, int]:
        values: list[int] = []

        normalized_input = (
            len(color) > 0
            and max(color) <= 1.0
        )

        for component in color[:4]:
            value = float(component)

            if normalized_input:
                value *= 255.0

            values.append(
                max(
                    0,
                    min(
                        255,
                        int(round(value)),
                    ),
                )
            )

        while len(values) < 4:
            values.append(255)

        return (
            values[0],
            values[1],
            values[2],
            values[3],
        )

    @staticmethod
    def set_value_if_exists(
        tag: str,
        value: object,
    ) -> None:
        if dpg.does_item_exist(tag):
            dpg.set_value(
                tag,
                value,
            )