# Apply NN Inference

`Apply NN Inference` layer is used to apply a neural network to the input data. Layer connects to deployed model such as Serve YOLOv8 app and applies it to the input data.

There are 2 ways to connect model in `Apply NN Inference` layer:

1. Run one of the serving apps manually and then select app session in the model selector or if you already have a running model session, you can just select it.
2. Add `Deploy` layer to the scene and deploy model via this layer then simply link this layer to the `Apply NN Inference` layer's `Deployed model (optional)` socket.

Read our post on [Supervisely blog](https://supervisely.com/blog/) to learn how to effectively train, deploy and use the model on the YOLOv8 example: [No-code tutorial: train and predict YOLOv8 on custom data](https://supervisely.com/blog/train-yolov8-on-custom-data-no-code/).

Supported models:

- [YOLOv5](/ecosystem/apps/yolov5/supervisely/serve)
- [YOLOv5 2.0](/ecosystem/apps/yolov5_2.0/serve)
- [YOLOv8](/ecosystem/apps/yolov8/serve)
- [MMSegmentation](/ecosystem/apps/mmsegmentation/serve)
- [MMDetection](/ecosystem/apps/mmdetection/serve)
- [MMDetection 3.0](/ecosystem/apps/serve-mmdetection-v3)
- [Detectron2](/ecosystem/apps/detectron2/supervisely/instance_segmentation/serve)
- [UNet](/ecosystem/apps/unet/supervisely/serve)

### Settings:

- **Connect to Model** - Select the deployed model that will be applied to the data.
- **Сlasses** - Choose model classes that will be labeled on the data. If no classes are selected, no classes will be labeled.
- **Tags** - Choose model tags that will be assigned to the labeled objects. If no tags are selected, no tags will be assigned.
- **Class / Tag name suffix** - Suffix that will be added to the class / tag name if it have conflict with existing class / tag in the project. For example, if the input project has existing class with name `person` and the suffix is `model`, the resulting class name will be `person-model`.
- **Model Settings**
  - **Add suffix method** - Select how to add suffix to the class / tag name.
    - Available methods:
      - **Add only to classes that already exists** - Suffix will be added only to classes that already exists in both model and project metas.
      - **Add only to incompatible classes** - Suffix will be added only to classes that have different shapes in model and project metas.
      - **Always add suffix** - Suffix will be added to all classes and tags.
  - **How to add predictions** - Select how to add the predicted annotation to the image.
    - Available methods:
      - **Merge** - Merge predicted annotation with the existing one.
      - **Replace** - Replace the existing annotation with the one predicted by the model. All original labels will be removed.
      - **Replace and keep image tags** - Works as **Replace** method but keeps the image tags.
  - **Skip already labeled images** - If enabled, the model will not be applied to the images that already have labels or image tags.
  - **Inference settings** - Model specific settings in `YAML` format
  - **Apply method** - Method that will be used to apply the model to the data.
    - Available methods:
      - **Full Image** - Model will be applied to the full image.
      - **ROI (Coming Soon)** - Model will be applied only for ROIs defined by object's bounding box.
      - **Sliding Window (Coming Soon)** - Model will be applied to image using sliding window approach.


<table>
<tr>
<td style="text-align:center; width:33%"><strong>Original image</strong></td>
<td style="text-align:center; width:33%"><strong>YOLOv5 applied (Object Detection)</strong></td>
<td style="text-align:center; width:33%"><strong>YOLOv8 applied (Instance Segmentation)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/9620df11-26ae-4170-8188-1f6f1810971f" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/32abd297-107a-4edf-8a70-1545d2967e88" alt="YOLOv5 applied (Object Detection)" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/fdfd2613-8e35-4560-9677-b89aa7e036ac" alt="YOLOv8 applied (Instance Segmentation)" /> </td>
</tr>
</table>

### Examples

<details>
  <summary>JSON view</summary>
<pre>

```json
{
	"action": "apply_nn_inference",
	"src": [
		"$data_1"
	],
	"dst": "$apply_nn_inference_2",
	"settings": {
		"current_meta": {
			"classes": [],
			"tags": []
		},
		"session_id": 47491,
		"model_info": {
			"app_name": "Serve YOLOv8",
			"session_id": 47491,
			"number_of_classes": 80,
			"sliding_window_support": "basic",
			"videos_support": true,
			"async_video_inference_support": true,
			"tracking_on_videos_support": true,
			"async_image_inference_support": true,
			"task type": "object detection"
		},
		"model_meta": {
			"classes": [
				{
					"title": "person",
					"shape": "rectangle",
					"color": "#0F718A",
					"geometry_config": {},
					"hotkey": ""
				},
				{
					"title": "bicycle",
					"shape": "rectangle",
					"color": "#0F148A",
					"geometry_config": {},
					"hotkey": ""
				},
				{
					"title": "car",
					"shape": "rectangle",
					"color": "#8A500F",
					"geometry_config": {},
					"hotkey": ""
				},
                		...
                		...
                		...
				{
					"title": "toothbrush",
					"shape": "rectangle",
					"color": "#8A0F52",
					"geometry_config": {},
					"hotkey": ""
				}
			],
			"tags": [
				{
					"name": "confidence",
					"value_type": "any_number",
					"color": "#0F478A",
					"hotkey": "",
					"applicable_type": "all",
					"classes": []
				}
			]
		},
		"model_settings": {
			"conf": 0.25,
			"iou": 0.7,
			"half": false,
			"max_det": 300,
			"agnostic_nms": false,
			"point_threshold": 0.1
		},
		"model_suffix": "model",
		"model_conflict": "replace",
		"use_model_suffix": true,
		"apply_method": "image",
		"classes": [
				"person",
            	"car",
            	"sheep",
            	"dog",
            	"cat",
		],
		"tags": [
			"confidence"
		]
	}
}
```
</pre>
</details>
