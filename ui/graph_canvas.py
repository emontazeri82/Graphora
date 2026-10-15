import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor


def create_graph_editor(
    editor: GraphEditor,
) -> None:
    with dpg.child_window(
        width=-270,
        height=-35,
        border=True,
        tag="graph_editor",
    ):
        # ======================================================
        # HEADER
        # ======================================================

        with dpg.group(
            horizontal=True
        ):
            dpg.add_text(
                "GRAPH EDITOR"
            )

            dpg.add_spacer(
                width=20
            )

            dpg.add_button(
                label="-",
                width=32,
                height=28,
                callback=editor.zoom_out,
            )

            dpg.add_button(
                label="100%",
                width=60,
                height=28,
                tag="zoom_display",
                callback=editor.reset_view,
            )

            dpg.add_button(
                label="+",
                width=32,
                height=28,
                callback=editor.zoom_in,
            )

            dpg.add_spacer(
                width=8
            )

            dpg.add_button(
                label="Fit",
                width=50,
                height=28,
                callback=editor.fit_view,
            )

            dpg.add_button(
                label="Reset",
                width=60,
                height=28,
                callback=editor.reset_view,
            )

        dpg.add_separator()

        dpg.add_spacer(
            height=5
        )

        # ======================================================
        # CANVAS
        # ======================================================

        with dpg.child_window(
            width=-1,
            height=-1,
            border=True,
            tag="canvas_container",
        ):
            dpg.bind_item_theme(
                "canvas_container",
                "canvas_theme",
            )

            with dpg.drawlist(
                width=2000,
                height=2000,
                tag="graph_canvas",
            ):
                with dpg.draw_node(
                    tag="canvas_layer",
                ):
                    pass

        # ======================================================
        # HANDLERS
        # ======================================================

        with dpg.item_handler_registry(
            tag="canvas_handlers"
        ):
            dpg.add_item_clicked_handler(
                button=dpg.mvMouseButton_Left,
                callback=editor.handle_canvas_click,
            )

        dpg.bind_item_handler_registry(
            "graph_canvas",
            "canvas_handlers",
        )

        # ======================================================
        # GLOBAL MOUSE HANDLERS
        # ======================================================

        with dpg.handler_registry(
            tag="graph_mouse_handlers"
        ):
            dpg.add_mouse_drag_handler(
                button=dpg.mvMouseButton_Left,
                threshold=2.0,
                callback=editor.handle_mouse_drag,
            )

            dpg.add_mouse_release_handler(
                button=dpg.mvMouseButton_Left,
                callback=editor.handle_mouse_release,
            )

            dpg.add_key_press_handler(
                key=dpg.mvKey_Delete,
                callback=editor.handle_delete_key,
            )

            dpg.add_key_press_handler(
                key=dpg.mvKey_Back,
                callback=editor.handle_delete_key,
            )