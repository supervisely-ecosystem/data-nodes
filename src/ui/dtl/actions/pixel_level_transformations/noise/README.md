# Noise

`Noise` layer adds noise of Gaussian distribution to the images.

### Settings:

- **Mean** - Set value to specify the peak of the noise distribution.
- **Spread** - Set value to increase the spread of the noise distribution.

Minimum area (`min_area`) for pixel group to be removed can be provided in pixels (`ex. 10px`) or in percentage (`1%`).

If min_area is in percentage, area of pixel group to delete can be calculated based on total resoultion of image (`src_type` `=` `image`) or based on area of bounding box of annotation (`src_type` `=` `bbox`).

Only annotations of classes from array `classes` would be processed. Those classes should have shape `bitmap`.

### Example. Add noise to image

In this example, we add noise to the image with mean 23 and spread 65.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Noise: Mean: 23, Spread: 65</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/62298fa3-3720-4e49-8b07-271162a8e8fb" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/8851e6aa-8316-4f9d-ba5b-9c4a64f20bb6" alt="Noise" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "noise",
  "src": ["$images_project_1"],
  "dst": "$noise_2",
  "settings": {
    "mean": 23,
    "std": 65
  }
}
</pre>
</details>
