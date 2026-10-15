import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor


def create_selecting_panel(
    editor: GraphEditor,
) -> None:
    with dpg.child_window(
        width=190,
        height=-35,
        border=True,
        tag="selecting_panel"
    ):
        dpg.add_text("TOOLS")
        dpg.add_separator()
        dpg.add_spacer(height=5)

        select_button = dpg.add_button(
            label="Select",
            width=-1,
            height=40,
            callback=editor.change_mode,
            user_data="Select"
        )

        dpg.add_spacer(height=4)

        node_button = dpg.add_button(
            label="+  Node",
            width=-1,
            height=40,
            callback=editor.change_mode,
            user_data="Node"
        )

        dpg.add_spacer(height=4)

        directed_button = dpg.add_button(
            label="->  Directed Edge",
            width=-1,
            height=40,
            callback=editor.change_mode,
            user_data="Directed Edge"
        )

        dpg.add_spacer(height=4)

        undirected_button = dpg.add_button(
            label="--  Undirected Edge",
            width=-1,
            height=40,
            callback=editor.change_mode,
            user_data="Undirected Edge"
        )

        dpg.bind_item_theme(
            select_button,
            "tool_button_theme"
        )

        dpg.bind_item_theme(
            node_button,
            "tool_button_theme"
        )

        dpg.bind_item_theme(
            directed_button,
            "tool_button_theme"
        )

        dpg.bind_item_theme(
            undirected_button,
            "tool_button_theme"
        )

        dpg.add_spacer(height=25)

        dpg.add_text("GRAPH")
        dpg.add_separator()
        dpg.add_spacer(height=8)

        with dpg.group(horizontal=True):
            dpg.add_text("Nodes")

            dpg.add_text(
                "0",
                tag="node_count"
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Edges")

            dpg.add_text(
                "0",
                tag="edge_count"
            )

        dpg.add_spacer(height=25)

        dpg.add_text("MODE")
        dpg.add_separator()
        dpg.add_spacer(height=8)

        dpg.add_text(
            "Select",
            tag="current_mode"
        )