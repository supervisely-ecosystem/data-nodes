# Copy Annotations

`Copy Annotations` is an `output` node that copies annotations from the input project to the destination project by matching selected datasets and image names. Any modifications to the images will not be applied to the destination project images.

### How node works:

1. Take the input and the destination projects.
2. Select destination datasets for matching:
   - If the input contains one dataset, all selected destination datasets are checked. Dataset names do not have to match.
   - If the input contains multiple datasets, each input dataset is matched only with a destination dataset that has the same name.
3. Match the images from the input and destination datasets:
   - Matched by names
   - Matched by links (if strict match is enabled)
   - Matched by hashes (if strict match is enabled)
   - Matched by sizes (height and width)
4. Copy the annotations from the input project to the destination project by matching the image names.

### How to use:

* **Simple use case:** You have a project with images and annotations and you want to copy the annotations from one project to another project. You can use `Images Project` node to set input project and node `Copy Annotations` to set the destination project, then simply run the workflow. The annotations from the input project will be copied to the destination project.

	![simpleuse](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/10ad7098-3d74-417e-8ee3-06972551926a)

* **Do not use any layers that modify image size:** Layers from **Spatial-level transforms** are not supported, the node will not process the images if you use it, because it will modify the image size.

	![donotuse](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/90ecdc65-79d8-4ddd-bb73-4e8c2013cf34)


* **You can use layers that modify annotations:** The node will add new annotations to the existing image in the destination project or replace its current annotations with the ones from the input project.

	![correctuse](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/ac908960-fdaa-41ce-b586-b782a59f336f)

* **When Datasets and Images Match by Name:** If there's an image in your destination project that shares its name with an image from the input project, what happens next depends on your chosen settings. You can either add new annotations to the existing image in the destination project or replace its current annotations with the ones from the input project.

* **Matching Images by Name Only:** If the input contains one dataset, images will be matched across all selected destination datasets based on their names and properties. Destination dataset names do not have to match the input dataset name.

* **What Happens to Unmatched Images:** If an image from the input project doesn't have a matching name in the destination project, it will not be processed.

* **Handling Images of Different Sizes:** If two images share the same name across the input and destination projects but differ in size, the node will not process them.

* **Modifying Existing Annotations:** Annotation-only changes can be copied. If image size is modified in the pipeline, the node will not process those images because it only copies annotations and does not modify destination images.

* **Dealing with Duplicate Projects and the 'Replace' Option:** If you have two input projects that contain the same dataset names and identical images, and you choose the `Replace Annotations` option, the annotations from the second input project will overwrite the annotations from the first input project in the destination project. We don't recommend using the `Replace Annotations` option in this case.

### Settings

- **Select project** - select the destination project and dataset(s):
    - `Project` - select the project
    - `Select all datasets` - if this option is enabled, all datasets from the selected project will be used
    - `Dataset` - select one or more datasets from the selected project
    - If the input contains one dataset, selected destination datasets are matched by image names. If the input contains multiple datasets, destination dataset names must match input dataset names.
- **Select how to copy** - select how to add annotations to the project. Option `Replace Annotations` will replace the annotations in the destination project with the annotations from the input project. Option `Merge Annotations` will merge the annotations from the input project and the destination project.
- **Strict match** - if enabled, items will be also matched by links and hashes
- **Backup selected project** - if this option is enabled, the destination project will be backed up before the transformation process starts

### JSON views

<details>
  <summary>JSON Preview</summary>
  <pre>
{
	"action": "copy_annotations",
	"src": [
		"$images_project_1"
	],
	"dst": "34747",
	"settings": {
		"project_id": 34747,
		"dataset_ids": [
			84993
		],
		"add_option": "merge",
		"backup_destination_project": true
	}
}
  </pre>
</details>
