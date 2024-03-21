# Mask to Lines

`Mask to Lines` layer converts thinned (skeletonized) bitmaps to lines.

It is extremely useful if you have some raster objects representing lines or edges, maybe forming some tree or net structure, and want to work with vector objects.

Each input bitmap should be already thinned (use `Skeletonize` layer to do it), and for single input mask a number of lines will be produced.

Resulting lines may have very many vertices, so consider applying `Approx Vector` layer to results of this layer.
Internally the layer builds a graph of 8-connected pixels, determines minimum spanning tree(s), then extracts diameters from connected components of the tree.

### Settings

- **Classes** — Select classes that will be converted to Lines. Only classes with shape `Bitmap` (Mask) can be selected. If no classes are selected, all classes will be ignored.
- **Min Points Count** — Minimal number of points (vertices) for each output line. Other lines will be dropped.

### Example. Convert mask to lines

In this example we will convert mask to lines. We will use `Mask to Lines` layer to do it.
But first we need to use `Skeletonize` layer to thin our bitmap. After that we will apply `Mask to Lines` layer to get lines. And finally we will apply `Approx Vector` layer to reduce number of vertices and simplify lines.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image (Bitmap)</strong></td>
<td style="text-align:center; width:50%"><strong>Skeletonize + Mask to Lines</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e7ad65e5-96ee-4e8e-8883-4948494e8a2f" alt="Original image (Bitmap)"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/b1baf468-0891-4d10-b4e6-3fff18817a04" alt="Mask to Lines"/> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "mask_to_lines",
  "src": ["$images_project_1"],
  "dst": "$mask_to_lines_7",
  "settings": {
    "classes_mapping": {
      "squirrel": "__default__"
    },
    "min_points_cnt": 2
  }
}
</pre>
</details>
