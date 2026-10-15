import dearpygui.dearpygui as dpg

from model.graph import Graph
from model.node import Node


class GraphEditor:
    def __init__(self) -> None:
        self.graph: Graph = Graph()

        self.current_mode: str = "Select"
        self.next_node_id: int = 1

        self.node_positions: dict[
            int,
            tuple[float, float]
        ] = {}

        self.selected_node: Node | None = None

    def change_mode(
        self,
        sender: int | str,
        app_data: object,
        user_data: str,
    ) -> None:
        self.current_mode = user_data

        dpg.set_value(
            "current_mode",
            self.current_mode
        )

        dpg.set_value(
            "status_mode",
            self.current_mode
        )

        dpg.set_value(
            "status_text",
            f"{self.current_mode} mode"
        )

    def create_node_at(
        self,
        x: float,
        y: float,
    ) -> None:
        node_id = self.next_node_id

        node = Node(
            node_id=node_id,
            name=f"Node {node_id}"
        )

        self.graph.add_node(node)

        self.node_positions[node_id] = (x, y)

        dpg.draw_circle(
            center=(x, y),
            radius=25,
            color=(180, 200, 255, 255),
            fill=(70, 110, 220, 255),
            thickness=2,
            parent="graph_canvas",
            tag=f"node_{node_id}"
        )

        dpg.draw_text(
            pos=(x - 20, y - 7),
            text=node.name,
            color=(255, 255, 255, 255),
            size=14,
            parent="graph_canvas",
            tag=f"node_label_{node_id}"
        )

        self.next_node_id += 1

        dpg.set_value(
            "node_count",
            str(self.graph.node_count)
        )

        dpg.set_value(
            "status_nodes",
            str(self.graph.node_count)
        )

        dpg.set_value(
            "status_text",
            f"Created {node.name}"
        )

    def handle_canvas_click(
        self,
        sender: int | str,
        app_data: object,
    ) -> None:
        if not dpg.is_item_hovered("graph_canvas"):
            return

        mouse_x, mouse_y = dpg.get_mouse_pos(
            local=False
        )

        canvas_x, canvas_y = dpg.get_item_rect_min(
            "graph_canvas"
        )

        x = mouse_x - canvas_x
        y = mouse_y - canvas_y

        if self.current_mode == "Node":
            self.create_node_at(x, y)
            return

        if self.current_mode == "Select":
            node = self.find_node_at(x, y)

            if node is None:
                self.clear_node_selection()
                return

            self.select_node(node)

    def find_node_at(
        self,
        x: float,
        y: float,
    ) -> Node | None:
        node_radius: float = 25.0

        for node in self.graph.nodes:
            position = self.node_positions.get(
                node.node_id
            )

            if position is None:
                continue

            node_x, node_y = position

            dx = x - node_x
            dy = y - node_y

            distance_squared = dx * dx + dy * dy

            if distance_squared <= node_radius * node_radius:
                return node

        return None
    
    def select_node(
        self,
        node: Node,
    ) -> None:
        self.clear_node_selection()
        
        self.selected_node = node

        dpg.configure_item(
            f"node_{node.node_id}",
            color=(255, 220, 100, 255),
            thickness=4
        )

        dpg.set_value(
            "selected_object",
            node.name
        )

        dpg.set_value(
            "node_id",
            str(node.node_id)
        )

        dpg.set_value(
            "node_label",
            node.name
        )

        position = self.node_positions.get(
            node.node_id
        )

        if position is not None:
            x, y = position

            dpg.set_value(
                "node_x",
                int(x)
            )

            dpg.set_value(
                "node_y",
                int(y)
            )

        dpg.configure_item(
            "node_properties",
            show=True
        )

        dpg.configure_item(
            "edge_properties",
            show=False
        )

        dpg.set_value(
            "property_page_title",
            "NODE"
        )

        dpg.set_value(
            "status_text",
            f"Selected {node.name}"
        )
        
    def clear_node_selection(self) -> None:
        if self.selected_node is None:
            return

        dpg.configure_item(
            f"node_{self.selected_node.node_id}",
            color=(180, 200, 255, 255),
            thickness=2
        )

        self.selected_node = None