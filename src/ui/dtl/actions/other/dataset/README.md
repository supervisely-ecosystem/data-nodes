# Dataset

`Dataset` layer places every image that it sees to the dataset with a specified name.

### Settings

- **Keep original datasets** — Keep original datasets names. In this case, input field `name` will be hidden.
- **Name** — Set the name of the resulting dataset. This setting is available only if `Keep original datasets` is disabled.

### Example 1. Keep original datasets

For example, we have a project with two datasets: `cats` and `dogs`.
We will use `Dataset` layer and set `Keep original datasets` rule. As a result, all images will be placed to the same dataset names as they were before (in new project).

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original datasets</strong></td>
<td style="text-align:center; width:50%"><strong>Result: keep original datsets structure</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/63a72eec-6851-4e5d-9067-37a0b0e387b5" alt="Original datasets"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/5bc9dee2-3ae7-4f41-8945-927c039c611e" alt="Result datasets"/> </td>
</tr>
</table>

### Example 2. Set new dataset name

In this example we will use `Dataset` layer and set new dataset name "cats and dogs dataset". As a result, all images will be placed to the dataset with name "cats and dogs dataset" (in new project).


<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original datasets</strong></td>
<td style="text-align:center; width:50%"><strong>Result: set new dataset name</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/63a72eec-6851-4e5d-9067-37a0b0e387b5" alt="Original datasets"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/91af2e74-d5e9-4b4e-b3c4-3248f99ffb12" alt="Result datasets"/> </td>
</tr>
</table>


### JSON views

<details>
  <summary>save original dataset name</summary>
<pre>
{
  "action": "dataset",
  "src": ["$if_9__true"],
  "dst": "$dataset_10",
  "settings": {
    "rule": "save_original"
  }
}
</pre>
</details>

<details>
  <summary>set new dataset name</summary>
<pre>
{
  "action": "dataset",
  "src": ["$if_9__true"],
  "dst": "$dataset_10",
  "settings": {
    "name": "cats and dogs dataset"
  }
}
</pre>
</details>
