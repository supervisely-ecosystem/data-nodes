# Drop Object by Class

`Drop Object by Class` layer simply removes annotations of specified classes.

> ℹ️ You can also use `Images Project` layer and select classes that you want to keep. All other classes will be removed.

### Settings

- **Сlasses** — Select classes that you want to remove. All objects of selected classes will be removed.

### Example. Remove objects of selected classes

Remove objects of classes `bishop`, `king`, `knight`, `queen` and `rook` and keep all other objects (with class `pawn`).

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Remove objects of selected classes</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/00a385f1-0637-4da2-8767-7b470e790206" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/b53de5d1-9e1b-4a42-b32e-d8cac5570a5e" alt="Drop by Class" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "drop_obj_by_class",
  "src": ["$images_project_5"],
  "dst": "$drop_obj_by_class_12",
  "settings": {
    "classes": ["bishop", "king", "knight", "queen", "rook"]
  }
}
</pre>
</details>
