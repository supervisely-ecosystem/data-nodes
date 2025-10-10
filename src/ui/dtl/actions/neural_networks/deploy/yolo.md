# YOLO v8 - v12

`Deploy YOLO v8 - v12` using [Serve YOLO v8 - v12](../../../../supervisely-ecosystem/yolo/supervisely_integration/serve) app to serve models and can be used to deploy custom and pretrained models that you can use via `Apply NN` layer. Custom models will appear in the custom tab of the table only if you have any trained YOLO v8 - v12 models in your Team Files. You can train your own model using [Train YOLO v8 - v12](../../../../../../supervisely-ecosystem/yolo/supervisely_integration/train) app. If you want to use pretrained models, simply select "Pretrained public models" tab in model selector.


- YOLOv8 is a powerful neural network architecture that provides both decent accuracy of predictions and high speed of inference. In comparison to YOLOv5, YOLOv8 uses an anchor-free head (allowing to speed up the non-max suppression (NMS) process), a new backbone, and new loss functions.
- YOLOv9 builds on the advancements of YOLOv8 by further improving the model's performance and efficiency. It incorporates extended feature extraction techniques, advanced loss functions and optimized training processes for better accuracy and faster inference times.
- YOLOv10 introduces consistent dual assignments for NMS-free training and adopts a holistic efficiency-accuracy-driven model design strategy.
- YOLOv12, the latest iteration in the YOLO series, continues the trend of balancing accuracy and efficiency with significant advancements. It introduces a hybrid architecture that combines the strengths of anchor-free and anchor-based methods, allowing the model to adapt dynamically based on the characteristics of the input data.

### Settings:

### How to use:

1. Add `Deploy YOLO v8 - v12` layer
2. Open agent settings and select agent and device
3. Open models selector and select one of the available models
4. Press `SERVE`
5. Wait until model is deployed, you will see "Model deployed" message in the bottom of the layer card
6. Connect this layer to `Apply NN Inference` layer's `Deployed model (optional)` socket
7. If you want to deploy another model, press `STOP` and repeat steps 3, 4, 5 and 6

### Settings:

- **Select agent** - select agent and device that will be used for deployment:
    - `Agent` - select agent
    - `Device` - select CPU or GPU (faster) device if available
- **Select model** - select custom or pretrained model
    - `Model type` - custom or pretrained
    - `Task type` - select task type from "object detection" or "instance segmentation"
    - `Checkpoint` - select checkpoint
- **Auto stop model session** - automatically stop model session when pipeline is finished

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "deploy_yolo",
  "src": [],
  "dst": "$deploy_yolo_1",
  "settings": {
    "agent_id": 348,
    "device": "cuda:0",
    "model_type": "Pretrained models",
    "model_name": "YOLOv12n",
    "task_type": "object detection",
    "model_path": null,
    "stop_model_session": true,
    "session_id": 73456
  }
}
</pre>
</details>
