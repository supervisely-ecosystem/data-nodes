<div align="center" markdown>

<img src="https://github.com/user-attachments/assets/58d6d5d7-3c05-4c56-9661-90d0a76747aa"/>

# ML Pipelines

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/data-nodes)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/data-nodes)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/data-nodes.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/data-nodes.png)](https://supervisely.com)

</div>

## Overview

This application is a versatile tool designed for data transformation tasks (like filtering and augmentation). It allows you to create and manage Data transformation workflows by leveraging graphical nodes with settings.

## Available Layers

| Layers                                                                                                                                                                                                                      | Description                                                                                                | Images | Videos |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------ | ------ |
| **Input**                                                                                                                                                                                                                   |                                                                                                            |        |        |
| [Images Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/input/images_project/README.md#images-project)                                                                          | Selects a project with images as the source data for processing through the pipeline.                      | +      | -      |
| [Videos Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/input/videos_project/README.md#videos-project)                                                                          | Selects a project with videos as the source data for processing through the pipeline.                      | -      | +      |
| [Input Labeling Job](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/input/input_labeling_job/README.md#input-labeling-job)                                                              | Imports data and annotations from an existing labeling job as pipeline input.                              | +      | -      |
| [Filtered Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/input/filtered_project/README.md#filtered-project)                                                                    | Uses a predefined project with pre-filtered images based on specific criteria.                             | +      | -      |
| **Pixel Level Transformations**                                                                                                                                                                                             |                                                                                                            |        |        |
| [Anonymize](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/pixel_level_transformations/anonymize/README.md#anonymize)                                                                   | Applies pixelation or blurring effects to objects in images to hide sensitive information.                 | +      | -      |
| [Blur](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/pixel_level_transformations/blur/README.md#blur)                                                                                  | Applies various blur effects (Gaussian, median, etc.) to enhance or smooth image quality.                  | +      | -      |
| [Contrast Brightness](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/pixel_level_transformations/contrast_brightness/README.md#contrast-and-brightness)                                 | Adjusts image contrast and brightness levels with precise control over parameters.                         | +      | -      |
| [Noise](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/pixel_level_transformations/noise/README.md#noise)                                                                               | Adds controlled noise patterns to images for data augmentation or testing model robustness.                | +      | -      |
| [Random Color](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/pixel_level_transformations/random_color/README.md#random-color)                                                          | Randomizes or systematically alters color values in images for augmentation purposes.                      | +      | -      |
| **Spatial Level Transformations**                                                                                                                                                                                           |                                                                                                            |        |        |
| [Crop](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/crop/README.md#crop)                                                                                     | Extracts specific regions from images based on configurable parameters or annotations.                     | +      | -      |
| [Flip](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/flip/README.md#flip)                                                                                     | Mirrors images horizontally or vertically while preserving annotation coordinates.                         | +      | -      |
| [Instance Crop](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/instances_crop/README.md#instances-crop)                                                        | Creates separate images for each detected object instance with configurable padding.                       | +      | -      |
| [Multiply](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/multiply/README.md#multiply)                                                                         | Duplicates objects across the image with specified patterns and transformations.                           | +      | -      |
| [Resize](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/resize/README.md#resize)                                                                               | Rescales images to target dimensions while properly transforming associated annotations.                   | +      | -      |
| [Rotate](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/rotate/README.md#rotate)                                                                               | Rotates images by specified angles with proper transformation of associated annotations.                   | +      | -      |
| [Sliding Window](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/spatial_level_transforms/sliding_window/README.md#sliding-window)                                                       | Generates multiple overlapping crops from large images using a sliding window approach.                    | +      | -      |
| **ImgAug Augmentations**                                                                                                                                                                                                    |                                                                                                            |        |        |
| [ImgAug Studio](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/studio/README.md)                                                                                            | ImgAug Studio is a wrapper around [ImgAug Library](https://github.com/aleju/imgaug).                       | +      | -      |
| [ImgAug.ImgCorruptlike.Noise](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/corruptlike/noise.md)                                                                          | ImgAug imgcorruptlike Noise augmentators.                                                                  | +      | -      |
| [ImgAug.ImgCorruptlike.Blur](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/corruptlike/blur.md)                                                                            | ImgAug imgcorruptlike Blur augmentators.                                                                   | +      | -      |
| [ImgAug.ImgCorruptlike.Weather](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/corruptlike/weather.md)                                                                      | ImgAug imgcorruptlike Weather augmentators.                                                                | +      | -      |
| [ImgAug.ImgCorruptlike.Color](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/corruptlike/color.md)                                                                          | ImgAug imgcorruptlike Color augmentators.                                                                  | +      | -      |
| [ImgAug.ImgCorruptlike.Compression](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/corruptlike/compression.md)                                                              | ImgAug imgcorruptlike Compression augmentators.                                                            | +      | -      |
| [ImgAug.Geometric.ElasticTransformation](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/geometric/elastic_transformation/README.md)                                         | ImgAug geometric Elastic Transformation augmentator.                                                       | +      | -      |
| [ImgAug.Geometric.PerspectiveTransform](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/imgaug_augs/geometric/perspective_transform/README.md)                                           | ImgAug geometric Perspective Transform augmentator.                                                        | +      | -      |
| **Annotation Transforms**                                                                                                                                                                                                   |                                                                                                            |        |        |
| [Approximate Vector](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/approx_vector/README.md#approx-vector)                                                       | Simplifies complex vector objects by reducing point count while preserving shape.                          | +      | -      |
| [Background](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/background/README.md#background)                                                                     | Creates and assigns a background class to areas without object annotations.                                | +      | +      |
| [Bounding Box](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/bbox/README.md#bounding-box)                                                                       | Converts any object annotation types to rectangular bounding boxes.                                        | +      | +      |
| [Bounding Box to Polygon](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/bbox_to_polygon/README.md#bbox-to-polygon)                                              | Converts rectangular bounding boxes to polygon annotations with configurable vertices.                     | +      | +      |
| [Bitwise Masks](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/bitwise_masks/README.md#bitwise-masks)                                                            | Performs logical operations (AND, OR, XOR) between masks of different classes.                             | +      | -      |
| [Change Class Color](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/change_class_color/README.md#change-class-color)                                             | Modifies the display color of object classes without changing geometry or labels.                          | +      | -      |
| [Drop Lines by Length](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/drop_lines_by_length/README.md#drop-lines-by-length)                                       | Removes line annotations based on their length using min/max thresholds.                                   | +      | -      |
| [Drop Noise](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/drop_noise/README.md#drop-noise)                                                                     | Filters out small mask fragments below specified area thresholds to reduce noise.                          | +      | -      |
| [Drop Object by Class](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/drop_object_by_class/README.md#drop-object-by-class)                                       | Removes all objects of specified classes from annotations.                                                 | +      | -      |
| [Duplicate Objects](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/duplicate_objects/README.md#duplicate-objects)                                                | Creates copies of selected objects with new class names while preserving geometry.                         | +      | -      |
| [Image Tag](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/image_tag/README.md#image-tag)                                                                        | Adds custom metadata tags to images based on configurable conditions.                                      | +      | -      |
| [Line to Mask](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/line_to_mask/README.md#line-to-mask)                                                               | Converts line annotations to mask annotations with configurable thickness.                                 | +      | -      |
| [Mask to Lines](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/mask_to_lines/README.md#mask-to-lines)                                                            | Extracts the contours or center lines from mask annotations.                                               | +      | -      |
| [Mask to Polygon](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/mask_to_polygon/README.md#mask-to-polygon)                                                      | Converts bitmap masks to polygon annotations with configurable precision.                                  | +      | -      |
| [Merge Classes](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/merge_classes/README.md#merge-classes)                                                            | Combines multiple object classes into a single target class using an intuitive mapping table.              | +      | -      |
| [Merge Masks](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/merge_masks/README.md#merge-masks)                                                                  | Combines multiple mask annotations of the same class into a unified single mask.                           | +      | -      |
| [Objects Filter](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/objects_filter/README.md#objects-filter)                                                         | Selectively keeps or removes objects based on custom filtering criteria.                                   | +      | -      |
| [Objects Filter by Area](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/objects_filter_by_area/README.md#objects-filter-by-area)                                 | Tags or removes objects based on their area using configurable thresholds.                                 | +      | -      |
| [Polygon to Mask](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/polygon_to_mask/README.md#polygon-to-mask)                                                      | Converts polygon annotations to bitmap mask representations.                                               | +      | -      |
| [Rasterize](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/rasterize/README.md#rasterize)                                                                        | Converts all vector annotations to bitmap mask representations.                                            | +      | -      |
| [Rename Classes](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/rename_classes/README.md#rename-classes)                                                         | Renames object classes while preserving their original geometry and attributes.                            | +      | -      |
| [Skeletonize](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/skeletonize/README.md#skeletonize)                                                                  | Creates skeletal representations (center lines) from mask annotations.                                     | +      | -      |
| [Split Masks](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/split_masks/README.md#split-masks)                                                                  | Separates connected mask regions into individual object instances.                                         | +      | -      |
| [Split Videos by Duration](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl//actions/annotation_transforms/split_videos_by_duration/README.md#split-video-by-duration)                            | Segments longer videos into smaller clips based on specified duration.                                     | -      | +      |
| **Filters and Conditions**                                                                                                                                                                                                  |                                                                                                            |        |        |
| [Filter Image by Object](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_image_by_object/README.md#filter-images-by-object-classes)                        | Includes or excludes images based on the presence of specific object classes.                              | +      | -      |
| [Filter Image by Tag](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_image_by_tag/README.md#filter-images-by-tags)                                        | Selects images that match specific tag criteria for further processing.                                    | +      | -      |
| [Filter Images without Objects](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_images_without_objects/README.md#filter-images-without-object-classes)     | Identifies and processes only images that contain no object annotations.                                   | +      | -      |
| [Filter Videos by Duration](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_videos_by_duration/README.md#filter-videos-by-duration)                        | Selects videos based on their duration using min/max time thresholds.                                      | -      | +      |
| [Filter Videos by Objects](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_videos_by_objects/README.md#filter-videos-by-object-classes)                    | Includes or excludes videos based on the presence of specific object classes.                              | -      | +      |
| [Filter Videos by Tags](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_videos_by_tags/README.md#filter-videos-by-tags)                                    | Processes only videos that match specified tag criteria.                                                   | -      | +      |
| [Filter Videos without Annotations](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_videos_without_annotation/README.md#filter-videos-without-annotations) | Identifies and processes videos that have no annotations.                                                  | -      | +      |
| [Filter Videos without Objects](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/filter_videos_without_objects/README.md#filter-videos-without-object-classes)     | Selects videos that do not contain any object annotations.                                                 | -      | +      |
| [IF Action](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/filters_and_conditions/if_action/README.md#if-action)                                                                        | Creates conditional processing branches based on specified criteria or image properties.                   | +      | -      |
| **Neural Networks**                                                                                                                                                                                                         |                                                                                                            |        |        |
| [Apply NN Inference](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/apply_nn_inference/README.md#apply-nn-inference)                                                    | Runs any deployed neural network model on images and incorporates results into the pipeline.               | +      | -      |
| [Deploy YOLOv5](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/yolov5.md)                                                                                        | Integrates and runs YOLOv5 object detection models with support for custom weights.                        | +      | -      |
| [Deploy YOLO (v8, v9, v10, v11)](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/yolov8.md)                                                                       | Deploys and runs multiple YOLO versions with support for detection, segmentation and classification tasks. | +      | -      |
| [Deploy YOLO (v8 - v12)](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/yolo.md)                                                                                 | Deploys the latest YOLO models with comprehensive support for all model variants and tasks.                | +      | -      |
| [Deploy MMDetection](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/mmdetection.md)                                                                              | Integrates the MMDetection library with access to numerous object detection architectures.                 | +      | -      |
| [Deploy MMSegmentation](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/mmsegmentation.md)                                                                        | Runs semantic segmentation models from the MMSegmentation ecosystem with custom weights.                   | +      | -      |
| [Deploy RT-DETR](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/rtdetr.md)                                                                                       | Deploys Real-Time Detection Transformer models for efficient object detection.                             | +      | -      |
| [Deploy RT-DETRv2](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/rtdetrv2.md)                                                                                   | Integrates the improved version of RT-DETR with enhanced accuracy and performance.                         | +      | -      |
| [Deploy DEIM](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/neural_networks/deploy/deim.md)                                                                                            | Deploys DEIM Models for efficient object detection.                                                        | +      | -      |
| **Other**                                                                                                                                                                                                                   |                                                                                                            |        |        |
| [Dummy](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/other/dummy/README.md#dummy)                                                                                                     | Passes data through unchanged; useful for merging branches or as a placeholder.                            | +      | -      |
| [Dataset](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/other/dataset/README.md#dataset)                                                                                               | Consolidates all processed data into a single dataset with configurable naming.                            | +      | -      |
| [Split Data](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/other/split_data/README.md)                                                                                                 | Distributes processed data across multiple datasets using various splitting strategies.                    | +      | -      |
| **Output**                                                                                                                                                                                                                  |                                                                                                            |        |        |
| [Output Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/output_project/README.md#output_project)                                                                         | Saves processed data and annotations to a new or existing project with configurable settings.              | +      | -      |
| [Create new Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/create_new_project/README.md#create-new-project)                                                             | Creates a new project to store the pipeline's output data and metadata.                                    | +      | +      |
| [Add to Existing Project](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/add_to_existing_project/README.md#add-to-existing-project)                                              | Appends processed data to a specified existing project with flexible dataset options.                      | +      | +      |
| [Export Archive](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/export_archive/README.md#export-archive)                                                                         | Packages processed data and annotations as a downloadable archive in TeamFiles.                            | +      | +      |
| [Export Archive with Masks](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/export_archive_with_masks/README.md#export-archive-with-masks)                                        | Exports data with separate mask files for each annotation in TeamFiles.                                    | +      | -      |
| [Copy Annotations](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/copy_annotations/README.md#copy-annotations)                                                                   | Transfers annotations between projects while maintaining original image references.                        | +      | -      |
| [Create Labeling Job](https://github.com/supervisely-ecosystem/data-nodes/blob/master/src/ui/dtl/actions/output/create_labeling_job/README.md#create-labeling-job)                                                          | Creates a new labeling job from processed data for further refinement.                                     | +      | +      |

#### Key features:

- **Transform Data:** Apply a wide variety of data transformation operations to images within a project. These transformations include rotation, cropping, blurring, resizing, and many more.

  ![transform-data](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/58d857fe-91af-413b-995b-20c674d72a9f)

- **Use Neural Networks:** Apply deployed models on your data to perform object detection, instance segmentation, and other tasks. You can use any of the neural network models available in the Supervisely Ecosystem, or train your custom models.

  ![apply-nn](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/9f715cf2-9106-47d0-bda3-500d2508f3b8)

- **Enhance Data:** Improve the quality and usability of your image data by adjusting contrast, brightness, and noise levels.

- **Object-Level Manipulation:** Perform operations on individual objects or instances within images, such as cropping, duplicating, or changing their color classes.

  ![object-transforms](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/34294f35-b720-4941-9e19-5fce70be9c33)

- **Customize Workflows:** Create complex data transformation workflows by combining multiple transformation nodes to meet your specific requirements.

- **Node Documentation:** Detailed documentation is available for each transformation node, explaining how to use it effectively. These guides provide step-by-step instructions and examples for each node, making it easy for users to understand and leverage the full power of the application.

  ![node-docs](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/6d5d1c8a-9a72-4827-9869-714b98b2e418)

- **Save & Load Presets:** Save your customized transformation workflows as presets for future use. This feature allows you to store and reuse your preferred configurations quickly.

  ![load-preset](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/5cd9ebb7-0fd5-4901-a1d3-9ecee38b629f)

- **Output Flexibility:** Choose from multiple export options to save your transformed data in a format that best suits your needs.

  ![merge-projects](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/1baaedff-3d02-46bb-a307-d690036509d2)

## How To Run

There are several ways to run the application, depending on your needs and preferences:

<details open>
<summary><b>1. Run App from Ecosystem</b></summary>

![run-from-ecosystem](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/f9d5ab6d-68e0-40d4-96a4-571eea41a383)

</details>

<details>
<summary><b>2. Run App from the context menu of the Project</b></summary>

![run-from-project](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/1df4ad60-4969-4c2a-b2bb-6cb9032fa13c)

</details>

<details>
<summary><b>3. Run App from the context menu of the Dataset</b></summary>

![run-from-dataset](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/ec9b955e-8abc-4908-821c-768eb7bcdd68)

</details>

<details>
<summary><b>4. Run Pipeline from Project</b></summary>

![run-pipeline-from-project](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/0bbf3f31-2a03-4f7c-b8a1-38eeaa314a99)

</details>

<details>
<summary><b>5. Run Pipeline from Dataset</b></summary>

![run-pipeline-from-dataset](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/0a2da1c9-97ae-4d44-b087-f24657fb0370)

</details>

<details>
<summary><b>6. Run Pipeline with Filters</b></summary>

![run-pipeline-from-filters](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/1bf0e32c-8af7-44f5-8fa8-921320cedb95)

</details>

<!-- <details open>
<summary><b>3. Run App from Team Files</b></summary>

![run-from-teamfiles-min](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/ae996fcb-b9e0-4b1a-a514-bfab1097b40d)

</details> -->
