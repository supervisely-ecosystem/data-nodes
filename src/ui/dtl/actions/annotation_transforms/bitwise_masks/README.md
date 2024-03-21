# Bitwise Masks

`Bitwise Masks` layer make bitwise operations between bitmap annotations.
This layer is useful when you need to correct some classes in bitmap annotations.

It is possible to make 3 types of bitwise operations:

- `nor` operation — masks difference (include differs between classes objects masks into corrected class objects masks)
- `and` operation — intersect masks (exclude differs between classes objects masks from corrected class objects masks)
- `or` operation — join masks (include unchanged class objects masks into corrected class objects masks)

### Settings

- **Operation type** — Choose between `and`, `or` and `nor` operations.
- **Class mask** — First element of bitwise operation. Selected class will be used as a mask for bitwise operation. Mask of this class will be unchanged.
- **Classes to correct** — Select classes that you want to correct.

### Example 1 – `nor` operation

In this example we will make `nor` operation between `branch` class and `chameleon` class.
`branch` class will be unchanged, `chameleon` class will be corrected.
As a result `chameleon` class will include only mask pixels only difference between `branch` and `chameleon` classes masks.

- `type`: `nor`
- `class_mask`: `branch`
- `classes_to_correct`: `chameleon`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>type `nor`</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/81277d2e-0ec0-4822-a85a-ded8f896baf9" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/7270245c-d8d1-4c16-b6ac-48e4fd916853" alt="type `nor`" /> </td>
</tr>
</table>

### Example 2 – `and` operation

In this example we will make `and` operation between `branch` class and `chameleon` class.
`branch` class will be unchanged, `chameleon` class will be corrected.
As a result we will get only intersection between `branch` and `chameleon` classes masks.

- `type`: `and`
- `class_mask`: `branch`
- `classes_to_correct`: `chameleon`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>type `and`</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/81277d2e-0ec0-4822-a85a-ded8f896baf9" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/f8806a8e-98c2-4993-ac6b-9bf7da4d1941" alt="type `and`" /> </td>
</tr>
</table>

### Example 3 – `or` operation

In this example we will make `or` operation between `branch` class and `chameleon` class.
`branch` class will be unchanged, `chameleon` class will be corrected.
As a result we will get union between `branch` and `chameleon` classes masks.

- `type`: `or`
- `class_mask`: `branch`
- `classes_to_correct`: `chameleon`

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>type `or`</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/81277d2e-0ec0-4822-a85a-ded8f896baf9" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/b0b8ce6c-134b-4a4b-a7d8-66a44351fa1d" alt="type `or`" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>type `nor`</summary>
<pre>
{
  "action": "bitwise_masks",
  "src": ["$images_project_7"],
  "dst": "$bitwise_masks_6",
  "settings": {
    "type": "nor",
    "class_mask": "branch",
    "classes_to_correct": ["chameleon"]
  }
}
</pre>
</details>

<details>
  <summary>type `and`</summary>
<pre>
{
  "action": "bitwise_masks",
  "src": ["$images_project_7"],
  "dst": "$bitwise_masks_6",
  "settings": {
    "type": "and",
    "class_mask": "branch",
    "classes_to_correct": ["chameleon"]
  }
}
</pre>
</details>

<details>
  <summary>type `or`</summary>
<pre>
{
  "action": "bitwise_masks",
  "src": ["$images_project_7"],
  "dst": "$bitwise_masks_6",
  "settings": {
    "type": "or",
    "class_mask": "branch",
    "classes_to_correct": ["chameleon"]
  }
}
</pre>
</details>
