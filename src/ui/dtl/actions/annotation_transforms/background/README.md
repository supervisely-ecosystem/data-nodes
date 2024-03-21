# Background

`Background` layer adds background class with shape `rectangle` (size equals to image size) to image annotation, providing a clear label for the areas of the image that do not contain any specific objects or regions of interest.

This layer can be used to prepare data for semantic segmentation training tasks.

### Settings:

- **Background Class name** - name of the class that will be added to image annotations as background rectangle.

### Example. Add background class to image annotations

This example adds polygon object with class "background" to the image annotations as bottom layer.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Background class: "background"</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/413384a4-d4d3-4542-96c5-f809b12ec104" alt="Original" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/553f4ee7-1525-4d94-b21c-f5f605c8fb70" alt="With background" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "background",
  "src": ["$images_project_1"],
  "dst": "$background_3",
  "settings": {
    "class": "background"
  }
}
</pre>
</details>
