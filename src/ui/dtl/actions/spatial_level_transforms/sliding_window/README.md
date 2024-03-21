# Sliding Window

`Sliding Window` layer is used to crop part of image with its annotations by sliding of window from left to rigth, from top to bottom.

### Settings

- **Window** - Set the `width` and `height` (in pixels) of the sliding window.
- **Min overlap** - Set the minimum overlap (in pixels) of the sliding window along `x` and `y` axis.

Here is the graphical description of fields:

![sw_schema](https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/44ff0861-212b-460b-93b9-a7fc8436b0f3)

### Example. Sliding window (512x512, overlap: 32)

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Sliding windows (512x512, overlap: 32)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/5c821ec5-8a52-4f25-9ffb-316dcb4709f2" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/f6dace1f-565d-4651-8c39-94ab96ebb3dc" alt="Sliding window" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "sliding_window",
  "src": ["$images_project_1"],
  "dst": "$sliding_window_5",
  "settings": {
    "window": {
      "width": 512,
      "height": 512
    },
    "min_overlap": {
      "x": 32,
      "y": 32
    }
  }
}
</pre>
</details>
