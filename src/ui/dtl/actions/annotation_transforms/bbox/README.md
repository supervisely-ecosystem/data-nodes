# Bounding Box

`Bounding Box` layer converts classes with shapes of other types into classes with bounding boxes.

Coordinates of bounding boxes are calculated like this:

```python
min_x = min(x_coords)
max_x = max(x_coords)
min_y = min(y_coords)
max_y = max(y_coords)
```

### Settings:

- **Classes** - Select classes that will be converted to bounding boxes. If no classes are selected, all classes will be ignored.

❗ Selected classes will replace original classes. If you want to keep them, use `Duplicate Objects` layer first.

### Example. Convert annotations to bounding boxes

In this example we will take all objects of class "nearest ballon" and convert them to rectangles.
Objects of other classes ("ballon") will be left unchanged.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image: bitmap and polygon annotations</strong></td>
<td style="text-align:center; width:50%"><strong>Output: bounding boxes</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/249cb518-b46d-46cd-9169-c2aec71ec690" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/3386d230-5b7b-4117-9245-c5134be6d62b" alt="Bounding boxes" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
    "action": "bbox",
    "src": [
        "$data_1"
    ],
    "dst": "$bbox_12",
    "settings": {
        "classes_mapping": {
            "nearest ballon": "nearest ballon"
        }
    }
}
</pre>
</details>
