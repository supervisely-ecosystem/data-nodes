# Filter Video without Objects

`Filter Video without Objects` layer is used to filter videos depending on not having any objects of the selected class on it.

# Settings

- **Exclude classes** - List of classes that should not be present on the video.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "filter_video_without_objects",
	"src": [
		"$data_1"
	],
	"dst": [
		"$filter_video_without_objects_2__true",
		"$filter_video_without_objects_2__false"
	],
	"settings": {
		"exclude_classes": [
			"car",
			"pedestrian"
		]
	}
},
```

</details>
