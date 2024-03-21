# Multiply

`Multiply` layer duplicates the image and annotations (multiplying by a given value).

This layer is useful when we are going to balance or unbalance data in training dataset.

### Settings:

- **Multiply number** - Set the value to multiply by. For example, if you set the value to 2, then the image and annotations will be duplicated twice.

## Example. Multiply images

For example, we have project with two datasets:

- "cats dataset" with 200 images of cats
- "dogs dataset" with 600 images of dogs.

We are going to prepare training dataset for cat-dog classifier and we want to have **equal number of images** of cats and dogs.
In this case we will use 2 `Images Project` nodes for each dataset and 1 `Multiply` node for "cats dataset" with value 3. After that we will join two datasets into resulting project using `New project` node.

As a result we will have will have 600 images of cats and 600 images of dogs.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original project</strong></td>
<td style="text-align:center; width:50%"><strong>Project with multiplied images</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/69396043-c99b-4bbe-8ca9-97d3700bc35b" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/a7efbcb0-4574-438a-b563-3977526e2506" alt="Multiply" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "multiply",
  "src": ["$images_project_7"],
  "dst": "$multiply_9",
  "settings": {
    "multiply": 3
  }
}
</pre>
</details>
