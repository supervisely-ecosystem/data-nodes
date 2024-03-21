# Image Tag

`Image Tag` layer adds or removes tags from images.

Tags are used for several things, e.g. to split images by folders in save layers or to filter images by tag.

### Settings

- **Image Tag** — choose tag name that will be added or removed.
- **Action** — select action that will be performed with tag. Can be `add` or `delete`.

### Example

Assign tag `train` to all images in train dataset. You can use `If` node to split images by different conditions and assign different tags.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>`train` tag is assigned</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/c4cad73d-2bde-4d4f-858b-f5c1144ca4ff" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/48856f8d-0874-4385-8f62-7b116bb3ae79" alt="train tag is assigned" /> </td>
</tr>
</table>

### JSON view

<details>
<summary>JSON view</summary>
<pre>
{
  "action": "image_tag",
  "src": ["$images_project_1"],
  "dst": "$image_tag_2",
  "settings": {
    "tag": "train",
    "action": "add"
  }
}
</pre>
</details>
