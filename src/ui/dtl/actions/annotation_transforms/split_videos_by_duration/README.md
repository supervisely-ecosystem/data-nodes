# Split Video by Duration

`Split Video by Duration` layer is used to split videos by the duration.

# Settings

- **Duration unit** - Set duration in frames or seconds of the video.
- **Split step** - Set the step of the split. For example, if you set the step to 10 seconds, the video will be split every 10 seconds.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "split_video_by_duration",
	"src": [
		"$videos_project_1"
	],
	"dst": "$split_video_by_duration_2",
	"settings": {
		"duration_unit": "frames",
		"split_step": 500
	}
}
```

</details>
