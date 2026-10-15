import dearpygui.dearpygui as dpg

def create_status_bar() -> None:
    with dpg.group(horizontal=True):

        dpg.add_text(
            "Ready",
            tag="status_text"
        )

        dpg.add_spacer(width=30)

        dpg.add_text("Mode:")
        dpg.add_text(
            "Select",
            tag="status_mode"
        )

        dpg.add_spacer(width=30)

        dpg.add_text("Nodes:")
        dpg.add_text(
            "0",
            tag="status_nodes"
        )

        dpg.add_text("|")

        dpg.add_text("Edges:")
        dpg.add_text(
            "0",
            tag="status_edges"
        )

        dpg.add_spacer(width=30)

        dpg.add_text("Zoom:")
        dpg.add_text(
            "100%",
            tag="status_zoom"
        )
