# Resize

`Resize` layer resizes the image to the specified width and height.

#### Settings:

- **Width** - Set the width of the resized image.
- **Height** - Set the height of the resized image.
- **Keep aspect ratio** - Specify whether to keep the aspect ratio of the image.

If `aspect_ratio` setting is enabled, the image will be resized with keeping the aspect ratio of original image. In this case, the image will be resized proportionally to the specified width or height, and the other dimension will be automatically adjusted to keep the aspect ratio. Empty areas will be filled with black color to match the specified width and height.

### Example 1. Resize image by specifying width and height

In this example we will resize image **with keeping aspect ratio.**

**Original image sizes**: width 3200px and height 5000px.
**Resized image sizes**: width 1200px and height 1200px. Aspect ratio is kept, empty areas are filled with black color.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image (3200x5000)</strong></td>
<td style="text-align:center; width:50%"><strong>Result image (1200x1200) with keeping aspect ratio</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/d64f9c56-1452-4433-b393-a31d23c5a9c0" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/f3d665fd-a924-4f66-8110-0f575710c839" alt="Resized image" /> </td>
</tr>
</table>

### Example 2. Resize image by specifying width and height

In this example we will resize image **without keeping aspect ratio.**

**Original image sizes**: width 3200px and height 5000px.
**Resized image sizes**: width 1200px and height 1200px. Aspect ratio is not kept, image is stretched.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image (3200x5000)</strong></td>
<td style="text-align:center; width:50%"><strong>Result image (1200x1200) without keeping aspect ratio</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/d64f9c56-1452-4433-b393-a31d23c5a9c0" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/5b2ae4e5-efd0-4232-a32d-405fb1ce6695" alt="Resized image" /> </td>
</tr>
</table>

### JSON views

<details>
  <summary>Resize image and keep aspect ratio</summary>
<pre>
{
    "action": "resize",
    "src": [
        "$data_4"
    ],
    "dst": "$resize_5",
    "settings": {
        "width": 1200,
        "height": 1200,
        "aspect_ratio": {
            "keep": true
        }
    }
}
</pre>
</details>

<details>
  <summary>Resize image and change aspect ratio</summary>
<pre>
{
    "action": "resize",
    "src": [
        "$data_4"
    ],
    "dst": "$resize_5",
    "settings": {
        "width": 1200,
        "height": 1200,
        "aspect_ratio": {
            "keep": false
        }
    }
}
</pre>
</details>
