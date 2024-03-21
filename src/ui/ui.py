from supervisely.app.widgets import Container, Flexbox, Button, Dialog

from src.ui.tabs.configure import layout as configure_tab_layout
from src.ui.tabs.presets import (
    update_save_dialog,
    update_load_dialog,
    save_dialog,
    load_dialog,
)
from src.ui.tabs.run import layout as run_layout, circle_progress, show_run_dialog_btn
from src.globals import error_dialog


run_dialog = Dialog(title="Run", content=run_layout)
save_button = Button(
    "save",
    icon="zmdi zmdi-floppy",
    button_size="large",
    button_type="text",
    style="border: 1px solid rgb(191, 203, 217); color: black; margin: 10px 0 0; background-color: white; padding: 9px 13px; border-radius: 6px; font-size: 12px; text-transform: uppercase; font-weight: 500; height: 32px;",
)
load_button = Button(
    "load",
    icon="zmdi zmdi-cloud-download",
    button_size="large",
    button_type="text",
    style="border: 1px solid rgb(191, 203, 217); color: black; margin: 10px 0 0; background-color: white; padding: 9px 13px; border-radius: 6px; font-size: 12px; text-transform: uppercase; font-weight: 500; height: 32px;",
)

header = Container(
    [
        Flexbox(
            widgets=[
                Flexbox([show_run_dialog_btn, circle_progress]),
                save_button,
                load_button,
                # Container([Empty(style="padding: 4px;"), connect_node_checkbox]),
            ],
            gap=7,
        )
    ],
    style="height: 55px;",
)
layout = Container(
    widgets=[error_dialog, run_dialog, save_dialog, load_dialog, configure_tab_layout],
    gap=0,
)


@show_run_dialog_btn.click
def show_run_dialog():
    run_dialog.show()


@save_button.click
def save_presets_dialog():
    save_dialog.show()
    update_save_dialog()


@load_button.click
def load_presets_dialog():
    load_dialog.show()
    update_load_dialog()
