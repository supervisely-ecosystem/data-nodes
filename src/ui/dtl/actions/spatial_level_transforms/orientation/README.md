# Orientation

`Orientation` rotates an image by 90 degrees only when its current width/height ratio does not match the target orientation.

#### Settings:

- **Target orientation**: desired orientation of the result. Available values: `landscape`, `portrait`.
- **Rotation direction**: side of the 90-degree rotation applied when a change is needed. Available values: `clockwise`, `counter_clockwise`.

Rules:

- Images that already match the target orientation are kept unchanged
- Square images are kept unchanged
- Image annotations are rotated together with the image

### Example

If `target_orientation` is `landscape`, then portrait images will be rotated by 90 degrees.  
If `target_orientation` is `portrait`, then landscape images will be rotated by 90 degrees.

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "orientation",
  "src": ["$images_project_5"],
  "dst": "$orientation_4",
  "settings": {
    "target_orientation": "landscape",
    "rotation_direction": "clockwise"
  }
}
</pre>
</details>
