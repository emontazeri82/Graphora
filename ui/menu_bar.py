import dearpygui.dearpygui as dpg

# ============================================================
# Menu Bar
# ============================================================

def create_menu_bar() -> None:
    with dpg.menu_bar():

        with dpg.menu(label="File"):
            dpg.add_menu_item(label="New")
            dpg.add_menu_item(label="Open...")
            dpg.add_separator()

            dpg.add_menu_item(label="Save")
            dpg.add_menu_item(label="Save As...")

            dpg.add_separator()
            dpg.add_menu_item(label="Exit")

        with dpg.menu(label="Edit"):
            dpg.add_menu_item(label="Undo")
            dpg.add_menu_item(label="Redo")

            dpg.add_separator()

            dpg.add_menu_item(label="Cut")
            dpg.add_menu_item(label="Copy")
            dpg.add_menu_item(label="Paste")
            dpg.add_menu_item(label="Delete")

        with dpg.menu(label="View"):
            dpg.add_menu_item(label="Reset View")
            dpg.add_menu_item(label="Fit Graph to Window")

        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="User Guide")
            dpg.add_separator()
            dpg.add_menu_item(label="About Graphora")