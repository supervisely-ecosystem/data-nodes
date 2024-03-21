from typing import List, Literal, Union
from os.path import join, exists

from supervisely import ObjClass, ObjClassCollection, TagMeta, TagMetaCollection
from supervisely.app.widgets import (
    NodesFlow,
    Container,
    Text,
    Button,
    Empty,
    ClassesTable,
    Flexbox,
    TagsTable,
)

from src.ui.widgets import (
    ClassesMapping,
    ClassesMappingPreview,
    ClassesList,
    ClassesListPreview,
    TagsList,
    TagsListPreview,
    MembersList,
    MembersListPreview,
)
from src.exceptions import BadSettingsError


# Classes Mapping utils


def _unpack_classes_mapping_settings(
    mapping: dict, all_obj_classes_names, missing_value: Literal["default", "ignore"] = "ignore"
):
    unpacked = {}
    if mapping == "default":
        for obj_class_name in all_obj_classes_names:
            unpacked[obj_class_name] = obj_class_name
        return unpacked
    missing_value = f"__{missing_value}__"
    other = mapping.get("__other__", None)
    for obj_class_name in all_obj_classes_names:
        old_value = mapping.get(obj_class_name, other)
        if old_value is None:
            old_value = missing_value
        unpacked[obj_class_name] = old_value
    return unpacked


def _pack_classes_mapping_settings(
    mapping: dict,
    default_action: Literal["skip", "keep", "copy"] = "skip",
    ignore_action: Literal["skip", "keep", "empty"] = "skip",
    other_allowed: bool = False,
):
    new_mapping = {}
    for name, value in mapping.items():
        if value in ["__default__", name]:
            if default_action == "skip":
                continue
            elif default_action == "keep":
                new_mapping[name] = "__default__"
            elif default_action == "copy":
                new_mapping[name] = name
        elif value in ["__ignore__", ""]:
            if ignore_action == "skip":
                continue
            elif ignore_action == "keep":
                new_mapping[name] = "__ignore__"
            elif ignore_action == "empty":
                new_mapping[name] = ""
        else:
            new_mapping[name] = value
    if other_allowed:
        default = [name for name, value in new_mapping.items() if value == "__default__"]
        ignore = [name for name, value in new_mapping.items() if value == "__ignore__"]
        if len(ignore) > 0:
            for name in ignore:
                del new_mapping[name]
            new_mapping["__other__"] = "__ignore__"
        elif len(default) > 0:
            for name in default:
                del new_mapping[name]
            new_mapping["__other__"] = "__default__"
    return new_mapping


def classes_list_to_mapping(
    selected_classes: list,
    all_classes: list,
    other: Literal["skip", "default", "ignore"] = "skip",
    default_allowed: bool = False,
):
    if default_allowed and len(selected_classes) == len(all_classes):
        return "default"
    mapping = {}
    for cls_name in selected_classes:
        mapping[cls_name] = cls_name
    if other == "skip":
        return mapping
    if len(mapping) < len(all_classes):
        mapping["__other__"] = f"__{other}__"
    return mapping


def mapping_to_list(mapping: dict, rename: bool = False):
    """Converts mapping to list"""
    classes = []
    for cls_name, cls_value in mapping.items():
        if cls_value == "__ignore__":
            continue
        if rename:
            classes.append(cls_value if cls_value != "__default__" else cls_name)
        else:
            classes.append(cls_name)
    return classes


def get_classes_mapping_value(
    classes_mapping_widget: ClassesMapping,
    default_action: Literal["skip", "keep", "copy"] = "skip",
    ignore_action: Literal["skip", "keep", "empty"] = "skip",
    other_allowed: bool = False,
    default_allowed: bool = False,
):
    mapping = classes_mapping_widget.get_mapping()
    if default_allowed:
        default = [cls_name for cls_name, cls_values in mapping.items() if cls_values["default"]]
        classes = classes_mapping_widget.get_classes()
        if len(default) == len(classes):
            return "default"

    result_mapping = _pack_classes_mapping_settings(
        {k: v["value"] for k, v in mapping.items()},
        default_action=default_action,
        ignore_action=ignore_action,
        other_allowed=other_allowed,
    )

    return result_mapping


def classes_mapping_settings_changed_meta(
    settings: dict,
    old_obj_classes: Union[List[ObjClass], ObjClassCollection],
    new_obj_classes: Union[List[ObjClass], ObjClassCollection],
    default_action: Literal["skip", "keep", "copy"] = "skip",
    ignore_action: Literal["skip", "keep", "empty"] = "skip",
    new_value: Literal["default", "ignore"] = "ignore",
    other_allowed: bool = False,
):
    if settings == "default":
        return "default"
    new_settings = {}

    old_obj_classes_names = {obj_class.name for obj_class in old_obj_classes}
    new_obj_classes_names = {obj_class.name for obj_class in new_obj_classes}

    # unpack old settings
    new_settings = _unpack_classes_mapping_settings(settings, old_obj_classes_names, new_value)

    # remove obj classes that are not in new obj classes
    for obj_class_name in old_obj_classes_names:
        if obj_class_name not in new_obj_classes_names:
            del new_settings[obj_class_name]

    # add new object classes
    for obj_class_name in new_obj_classes_names:
        if obj_class_name not in old_obj_classes_names:
            new_settings[obj_class_name] = f"__{new_value}__"

    # pack new settings
    new_settings = _pack_classes_mapping_settings(
        new_settings,
        default_action=default_action,
        ignore_action=ignore_action,
        other_allowed=other_allowed,
    )
    return new_settings


def set_classes_mapping_preview(
    classes_mapping_widget: ClassesMapping,
    classes_mapping_preview_widget: ClassesMappingPreview,
    classes_mapping_settings: dict,
    default_action: Literal["skip", "keep", "copy"] = "skip",
    ignore_action: Literal["skip", "keep", "empty"] = "skip",
    missing_value: Literal["default", "ignore"] = "ignore",
    classes_mapping_preview_text: Text = None,
    classes_mapping_text_preview_title="Classes Mapping",
    show_counter: bool = True,
):
    obj_classes = classes_mapping_widget.get_classes()
    obj_classes_names = [obj_class.name for obj_class in obj_classes]
    unpacked = _unpack_classes_mapping_settings(
        classes_mapping_settings, obj_classes_names, missing_value=missing_value
    )
    packed = _pack_classes_mapping_settings(
        unpacked, default_action=default_action, ignore_action=ignore_action, other_allowed=False
    )
    classes_mapping_preview_widget.set(
        [obj_class for obj_class in obj_classes if obj_class.name in packed], packed
    )

    if classes_mapping_preview_text is not None:
        if show_counter:
            classes_mapping_preview_text.set(
                f"{classes_mapping_text_preview_title}: {len(packed)} / {len(obj_classes)}", "text"
            )
        else:
            classes_mapping_preview_text.set({classes_mapping_text_preview_title}, "text")


def set_classes_mapping_settings_from_json(
    classes_mapping_widget: ClassesMapping,
    settings: dict,
    missing_in_settings_action: Literal["raise", "ignore"] = "raise",
    missing_in_meta_action: Literal["raise", "ignore"] = "raise",
    select: Literal["all", "none", "unique", "default", "empty", "skip_select"] = "skip_select",
):
    if settings == "default":
        classes_mapping_widget.set_default()
        return
    classes_mapping = {}
    other_default = settings.get("__other__", None) == "__default__"
    other_ignore = settings.get("__other__", None) == "__ignore__"
    obj_classes = classes_mapping_widget.get_classes()

    # check that all the classes from settings are present in meta
    if missing_in_meta_action == "raise":
        if isinstance(obj_classes, ObjClassCollection):
            in_func = lambda cls_name: obj_classes.has_key(cls_name)
        else:
            in_func = lambda cls_name: cls_name in [obj_class.name for obj_class in obj_classes]
        for cls_name in settings.keys():
            if cls_name != "__other__" and not in_func(cls_name):
                raise BadSettingsError("Class not found in meta", extra={"class": cls_name})

    # set classes mapping to widget
    for obj_class in obj_classes:
        if obj_class.name in settings:
            value = settings[obj_class.name]
            if value == "__default__":
                value = obj_class.name
            if value == "__ignore__":
                value = ""
            classes_mapping[obj_class.name] = value
        elif other_default:
            classes_mapping[obj_class.name] = obj_class.name
        elif other_ignore:
            classes_mapping[obj_class.name] = ""
        elif missing_in_settings_action == "raise":
            raise BadSettingsError(
                "Class not found in settings",
                extra={"class": obj_class.name},
            )
        else:
            classes_mapping[obj_class.name] = ""
    classes_mapping_widget.set_mapping(classes_mapping)

    if select != "skip_select":
        if select == "all":
            classes_mapping_widget.select_all()
        elif select == "none":
            classes_mapping_widget.deselect_all()
        elif select == "unique":
            to_select = [
                cls_name
                for cls_name, cls_value in classes_mapping.items()
                if cls_name != cls_value
                and cls_value != ""
                and cls_value != "__default__"
                and cls_value != "__ignore__"
            ]
            classes_mapping_widget.select(to_select)
        elif select == "empty":
            to_select = [
                cls_name
                for cls_name, cls_value in classes_mapping.items()
                if cls_value == "" or cls_name == "__ignore__"
            ]
            classes_mapping_widget.select(to_select)
        elif select == "default":
            to_select = [
                cls_name
                for cls_name, cls_value in classes_mapping.items()
                if cls_value == cls_name or cls_name == "__default__"
            ]
            classes_mapping_widget.select(to_select)


# Classes List utils


def get_classes_list_value(
    classes_list_widget: Union[ClassesList, ClassesTable], multiple: bool = True
):
    selected = classes_list_widget.get_selected_classes()
    if multiple:
        if isinstance(classes_list_widget, ClassesList):
            return [obj_class.name for obj_class in selected]
        else:
            return [obj_class for obj_class in selected]
    else:
        if len(selected) == 0:
            return ""
        elif isinstance(classes_list_widget, ClassesList):
            return selected[0].name
        return selected[0].name


def classes_list_settings_changed_meta(
    settings: Union[list, str],
    new_obj_classes: Union[List[ObjClass], ObjClassCollection],
):
    names = {obj_class.name for obj_class in new_obj_classes}
    if isinstance(settings, str):
        if settings == "default":
            return "default"
        return settings if settings in names else ""
    return [class_name for class_name in settings if class_name in names]


def set_classes_list_preview(
    classes_list_widget: Union[ClassesList, ClassesMapping, ClassesTable],
    classes_list_preview_widget: ClassesListPreview,
    classes_list_settings: Union[list, str],
    classes_list_text_preview: Text = None,
    classes_list_text_preview_title: str = "Classes",
    show_counter: bool = True,
):
    if isinstance(classes_list_settings, str):
        if classes_list_settings == "default":
            if isinstance(classes_list_widget, ClassesMapping):
                classes_list_preview_widget.set(classes_list_widget.get_classes())
            elif isinstance(classes_list_widget, ClassesList):
                classes_list_preview_widget.set(classes_list_widget.get_all_classes())
            else:
                classes_list_widget.select_all()
                meta = classes_list_widget.project_meta
                if meta is None:
                    all_classes = []
                else:
                    all_classes = [obj_class for obj_class in meta.obj_classes]
                classes_list_preview_widget.set(all_classes)

        names = [classes_list_settings]
    else:
        names = classes_list_settings

    if not isinstance(classes_list_widget, ClassesTable):
        # both ClassesList and ClassesMapping
        obj_classes = classes_list_widget.get_all_classes()
    else:
        if classes_list_widget.project_meta is None:
            obj_classes = []
        else:
            obj_classes = [obj_class for obj_class in classes_list_widget.project_meta.obj_classes]

    if classes_list_settings != "default":
        classes_list_preview_widget.set(
            [obj_class for obj_class in obj_classes if obj_class.name in names]
        )

    # set classes N preview
    if classes_list_text_preview is not None:
        if isinstance(classes_list_widget, ClassesList) or isinstance(
            classes_list_widget, ClassesMapping
        ):
            total_classes_n = len(obj_classes)
            selected_classes_n = len(classes_list_widget.get_selected_classes())
        else:
            if classes_list_widget.project_meta is None:
                total_classes_n = 0
            else:
                total_classes_n = len(classes_list_widget.project_meta.obj_classes)
            if len(names) > 0 and names[0] == "default":
                selected_classes_n = total_classes_n
            else:
                selected_classes_n = len(names)

        if show_counter:
            classes_list_text_preview.set(
                f"{classes_list_text_preview_title}: {selected_classes_n} / {total_classes_n}",
                "text",
            )
        else:
            classes_list_text_preview.set(f"{classes_list_text_preview_title}", "text")


def set_classes_list_settings_from_json(
    classes_list_widget: Union[ClassesList, ClassesTable], settings: Union[list, str]
):
    if isinstance(settings, str):
        if settings == "default":
            classes_list_widget.select_all()
            return
        settings = [settings]

    if isinstance(classes_list_widget, ClassesList):
        classes_list_widget.select(settings)
    elif isinstance(classes_list_widget, ClassesTable):
        classes_list_widget.select_classes(settings)
        return


# tags mapping utils


def tags_list_to_mapping(
    selected_tags: list,
    all_tags: list,
    other: Literal["skip", "default", "ignore"] = "skip",
    default_allowed: bool = False,
):
    if default_allowed and len(selected_tags) == len(all_tags):
        return "default"
    mapping = {}
    for cls_name in selected_tags:
        mapping[cls_name] = cls_name
    if other == "skip":
        return mapping
    if len(mapping) < len(all_tags):
        mapping["__other__"] = f"__{other}__"
    return mapping


# tags list utils


def tags_list_settings_changed_meta(
    settings: Union[list, str],
    new_tag_metas: Union[List[TagMeta], TagMetaCollection],
):
    names = {tag_meta.name for tag_meta in new_tag_metas}
    if isinstance(settings, str):
        if settings == "default":
            return "default"
        return settings if settings in names else ""
    return [tag_name for tag_name in settings if tag_name in names]


def set_tags_list_settings_from_json(tags_list_widget: TagsList, settings: Union[list, str]):
    if isinstance(settings, str):
        if settings == "default":
            tags_list_widget.select_all()
            return
        settings = [settings]
    if isinstance(tags_list_widget, TagsList):
        tags_list_widget.select(settings)
        return


def set_tags_list_preview(
    tags_list_widget: Union[TagsList, TagsTable],
    tags_list_preview_widget: TagsListPreview,
    tags_list_settings: Union[list, str],
    tags_list_text_preview: Text = None,
    tags_list_text_preview_title: str = "Tags",
    show_counter: bool = True,
):
    if isinstance(tags_list_settings, str):
        if tags_list_settings == "default":
            if isinstance(tags_list_widget, TagsList):
                tags_list_preview_widget.set(tags_list_widget.get_all_tags())
            else:
                tags_list_widget.select_all()
                meta = tags_list_widget.project_meta
                if meta is None:
                    all_tags = []
                else:
                    all_tags = [obj_class for obj_class in meta.tag_metas]
                tags_list_preview_widget.set(all_tags)

        names = [tags_list_settings]
    else:
        names = tags_list_settings

    if not isinstance(tags_list_widget, TagsTable):
        # both TagsList and TagsMapping
        tag_metas = tags_list_widget.get_all_tags()
    else:
        if tags_list_widget.project_meta is None:
            tag_metas = []
        else:
            tag_metas = [tag_meta for tag_meta in tags_list_widget.project_meta.tag_metas]

    if tags_list_settings != "default":
        tags_list_preview_widget.set([tag_meta for tag_meta in tag_metas if tag_meta.name in names])

    # set tags N preview
    if tags_list_text_preview is not None:
        if isinstance(tags_list_widget, TagsList):
            total_tags_n = len(tag_metas)
            selected_tags_n = len(tags_list_widget.get_selected_tags())
        else:
            if tags_list_widget.project_meta is None:
                total_tags_n = 0
            else:
                total_tags_n = len(tags_list_widget.project_meta.tag_metas)
            if len(names) > 0 and names[0] == "default":
                selected_tags_n = total_tags_n
            else:
                selected_tags_n = len(names)

        if show_counter:
            tags_list_text_preview.set(
                f"{tags_list_text_preview_title}: {selected_tags_n} / {total_tags_n}", "text"
            )
        else:
            tags_list_text_preview.set(f"{tags_list_text_preview_title}", "text")


def get_tags_list_value(tags_list_widget: Union[TagsList, TagsTable], multiple: bool = True):
    selected = tags_list_widget.get_selected_tags()
    if multiple:
        if isinstance(tags_list_widget, TagsList):
            return [tag_meta.name for tag_meta in selected]
        else:
            return [tag_meta for tag_meta in selected]
    else:
        if len(selected) == 0:
            return ""
        elif isinstance(tags_list_widget, TagsList):
            return selected[0].name
        return selected[0].name


# members
def set_members_list_settings_from_json(
    members_list_widget: MembersList, settings: Union[list, str]
):
    if isinstance(settings, str):
        if settings == "default":
            members_list_widget.select_all()
            return
        settings = [settings]

    if isinstance(settings, list):
        if len(settings) == 0:
            members_list_widget.deselect_all()
            return
        else:
            if isinstance(settings[0], int):
                settings = [
                    user.login
                    for user in members_list_widget.get_all_members()
                    if user.id in settings
                ]

    if isinstance(members_list_widget, MembersList):
        members_list_widget.select(settings)
        return


def set_members_list_preview(
    members_list_widget: MembersList,
    members_list_preview_widget: MembersListPreview,
    members_list_settings: Union[list, str],
):
    if isinstance(members_list_settings, str):
        if members_list_settings == "default":
            if isinstance(members_list_widget, TagsList):
                members_list_preview_widget.set(members_list_widget.get_all_tags())
            # TO BE ADDED WHEN MembersMapping IS READY
            # elif isinstance(tags_list_widget, TagsMapping):
            #   tags_list_preview_widget.set(tags_list_widget.get_tags())
            return
        names = [members_list_settings]
    else:
        if len(members_list_settings) == 0:
            names = []
        else:
            if isinstance(members_list_settings[0], int):
                names = [
                    user.login
                    for user in members_list_widget.get_all_members()
                    if user.id in members_list_settings
                ]
            else:
                names = members_list_settings

    users = members_list_widget.get_all_members()
    members_list_preview_widget.set([user for user in users if user.login in names])


def get_members_list_value(members_list_widget: MembersList, multiple: bool = True):
    selected = members_list_widget.get_selected_members()
    if multiple:
        if isinstance(members_list_widget, MembersList):
            return [user.login for user in selected]
        else:
            return [user for user in selected]
    else:
        if len(selected) == 0:
            return ""
        elif isinstance(members_list_widget, MembersList):
            return selected[0].login
        return selected[0].login


# Options utils


def get_separator(idx: int = 0):
    return NodesFlow.Node.Option(
        name=f"separator {idx}",
        option_component=NodesFlow.HtmlOptionComponent("<hr>"),
    )


empty = Empty()


def get_set_settings_container(text: Text, button: Button):
    return Container(
        widgets=[text, empty, button],
        direction="horizontal",
        style="place-items: center",
        gap=0,
        fractions=[6, 1, 3],
    )


def get_set_settings_button_style():
    return "flex: auto; border: 1px solid #bfcbd9; color: black; background-color: white;"


# Sidebar action options utils


def create_save_btn() -> Button:
    return Button("Save", icon="zmdi zmdi-floppy", call_on_click="closeSidebar();")


def create_set_default_btn() -> Button:
    return Button("Set Default", button_type="info", plain=True, icon="zmdi zmdi-refresh")


def create_sidebar_btn_container(
    save_btn: Button, default_btn: Button = None, need_separator: bool = True
):
    return Container(
        [
            Text("<hr>") if need_separator else Empty(),
            Flexbox(
                widgets=[
                    save_btn,
                    default_btn if default_btn is not None else Empty(),
                ],
                gap=110,
            ),
        ]
    )


# Layer docs utils


def get_layer_docs(layer_dir: str) -> str:
    md_description = ""
    for p in ("readme.md", "README.md"):
        p = join(layer_dir, p)
        if exists(p):
            with open(p) as f:
                md_description = f.read()
            break
    return md_description


# Widgets utils


def get_slider_style():
    return "padding: 0 7px"


def get_text_font_size():
    return 13
