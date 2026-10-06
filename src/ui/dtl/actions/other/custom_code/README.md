# Custom Code

`Custom Code` runs your own Python script on every video and keeps the frame ranges it returns. Each range becomes a clip with its annotations, so the node can select, trim and split videos by any logic: OpenCV, a model, or code from your own packages.

The node is off unless the app's image sets the environment variable `ML_PIPELINES_CUSTOM_CODE=1`, because it runs arbitrary code inside the app.

# Settings

- **Script** - a `.py` file in Team Files. Pick one from `/ml-pipelines/custom-code/`, pick any `.py` file in Team Files, or start from the template. Edit it in the node, then **Save** writes it back to Team Files and **Save as** creates a new file. Unsaved changes are saved when the pipeline starts. The node keeps the path of the script, not its text.
- **Parameters** - JSON passed to the script as `params`.
- **Workers** - how many videos run at the same time, each in its own process. `0` uses all CPU cores of the agent.

The script defines:

```python
def process(video_path: str, video_info, ann, params: dict) -> list[tuple[int, int]]:
    ...
```

It returns inclusive `(start, end)` frame ranges. `[]` drops the video, and `[(0, video_info.frames_count - 1)]` passes it through unchanged. Clips are cut at exact frames and re-encoded to H.264 MP4. A video whose script fails is skipped with an error in the log, and the run continues.

### JSON views

<details>
  <summary>JSON View</summary>

```json
{
	"action": "custom_code",
	"src": [
		"$videos_project_1"
	],
	"dst": "$custom_code_2",
	"settings": {
		"script_path": "/ml-pipelines/custom-code/select_motion.py",
		"params": {
			"width": 320,
			"threshold": 5.0,
			"min_length": 25
		},
		"workers": 0
	}
}
```

</details>
