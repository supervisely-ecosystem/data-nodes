# Filter Videos without Annotations

`Filter Videos without Annotations` layer is used to filter videos without objects and tags.

# Settings

This layer doesn't have any settings.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "filter_video_without_annotation",
	"src": [
		"$videos_project_1"
	],
	"dst": [
		"$filter_video_without_objects_2__true",
		"$filter_video_without_objects_2__false"
	],
	"settings": {}
},
```

</details>
