_DISABLED_IMGAUG_MULTICORE_MESSAGE = (
    "imgaug.multicore.BatchLoader and BackgroundAugmenter are disabled in "
    "data-nodes because they rely on unsafe pickle-based inter-process "
    "communication. Use imgaug.multicore.Pool instead."
)


class _DisabledImgAugDeprecatedMulticore:
    def __init__(self, *args, **kwargs):
        raise RuntimeError(_DISABLED_IMGAUG_MULTICORE_MESSAGE)


def _patch_attr(module, attr_name):
    if module is not None and hasattr(module, attr_name):
        setattr(module, attr_name, _DisabledImgAugDeprecatedMulticore)


def harden_imgaug_runtime():
    try:
        import imgaug
        import imgaug.imgaug as imgaug_root
        import imgaug.multicore as imgaug_multicore
    except Exception:
        return

    for module in (imgaug, imgaug_root, imgaug_multicore):
        _patch_attr(module, "BatchLoader")
        _patch_attr(module, "BackgroundAugmenter")
