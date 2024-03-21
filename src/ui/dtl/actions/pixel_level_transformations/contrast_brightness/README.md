# Contrast and Brightness

`contrast_brightness` layer randomly changes contrast and brightness of images.

### Settings:

- **Contrast** - Switch on if you want to change color contrast of the image. Set `min` and `max` values for contrast. To disable contrast switch parameter off or set `min` and `max` to 1.
  - **Center grey** - Switch on if you want to center colors of images (subtract 128) first.
- **Brightness** - Switch on if you want to change brightness of the image. Set `min` and `max` values for brightness. To disable brightness switch parameter off or set `min` and `max` to 0.

Image `contrast` is changed by multiplying each pixel by random value with uniform distribution from `min` to `max`. To disable, set `min` and `max` to 1. To center colors of images (subtract 128) first, set `center_grey` to `true`.

Image `brightness` is changed by adding to each pixel a random value with uniform distribution from `min` to `max`. To disable, set `min` and `max` to 0.

### Example 1. Contrast

<table>
<tr>
<td style="text-align:center; width:33%"><strong>Contrast: 0.4...0.8, center_grey: true</strong></td>
<td style="text-align:center; width:33%"><strong>Original image</strong></td>
<td style="text-align:center; width:33%"><strong>Contrast: 6...8, center_grey: true</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/dda6939b-e8a7-4afd-ab1a-e9212dd4a156" alt="Contrast 0.4-0.8" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/92069f7c-c2f0-4c1a-be22-0a59602039a6" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/1f43c7a3-abfe-4d05-8506-7967628270f5" alt="Contrast 6-8" /> </td>
</tr>
</table>

### Example 2. Brightness

<table>
<tr>
<td style="text-align:center; width:33%"><strong>Brightness: -110...-60</strong></td>
<td style="text-align:center; width:33%"><strong>Original image</strong></td>
<td style="text-align:center; width:33%"><strong>Brightness: 60...110</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/9b09084b-943c-42b0-aea5-5df1fb66673f" alt="Brightness-" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/d52872cb-8d05-4239-a959-7f232fc2027e" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/910a4044-6c3e-4fb3-bb0b-96afdbde368b" alt="Brightness+" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "contrast_brightness",
  "src": ["$images_project_5"],
  "dst": "$contrast_brightness_9",
  "settings": {
    "contrast": {
      "min": 6,
      "max": 8,
      "center_grey": true
    },
    "brightness": {
      "min": 60,
      "max": 110
    }
  }
}
</pre>
</details>
