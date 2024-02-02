# Copy Annotations

`Copy Annotations` is an `output` node that copies annotations from the input project to the destination project by matching the dataset and image names. Any modifications to the images will not be applied to the destination project images.

### How node works:

1. Take the input and the destination projects.
2. Match the images from datasets in the input and the destination projects.
   1. :white_check_mark: Matched by names
   2. :white_check_mark: Matched by links
   3. :white_check_mark: Matched by hashes
   4. :white_check_mark: Matched by sizes (height and width)
3. Copy the annotations from the input project to the destination project by matching the image names.

### How to use:

* **When Datasets and Images Match by Name:** If there's an image in your destination project that shares its name with an image from the input project, what happens next depends on your chosen settings. You can either add new annotations to the existing image in the destination project or replace its current annotations with the ones from the input project.

* **Matching Images by Name Only:** If both the input and destination projects are working with a single dataset (either because they only contain one or you've selected just one), then images will be matched and processed based solely on their names.

* **What Happens to Unmatched Images:** If an image from the input project doesn't have a matching name in the destination project, it will not be processed.

* **Handling Images of Different Sizes:** If two images share the same name across the input and destination projects but differ in size, the node will not process them.

* **Modifying Existing Annotations:** If you're using layers that modify annotations or image size, the node will not process the images. This is because the node only copies annotations and does not modify the images themselves.

* **Dealing with Duplicate Projects and the 'Replace' Option:** If you have two input projects that contain the same dataset names and identical images, and you choose the `Replace Annotations` option, the annotations from the second input project will overwrite the annotations from the first input project in the destination project. We don't recommend using the `Replace Annotations` option in this case.

### Settings

- **Select project** - select the destination project and dataset(s):
    - `Project` - select the project
    - `Select all datasets` - if this option is enabled, all datasets from the selected project will be used
    - `Dataset` - select one or more datasets from the selected project
- **Select how to copy** - select how to add annotations to the project. Option `Replace Annotations` will replace the annotations in the destination project with the annotations from the input project. Option `Merge Annotations` will merge the annotations from the input project and the destination project.
- **Backup selected project** - if this option is enabled, the destination project will be backed up before the transformation process starts

### JSON views

<details>
  <summary>JSON Preview</summary>
  <pre>
{
	"action": "copy_annotations",
	"src": [
		"$data_1"
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
