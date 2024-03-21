# Line to Mask

`Line to Bitmap` layer convert labels with shape `Polyline` to `Bitmap`.

### Settings

- **Classes** — Select classes to convert from `Polyline` to `Bitmap`.
- **Width** — Specify width of the lines of the resulting bitmaps in pixels.

### Example

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Line covnerted to Bitmap</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/48913536/2a181111-2ef9-406f-b076-57b0708d7b34" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/48913536/c658e27e-4827-4d9d-bc89-d7542f4ea571" alt="Line covnerted to Bitmap" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
```json
{
  "action": "line_to_mask",
  "src": ["$images_project_1"],
  "dst": "$line_to_mask_2",
  "settings": {
      "classes_mapping": {
          "Crossing": "Crossing",
          "__other__": "__ignore__"
      },
      "width": 15
  }
}
```
</details>
