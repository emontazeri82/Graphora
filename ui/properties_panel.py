import dearpygui.dearpygui as dpg

def show_node_properties() -> None:
    dpg.configure_item("node_properties", show=True)
    dpg.configure_item("edge_properties", show=False)

    dpg.set_value("property_page_title", "NODE")


def show_edge_properties() -> None:
    dpg.configure_item("node_properties", show=False)
    dpg.configure_item("edge_properties", show=True)

    dpg.set_value("property_page_title", "EDGE")
# ============================================================
# Properties Panel
# ============================================================

def create_properties_panel() -> None:
    with dpg.child_window(
        width=260,
        height=-35,
        border=True,
        tag="properties_panel"
    ):
        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        dpg.add_text("PROPERTIES")
        dpg.add_separator()
        dpg.add_spacer(height=8)

        dpg.add_text("Selected:")
        dpg.add_text(
            "Nothing selected",
            tag="selected_object"
        )

        dpg.add_spacer(height=12)

        # ----------------------------------------------------
        # Page navigation
        # ----------------------------------------------------

        with dpg.group(horizontal=True):

            dpg.add_text(
                "NODE",
                tag="property_page_title"
            )

            dpg.add_spacer(width=80)

            dpg.add_button(
                label="<",
                width=35,
                callback=show_node_properties
            )

            dpg.add_button(
                label=">",
                width=35,
                callback=show_edge_properties
            )

        dpg.add_separator()
        dpg.add_spacer(height=10)

        # ====================================================
        # NODE PROPERTY PAGE
        # ====================================================

        with dpg.group(
            tag="node_properties",
            show=True
        ):
            dpg.add_text("NODE PROPERTIES")
            dpg.add_spacer(height=8)

            # ID
            with dpg.group(horizontal=True):
                dpg.add_text("ID:")
                dpg.add_spacer(width=20)
                dpg.add_text(
                    "-",
                    tag="node_id"
                )

            dpg.add_spacer(height=10)

            # Name
            dpg.add_text("Name:")

            dpg.add_input_text(
                tag="node_label",
                hint="Node name",
                width=-1
            )

            dpg.add_spacer(height=10)

            # Position
            dpg.add_text("Position:")

            with dpg.group(horizontal=True):
                dpg.add_text("X:")

                dpg.add_input_int(
                    tag="node_x",
                    default_value=0,
                    width=80,
                    step=1
                )

                dpg.add_text("Y:")

                dpg.add_input_int(
                    tag="node_y",
                    default_value=0,
                    width=80,
                    step=1
                )

            dpg.add_spacer(height=10)

            # Size
            dpg.add_text("Size:")

            dpg.add_slider_int(
                tag="node_size",
                default_value=50,
                min_value=20,
                max_value=200,
                width=-1
            )

            dpg.add_spacer(height=10)

            # Shape
            dpg.add_text("Shape:")

            dpg.add_combo(
                [
                    "Circle",
                    "Rectangle",
                    "Square"
                ],
                tag="node_shape",
                default_value="Circle",
                width=-1
            )

            dpg.add_spacer(height=10)

            # Color
            dpg.add_text("Color:")

            dpg.add_color_edit(
                tag="node_color",
                default_value=(70, 110, 220, 255),
                width=-1,
                no_inputs=True
            )

        # ====================================================
        # EDGE PROPERTY PAGE
        # ====================================================

        with dpg.group(
            tag="edge_properties",
            show=False
        ):
            dpg.add_text("EDGE PROPERTIES")
            dpg.add_spacer(height=8)

            # ID
            with dpg.group(horizontal=True):
                dpg.add_text("ID:")
                dpg.add_spacer(width=20)

                dpg.add_text(
                    "-",
                    tag="edge_id"
                )

            dpg.add_spacer(height=12)

            # Connected Nodes
            dpg.add_text("CONNECTED NODES")

            dpg.add_separator()

            dpg.add_spacer(height=6)

            with dpg.group(horizontal=True):
                dpg.add_text("From:")
                dpg.add_spacer(width=20)

                dpg.add_text(
                    "-",
                    tag="edge_from"
                )

            with dpg.group(horizontal=True):
                dpg.add_text("To:")
                dpg.add_spacer(width=34)

                dpg.add_text(
                    "-",
                    tag="edge_to"
                )

            dpg.add_spacer(height=12)

            # Direction
            with dpg.group(horizontal=True):
                dpg.add_text("Direction:")

                dpg.add_text(
                    "Directed",
                    tag="edge_direction"
                )

            dpg.add_spacer(height=12)

            # Line Style
            dpg.add_text("Line Style:")

            dpg.add_combo(
                [
                    "Solid",
                    "Dashed",
                    "Dotted"
                ],
                tag="edge_line_style",
                default_value="Solid",
                width=-1
            )

            dpg.add_spacer(height=12)

            # Thickness
            dpg.add_text("Thickness:")

            dpg.add_slider_int(
                tag="edge_thickness",
                default_value=2,
                min_value=1,
                max_value=10,
                width=-1
            )

            dpg.add_spacer(height=12)

            # Color
            dpg.add_text("Color:")

            dpg.add_color_edit(
                tag="edge_color",
                default_value=(100, 110, 130, 255),
                width=-1,
                no_inputs=True
            )
