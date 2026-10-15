import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor


def create_graph_editor(
    editor: GraphEditor,
) -> None:
    with dpg.child_window(
        width=-270,
        height=-35,
        border=True,
        tag="graph_editor"
    ):

        # Editor header
        with dpg.group(horizontal=True):
            dpg.add_text("GRAPH EDITOR")

            dpg.add_spacer(width=20)

            dpg.add_button(
                label="-",
                width=32,
                height=28
            )

            dpg.add_button(
                label="100%",
                width=60,
                height=28
            )

            dpg.add_button(
                label="+",
                width=32,
                height=28
            )

            dpg.add_spacer(width=8)

            dpg.add_button(
                label="Fit",
                width=50,
                height=28
            )

            dpg.add_button(
                label="Reset",
                width=60,
                height=28
            )

        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Actual graph canvas
        with dpg.child_window(
            width=-1,
            height=-1,
            border=True,
            tag="canvas_container"
        ):
            dpg.bind_item_theme(
                "canvas_container",
                "canvas_theme"
            )

            with dpg.drawlist(
                width=-1,
                height=-1,
                tag="graph_canvas"
            ):
                pass

        # Canvas mouse handlers
        with dpg.item_handler_registry(
            tag="canvas_handlers"
        ):
            dpg.add_item_clicked_handler(
                button=dpg.mvMouseButton_Left,
                callback=editor.handle_canvas_click
            )

        dpg.bind_item_handler_registry(
            "graph_canvas",
            "canvas_handlers"
        )