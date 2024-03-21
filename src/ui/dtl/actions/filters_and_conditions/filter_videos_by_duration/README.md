# Filter Videos by Duration

`Filter Videos by Duration` layer is used to filter videos by the duration.

# Settings

- **Duration unit** - Set duration in frames or seconds of the video.
- **Duration threshold** - Set duration threshold.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "filter_video_by_duration",
	"src": [
		"$videos_project_1"
	],
	"dst": "$filter_video_by_duration_2",
	"settings": {
		"duration_unit": "frames",
		"duration_threshold": 500
	}
}
```

</details>
