import dearpygui.dearpygui as dpg

from editor.graph_editor import GraphEditor


# ============================================================
# PAGE NAVIGATION
# ============================================================

def show_node_properties() -> None:
    dpg.configure_item(
        "node_properties",
        show=True,
    )

    dpg.configure_item(
        "edge_properties",
        show=False,
    )

    dpg.set_value(
        "property_page_title",
        "NODE",
    )


def show_edge_properties() -> None:
    dpg.configure_item(
        "node_properties",
        show=False,
    )

    dpg.configure_item(
        "edge_properties",
        show=True,
    )

    dpg.set_value(
        "property_page_title",
        "EDGE",
    )


# ============================================================
# PROPERTIES PANEL
# ============================================================

def create_properties_panel(
    editor: GraphEditor,
) -> None:
    with dpg.child_window(
        width=260,
        height=-35,
        border=True,
        tag="properties_panel",
    ):

        # ======================================================
        # HEADER
        # ======================================================

        dpg.add_text(
            "PROPERTIES"
        )

        dpg.add_separator()

        dpg.add_spacer(
            height=8
        )

        dpg.add_text(
            "Selected:"
        )

        dpg.add_text(
            "Nothing selected",
            tag="selected_object",
        )

        dpg.add_spacer(
            height=12
        )

        # ======================================================
        # PAGE NAVIGATION
        # ======================================================

        with dpg.group(
            horizontal=True
        ):
            dpg.add_text(
                "NODE",
                tag="property_page_title",
            )

            dpg.add_spacer(
                width=80
            )

            dpg.add_button(
                label="<",
                width=35,
                callback=show_node_properties,
            )

            dpg.add_button(
                label=">",
                width=35,
                callback=show_edge_properties,
            )

        dpg.add_separator()

        dpg.add_spacer(
            height=10
        )

        # ======================================================
        # NODE PROPERTY PAGE
        # ======================================================

        with dpg.group(
            tag="node_properties",
            show=True,
        ):
            dpg.add_text(
                "NODE PROPERTIES"
            )

            dpg.add_spacer(
                height=8
            )

            # --------------------------------------------------
            # NODE ID
            # --------------------------------------------------

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "ID:"
                )

                dpg.add_spacer(
                    width=20
                )

                dpg.add_text(
                    "-",
                    tag="node_id",
                )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # NODE NAME
            # --------------------------------------------------

            dpg.add_text(
                "Name:"
            )

            dpg.add_input_text(
                tag="node_label",
                hint="Node name",
                width=-1,
                callback=editor.update_selected_node_name,
                on_enter=True,
            )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # POSITION
            # --------------------------------------------------

            dpg.add_text(
                "Position:"
            )

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "X:"
                )

                dpg.add_input_int(
                    tag="node_x",
                    default_value=0,
                    width=80,
                    step=1,
                    callback=editor.update_selected_node_x,
                )

                dpg.add_text(
                    "Y:"
                )

                dpg.add_input_int(
                    tag="node_y",
                    default_value=0,
                    width=80,
                    step=1,
                    callback=editor.update_selected_node_y,
                )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # SIZE
            # --------------------------------------------------

            dpg.add_text(
                "Size:"
            )

            dpg.add_slider_int(
                tag="node_size",
                default_value=50,
                min_value=20,
                max_value=200,
                width=-1,
                callback=editor.update_selected_node_size,
            )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # SHAPE
            # --------------------------------------------------

            dpg.add_text(
                "Shape:"
            )

            dpg.add_combo(
                [
                    "Circle",
                    "Rectangle",
                    "Square",
                ],
                tag="node_shape",
                default_value="Circle",
                width=-1,
                callback=editor.update_selected_node_shape,
            )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # NODE COLOR
            # --------------------------------------------------

            dpg.add_text(
                "Color:"
            )

            dpg.add_color_edit(
                tag="node_color",
                default_value=(
                    70,
                    110,
                    220,
                    255,
                ),
                width=-1,
                no_inputs=True,
                callback=editor.update_selected_node_color,
            )

        # ======================================================
        # EDGE PROPERTY PAGE
        # ======================================================

        with dpg.group(
            tag="edge_properties",
            show=False,
        ):
            dpg.add_text(
                "EDGE PROPERTIES"
            )

            dpg.add_spacer(
                height=8
            )

            # --------------------------------------------------
            # EDGE ID
            # --------------------------------------------------

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "ID:"
                )

                dpg.add_spacer(
                    width=20
                )

                dpg.add_text(
                    "-",
                    tag="edge_id",
                )

            dpg.add_spacer(
                height=10
            )

            # --------------------------------------------------
            # EDGE NAME
            # --------------------------------------------------

            dpg.add_text(
                "Name:"
            )

            dpg.add_input_text(
                tag="edge_label",
                hint="Edge name",
                width=-1,
                callback=editor.update_selected_edge_name,
                on_enter=True,
            )

            dpg.add_spacer(
                height=12
            )

            # --------------------------------------------------
            # CONNECTION INFORMATION
            # --------------------------------------------------

            dpg.add_text(
                "CONNECTED NODES"
            )

            dpg.add_separator()

            dpg.add_spacer(
                height=6
            )

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "From:"
                )

                dpg.add_spacer(
                    width=20
                )

                dpg.add_text(
                    "-",
                    tag="edge_source",
                )

            dpg.add_spacer(
                height=4
            )

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "To:"
                )

                dpg.add_spacer(
                    width=34
                )

                dpg.add_text(
                    "-",
                    tag="edge_target",
                )

            dpg.add_spacer(
                height=12
            )

            # --------------------------------------------------
            # EDGE TYPE
            # --------------------------------------------------

            with dpg.group(
                horizontal=True
            ):
                dpg.add_text(
                    "Type:"
                )

                dpg.add_spacer(
                    width=20
                )

                dpg.add_text(
                    "-",
                    tag="edge_type",
                )

            dpg.add_spacer(
                height=12
            )

            # --------------------------------------------------
            # THICKNESS
            # --------------------------------------------------

            dpg.add_text(
                "Thickness:"
            )

            dpg.add_slider_int(
                tag="edge_thickness",
                default_value=2,
                min_value=1,
                max_value=10,
                width=-1,
                callback=editor.update_selected_edge_thickness,
            )

            dpg.add_spacer(
                height=12
            )

            # --------------------------------------------------
            # EDGE COLOR
            # --------------------------------------------------

            dpg.add_text(
                "Color:"
            )

            dpg.add_color_edit(
                tag="edge_color",
                default_value=(
                    180,
                    190,
                    220,
                    255,
                ),
                width=-1,
                no_inputs=True,
                callback=editor.update_selected_edge_color,
            )

            dpg.add_spacer(
                height=14
            )

            # --------------------------------------------------
            # EDGE INFORMATION
            # --------------------------------------------------

            dpg.add_separator()

            dpg.add_spacer(
                height=8
            )

            dpg.add_text(
                "Select an edge on the canvas"
            )

            dpg.add_text(
                "to edit its properties."
            )