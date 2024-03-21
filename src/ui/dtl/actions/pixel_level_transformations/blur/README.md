# Blur

`Blur` layer blurs the image by applying a Gaussian or Median filter.

### Settings:

- **Blur type** - Select between Median and Gaussian blur.
- **Kernel size** - Set kernel size for Median blur (must be **odd** and positive number).
- **Sigma** - Set minimal and maximum values for Gaussian blur.

### Example 1. Gaussian blur

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Gaussian blur. Sigma: 11-13</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/c7fb97a7-2fe3-44ce-be7a-34f1df16d213" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/de46a415-6115-4334-add1-07756e52445a" alt="Gaussian sigma: 11-13" /> </td>
</tr>
</table>

### Example 2. Median blur

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Median blur, kernel size: 65</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/4ac0f71e-73c1-4046-8628-b666d6e75a43" alt="Original image" /> </td>
<td> <img src="https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/0d784925-6a11-44cd-b4d5-4210a949627d" alt="Median, kernel size: 65" /> </td>
</tr>
</table>

### JSON views

<details>
  <summary>JSON view for Gaussian blur</summary>
<pre>
{
  "action": "blur",
  "src": ["$images_project1"],
  "dst": "$images_project2",
  "settings": {
    "blur_type": "gaussian",
    "sigma": { "min": 11, "max": 13 }
  }
}
</pre>
</details>

<details>
  <summary>JSON view for Median blur</summary>
<pre>
{
  "action": "blur",
  "src": ["$images_project1"],
  "dst": "$images_project",
  "settings": {
    "blur_type": "Median",
    "kernel_size": 65
  }
}
</pre>
</details>
