# Deploy RT-DETRv2

`Deploy RT-DETRv2` using [Serve RT-DETRv2](../../../../supervisely-ecosystem/rt-detrv2/supervisely_integration/serve) app to serve models and can be used to deploy custom and pretrained models that you can use via `Apply NN` layer. Custom models will appear in the custom tab of the table only if you have any trained RT-DETRv2 models in your Team Files. You can train your own model using [Train RT-DETRv2](../../../../supervisely-ecosystem/rt-detrv2/supervisely_integration/train) app. If you want to use pretrained models, simply select "Pretrained public models" tab in model selector.

### Settings:

### How to use:

1. Add `Deploy RT-DETRv2` layer
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
    - `Checkpoint` - select checkpoint
- **Auto stop model session** - automatically stop model session when pipeline is finished

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "deploy_rtdetrv2",
  "src": [],
  "dst": "$deploy_rtdetrv2_1",
  "settings": {
    "agent_id": 348,
    "device": "cuda:0",
    "model_type": "Pretrained models",
    "model_name": "RT-DETRv2-S",
    "task_type": "object detection",
    "model_path": null,
    "stop_model_session": true,
    "session_id": 74355
  }
}
</pre>
</details>
