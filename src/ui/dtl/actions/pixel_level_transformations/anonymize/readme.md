# Anonymize

Layer for obscuring unwanted objects on image. You can specify object classes and anonymization method from "blur", "pick color" and "same color as class". All objects of selected classes will be anonymized with selected method.

### Settings:

- **Classes** - Choose classes to apply transformation.
- **Anonymization method** - Select anonymization method:
    - **Blur** - Blur the image area under objects of selected classes.
    - **Pick color** - Draw objects on the image using selected color.
    - **Same as class color** - Draw objects on the image using their class color.

### Examples

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Original image</strong></td>
<td style="text-align:center; width:50%"><strong>Anonymized image: blur method</strong></td>
</tr>
<tr>
<td> <img src="https://github-production-user-asset-6210df.s3.amazonaws.com/61844772/282115231-461abda7-f51a-4dd1-b056-74206e48a1d0.jpg" alt="Original image" /> </td>
<td> <img src="https://github-production-user-asset-6210df.s3.amazonaws.com/61844772/282114939-a9cb4f81-da51-422b-9375-87e76ed99e30.jpg" alt="Anonymization type: Blur" /> </td>
</tr>
<tr>
<td style="text-align:center; width:50%"><strong>Anonymized image: pick color</strong></td>
<td style="text-align:center; width:50%"><strong>Anonymized image: same as class color</strong></td>
</tr>
<tr>
<td> <img src="https://github-production-user-asset-6210df.s3.amazonaws.com/61844772/282133633-08d7be52-17df-4587-ba44-d1fd6712f465.jpg" alt="Anonymization type: Pick color [0, 0, 0]" /> </td>
<td> <img src="https://github-production-user-asset-6210df.s3.amazonaws.com/61844772/282134496-e63a8351-aa19-44f9-8fd9-5076ded5e0dc.jpg" alt="Anonymization type: Same as class color" /> </td>
</tr>
</table>


<details>
  <summary>JSON config `Blur` Anonymization method</summary>
<pre>
{
  "action": "anonymize",
  "src": [
    "$data_1"
  ],
  "dst": "$anonymize_2",
  "settings": {
    "classes": [
      "Face"
    ],
    "type": "blur"
  }
}
</pre>
</details>

<details>
  <summary>JSON config `Pick color` Anonymization method</summary>
<pre>
{
  "action": "anonymize",
  "src": [
    "$data_1"
  ],
  "dst": "$anonymize_2",
  "settings": {
    "classes": [
      "Face"
    ],
    "type": "color",
    "color": [
        0,
        0,
        0
    ]
  }
}
</pre>
</details>

<details>
  <summary>JSON config `Same as class color` Anonymization method</summary>
<pre>
{
  "action": "anonymize",
  "src": [
    "$data_1"
  ],
  "dst": "$anonymize_2",
  "settings": {
    "classes": [
      "Face"
    ],
    "type": "class_color",
  }
}
</pre>
</details>
