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
from .actions.input.images_project.images_project import ImagesProjectAction
from .actions.pixel_level_transformations.anonymize.anonymize import AnonymizeAction
from .actions.annotation_transforms.approx_vector.approx_vector import ApproxVectorAction
from .actions.annotation_transforms.background.background import BackgroundAction
from .actions.annotation_transforms.bbox.bbox import BBoxAction
from .actions.annotation_transforms.bbox_to_polygon.bbox_to_polygon import BboxToPolygonAction
from .actions.annotation_transforms.bitwise_masks.bitwise_masks import BitwiseMasksAction
from .actions.pixel_level_transformations.blur.blur import BlurAction
from .actions.annotation_transforms.mask_to_lines.mask_to_lines import MaskToLinesAction
from .actions.annotation_transforms.change_class_color.change_class_color import (
    ChangeClassColorAction,
)
from .actions.pixel_level_transformations.contrast_brightness.contrast_brightness import (
    ContrastBrightnessAction,
)
from .actions.spatial_level_transforms.crop.crop import CropAction
from .actions.other.dataset.dataset import DatasetAction
from .actions.annotation_transforms.drop_object_by_class.drop_object_by_class import (
    DropObjectByClassAction,
)
from .actions.annotation_transforms.drop_lines_by_length.drop_lines_by_length import (
    DropLinesByLengthAction,
)
from .actions.annotation_transforms.drop_noise.drop_noise import DropNoiseAction
from .actions.other.dummy.dummy import DummyAction
from .actions.annotation_transforms.duplicate_objects.duplicate_objects import (
    DuplicateObjectsAction,
)
from .actions.filters_and_conditions.filter_image_by_object.filter_image_by_object import (
    FilterImageByObject,
)
from .actions.filters_and_conditions.filter_image_by_tag.filter_image_by_tag import FilterImageByTag
from .actions.annotation_transforms.mask_to_polygon.mask_to_polygon import MaskToPolygonAction
from .actions.spatial_level_transforms.flip.flip import FlipAction
from .actions.filters_and_conditions.if_action.if_action import IfAction
from .actions.spatial_level_transforms.instances_crop.instances_crop import InstancesCropAction
from .actions.annotation_transforms.line_to_mask.line_to_mask import LineToMaskAction
from .actions.annotation_transforms.merge_masks.merge_masks import MergeMasksAction
from .actions.spatial_level_transforms.multiply.multiply import MultiplyAction
from .actions.pixel_level_transformations.noise.noise import NoiseAction
from .actions.annotation_transforms.objects_filter.objects_filter import ObjectsFilterAction
from .actions.annotation_transforms.polygon_to_mask.polygon_to_mask import PolygonToMaskAction
from .actions.pixel_level_transformations.random_color.random_color import RandomColorsAction
from .actions.annotation_transforms.rename_classes.rename_classes import RenameClassesAction
from .actions.annotation_transforms.rasterize.rasterize import RasterizeAction
from .actions.spatial_level_transforms.resize.resize import ResizeAction
from .actions.spatial_level_transforms.rotate.rotate import RotateAction
from .actions.annotation_transforms.skeletonize.skeletonize import SkeletonizeAction
from .actions.spatial_level_transforms.sliding_window.sliding_window import SlidingWindowAction
from .actions.annotation_transforms.split_masks.split_masks import SplitMasksAction
from .actions.annotation_transforms.image_tag.image_tag import ImageTagAction
from .actions.output.export_archive.export_archive import ExportArchiveAction
from .actions.output.export_archive_with_masks.export_archive_with_masks import (
    ExportArchiveWithMasksAction,
)
from .actions.output.create_new_project.create_new_project import CreateNewProjectAction
from .actions.output.add_to_existing_project.add_to_existing_project import (
    AddToExistingProjectAction,
)
from .actions.filters_and_conditions.filter_images_without_objects.filter_images_without_objects import (
    FilterImageWithoutObjects,
)
from .actions.output.copy_annotations.copy_annotations import (
    CopyAnnotationsAction,
)

# Neural networks
from .actions.neural_networks.deploy_yolov8.deploy_yolov8 import DeployYOLOV8Action
from .actions.neural_networks.apply_nn_inference.apply_nn_inference import ApplyNNInferenceAction

# Video
from .actions.input.videos_project.videos_project import VideosProjectAction
from .actions.filters_and_conditions.filter_videos_without_objects.filter_videos_without_objects import (
    FilterVideoWithoutObjects,
)
from .actions.filters_and_conditions.filter_videos_without_annotation.filter_videos_without_annotation import (
    FilterVideoWithoutAnnotation,
)
from .actions.filters_and_conditions.filter_videos_by_duration.filter_videos_by_duration import (
    FilterVideoByDuration,
)
from .actions.annotation_transforms.split_videos_by_duration.split_videos_by_duration import (
    SplitVideoByDuration,
)
from .actions.filters_and_conditions.filter_videos_by_objects.filter_videos_by_objects import (
    FilterVideosByObject,
)
from .actions.filters_and_conditions.filter_videos_by_tags.filter_videos_by_tags import (
    FilterVideosByTag,
)

# ---

# Labeling job
from .actions.input.input_labeling_job.input_labeling_job import InputLabelingJobAction
from .actions.output.create_labeling_job.create_labeling_job import CreateLabelingJobAction

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
    SOURCE_ACTIONS: [ImagesProjectAction.name, InputLabelingJobAction.name],
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
        BboxToPolygonAction.name,
        MaskToLinesAction.name,
        BitwiseMasksAction.name,
        ChangeClassColorAction.name,
        DropObjectByClassAction.name,
        DropLinesByLengthAction.name,
        DropNoiseAction.name,
        DuplicateObjectsAction.name,
        MaskToPolygonAction.name,
        LineToMaskAction.name,
        MergeMasksAction.name,
        ObjectsFilterAction.name,
        PolygonToMaskAction.name,
        RasterizeAction.name,
        RenameClassesAction.name,
        SkeletonizeAction.name,
        SplitMasksAction.name,
        ImageTagAction.name,
    ],
    FILTERS_AND_CONDITIONS: [
        FilterImageByObject.name,
        FilterImageByTag.name,
        FilterImageWithoutObjects.name,
        IfAction.name,
    ],
    NEURAL_NETWORKS: [DeployYOLOV8Action.name, ApplyNNInferenceAction.name],
    OTHER: [DatasetAction.name, DummyAction.name],
    SAVE_ACTIONS: [
        CreateNewProjectAction.name,
        AddToExistingProjectAction.name,
        ExportArchiveAction.name,
        ExportArchiveWithMasksAction.name,
        CopyAnnotationsAction.name,
        CreateLabelingJobAction.name,
    ],
}

# Image Actions
image_actions_dict = {
    # Data layers
    ImagesProjectAction.name: ImagesProjectAction,
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
    BboxToPolygonAction.name: BboxToPolygonAction,
    MaskToLinesAction.name: MaskToLinesAction,
    BitwiseMasksAction.name: BitwiseMasksAction,
    ChangeClassColorAction.name: ChangeClassColorAction,
    DropObjectByClassAction.name: DropObjectByClassAction,
    DropLinesByLengthAction.name: DropLinesByLengthAction,
    DropNoiseAction.name: DropNoiseAction,
    DuplicateObjectsAction.name: DuplicateObjectsAction,
    MaskToPolygonAction.name: MaskToPolygonAction,
    LineToMaskAction.name: LineToMaskAction,
    MergeMasksAction.name: MergeMasksAction,
    ObjectsFilterAction.name: ObjectsFilterAction,
    PolygonToMaskAction.name: PolygonToMaskAction,
    RasterizeAction.name: RasterizeAction,
    RenameClassesAction.name: RenameClassesAction,
    SkeletonizeAction.name: SkeletonizeAction,
    SplitMasksAction.name: SplitMasksAction,
    ImageTagAction.name: ImageTagAction,
    # Filters and conditions
    FilterImageByObject.name: FilterImageByObject,
    FilterImageByTag.name: FilterImageByTag,
    FilterImageWithoutObjects.name: FilterImageWithoutObjects,
    IfAction.name: IfAction,
    # Neural Networks
    DeployYOLOV8Action.name: DeployYOLOV8Action,
    ApplyNNInferenceAction.name: ApplyNNInferenceAction,
    # Other layers
    DatasetAction.name: DatasetAction,
    DummyAction.name: DummyAction,
    # Save layers
    CreateNewProjectAction.name: CreateNewProjectAction,
    AddToExistingProjectAction.name: AddToExistingProjectAction,
    ExportArchiveAction.name: ExportArchiveAction,
    ExportArchiveWithMasksAction.name: ExportArchiveWithMasksAction,
    CopyAnnotationsAction.name: CopyAnnotationsAction,
    CreateLabelingJobAction.name: CreateLabelingJobAction,
}

image_actions_legacy_dict = {
    ImagesProjectAction.legacy_name: ImagesProjectAction.name,
    ApplyNNInferenceAction.legacy_name: ApplyNNInferenceAction.name,
    BboxToPolygonAction.legacy_name: BboxToPolygonAction.name,
    ChangeClassColorAction.legacy_name: ChangeClassColorAction.name,
    DropObjectByClassAction.legacy_name: DropObjectByClassAction.name,
    ImageTagAction.legacy_name: ImageTagAction.name,
    LineToMaskAction.legacy_name: LineToMaskAction.name,
    MaskToLinesAction.legacy_name: MaskToLinesAction.name,
    MaskToPolygonAction.legacy_name: MaskToPolygonAction.name,
    MergeMasksAction.legacy_name: MergeMasksAction.name,
    PolygonToMaskAction.legacy_name: PolygonToMaskAction.name,
    RenameClassesAction.legacy_name: RenameClassesAction.name,
    AddToExistingProjectAction.legacy_name: AddToExistingProjectAction.name,
    CreateLabelingJobAction.legacy_name: InputLabelingJobAction.name,
    CreateNewProjectAction.legacy_name: CreateNewProjectAction.name,
    ExportArchiveAction.legacy_name: ExportArchiveAction.name,
    ExportArchiveWithMasksAction.legacy_name: ExportArchiveWithMasksAction.name,
}

video_actions_list = {
    SOURCE_ACTIONS: [VideosProjectAction.name],
    ANNOTATION_TRANSFORMS: [
        BackgroundAction.name,
        BBoxAction.name,
        BboxToPolygonAction.name,
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
        CreateNewProjectAction.name,
        AddToExistingProjectAction.name,
        ExportArchiveAction.name,
        CreateLabelingJobAction.name,
    ],
}

video_actions_dict = {
    # Data layers
    VideosProjectAction.name: VideosProjectAction,
    # Annotation layers
    BackgroundAction.name: BackgroundAction,
    BBoxAction.name: BBoxAction,
    BboxToPolygonAction.name: BboxToPolygonAction,
    # Video transofrms
    SplitVideoByDuration.name: SplitVideoByDuration,
    # Filter and condition layers
    FilterVideosByObject.name: FilterVideosByObject,
    FilterVideosByTag.name: FilterVideosByTag,
    FilterVideoWithoutObjects.name: FilterVideoWithoutObjects,
    FilterVideoWithoutAnnotation.name: FilterVideoWithoutAnnotation,
    FilterVideoByDuration.name: FilterVideoByDuration,
    # Save layers
    CreateNewProjectAction.name: CreateNewProjectAction,
    AddToExistingProjectAction.name: AddToExistingProjectAction,
    ExportArchiveAction.name: ExportArchiveAction,
    CreateLabelingJobAction.name: CreateLabelingJobAction,
}

video_actions_legacy_dict = {
    VideosProjectAction.legacy_name: VideosProjectAction.name,
    CreateNewProjectAction.legacy_name: CreateNewProjectAction.name,
    AddToExistingProjectAction.legacy_name: AddToExistingProjectAction.name,
    ExportArchiveAction.legacy_name: ExportArchiveAction.name,
    CreateLabelingJobAction.legacy_name: CreateLabelingJobAction.name,
}


modality_dict = {"images": image_actions_dict, "videos": video_actions_dict}
modality_list = {"images": image_actions_list, "videos": video_actions_list}
modality_dict_legacy = {"images": image_actions_legacy_dict, "videos": video_actions_legacy_dict}

actions_dict = modality_dict[g.MODALITY_TYPE]
actions_list = modality_list[g.MODALITY_TYPE]
actions_dict_legacy = modality_dict_legacy[g.MODALITY_TYPE]
