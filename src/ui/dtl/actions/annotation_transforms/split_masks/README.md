# Split Masks

`Split Masks` layer takes one bitmap label mask and split it into few bitmap masks if it contains non-connected components.

### Settings

- **Classes** - Select classes for which you want to split masks. 

### Example. Split masks of class `bird`

In this example we will split masks of class `bird` (i.e. if mask contain few non-connected components, then each component will be saved as separate mask).

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Splitted masks</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/57d3cc8e-0222-49f3-bb75-77c39cd30bcc" alt="Merged masks" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/060f54c7-abe9-4097-ae84-5630be822596" alt="Original image" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "split_masks",
  "src": ["$images_project_7"],
  "dst": "$split_masks_9",
  "settings": {
    "classes": ["bird"]
  }
}
</pre>
</details>
