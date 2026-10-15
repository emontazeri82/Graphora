import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor


# ============================================================
# Menu Bar
# ============================================================

def create_menu_bar(
    editor: GraphEditor,
) -> None:
    with dpg.menu_bar():

        # ====================================================
        # File Menu
        # ====================================================

        with dpg.menu(label="File"):
            dpg.add_menu_item(
                label="New",
                shortcut="Ctrl+N",
                enabled=False,
            )

            dpg.add_menu_item(
                label="Open...",
                shortcut="Ctrl+O",
                enabled=False,
            )

            dpg.add_separator()

            dpg.add_menu_item(
                label="Save",
                shortcut="Ctrl+S",
                enabled=False,
            )

            dpg.add_menu_item(
                label="Save As...",
                shortcut="Ctrl+Shift+S",
                enabled=False,
            )

            dpg.add_separator()

            dpg.add_menu_item(
                label="Exit",
                shortcut="Alt+F4",
                callback=lambda: dpg.stop_dearpygui()
            )

        # ====================================================
        # Edit Menu
        # ====================================================

        with dpg.menu(label="Edit"):
            dpg.add_menu_item(
                label="Undo",
                shortcut="Ctrl+Z",
                callback=editor.undo,
            )

            dpg.add_menu_item(
                label="Redo",
                shortcut="Ctrl+Y",
                callback=editor.redo
            )

            dpg.add_separator()

            dpg.add_menu_item(
                label="Cut",
                shortcut="Ctrl+X",
                callback=editor.cut_selected,
            )

            dpg.add_menu_item(
                label="Copy",
                shortcut="Ctrl+C",
                callback=editor.copy_selected,
            )

            dpg.add_menu_item(
                label="Paste",
                shortcut="Ctrl+V",
                callback=editor.paste_clipboard,
            )

            dpg.add_separator()

            dpg.add_menu_item(
                label="Delete Selected",
                shortcut="Delete",
                callback=editor.delete_selected,
            )

        # ====================================================
        # View Menu
        # ====================================================

        with dpg.menu(label="View"):
            dpg.add_menu_item(
                label="Reset View",
                shortcut="Ctrl+0",
                callback=editor.reset_view,
            )

            dpg.add_menu_item(
                label="Fit Graph to Window",
                shortcut="F",
                callback=editor.fit_view,
            )

        # ====================================================
        # Help Menu
        # ====================================================

        with dpg.menu(label="Help"):
            dpg.add_menu_item(
                label="User Guide",
                shortcut="F1",
                enabled=False,
            )

            dpg.add_separator()

            dpg.add_menu_item(
                label="About Graphora",
                enabled=False,
            )