from typing import List
from supervisely import ProjectMeta, ObjClass, TagMeta
from supervisely.nn.inference.session import Session, SessionJSON
from supervisely.app.widgets import (
    Container,
    Text,
    Select,
    Input,
    Checkbox,
    Editor,
    ModelInfo,
    SelectAppSession,
    Button,
    NotificationBox,
)
from src.ui.widgets import ClassesList, ClassesListPreview, TagsList, TagsListPreview

from src.ui.dtl.utils import (
    set_classes_list_preview,
    set_tags_list_preview,
)
import src.globals as g


### CONNECT MODEL AND MODEL INFO
def update_model_info_preview(
    session_id: int,
    connect_nn_model_info_empty_text: Text,
    connect_nn_model_info: ModelInfo,
    connect_nn_connect_btn: Button,
) -> None:
    connect_nn_model_info_empty_text.loading = True
    try:
        connect_nn_model_info.loading = True
        connect_nn_model_info.set_session_id(session_id)
        connect_nn_model_info.show()
        connect_nn_connect_btn.enable()
    except:
        connect_nn_connect_btn.disable()
        connect_nn_model_info_empty_text.set(
            (
                "Couldn't connect to the model. "
                "<br><br>Open app session page and make sure that the model has been successfully deployed - "
                f'<a href="{g.api.server_address}{g.api.app.get_url(session_id)}" target="_blank">open app</a>. '
                "<br>If the model is served, try to re-link Deploy and Apply NN nodes."
                "<br><br>If the problem still persists, check deployed model logs or contact support"
            ),
            status="error",
        )
        connect_nn_model_info.loading = False
        connect_nn_model_info_empty_text.loading = False
        return
    connect_nn_model_info.loading = False
    connect_nn_model_info_empty_text.loading = False
    connect_nn_model_info_empty_text.hide()


def get_model_settings(
    session_id: int,
    connect_notification: NotificationBox,
    connect_nn_model_selector: SelectAppSession,
    connect_nn_model_info: ModelInfo,
    connect_nn_model_info_empty_text: Text,
    is_deploy_connected: bool = False,
) -> tuple:
    try:
        session = Session(g.api, session_id)
        model_meta = session.get_model_meta()
        session_json = SessionJSON(g.api, session_id)
        model_info = session_json.get_session_info()
        model_settings = session.get_default_inference_settings()
    except:
        error_message = (
            "<br>Open app session page and make sure that the model has been successfully deployed - "
            f"<a href='{g.api.server_address}{g.api.app.get_url(session_id)}' target='_blank'>open app</a>. "
            "<br>If the model is served, try to re-link Deploy and Apply NN nodes."
            "<br><br>If the problem still persists, check deployed model logs, restart app session or contact support"
        )

        connect_notification.loading = False
        connect_notification.set(title="Couldn't connect to the model.", description=error_message)
        connect_nn_model_selector.set_session_id(None)
        if is_deploy_connected:
            connect_nn_model_selector.disable()
        else:
            connect_nn_model_selector.enable()

        connect_nn_model_info.hide()
        connect_nn_model_info_empty_text.set("Select model first", "info")
        connect_nn_model_info_empty_text.show()
        return None, None, None
    return model_meta, model_info, model_settings


def set_model_settings(model_settings: dict, inf_settings_editor: Editor) -> None:
    inf_settings_editor.loading = True
    model_settings_lines = [f"{key}: {value}" for key, value in model_settings.items()]
    inf_settings_editor.set_text("\n".join(model_settings_lines))
    inf_settings_editor.readonly = False
    inf_settings_editor.loading = False


def model_settings_from_yaml(_model_settings: dict, inf_settings_editor: Editor) -> dict:
    model_settings = {}

    model_settings_lines = {}
    if _model_settings != {}:
        model_settings_lines = inf_settings_editor.get_text().split("\n")
    for line in model_settings_lines:
        if line == "":
            continue
        key, value = line.split(": ")
        model_settings[key] = value
    return model_settings


def update_model_inference_settings(
    session_id: int, model_settings: dict, inf_settings_editor: Editor
) -> None:
    session = Session(g.api, session_id)
    model_settings = model_settings_from_yaml(model_settings, inf_settings_editor)
    session.set_inference_settings(model_settings)


### -----------------------------


### CLASSES AND TAGS
def set_model_classes(classes_list_widget: ClassesList, obj_classes: List[ObjClass]) -> List[str]:
    classes_list_widget.loading = True
    obj_classes = [obj_class for obj_class in obj_classes]

    classes_list_widget.set(obj_classes)
    classes_list_widget.select_all()

    saved_classes_settings = [obj_class.name for obj_class in obj_classes]
    classes_list_widget.loading = False
    return saved_classes_settings


def set_model_classes_preview(
    classes_list_widget: ClassesList,
    classes_list_preview: ClassesListPreview,
    saved_classes_settings: List[str],
    classes_list_text_preview: Text = None,
    classes_list_text_preview_title: str = "Classes",
) -> None:
    set_classes_list_preview(
        classes_list_widget,
        classes_list_preview,
        saved_classes_settings,
        classes_list_text_preview,
        classes_list_text_preview_title,
    )


def set_model_tags(tags_list_widget: TagsList, tag_metas: List[TagMeta]) -> List[str]:
    tags_list_widget.loading = True
    tag_metas = [tag_meta for tag_meta in tag_metas]

    tags_list_widget.set(tag_metas)
    tags_list_widget.select_all()

    saved_tags_settings = [tag_meta.name for tag_meta in tag_metas]
    tags_list_widget.loading = False
    return saved_tags_settings


def set_model_tags_preview(
    tags_list_widget: TagsList,
    tags_list_preview: TagsListPreview,
    saved_tags_settings: List[str],
    tags_list_edit_text: Text,
) -> None:
    set_tags_list_preview(
        tags_list_widget, tags_list_preview, saved_tags_settings, tags_list_edit_text, "Model Tags"
    )


### -----------------------------


### LOAD SETTINGS FROM PRESET (JSON)
def set_deployed_model_from_json(
    settings: dict, connect_nn_model_selector: SelectAppSession
) -> int:
    session_id = settings.get("session_id", None)
    if session_id is not None:
        try:
            connect_nn_model_selector.set_session_id(session_id)
        except:
            session_id = None
    return session_id


def set_model_info_from_json(
    settings: dict,
    connect_nn_model_info_empty_text: Text,
    connect_nn_model_info: ModelInfo,
    connect_nn_connect_btn: Button,
) -> dict:
    session_id = settings.get("session_id", None)
    model_info = settings.get("model_info", {})
    if model_info != {}:
        update_model_info_preview(
            session_id,
            connect_nn_model_info_empty_text,
            connect_nn_model_info,
            connect_nn_connect_btn,
        )
    return model_info


def set_model_meta_from_json(settings: dict) -> ProjectMeta:
    model_meta = settings.get("model_meta", {})
    if model_meta == {}:
        model_meta = ProjectMeta()
    else:
        model_meta = ProjectMeta.from_json(model_meta)
    return model_meta


def set_model_suffix_from_json(settings: dict, model_suffix_input: Input) -> None:
    model_suffix = settings.get("model_suffix", "model")
    model_suffix_input.set_value(model_suffix)


def set_use_model_suffix_from_json(settings: dict, always_add_suffix_checkbox: Checkbox) -> None:
    model_use_suffix = settings.get("use_model_suffix", False)
    if model_use_suffix:
        always_add_suffix_checkbox.check()
    else:
        always_add_suffix_checkbox.uncheck()


def set_model_conflict_from_json(settings: dict, resolve_conflict_method_selector: Select) -> None:
    model_conflict = settings.get("model_conflict", "merge")
    resolve_conflict_method_selector.set_value(model_conflict)


def set_model_settings_from_json(settings: dict, inf_settings_editor: Editor) -> dict:
    model_settings = settings.get("model_settings", {})
    if model_settings != {}:
        set_model_settings(model_settings, inf_settings_editor)
    return model_settings


def set_model_apply_method_from_json(settings: dict, apply_nn_methods_selector: Select) -> None:
    apply_method = settings.get("type", "image")
    apply_nn_methods_selector.set_value(apply_method)


### -----------------------------


### SET PREVIEW
def set_model_preview(model_info: dict, connect_nn_model_preview: Text) -> None:
    model_name = model_info.get("app_name", "Couldn't get model name")
    model_name_w_link = f'<a href="{g.api.server_address}{g.api.app.get_url(model_info["session_id"])}" target="_blank">{model_name}</a>'
    connect_nn_model_preview.set(model_name_w_link, "text")


def set_model_settings_preview(
    model_suffix_input: Input,
    always_add_suffix_checkbox: Checkbox,
    resolve_conflict_method_selector: Select,
    apply_nn_methods_selector: Select,
    suffix_preview: Text,
    use_suffix_preview: Text,
    conflict_method_preview: Text,
    apply_method_preview: Text,
) -> None:
    model_suffix = model_suffix_input.get_value()
    model_use_suffix = always_add_suffix_checkbox.is_checked()
    model_conflict = resolve_conflict_method_selector.get_label()
    apply_method = apply_nn_methods_selector.get_label()

    suffix_preview.set(f"Suffix: {model_suffix}", "text")
    use_suffix_preview.set(f"Always use suffix: {str(model_use_suffix)}", "text")
    conflict_method_preview.set(f"How to add prediction: {model_conflict}", "text")
    apply_method_preview.set(f"Apply method: {apply_method}", "text")

    suffix_preview.show()
    use_suffix_preview.show()
    conflict_method_preview.show()
    apply_method_preview.show()


### -----------------------------


### OTHER


# to use with deploy nodes
def reset_model(
    connect_nn_model_selector: SelectAppSession,
    connect_nn_model_info: ModelInfo,
    connect_nn_model_info_empty_text: Text,
    connect_nn_model_preview: Text,
    classes_list_widget: ClassesList,
    classes_list_preview: ClassesListPreview,
    classes_list_edit_container: Container,
    tags_list_widget: TagsList,
    tags_list_preview: TagsListPreview,
    tags_list_edit_container: Container,
    inf_settings_edit_container: Container,
    suffix_preview: Text,
    use_suffix_preview: Text,
    conflict_method_preview: Text,
    apply_method_preview: Text,
    connect_notification: NotificationBox,
    update_preview_btn: Button,
    model_separator: Text,
    classes_separator: Text,
    tags_separator: Text,
    connect_nn_disconnect_btn: Button,
):
    # reset model selector
    try:
        connect_nn_model_selector.set_session_id(None)
        connect_nn_model_selector.enable()
        connect_nn_disconnect_btn.disable()
        connect_nn_model_info.set_session_id(None)
    except:
        pass
    connect_nn_model_info.hide()
    connect_nn_model_info_empty_text.set("Select model first", "info")
    connect_nn_model_info_empty_text.show()
    connect_nn_model_preview.set("No model selected", "text")
    connect_nn_model_preview.hide()

    # reset classes
    classes_list_widget.set([])
    classes_list_preview.set([])

    classes_list_preview.hide()
    classes_list_edit_container.hide()
    classes_separator.hide()

    # reset tags
    tags_list_widget.set([])
    tags_list_preview.set([])
    tags_list_preview.hide()
    tags_list_edit_container.hide()
    tags_separator.hide()

    # reset settings
    inf_settings_edit_container.hide()
    suffix_preview.hide()
    use_suffix_preview.hide()
    conflict_method_preview.hide()
    apply_method_preview.hide()
    model_separator.hide()

    # reset layout
    connect_notification.set(
        title="Connect to deployed model",
        description="to select classes, tags and inference settings",
    )
    connect_notification.show()
    update_preview_btn.disable()


def set_default_model_settings(
    session_id: int,
    model_suffix_input: Input,
    always_add_suffix_checkbox: Checkbox,
    resolve_conflict_method_selector,
    apply_nn_methods_selector: Select,
    inf_settings_editor: Editor,
    connect_nn_model_preview: Text,
) -> None:
    model_suffix_input.loading = True
    model_suffix_input.set_value("model")
    model_suffix_input.loading = False

    always_add_suffix_checkbox.loading = True
    always_add_suffix_checkbox.uncheck()
    always_add_suffix_checkbox.loading = False

    resolve_conflict_method_selector.loading = True
    resolve_conflict_method_selector.set_value("merge")
    resolve_conflict_method_selector.loading = False

    apply_nn_methods_selector.loading = True
    apply_nn_methods_selector.set_value("image")
    apply_nn_methods_selector.loading = False

    inf_settings_editor.loading = True
    model_meta, model_info, model_settings = get_model_settings(session_id)
    set_model_preview(model_info, connect_nn_model_preview)
    set_model_settings(model_settings, inf_settings_editor)
    inf_settings_editor.loading = False


def show_node_gui(
    connect_nn_model_preview: Text,
    classes_list_edit_container: Container,
    classes_list_preview: ClassesListPreview,
    tags_list_edit_container: Container,
    tags_list_preview: TagsListPreview,
    inf_settings_edit_container: Container,
) -> None:
    connect_nn_model_preview.show()
    classes_list_edit_container.show()
    classes_list_preview.show()
    tags_list_edit_container.show()
    tags_list_preview.show()
    inf_settings_edit_container.show()


### -----------------------------


### Legacy connection to model
# def connect_to_model(
#     session_id: int,
#     current_meta: ProjectMeta,
#     model_info: ProjectMeta,
#     update_preview_btn: Button,
#     connect_nn_model_info: ModelInfo,
#     connect_nn_model_preview: Text,
# ):
#     update_preview_btn.disable()

#     session_id = connect_nn_model_info._session_id
#     if session_id is None:
#         return

#     try:
#         session = Session(g.api, session_id)
#         model_meta = session.get_model_meta()

#         session_json = SessionJSON(g.api, session_id)
#         model_info = session_json.get_session_info()
#     except:
#         raise ConnectionError("Couldn't connect to model. Check deployed model logs")

#     model_name = model_info["app_name"]
#     connect_nn_model_preview.set(model_name, "text")

#     # has_classes_conflict = check_conflict_classes(current_meta, model_meta)
#     # has_tags_conflict = check_conflict_tags(current_meta, model_meta)

#     if not has_classes_conflict and not has_tags_conflict:
#         update_preview_btn.enable()
#         g.updater("metas")
#     return current_meta, model_meta

### CHECK CURRENT AND MODEL META CONFLICTS | WON'T USE
# def check_conflict_classes(current_meta: ProjectMeta, model_meta: ProjectMeta) -> bool:
#     match_obj_classes_widget.hide()
#     classes_list_widget.hide()
#     has_classes_conflict = False
#     original_classes = []
#     conflict_classes = []
#     for curr_obj_class in current_meta.obj_classes:
#         model_obj_class = model_meta.get_obj_class(curr_obj_class.name)
#         if model_obj_class is not None:
#             if curr_obj_class.geometry_type != model_obj_class.geometry_type:
#                 original_classes.append(curr_obj_class)
#                 conflict_classes.append(model_obj_class)
#     if len(conflict_classes) > 0:
#         has_classes_conflict = True
#         match_obj_classes_widget.set(original_classes, conflict_classes)
#         classes_list_widget_notification.set(
#             title="Classes conflict",
#             description="Project meta and model meta have classes with the same names, but different shapes. Disable conflicting classes in previous nodes or select other model.",
#         )
#         match_obj_classes_widget.show()
#     else:
#         classes_list_widget_notification.set(
#             title="No classes",
#             description="Connect to deployed model to display classes.",
#         )
#         if len(model_meta.obj_classes) == 0:
#             classes_list_widget_notification.show()
#     if not has_classes_conflict:
#         classes_list_widget.show()
#     if len(model_meta.obj_classes) > 0 and not has_classes_conflict:
#         set_model_classes(model_meta)
#     else:
#         set_model_classes(ProjectMeta())
#     return has_classes_conflict


# def check_conflict_tags(current_meta: ProjectMeta, model_meta: ProjectMeta) -> bool:
#     tags_list_widget_notification.hide()
#     tags_list_widget.hide()
#     has_tags_conflict = False
#     original_tags = []
#     conflict_tags = []
#     for curr_tag_meta in current_meta.tag_metas:
#         model_tag_meta = model_meta.get_tag_meta(curr_tag_meta.name)
#         if model_tag_meta is not None:
#             original_tags.append(curr_tag_meta)
#             conflict_tags.append(model_tag_meta)
#     if len(conflict_tags) > 0:
#         match_tag_metas_widget.set(original_tags, conflict_tags)
#         conflict_stat = match_tag_metas_widget.get_stat()
#         if (
#             conflict_stat["different_value_type"] > 0
#             or conflict_stat["different_one_of_options"] > 0
#             or conflict_stat["different_value_type_suffix"] > 0
#             or conflict_stat["different_one_of_options_suffix"] > 0
#         ):
#             has_tags_conflict = True
#             tags_list_widget_notification.set(
#                 title="Tags conflict",
#                 description="Project meta and model meta have tag metas with the same names, but different values. Disable conflicting tags in previous nodes or select other model.",
#             )
#     if len(model_meta.tag_metas) == 0:
#         tags_list_widget_notification.set(
#             title="No tags",
#             description="Connect to deployed model to display tags.",
#         )
#     if not has_tags_conflict:
#         tags_list_widget_notification.show()
#         tags_list_widget.show()
#     else:
#         match_tag_metas_widget.show()
#         tags_list_widget.hide()
#     if len(model_meta.tag_metas) > 0 and not has_tags_conflict:
#         set_model_tags(model_meta)
#     else:
#         set_model_tags(ProjectMeta())
#     return has_tags_conflict
### -----------------------------
