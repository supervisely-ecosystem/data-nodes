# Filter Images without Object Classes

`Filter Images without Object Classes` layer is used to filter images depending on not having any objects of the selected class on it.

# Settings

- **Exclude classes** - List of classes that should not be present on the image.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "filter_image_without_objects",
	"src": [
		"$data_1"
	],
	"dst": [
		"$filter_image_without_objects_2__true",
		"$filter_image_without_objects_2__false"
	],
	"settings": {
		"exclude_classes": [
			"cat",
			"dog",
			"horse",
		]
	}
},
```

</details>
