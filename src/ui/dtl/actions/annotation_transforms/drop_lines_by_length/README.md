# Drop Lines by Length

`Drop Lines by Length` layer remove too long or to short lines.

Also this layer can drop lines with length in range.

Lines with more than two points also supported. For multi-lines total length is calculated as sum of sections.

### Settings

- **Classes** - Select classes whose lines you want to drop. Only classes with shape `Line` are available.
- **Resolution Compensation** - used for images with different resolution (scales). If `false` - line length is calculated with pixels. If `true` - in relative units.
- **Invert** - Invert drop results. This mode can be used to remove lines with length in range.
- **Min Length** - Activate to set minimal line length.
- **Max Length** - Activate to set maximal line length.

**Resolution compensation**:

Imagine that we have images with width `1000px` and `2000px`. Also we want to remove lines with length less than `10px`.

Resolution compenstation based on images width and calculated as:
`new_min_length = (image_width / 1000) * min_length`
If resolution_compensation is enabled, actual minimal line length will be `10px` and `20px` respectively.

### Example 1. **Save** lines with length in range [650px, 1500px]

In this example we will remove lines with length **less** than `650px` and **more** than `1500px`:

- `min_length`: `650px`
- `max_length`: `1500px`
- `invert`: `false`
- `resolution_compensation`: `false`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>650px < length < 1500px </strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/7d0a2600-6a2b-43a2-91cb-7efadd378db0" alt="Original image"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/509dc340-218a-4a82-825c-161b203e5eb4" alt="Result image"/> </td>

</tr>
</table>

### Example 2. **Drop** lines with length in range [650px, 1500px] (invert)

In this example we will remove lines with length **more** than `650px` but **less** than `1500px` (enable `invert` option):

- `min_length`: `650px`
- `max_length`: `1500px`
- `invert`: **`true`**
- `resolution_compensation`: `false`

<table>
<tr></tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>650px > length > 1500px (invert)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/7d0a2600-6a2b-43a2-91cb-7efadd378db0" alt="Original image"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/197bdd89-3f9b-4ae3-b6a3-8e794f6b9c19" alt="Result image"/> </td>
</tr>
</table>

### Example 3. Enable resolution compensation

In this example we will remove lines set minimal length to `350px`.
Also we will enable `resolution compensation` option:

- `min_length`: `350px`
- `invert`: `false`
- `resolution_compensation`: **`true`**

Image has width `1920px`. So actual minimal line length will be `350px * 1920 / 1000 = 672px`.
As a result, lines with length less than `672px` will be removed.

It is useful when you have a lot of images with different resolution and you want to preserve some relative length.

<table>
<tr></tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>350px < length and resolution compensation</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/7d0a2600-6a2b-43a2-91cb-7efadd378db0" alt="Original image"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a81ea704-7a75-432b-b799-c746868b9bf8" alt="Result image"/> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>

```json
{
  "action": "drop_lines_by_length",
  "src": ["$images_project_1"],
  "dst": "$drop_lines_by_length_2",
  "settings": {
    "lines_class": "squirrel_line",
    "resolution_compensation": true,
    "invert": true,
    "min_length": 1,
    "max_length": 5
  }
}
```

</details>
