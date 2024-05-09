from os.path import realpath, dirname

from src.ui.dtl.utils import get_layer_docs
from src.ui.dtl.actions.other_augs.imgaug_corruptlike.base.imgaug_corruptlike import (
    ImgAugCorruptLikeAction,
)


class ImgAugCorruptlikeCompressionAction(ImgAugCorruptLikeAction):
    name = "iaa_imgcorruptlike_compression"
    title = "iaa.imgcorruptlike Compression"
    docs_url = "https://imgaug.readthedocs.io/en/latest/source/overview/imgcorruptlike.html#elastictransform"
    description = ""
    md_description = get_layer_docs(dirname(realpath(__file__)))
    options = {"pixelate": "Pixelate", "elastic_transform": "Elastic Transform"}
