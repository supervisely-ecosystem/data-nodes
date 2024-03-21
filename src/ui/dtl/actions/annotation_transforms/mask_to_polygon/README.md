# Mask to Polygon

`Mask to Polygon` layer extracts contours from masks (bitmaps) and stores result as polygons with the same class names.

### Settings

**Classes** — Select classes to convert to Polygon shape.

### Example. Mask to Polygon for `squirrel` class object

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image (Bitmap)</strong></td>
<td style="text-align:center; width:50%"><strong>Result image (Polygon)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/5ac14178-2aa3-4da1-8d3f-b780cb5ed519" alt="Original image (Bitmap)" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/3a99af70-52a6-4a21-a45d-1d1bef0d0762" alt="Result image" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
  <pre>
{
  "action": "find_contours",
  "src": ["$images_project_12"],
  "dst": "$find_contours_18",
  "settings": {
    "classes_mapping": {
      "cat": "cat_contours",
      "squirrel": "squirrel_contours"
    }
  }
}
  </pre>
</details>
