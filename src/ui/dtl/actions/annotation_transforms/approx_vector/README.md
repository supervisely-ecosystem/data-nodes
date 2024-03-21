# Approx Vector

`Approx Vector` layer approximates vector figure – reduce the number of vertices in vector figures and simplify them.
Supported shapes: `polyline` and `polygon`.
The operation decreases number of vertices with Douglas-Peucker algorithm.

### Settings:

- **Сlasses** - Choose classes to apply transformation. Only classes with shape `line` or `polygon` are allowed.
- **Epsilon** - Determines how close or far points of interest should be considered for approximating vectors. The smaller the epsilon, the more detailed the result will be. The larger the epsilon, the more general the result will be.

### Example. Approximate vector figures

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Epsilon: 10</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a1389f2c-8bbc-4182-a7e0-b39c676be777" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/6e6ded99-f9ac-4980-bb8e-bab08a025378" alt="Epsilon: 10" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "approx_vector",
  "src": ["$images_project_5"],
  "dst": "$approx_vector_6",
  "settings": {
    "classes": ["ballon"],
    "epsilon": 10
  }
}
</pre>
</details>
