# Crop

Layer for cropping images by specifying pixels or percentage to crop from each side or by cropping the random part of the image with specified size.

### Settings:

- **Crop type** - Select crop type:
    - **Sides** - Crop image by specifying pixels or percentages to crop from each side (`top`, `left`, `right`, `bottom`).
    - **Random part** - Crop random part of the image by specifying min and max percentage range for `width` and `height`. Also you can specify whether to keep the aspect ratio of the image (should resulting random crop have the same aspect ratio as a source image).

### Example 1. Crop by sides

Set crop type to "**sides**" and specify pixels or percentage to crop from each side.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Cropped image: 350px from top, 250px from bottom</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/52483886-392d-43a8-aeb4-a5fb01950a30" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a4f39565-216a-427f-a1a3-b32f180991e0" alt="Crop type: Sides" /> </td>
</tr>
</table>

### Example 2. Crop random part

In this example we will crop **random part** of the image with specifying min and max percentage range for `width` and `height`.
Also we will **keep the aspect ratio** of the source image.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Random part crop with keeping aspect ratio</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/f29db46e-dc66-415f-a808-6f89a4a112ea" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a2380eb8-bc82-4321-99c1-e1a4cea2e204" alt="Crop type: Random part" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view `Sides` crop type</summary>
<pre>
{
  "action": "crop",
  "src": ["$images_project_7"],
  "dst": "$crop_8",
  "settings": {
    "sides": {
      "top": "350px",
      "left": "0px",
      "right": "0px",
      "bottom": "250px"
    }
  }
}
</pre>
</details>

<details>
  <summary>JSON config `Random part` crop type</summary>
<pre>
{
  "action": "crop",
  "src": ["$images_project_7"],
  "dst": "$crop_8",
  "settings": {
    "random_part": {
      "height": {
        "min_percent": 60,
        "max_percent": 65
      },
      "width": {
        "min_percent": 60,
        "max_percent": 65
      },
      "keep_aspect_ratio": true
    }
  }
}
</pre>
</details>
