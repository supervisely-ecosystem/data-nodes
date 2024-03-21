# Drop Noise

`Drop Noise` layer removes connected components smaller than the specified size from bitmap annotations.

This can be useful to eliminate noise after running neural network.

### Settings

- **Classes** - List of classes that will be affected. If empty, all classes will be ignored.
- **Min Area** - Minimal area of connected component to keep. Can be set in `pixels` or `percents`.
- **Source type** - Type of source data. Can be `image` or `bounding box`.

### Example

Drop noise from bitmap annotation with minimal area 5%

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original labels</strong></td>
<td style="text-align:center; width:50%"><strong>Result labels</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/b5258a62-0a47-4631-bbab-c39fb22609e4" alt="Original label"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e98942e3-6d1b-4218-9b13-c746d9bf3f63" alt="Result label"/> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "drop_noise",
  "src": ["$images_project_1"],
  "dst": "$drop_noise_2",
  "settings": {
    "classes": ["shoes"],
    "min_area": "5%",
    "src_type": "image"
  }
}
</pre>
</details>
