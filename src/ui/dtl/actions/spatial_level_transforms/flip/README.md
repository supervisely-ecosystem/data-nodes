# Flip

`Flip` layer simply flips data (images + annotations) vertically or horizontally.

Supports flipping `bitmap`, `polygon`, `rectangle`, `point`, `polyline`, `graph` (`keypoint`) geometry types.

### Settings:

- **Axis** - Choose the direction along which the images with annotations will be flipped (`vertical` or `horizontal`).

### Example 1. Vertical flip

Select `vertical` in layer settings.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Vertical flip</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/0edfa43f-84b2-4f3a-83da-0d34f0c6976e" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e901ac5a-156b-46bd-9050-539954221d44" alt="vertical flip" /> </td>
</tr>
</table>

### Example 2. Horizontal flip

Select `horizontal` in layer settings.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Horizontal flip</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a7e76acb-bc94-492b-aff5-2f19b3e9ecb4" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/67ac9ff5-b9da-459c-8fca-fc9037fc2095" alt="horizontal flip " /> </td>
</tr>
</table>

### JSON views

<details>
  <summary>JSON view for vertical flip</summary>
<pre>
{
  "action": "flip",
  "src": ["$images_project_1"],
  "dst": "$images_project_2",
  "settings": {
    "axis": "vertical"
  }
}
</pre>
</details>

<details>
  <summary>JSON view for horizontal flip</summary>
<pre>
{
  "action": "flip",
  "src": ["$images_project_1"],
  "dst": "$images_project_2",
  "settings": {
    "axis": "horizontal"
  }
}
</pre>
</details>
