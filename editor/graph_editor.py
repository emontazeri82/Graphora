from __future__ import annotations

import dearpygui.dearpygui as dpg

from editor.graph_clipboard import GraphClipboard
from editor.graph_history import GraphHistory, HistoryResult
from editor.graph_hit_tester import GraphHitTester
from editor.graph_renderer import GraphRenderer
from editor.graph_view import GraphView
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
        self.drag_history_recorded: bool = False

        self.hit_tester: GraphHitTester = GraphHitTester(self)
        self.view: GraphView = GraphView(self)
        self.renderer: GraphRenderer = GraphRenderer(self)

        self.history: GraphHistory = GraphHistory()
        self.clipboard: GraphClipboard = GraphClipboard()

    @property
    def zoom(self) -> float:
        return self.view.zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        self.view.zoom = float(value)

    @property
    def pan_x(self) -> float:
        return self.view.pan_x

    @pan_x.setter
    def pan_x(self, value: float) -> None:
        self.view.pan_x = float(value)

    @property
    def pan_y(self) -> float:
        return self.view.pan_y

    @pan_y.setter
    def pan_y(self, value: float) -> None:
        self.view.pan_y = float(value)

    @property
    def min_zoom(self) -> float:
        return self.view.min_zoom

    @min_zoom.setter
    def min_zoom(self, value: float) -> None:
        self.view.min_zoom = float(value)

    @property
    def max_zoom(self) -> float:
        return self.view.max_zoom

    @max_zoom.setter
    def max_zoom(self, value: float) -> None:
        self.view.max_zoom = float(value)

    @property
    def zoom_step(self) -> float:
        return self.view.zoom_step

    @zoom_step.setter
    def zoom_step(self, value: float) -> None:
        self.view.zoom_step = float(value)

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
        self.drag_history_recorded = False

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
    # CANVAS INTERACTION
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
            self.drag_history_recorded = False

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
        self.record_history("Create node")

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
    # NODE SELECTION / DRAGGING
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

        if not self.drag_history_recorded:
            self.record_history("Move node")
            self.drag_history_recorded = True

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
        self.record_history("Create edge")

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

        if new_name == node.name:
            return

        self.record_history("Rename node")
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

        new_x = float(app_data)
        if new_x == node.x:
            return

        self.record_history("Change node X")
        node.x = new_x

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

        new_y = float(app_data)
        if new_y == node.y:
            return

        self.record_history("Change node Y")
        node.y = new_y

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

        new_size = float(app_data)
        if new_size == node.size:
            return

        self.record_history("Change node size")
        node.size = new_size

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

        if app_data == node.shape:
            return

        self.record_history("Change node shape")
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

        new_color = self.normalize_color(app_data)
        if new_color == node.color:
            return

        self.record_history("Change node color")
        node.color = new_color

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

        if new_name == edge.name:
            return

        self.record_history("Rename edge")
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

        new_thickness = float(app_data)
        if new_thickness == edge.thickness:
            return

        self.record_history("Change edge thickness")
        edge.thickness = new_thickness

        self.draw_edge(edge)

    def update_selected_edge_color(
        self,
        sender: int | str,
        app_data: list[float],
    ) -> None:
        edge = self.selected_edge

        if edge is None:
            return

        new_color = self.normalize_color(app_data)
        if new_color == edge.color:
            return

        self.record_history("Change edge color")
        edge.color = new_color

        self.draw_edge(edge)

    # ==========================================================
    # DELETE
    # ==========================================================

    def handle_delete_key(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        text_inputs = (
            "node_label",
            "edge_label",
        )

        for item in text_inputs:
            if (
                dpg.does_item_exist(item)
                and dpg.is_item_active(item)
            ):
                return

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

        self.record_history("Delete node")

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

        self.record_history("Delete edge")

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
    # HISTORY / CLIPBOARD
    # ==========================================================

    def record_history(self, description: str) -> None:
        self.history.record(
            graph=self.graph,
            next_node_id=self.next_node_id,
            next_edge_id=self.next_edge_id,
            description=description,
        )

    def undo(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        result = self.history.undo(
            current_graph=self.graph,
            next_node_id=self.next_node_id,
            next_edge_id=self.next_edge_id,
        )

        if result is None:
            dpg.set_value("status_text", "Nothing to undo")
            return

        self.restore_history_result(result)
        dpg.set_value(
            "status_text",
            f"Undo: {result.description}" if result.description else "Undo",
        )

    def redo(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        result = self.history.redo(
            current_graph=self.graph,
            next_node_id=self.next_node_id,
            next_edge_id=self.next_edge_id,
        )

        if result is None:
            dpg.set_value("status_text", "Nothing to redo")
            return

        self.restore_history_result(result)
        dpg.set_value(
            "status_text",
            f"Redo: {result.description}" if result.description else "Redo",
        )

    def restore_history_result(self, result: HistoryResult) -> None:
        for edge in self.graph.edges:
            self.delete_edge_drawing(edge)

        for node in self.graph.nodes:
            self.delete_node_drawing(node)

        self.graph = result.graph
        self.next_node_id = result.next_node_id
        self.next_edge_id = result.next_edge_id

        self.selected_node = None
        self.selected_edge = None
        self.pending_edge_source = None
        self.dragging_node = None
        self.drag_history_recorded = False

        self.clear_properties_panel()
        self.redraw_all()
        self.update_graph_counters()
        self.apply_view_transform()

    def copy_selected(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        if self.selected_node is not None:
            node = self.selected_node
            self.clipboard.copy_node(
                node=node,
                connected_edges=self.graph.edges_for_node(node),
            )
            dpg.set_value("status_text", f"Copied {node.name}")
            return

        if self.selected_edge is not None:
            edge = self.selected_edge
            self.clipboard.copy(
                nodes=(edge.source, edge.target),
                edges=(edge,),
            )
            dpg.set_value("status_text", f"Copied {edge.name}")
            return

        dpg.set_value("status_text", "Nothing selected to copy")

    def cut_selected(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        if self.selected_node is None and self.selected_edge is None:
            dpg.set_value("status_text", "Nothing selected to cut")
            return

        self.copy_selected()
        self.delete_selected()

    def paste_clipboard(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        if self.clipboard.is_empty:
            dpg.set_value("status_text", "Clipboard is empty")
            return

        self.record_history("Paste")

        result = self.clipboard.paste(
            next_node_id=self.next_node_id,
            next_edge_id=self.next_edge_id,
        )

        added_nodes: list[Node] = []
        added_edges: list[Edge] = []

        for node in result.nodes:
            if self.graph.add_node(node):
                added_nodes.append(node)

        for edge in result.edges:
            if self.graph.add_edge(edge):
                added_edges.append(edge)

        self.next_node_id = result.next_node_id
        self.next_edge_id = result.next_edge_id

        self.selected_node = None
        self.selected_edge = None

        for edge in added_edges:
            self.draw_edge(edge)

        for node in added_nodes:
            self.draw_node(node)

        if len(added_nodes) == 1:
            self.select_node(added_nodes[0])
        else:
            self.clear_properties_panel()

        self.update_graph_counters()
        dpg.set_value(
            "status_text",
            f"Pasted {len(added_nodes)} node(s) and {len(added_edges)} edge(s)",
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

    def update_node_counters(
        self,
    ) -> None:
        self.update_graph_counters()

    # ==========================================================
    # VIEW DELEGATION
    # ==========================================================

    def get_canvas_mouse_position(self) -> tuple[float, float]:
        return self.view.get_canvas_mouse_position()

    def redraw_node_labels(self) -> None:
        self.renderer.redraw_node_labels()

    def apply_view_transform(self) -> None:
        self.view.apply_view_transform()

    def zoom_in(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.view.zoom_in()

    def zoom_out(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.view.zoom_out()

    def reset_view(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.view.reset_view()

    def fit_view(
        self,
        sender: int | str = 0,
        app_data: object = None,
    ) -> None:
        self.view.fit_view()

    # ==========================================================
    # HIT TESTING / GEOMETRY DELEGATION
    # ==========================================================

    def find_node_at(
        self,
        x: float,
        y: float,
    ) -> Node | None:
        return self.hit_tester.find_node_at(x, y)

    def point_inside_node(
        self,
        node: Node,
        x: float,
        y: float,
    ) -> bool:
        return self.hit_tester.point_inside_node(node, x, y)

    def get_edge_endpoints(
        self,
        edge: Edge,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        return self.hit_tester.get_edge_endpoints(edge)

    def get_node_connection_radius(
        self,
        node: Node,
        unit_x: float,
        unit_y: float,
    ) -> float:
        return self.hit_tester.get_node_connection_radius(
            node,
            unit_x,
            unit_y,
        )

    def find_edge_at(
        self,
        x: float,
        y: float,
    ) -> Edge | None:
        return self.hit_tester.find_edge_at(x, y)

    def point_near_edge(
        self,
        edge: Edge,
        x: float,
        y: float,
    ) -> bool:
        return self.hit_tester.point_near_edge(edge, x, y)

    def point_near_self_loop(
        self,
        edge: Edge,
        x: float,
        y: float,
    ) -> bool:
        return self.hit_tester.point_near_self_loop(edge, x, y)

    def distance_to_segment(
        self,
        px: float,
        py: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        return self.hit_tester.distance_to_segment(
            px,
            py,
            x1,
            y1,
            x2,
            y2,
        )

    # ==========================================================
    # RENDERER DELEGATION
    # ==========================================================

    def draw_node(self, node: Node) -> None:
        self.renderer.draw_node(node)

    def draw_node_label(self, node: Node) -> None:
        self.renderer.draw_node_label(node)

    def get_fitted_node_label(
        self,
        node: Node,
    ) -> tuple[str, float]:
        return self.renderer.get_fitted_node_label(node)

    def get_node_label_max_width(self, node: Node) -> float:
        return self.renderer.get_node_label_max_width(node)

    def delete_node_drawing(self, node: Node) -> None:
        self.renderer.delete_node_drawing(node)

    def node_tag(self, node: Node) -> str:
        return self.renderer.node_tag(node)

    def node_label_tag(self, node: Node) -> str:
        return self.renderer.node_label_tag(node)

    def draw_edge(self, edge: Edge) -> None:
        self.renderer.draw_edge(edge)

    def draw_regular_edge(
        self,
        edge: Edge,
        color: tuple[int, int, int, int],
        thickness: float,
    ) -> None:
        self.renderer.draw_regular_edge(edge, color, thickness)

    def draw_arrowhead(
        self,
        edge: Edge,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int, int],
    ) -> None:
        self.renderer.draw_arrowhead(edge, start, end, color)

    def draw_self_loop(
        self,
        edge: Edge,
        color: tuple[int, int, int, int],
        thickness: float,
    ) -> None:
        self.renderer.draw_self_loop(edge, color, thickness)

    def redraw_edges_for_node(self, node: Node) -> None:
        self.renderer.redraw_edges_for_node(node)

    def redraw_node_on_top(self, node: Node) -> None:
        self.renderer.redraw_node_on_top(node)

    def redraw_all(self) -> None:
        self.renderer.redraw_all()

    def edge_line_tag(self, edge: Edge) -> str:
        return self.renderer.edge_line_tag(edge)

    def edge_arrow_tag(self, edge: Edge) -> str:
        return self.renderer.edge_arrow_tag(edge)

    def delete_edge_drawing(self, edge: Edge) -> None:
        self.renderer.delete_edge_drawing(edge)

    # ==========================================================
    # HELPERS
    # ==========================================================

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

    def set_value_if_exists(
        tag: str,
        value: object,
    ) -> None:
        if dpg.does_item_exist(tag):
            dpg.set_value(
                tag,
                value,
            )
