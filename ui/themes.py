import dearpygui.dearpygui as dpg

def create_themes() -> None:
    # Main application theme
    with dpg.theme(tag="app_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg,
                (18, 22, 30)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ChildBg,
                (24, 29, 39)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Border,
                (55, 65, 81)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Text,
                (225, 230, 240)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Separator,
                (55, 65, 81)
            )

            dpg.add_theme_color(
                dpg.mvThemeCol_Button,
                (38, 46, 61)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (55, 85, 145)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                (65, 105, 190)
            )

            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg,
                (31, 38, 50)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgHovered,
                (42, 51, 67)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgActive,
                (49, 61, 82)
            )

            dpg.add_theme_color(
                dpg.mvThemeCol_Header,
                (45, 66, 110)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderHovered,
                (58, 85, 145)
            )

            dpg.add_theme_style(
                dpg.mvStyleVar_WindowPadding,
                10,
                10
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FramePadding,
                8,
                6
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ItemSpacing,
                8,
                8
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding,
                6
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ChildRounding,
                8
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_WindowRounding,
                8
            )

    # Blue tool button theme
    with dpg.theme(tag="tool_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(
                dpg.mvThemeCol_Button,
                (34, 43, 58)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (52, 85, 160)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                (64, 105, 210)
            )

            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding,
                7
            )

    # Canvas theme
    with dpg.theme(tag="canvas_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(
                dpg.mvThemeCol_ChildBg,
                (20, 24, 32)
            )

            dpg.add_theme_color(
                dpg.mvThemeCol_Border,
                (48, 58, 74)
            )

            dpg.add_theme_style(
                dpg.mvStyleVar_ChildRounding,
                8
            )
