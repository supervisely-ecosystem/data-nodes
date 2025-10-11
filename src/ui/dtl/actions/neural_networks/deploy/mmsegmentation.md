
# Deploy MMSegmentation

`Deploy MMSegmentation` using [Serve MMSegmentation](../../../../supervisely-ecosystem/mmsegmentation/serve) app to serve models and can be used to deploy custom and pretrained models that you can use via `Apply NN` layer. Custom models will appear in the custom tab of the table only if you have any trained MMSegmentation models in your Team Files. You can train your own model using [Train MMSegmentation](https://ecosystem.supervisely.com/apps/mmsegmentation/train) app. If you want to use pretrained models, simply select "Pretrained public models" tab in model selector.

### Settings:

### How to use:

1. Add `Deploy MMSegmentation` layer
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
    "action": "deploy_segmentation",
    "src": [],
    "dst": "$deploy_segmentation",
    "settings": {
      "agent_id": 359,
      "device": "cuda:0",
      "model_source": "Pretrained models",
      "task_type": "semantic segmentation",
      "checkpoint_name": "upernet_convnext_xlarge_fp16_640x640_160k_ade20k.pth",
      "checkpoint_url": "https://download.openmmlab.com/mmsegmentation/v0.5/convnext/upernet_convnext_xlarge_fp16_640x640_160k_ade20k/upernet_convnext_xlarge_fp16_640x640_160k_ade20k_20220226_080344-95fc38c2.pth",
      "config_url": "configs/convnext/upernet_convnext_xlarge_fp16_640x640_160k_ade20k.py",
      "arch_type": "ConvNeXt",
      "stop_model_session": true,
      "session_id": 60493
    }
  }
</pre>
</details>
