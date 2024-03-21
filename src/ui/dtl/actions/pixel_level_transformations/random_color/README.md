# Random Color

`Random Color` layer changes image colors by randomly moving each of RGB components.
Pixels (in matrix of width 3) are right multiplied by a random matrix A using the following formula:

```python
A = np.eye(3) + np.random.randn(3, 3) * strength / 5
```

### Settings

- **Strength** — Set the color multiplier strength (min: 0, max: 1). It controls how much image will change its colors.

### Example. Random change of colors

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Random color image</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/2a7ef9e3-1dba-488a-abf1-ded6d0fd1a87" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/9c0c1789-f40f-4816-9894-c16c70d5d6a2" alt="Random color image" /> </td>
</tr>
</table>

### JSON view

<details>
  <summary>JSON view</summary>
  <pre>
{
  "action": "random_color",
  "src": ["$images_project_12"],
  "dst": "$random_color_21",
  "settings": {
    "strength": 0.65
  }
}
</pre>
</details>
