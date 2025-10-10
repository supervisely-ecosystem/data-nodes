
# Deploy MMDetection

`Deploy MMDetection` using [Serve MMDetection 3.0](../../../../supervisely-ecosystem/serve-mmdetection-v3) app to serve models and can be used to deploy custom and pretrained models that you can use via `Apply NN` layer. Custom models will appear in the custom tab of the table only if you have any trained MMDetection models in your Team Files. You can train your own model using [Train MMDetection 3.0](../../../../supervisely-ecosystem/train-mmdetection-v3) app. If you want to use pretrained models, simply select "Pretrained public models" tab in model selector.

![image](https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/b888c691-5e03-4e45-80f8-8a5a3918caf0)

### Settings:

### How to use:

1. Add `Deploy MMDetection` layer
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
    "action": "deploy_mmdetection",
    "src": [],
    "dst": "$deploy_mmdetection_2",
    "settings": {
      "agent_id": 359,
      "device": "cuda:0",
      "model_source": "Pretrained models",
      "task_type": "instance segmentation",
      "checkpoint_name": "mask-rcnn_convnext-t-p4-w7_fpn_amp-ms-crop-3x_coco.pth",
      "checkpoint_url": "https://download.openmmlab.com/mmdetection/v2.0/convnext/mask_rcnn_convnext-t_p4_w7_fpn_fp16_ms-crop_3x_coco/mask_rcnn_convnext-t_p4_w7_fpn_fp16_ms-crop_3x_coco_20220426_154953-050731f4.pth",
      "config_url": "configs/convnext/mask-rcnn_convnext-t-p4-w7_fpn_amp-ms-crop-3x_coco.py",
      "arch_type": "ConvNeXt",
      "stop_model_session": true,
      "session_id": 59493
    }
  }
</pre>
</details>
