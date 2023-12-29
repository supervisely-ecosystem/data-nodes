from .Action import (
    Action,
    SourceAction,
    PixelLevelAction,
    SpatialLevelAction,
    AnnotationAction,
    OtherAction,
    OutputAction,
    FilterAndConditionAction,
    NeuralNetworkAction,
)
from .actions.data.data import DataAction
from .actions.anonymize.anonymize import AnonymizeAction
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
from .actions.filter_image_by_object.filter_image_by_object import FilterImageByObject
from .actions.filter_image_by_tag.filter_image_by_tag import FilterImageByTag
from .actions.bitmap2poly.bitmap2poly import BitmapToPolyAction
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
from .actions.existing_project.existing_project import ExistingProjectAction
from .actions.apply_nn.apply_nn import ApplyNNAction
from .actions.filter_images_without_objects.filter_images_without_objects import (
    FilterImageWithoutObjects,
)


# Video
from .actions.video_data.video_data import VideoDataAction
from .actions.filter_videos_without_objects.filter_videos_without_objects import (
    FilterVideoWithoutObjects,
)
from .actions.filter_videos_without_annotation.filter_videos_without_annotation import (
    FilterVideoWithoutAnnotation,
)
from .actions.filter_videos_by_duration.filter_videos_by_duration import FilterVideoByDuration
from .actions.split_videos_by_duration.split_videos_by_duration import SplitVideoByDuration
from .actions.filter_videos_by_objects.filter_videos_by_objects import FilterVideosByObject
from .actions.filter_videos_by_tags.filter_videos_by_tags import FilterVideosByTag

# ---

# Labeling job
from .actions.input_labeling_job.input_labeling_job import InputLabelingJobAction
from .actions.labeling_job.labeling_job import LabelingJobAction

import src.globals as g

SOURCE_ACTIONS = "Input"
# TRANSFORMATION_ACTIONS = "Transformation actions"
PIXEL_LEVEL_TRANSFORMS = "Pixel-level transforms"
SPATIAL_LEVEL_TRANSFORMS = "Spatial-level transforms"
ANNOTATION_TRANSFORMS = "Annotation transforms"
OTHER = "Other"
SAVE_ACTIONS = "Output"
FILTERS_AND_CONDITIONS = "Filters and conditions"
NEURAL_NETWORKS = "Neural networks"

# Video specific
VIDEO_TRANSFORMS = "Video transforms"
# ---

image_actions_list = {
    SOURCE_ACTIONS: [DataAction.name, InputLabelingJobAction.name],
    PIXEL_LEVEL_TRANSFORMS: [
        AnonymizeAction.name,
        BlurAction.name,
        ContrastBrightnessAction.name,
        NoiseAction.name,
        RandomColorsAction.name,
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
        BitmapToPolyAction.name,
        LineToBitmapAction.name,
        MergeBitmapsAction.name,
        ObjectsFilterAction.name,
        PolygonToBitmapAction.name,
        RasterizeAction.name,
        RenameAction.name,
        SkeletonizeAction.name,
        SplitMasksAction.name,
        TagAction.name,
    ],
    FILTERS_AND_CONDITIONS: [
        FilterImageByObject.name,
        FilterImageByTag.name,
        FilterImageWithoutObjects.name,
        IfAction.name,
    ],
    NEURAL_NETWORKS: [ApplyNNAction.name],
    OTHER: [DatasetAction.name, DummyAction.name],
    SAVE_ACTIONS: [
        SaveAction.name,
        SaveMasksAction.name,
        SuperviselyAction.name,
        ExistingProjectAction.name,
        LabelingJobAction.name,
    ],
}

# Image Actions
image_actions_dict = {
    # Data layers
    DataAction.name: DataAction,
    InputLabelingJobAction.name: InputLabelingJobAction,
    # Pixel-level transforms layers
    AnonymizeAction.name: AnonymizeAction,
    BlurAction.name: BlurAction,
    ContrastBrightnessAction.name: ContrastBrightnessAction,
    NoiseAction.name: NoiseAction,
    RandomColorsAction.name: RandomColorsAction,
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
    BitmapToPolyAction.name: BitmapToPolyAction,
    LineToBitmapAction.name: LineToBitmapAction,
    MergeBitmapsAction.name: MergeBitmapsAction,
    ObjectsFilterAction.name: ObjectsFilterAction,
    PolygonToBitmapAction.name: PolygonToBitmapAction,
    RasterizeAction.name: RasterizeAction,
    RenameAction.name: RenameAction,
    SkeletonizeAction.name: SkeletonizeAction,
    SplitMasksAction.name: SplitMasksAction,
    TagAction.name: TagAction,
    # Filters and conditions
    FilterImageByObject.name: FilterImageByObject,
    FilterImageByTag.name: FilterImageByTag,
    FilterImageWithoutObjects.name: FilterImageWithoutObjects,
    IfAction.name: IfAction,
    # Neural Networks
    ApplyNNAction.name: ApplyNNAction,
    # Other layers
    DatasetAction.name: DatasetAction,
    DummyAction.name: DummyAction,
    # Save layers
    SaveAction.name: SaveAction,
    SaveMasksAction.name: SaveMasksAction,
    SuperviselyAction.name: SuperviselyAction,
    ExistingProjectAction.name: ExistingProjectAction,
    LabelingJobAction.name: LabelingJobAction,
}

video_actions_list = {
    SOURCE_ACTIONS: [VideoDataAction.name],
    ANNOTATION_TRANSFORMS: [
        BackgroundAction.name,
        BBoxAction.name,
        BboxToPolyAction.name,
    ],
    VIDEO_TRANSFORMS: [SplitVideoByDuration.name],
    FILTERS_AND_CONDITIONS: [
        FilterVideosByObject.name,
        FilterVideosByTag.name,
        FilterVideoWithoutObjects.name,
        FilterVideoWithoutAnnotation.name,
        FilterVideoByDuration.name,
    ],
    SAVE_ACTIONS: [
        SaveAction.name,
        ExistingProjectAction.name,
        SuperviselyAction.name,
        LabelingJobAction.name,
    ],
}

video_actions_dict = {
    # Data layers
    VideoDataAction.name: VideoDataAction,
    # Annotation layers
    BackgroundAction.name: BackgroundAction,
    BBoxAction.name: BBoxAction,
    BboxToPolyAction.name: BboxToPolyAction,
    # Video transofrms
    SplitVideoByDuration.name: SplitVideoByDuration,
    # Filter and condition layers
    FilterVideosByObject.name: FilterVideosByObject,
    FilterVideosByTag.name: FilterVideosByTag,
    FilterVideoWithoutObjects.name: FilterVideoWithoutObjects,
    FilterVideoWithoutAnnotation.name: FilterVideoWithoutAnnotation,
    FilterVideoByDuration.name: FilterVideoByDuration,
    # Save layers
    SaveAction.name: SaveAction,
    SuperviselyAction.name: SuperviselyAction,
    ExistingProjectAction.name: ExistingProjectAction,
    LabelingJobAction.name: LabelingJobAction,
}

modality_dict = {"images": image_actions_dict, "videos": video_actions_dict}
modality_list = {"images": image_actions_list, "videos": video_actions_list}

actions_dict = modality_dict[g.MODALITY_TYPE]
actions_list = modality_list[g.MODALITY_TYPE]
