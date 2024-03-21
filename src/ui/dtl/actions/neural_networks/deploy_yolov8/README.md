# Deploy YOLOv8

`Deploy YOLOv8` layer can be used to deploy custom and pretrained YOLOv8 models that you can use via `Apply NN` layer. Custom models will appear in the custom tab of the table only if you have any trained `YOLOv8` models in your Team Files. You can train your own model using `Train YOLOv8` app. If you want to use pretrained models, simply select "Pretrained public models" tab in model selector.

![image](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/4d05e56b-9515-4fdd-a5fb-a139c9124e07)

### Settings:

### How to use:

1. Add `Deploy YOLOv8` layer
2. Open agent settings and select agent and device
3. Open models selector and select one of the available models
4. Press `SERVE`
5. Wait until model is deployed, you will see "Model deployed" message in the bottom of the layer card
6. Connect this layer to `Apply NN` layer and select session
7. If you want to deploy another model, press `STOP` and repeat steps 3, 4, 5 and 6

### Settings:

- **Select agent** - select agent and device that will be used for deployment:
    - `Agent` - select agent
    - `Device` - select CPU or GPU (faster) device if available
- **Select model** - select custom or pretrained model
    - `Model type` - custom or pretrained
    - `Task type` - select task type from "object detection", "instance segmentation" or "pose estimation"
    - `Checkpoint` - select checkpoint
- **Auto stop model session** - automatically stop model session when pipeline is finished

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "deploy_yolov8",
  "src": [],
  "dst": "$deploy_yolov8_1",
  "settings": {
    "agent_id": 348,
    "device": "cuda:0",
    "model_type": "Pretrained models",
    "model_name": "YOLOv8n-pose",
    "task_type": "pose estimation",
    "model_path": null,
    "stop_model_session": true,
    "session_id": 51340
  }
}
</pre>
</details>
