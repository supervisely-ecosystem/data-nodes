# Objects Filter

`Objects Filter` layer allows filtering objects by class names, area percentage or bounding box size. You can specify area size in percentage of image area or in pixels (width and height of bounding box) and filter objects by `less` or `greater` comparison.

### Settings

- **Filter by** - Select filter type:

  - **Names** - filter by class names:
    - **Classes** - Select classes to filter by names
  - **Area percent** - filter by area percentage:
    - **Classes** - Select classes to filter by area percentage
    - **Input %** - Specify area percentage of image area
    - **Comparator** - Select comparison type: `less` or `greater`. If `less` is selected, objects with area less than specified percentage of image area will be deleted. If `greater` is selected, objects with area greater than specified percentage of image area will be deleted.
  - **Bounding box size** - filter by bounding box size:
    - **Classes** - Select classes to filter by bounding box size
    - **Input size** - Specify bounding box size in pixels:
      - **Width** - Specify width of bounding box
      - **Height** - Specify height of bounding box
    - **Comparator** - Select comparison type: `less` or `greater`. If `less` is selected, objects with bounding box size less than specified size will be deleted. If `greater` is selected, objects with bounding box size greater than specified size will be deleted.

- **Action** - It is only possible to delete objects. If you want to keep objects, you can use `Objects Filter` layer with inverted settings.

Objects can be filtered in 3 ways: by class names, by area percentage and by bounding box size.
Here are examples of how to use each of them.

### Example 1. Filter by class names

In this example we will keep only annotations of classes "truck". All other annotations will be deleted.

`names`: `truck`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>All objects (`truck` + `car` classes)</strong></td>
<td style="text-align:center; width:50%"><strong>Only `truck` class</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e79d52cf-5921-4a78-af44-f242868d9ae2" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/c52d1092-e271-4295-a0ca-873fda2c9788" alt="Filtered objects" /> </td>
</tr>
</table>

### Example 2. Area percent filter

In this example we will delete annotations of classes from filtering_classes that have area greater than 4% of image area.

- area_size: `4%`
- comparator: `greater`
- action: `delete`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>All objects</strong></td>
<td style="text-align:center; width:50%"><strong>Objects with area less than 4%</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/12ad680d-52a7-4599-b0fa-e715fe7ac87b" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/8ba7e003-7fbf-4b21-b295-989f96acb75e" alt="Filtered objects" /> </td>
</tr>
</table>

### Example 3. Bounding box size filter

In this example we will delete annotations of classes from filtering_classes that have bounding box size greater than 140x140 pixels.

- area_size: `140x140 pixels`
- comparator: `greater`
- action: `delete`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>All objects</strong></td>
<td style="text-align:center; width:50%"><strong>Objects (bounding boxes sizes less than 140x140 pixels)</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/3665ff7f-de1f-47f3-8df4-c56f919e4c8d" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/389ac57e-28b9-4719-8a4c-ffd60d1440a2" alt="Filtered objects" /> </td>
</tr>
</table>

### JSON views

<details>
  <summary>Case: names</summary>
<pre>
{
  "action": "objects_filter",
  "src": ["$images_project_1"],
  "dst": "$objects_filter_4",
  "settings": {
    "filter_by": {
      "names": ["truck"]
    }
  }
}
</pre>
</details>

<details>
  <summary>Case: area percent</summary>
<pre>
{
  "action": "objects_filter",
  "src": ["$images_project_1"],
  "dst": "$objects_filter_2",
  "settings": {
    "filter_by": {
      "polygon_sizes": {
        "filtering_classes": ["bus", "car", "taxi", "truck"],
        "action": "delete",
        "comparator": "greater",
        "area_size": {
          "percent": 4
        }
      }
    }
  }
}
</pre>
</details>

<details>
  <summary>Case: bounding box size</summary>
<pre>
{
  "action": "objects_filter",
  "src": ["$images_project_1"],
  "dst": "$objects_filter_2",
  "settings": {
    "filter_by": {
      "polygon_sizes": {
        "filtering_classes": ["bus", "car", "taxi", "truck"],
        "action": "delete",
        "comparator": "greater",
        "area_size": {
          "width": 140,
          "height": 140
        }
      }
    }
  }
}
</pre>
</details>
