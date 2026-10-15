import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor
from ui.main_window import create_main_window
from ui.themes import create_themes


def main() -> None:
    dpg.create_context()

    editor = GraphEditor()

    create_themes()
    create_main_window(editor)

    dpg.bind_theme("app_theme")

    dpg.create_viewport(
        title="Graphora",
        width=1280,
        height=800,
        min_width=900,
        min_height=600
    )

    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_primary_window(
        "main_window",
        True
    )

    dpg.start_dearpygui()

    dpg.destroy_context()


if __name__ == "__main__":
    main()