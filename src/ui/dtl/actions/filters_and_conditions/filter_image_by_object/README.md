# Filter Images by Object Classes

`Filter Images by Object Classes` layer is used to route images down either the "True" or "False" branch, depending on specific class inclusion and exclusion criteria. Users can define "include" classes, representing objects that should be present in the image for it to be directed to the "True" branch, and "exclude" classes, ensuring that images containing unwanted objects are directed to the "False" branch.

### Settings

- **Include classes** - list classes that SHOULD be present on the image
- **Exclude classes** - list classes that SHOULD NOT be present on the image

### JSON views

<details>
  <summary>JSON view</summary>

```json
{
    "action": "filter_images_by_object",
    "src": [
        "$data_1"
    ],
    "dst": [
        "$filter_images_by_object_2__true",
        "$filter_images_by_object_2__false"
    ],
    "settings": {
        "include": [
            "lemon"
        ],
        "exclude": [
            "kiwi"
        ]
    }
}
```

</details>




