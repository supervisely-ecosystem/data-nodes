# Skeletonize

`Skeletonize` layer extracts skeletons from bitmap figures.

### Settings

- **Classes** - Choose classes to apply transformation. Only classes with shape `bitmap` are allowed.
- **Operation type** - Select algorithm of processing. Available options: `skeletonization`, `medial_axis`, `thinning`.

Each figure of selected classes will be reduced to 1 pixel wide representation. Each source mask (figure of shape "bitmap") produces one resulting mask (shape "bitmap").

It uses scikit-image as a backend, so three methods of skeletonization are provided. For more information, look [here](https://scikit-image.org/docs/dev/auto_examples/edges/plot_skeleton.html).

> For large images it may be not fast.

### Example

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Skeletonized image</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/5215ff13-d53d-4911-a156-8efe4d2b63a1" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/57fbff6c-a434-4c7f-83cd-b961e8f37c48" alt="Skeletonized image" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "skeletonize",
  "src": ["$images_project_12"],
  "dst": "$skeletonize_15",
  "settings": {
    "classes": ["Cat", "Squirrel"],
    "method": "skeletonization"
  }
}
</pre>
</details>
