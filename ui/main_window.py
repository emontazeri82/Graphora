import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor
from ui.graph_canvas import create_graph_editor
from ui.menu_bar import create_menu_bar
from ui.properties_panel import create_properties_panel
from ui.selecting_panel import create_selecting_panel
from ui.status_bar import create_status_bar


def create_main_window(
    editor: GraphEditor,
) -> None:
    with dpg.window(
        tag="main_window",
        label="Graphora",
        no_collapse=True
    ):
        create_menu_bar()

        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            create_selecting_panel(editor)
            create_graph_editor(editor)
            create_properties_panel()

        dpg.add_separator()

        create_status_bar()