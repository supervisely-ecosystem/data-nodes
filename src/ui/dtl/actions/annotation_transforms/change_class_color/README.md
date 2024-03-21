# Change Class Color

`Change Class Color` layer used for coloring classes as you wish.

### Settings:

- **Classes Colors** - Select classes whose colors you want to change and set new color using color picker. Unselected classes will remain unchanged.

### Example. Change color of classes `horse` and `person`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>New classes colors</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/8e03c98c-4c2c-4e30-8911-f17ada18b658" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/e1e24235-c7eb-40aa-bb03-af3cf859f0d5" alt="New classes colors" /> </td>
</tr>
</table>

### JSON view

Color format present as list of 3 components: [`RED`, `GREEN`, `BLUE`]. Use online color converters to more accurately achieve the desired color.

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "change_class_color",
  "src": ["$images_project_5"],
  "dst": "$change_class_color_11",
  "settings": {
    "classes_color_mapping": {
      "horse": [126, 211, 33],
      "person": [208, 2, 27]
    }
  }
}
</pre>
</details>
