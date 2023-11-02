from .Action import (
    Action,
    SourceAction,
    PixelLevelAction,
    SpatialLevelAction,
    AnnotationAction,
    OtherAction,
    OutputAction,
)
from .actions.data.data import DataAction
from .actions.approx_vector.approx_vector import ApproxVectorAction
from .actions.background.background import BackgroundAction
from .actions.bbox.bbox import BBoxAction
from .actions.bbox2poly.bbox2poly import BboxToPolyAction
from .actions.bitwise_masks.bitwise_masks import BitwiseMasksAction
from .actions.blur.blur import BlurAction
from .actions.bitmap2lines.bitmap2lines import Bitmap2LinesAction
from .actions.color_class.color_class import ColorClassAction
from .actions.contrast_brightness.contrast_brightness import ContrastBrightnessAction
from .actions.crop.crop import CropAction
from .actions.dataset.dataset import DatasetAction
from .actions.drop_obj_by_class.drop_obj_by_class import DropByClassAction
from .actions.drop_lines_by_length.drop_lines_by_length import DropLinesByLengthAction
from .actions.drop_noise.drop_noise import DropNoiseAction
from .actions.dummy.dummy import DummyAction
from .actions.duplicate_objects.duplicate_objects import DuplicateObjectsAction
from .actions.find_contours.find_contours import FindContoursAction
from .actions.flip.flip import FlipAction
from .actions.if_action.if_action import IfAction
from .actions.instances_crop.instances_crop import InstancesCropAction
from .actions.line2bitmap.line2bitmap import LineToBitmapAction
from .actions.merge_bitmaps.merge_bitmaps import MergeBitmapsAction
from .actions.multiply.multiply import MultiplyAction
from .actions.noise.noise import NoiseAction
from .actions.objects_filter.objects_filter import ObjectsFilterAction
from .actions.poly2bitmap.poly2bitmap import PolygonToBitmapAction
from .actions.random_color.random_color import RandomColorsAction
from .actions.rename.rename import RenameAction
from .actions.rasterize.rasterize import RasterizeAction
from .actions.resize.resize import ResizeAction
from .actions.rotate.rotate import RotateAction
from .actions.skeletonize.skeletonize import SkeletonizeAction
from .actions.sliding_window.sliding_window import SlidingWindowAction
from .actions.split_masks.split_masks import SplitMasksAction
from .actions.tag.tag import TagAction
from .actions.save.save import SaveAction
from .actions.save_masks.save_masks import SaveMasksAction
from .actions.supervisely.supervisely import SuperviselyAction
from .actions.images_filter.images_filter import ImagesFilterAction


SOURCE_ACTIONS = "Input"
# TRANSFORMATION_ACTIONS = "Transformation actions"
PIXEL_LEVEL_TRANSFORMS = "Pixel-level transforms"
SPATIAL_LEVEL_TRANSFORMS = "Spatial-level transforms"
ANNOTATION_TRANSFORMS = "Annotation transforms"
OTHER = "Other"
SAVE_ACTIONS = "Output"


actions_list = {
    SOURCE_ACTIONS: [DataAction.name],
    PIXEL_LEVEL_TRANSFORMS: [
        BlurAction.name,
        ContrastBrightnessAction.name,
        NoiseAction.name,
    ],
    SPATIAL_LEVEL_TRANSFORMS: [
        CropAction.name,
        FlipAction.name,
        InstancesCropAction.name,
        MultiplyAction.name,
        ResizeAction.name,
        RotateAction.name,
        SlidingWindowAction.name,
    ],
    ANNOTATION_TRANSFORMS: [
        ApproxVectorAction.name,
        BackgroundAction.name,
        BBoxAction.name,
        BboxToPolyAction.name,
        Bitmap2LinesAction.name,
        BitwiseMasksAction.name,
        ColorClassAction.name,
        DropByClassAction.name,
        DropLinesByLengthAction.name,
        DropNoiseAction.name,
        DuplicateObjectsAction.name,
        FindContoursAction.name,
        LineToBitmapAction.name,
        MergeBitmapsAction.name,
        ObjectsFilterAction.name,
        PolygonToBitmapAction.name,
        RandomColorsAction.name,
        RasterizeAction.name,
        RenameAction.name,
        SkeletonizeAction.name,
        SplitMasksAction.name,
        TagAction.name,
    ],
    OTHER: [DatasetAction.name, DummyAction.name, IfAction.name, ImagesFilterAction.name],
    SAVE_ACTIONS: [
        SaveAction.name,
        SaveMasksAction.name,
        SuperviselyAction.name,
    ],
}

actions_dict = {
    # Data layers
    DataAction.name: DataAction,
    # Pixel-level transforms layers
    BlurAction.name: BlurAction,
    ContrastBrightnessAction.name: ContrastBrightnessAction,
    NoiseAction.name: NoiseAction,
    # Spatial-level transform layers
    CropAction.name: CropAction,
    FlipAction.name: FlipAction,
    InstancesCropAction.name: InstancesCropAction,
    MultiplyAction.name: MultiplyAction,
    ResizeAction.name: ResizeAction,
    RotateAction.name: RotateAction,
    SlidingWindowAction.name: SlidingWindowAction,
    # Annotation layers
    ApproxVectorAction.name: ApproxVectorAction,
    BackgroundAction.name: BackgroundAction,
    BBoxAction.name: BBoxAction,
    BboxToPolyAction.name: BboxToPolyAction,
    Bitmap2LinesAction.name: Bitmap2LinesAction,
    BitwiseMasksAction.name: BitwiseMasksAction,
    ColorClassAction.name: ColorClassAction,
    DropByClassAction.name: DropByClassAction,
    DropLinesByLengthAction.name: DropLinesByLengthAction,
    DropNoiseAction.name: DropNoiseAction,
    DuplicateObjectsAction.name: DuplicateObjectsAction,
    FindContoursAction.name: FindContoursAction,
    LineToBitmapAction.name: LineToBitmapAction,
    MergeBitmapsAction.name: MergeBitmapsAction,
    ObjectsFilterAction.name: ObjectsFilterAction,
    PolygonToBitmapAction.name: PolygonToBitmapAction,
    RandomColorsAction.name: RandomColorsAction,
    RasterizeAction.name: RasterizeAction,
    RenameAction.name: RenameAction,
    SkeletonizeAction.name: SkeletonizeAction,
    SplitMasksAction.name: SplitMasksAction,
    TagAction.name: TagAction,
    # Other layers
    DatasetAction.name: DatasetAction,
    DummyAction.name: DummyAction,
    IfAction.name: IfAction,
    ImagesFilterAction.name: ImagesFilterAction,
    # Save layers
    SaveAction.name: SaveAction,
    SaveMasksAction.name: SaveMasksAction,
    SuperviselyAction.name: SuperviselyAction,
}
