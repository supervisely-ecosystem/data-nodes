import json
import os
import tempfile
from os.path import dirname, join, realpath
from typing import Optional

from supervisely.app.widgets import (
    Button,
    Container,
    Editor,
    Field,
    Input,
    InputNumber,
    NodesFlow,
    Select,
    TeamFilesSelector,
    Text,
)

import src.globals as g
from src.exceptions import BadSettingsError
from src.ui.dtl.Action import VideoAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_layer_docs,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)

TEMPLATE_PATH = join(dirname(realpath(__file__)), "template.py")
DEFAULT_PARAMS = {"width": 320, "threshold": 5.0, "min_length": 25}


def _read_template() -> str:
    with open(TEMPLATE_PATH) as f:
        return f.read()


def _list_scripts() -> list:
    if not g.api.file.dir_exists(g.TEAM_ID, g.CUSTOM_CODE_DIR):
        return []
    infos = g.api.file.list(g.TEAM_ID, g.CUSTOM_CODE_DIR, return_type="fileinfo")
    return sorted(info.path for info in infos if info.path.endswith(".py"))


def _download_text(path: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = join(tmp_dir, os.path.basename(path))
        g.api.file.download(g.TEAM_ID, path, local_path)
        with open(local_path) as f:
            return f.read()


def _upload_text(path: str, text: str) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = join(tmp_dir, os.path.basename(path))
        with open(local_path, "w") as f:
            f.write(text)
        g.api.file.upload(g.TEAM_ID, local_path, path)


def _to_script_path(name: str) -> str:
    """A bare name goes to the default folder; a path starting with / is used as it is."""
    name = name.strip()
    if not name.endswith(".py"):
        name += ".py"
    if name.startswith("/"):
        return name
    return g.CUSTOM_CODE_DIR + name


class CustomCodeAction(VideoAction):
    name = "custom_code"
    title = "Custom Code"
    docs_url = ""
    description = "Run your own Python script on every video and keep the frame ranges it returns."
    md_description = get_layer_docs(dirname(realpath(__file__)))
    width = 360

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        script_path = None  # path in Team Files of the script in the editor
        saved_text = ""  # the editor text that is in Team Files
        saved_settings = {"script_path": "", "params": dict(DEFAULT_PARAMS), "workers": 0}

        # Node
        script_text = Text("No script selected", status="text", font_size=get_text_font_size())
        edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        node_container = get_set_settings_container(script_text, edit_btn)

        # Sidebar: pick a script
        scripts_select = Select(items=[], placeholder="Select a script", filterable=True, size="small")
        scripts_refresh_btn = Button(
            "", icon="zmdi zmdi-refresh", button_type="text", button_size="small"
        )
        scripts_open_btn = Button("Open", button_size="small", plain=True)
        template_btn = Button(
            "New from template", button_size="small", plain=True, icon="zmdi zmdi-file-plus"
        )
        scripts_field = Field(
            Container(
                [scripts_select, scripts_refresh_btn, scripts_open_btn, template_btn],
                direction="horizontal",
                fractions=[1, 0, 0, 0],
                overflow="wrap",
            ),
            "Script",
            f"Scripts of the team in Team Files {g.CUSTOM_CODE_DIR}",
        )
        files_selector = TeamFilesSelector(
            g.TEAM_ID, selection_file_type="file", max_height=250, initial_folder="/"
        )
        files_open_btn = Button("Open selected file", button_size="small", plain=True)
        files_field = Field(
            Container([files_selector, files_open_btn]),
            "Or any .py file in Team Files",
        )

        # Sidebar: edit and save
        status_text = Text("", status="text", font_size=get_text_font_size())
        editor = Editor(
            initial_text="",
            height_px=450,
            language_mode="python",
            restore_default_button=False,
        )
        save_btn = Button("Save", icon="zmdi zmdi-floppy", button_size="small")
        save_as_input = Input(placeholder="new_script.py or /full/path/script.py", size="small")
        save_as_btn = Button("Save as", icon="zmdi zmdi-copy", button_size="small", plain=True)
        save_message = Text("", font_size=get_text_font_size())
        save_message.hide()
        editor_field = Field(
            Container(
                [
                    status_text,
                    editor,
                    Container(
                        [save_btn, save_as_input, save_as_btn],
                        direction="horizontal",
                        fractions=[0, 1, 0],
                    ),
                    save_message,
                ]
            ),
            "Code",
            "Defines process(video_path, video_info, ann, params) and returns the frame ranges to keep",
        )

        # Sidebar: run settings
        params_editor = Editor(
            initial_text=json.dumps(DEFAULT_PARAMS, indent=4),
            height_px=140,
            language_mode="json",
            restore_default_button=False,
        )
        params_field = Field(params_editor, "Parameters", "JSON passed to the script as params")
        workers_input = InputNumber(value=0, min=0, step=1, size="small")
        workers_field = Field(
            workers_input,
            "Workers",
            "Videos processed at the same time, one process each. 0 uses all CPU cores",
        )
        settings_message = Text("", status="error", font_size=get_text_font_size())
        settings_message.hide()
        settings_save_btn = Button("Save settings", icon="zmdi zmdi-floppy", emit_on_click="save")

        sidebar_container = Container(
            [
                scripts_field,
                files_field,
                editor_field,
                params_field,
                workers_field,
                settings_message,
                settings_save_btn,
            ]
        )

        def _show_message(widget: Text, text: str, status: str):
            widget.set(text, status)
            widget.show()

        def _update_status():
            if script_path is None and not editor.get_text().strip():
                status_text.set("Open a script or start a new one from the template", "text")
            elif script_path is None:
                status_text.set("New script, not saved to Team Files yet", "warning")
            else:
                status_text.set(f"Team Files: {script_path}", "text")

        def _update_node_text():
            path = saved_settings["script_path"]
            script_text.set(path if path else "No script selected", "text")

        def _open(path: str):
            nonlocal script_path, saved_text
            if not path.endswith(".py"):
                _show_message(save_message, f"Not a Python file: {path}", "error")
                return
            try:
                text = _download_text(path)
            except Exception as e:
                _show_message(save_message, f"Could not open {path}: {e}", "error")
                return
            script_path, saved_text = path, text
            editor.set_text(text, language_mode="python")
            save_message.hide()
            saved_settings["script_path"] = path
            _update_status()
            _update_node_text()

        def _refresh_scripts():
            scripts_select.set(
                [
                    Select.Item(path, path[len(g.CUSTOM_CODE_DIR) :])
                    for path in _list_scripts()
                ]
            )

        def _save(path: str) -> None:
            nonlocal script_path, saved_text
            text = editor.get_text()
            _upload_text(path, text)
            script_path, saved_text = path, text
            saved_settings["script_path"] = path
            _update_status()
            _update_node_text()

        @scripts_refresh_btn.click
        def scripts_refresh_btn_cb():
            _refresh_scripts()

        @scripts_open_btn.click
        def scripts_open_btn_cb():
            path = scripts_select.get_value()
            if path:
                _open(path)

        @files_open_btn.click
        def files_open_btn_cb():
            paths = files_selector.get_selected_paths()
            if len(paths) == 0:
                _show_message(save_message, "Select a .py file in Team Files first", "warning")
                return
            _open(paths[0])

        @template_btn.click
        def template_btn_cb():
            nonlocal script_path, saved_text
            script_path, saved_text = None, ""
            editor.set_text(_read_template(), language_mode="python")
            saved_settings["script_path"] = ""
            _show_message(save_message, "Use Save as to name the new script", "info")
            _update_status()
            _update_node_text()

        @save_btn.click
        def save_btn_cb():
            if script_path is None:
                _show_message(save_message, "Use Save as to name the new script", "warning")
                return
            try:
                _save(script_path)
            except Exception as e:
                _show_message(save_message, f"Not saved: {e}", "error")
                return
            _show_message(save_message, f"Saved {script_path}", "success")

        @save_as_btn.click
        def save_as_btn_cb():
            name = save_as_input.get_value()
            if not name or not name.strip():
                _show_message(save_message, "Enter a file name", "warning")
                return
            path = _to_script_path(name)
            if g.api.file.exists(g.TEAM_ID, path):
                _show_message(save_message, f"{path} already exists", "error")
                return
            try:
                _save(path)
            except Exception as e:
                _show_message(save_message, f"Not saved: {e}", "error")
                return
            _refresh_scripts()
            _show_message(save_message, f"Saved {path}", "success")

        def _read_run_settings() -> bool:
            try:
                params = json.loads(params_editor.get_text() or "{}")
                if not isinstance(params, dict):
                    raise ValueError("Parameters must be a JSON object")
            except ValueError as e:
                _show_message(settings_message, f"Parameters are not valid JSON: {e}", "error")
                return False
            settings_message.hide()
            saved_settings["params"] = params
            saved_settings["workers"] = int(workers_input.get_value() or 0)
            return True

        @settings_save_btn.click
        def settings_save_btn_cb():
            _read_run_settings()

        def before_run():
            """Every run uses a file in Team Files: save unsaved edits first."""
            nonlocal script_path
            if not _read_run_settings():
                raise BadSettingsError("Custom Code: the Parameters are not valid JSON", extra={})
            text = editor.get_text()
            if script_path is None:
                if not text.strip():
                    raise BadSettingsError("Custom Code: select or write a script", extra={})
                _save(g.api.file.get_free_name(g.TEAM_ID, _to_script_path("script")))
            elif text != saved_text:
                _save(script_path)

        def get_settings(options_json: dict) -> dict:
            return dict(saved_settings)

        def _set_settings_from_json(settings: dict):
            nonlocal script_path, saved_text
            params = settings.get("params", dict(DEFAULT_PARAMS))
            params_editor.set_text(json.dumps(params, indent=4), language_mode="json")
            workers_input.value = settings.get("workers", 0)
            saved_settings["params"] = params
            saved_settings["workers"] = settings.get("workers", 0)
            path = settings.get("script_path", "")
            if path and path != script_path:
                if g.api.file.exists(g.TEAM_ID, path):
                    _open(path)
                else:
                    script_path, saved_text = None, ""
                    saved_settings["script_path"] = ""
                    _show_message(save_message, f"Script not found in Team Files: {path}", "error")
            _update_status()
            _update_node_text()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _refresh_scripts()
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Script",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=node_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(sidebar_container),
                        sidebar_width=760,
                    ),
                ),
            ]
            return {
                "src": [],
                "dst": [],
                "settings": settings_options,
            }

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_settings=get_settings,
            need_preview=False,
            before_run=before_run,
        )
