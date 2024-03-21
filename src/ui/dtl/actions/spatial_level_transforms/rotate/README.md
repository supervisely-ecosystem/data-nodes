# Rotate

`Rotate` layer rotates images and its annotations.

#### Settings:

- **Rotate Angles** - Set the range of angles (`Min degrees` and `Max degrees`) to rotate the image.
- **Black Regions** - Select the `mode` to handle black regions (possible values: `keep`, `crop`, `preserve_size`).

Each image will be rotated by a random angle (around the image center, CCW) with uniform distribution from `min_degrees` to `max_degrees`. You can:

- keep original image data (`mode: keep`), then new regions will be filled with black color;
- crop rotated result to exclude black regions (`mode: crop`);
- crop rotated result to preserve original image size and scale of objects (`mode: preserve_size`);

### Example 1. Keep black regions

In this example we will rotate image and keep black regions (i.e. fill new regions with black color).

mode: `keep`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Keep black regions of rotated image</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/71d2924e-9c09-4da8-86e7-8fe883ea49d0" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e0025576-446f-44fd-8ccb-bc4ed14ce96e" alt="Rotated Image. Mode: keep" /> </td>
</tr>
</table>

### Example 2. Crop black regions

In this example rotated image will be cropped to exclude black regions.

mode: `crop`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Crop black regions of rotated image</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/71d2924e-9c09-4da8-86e7-8fe883ea49d0" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/c1d88825-5a7b-47de-86f3-ec5ec385fe21" alt="Rotated Image. Mode: crop" /> </td>
</tr>
</table>

### Example 3. Preserve size of image.

In this example rotated image will be cropped to preserve original image size and scale of objects.

mode: `preserve_size`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Preserve size of rotated image</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/71d2924e-9c09-4da8-86e7-8fe883ea49d0" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/9acbe2dd-be7c-49ea-ba0e-705daa9ce419" alt="Rotated Image. Mode: preserve size" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "rotate",
  "src": ["$images_project_5"],
  "dst": "$rotate_4",
  "settings": {
    "rotate_angles": {
      "min_degrees": -45,
      "max_degrees": 45
    },
    "black_regions": {
      "mode": "keep"
    }
  }
}
</pre>
</details>
