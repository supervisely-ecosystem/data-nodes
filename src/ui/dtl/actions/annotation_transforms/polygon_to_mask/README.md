# Polygon to Mask

`Polygon to Mask` converts annotations of shape polygon to shape bitmap.

Polygons will be drawn filled, considering holes.

> Figures of other shapes may also be converted to bitmap with the layer. Points will be drawn as single-pixel bitmaps, and lines will be drawn with thickness = 1.

### Settings

- **Classes** — Select classes to convert polygons to bitmaps. If no classes are selected, all objects will be preserved. Only `polygon` shapes are allowed.

### Example. Convert `road` class polygon to bitmap

</details>
<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original label (Polygon)</strong></td>
<td style="text-align:center; width:50%"><strong>Result label (Mask)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/95068603-8612-4ec7-b4ec-d4907d830ea3" alt="Original label (Polygon)"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/b7e0eaf0-202a-40d2-9c8d-3a8bda152265" alt="Result label (Mask)"/> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "polygon_to_mask",
  "src": ["$images_project_1"],
  "dst": "$polygon_to_mask_4",
  "settings": {
    "classes_mapping": {
      "road": "road"
    }
  }
}
</pre>
</details>
