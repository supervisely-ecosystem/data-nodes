# Filter Videos by Tags

`Filter Videos by Tags` layer is used to route videos down either the "True" or "False" branch, depending on specific tag inclusion and exclusion criteria. Users can define tag and filtering condition either "with tag" or "without tag". 

# Settings

- **Tag** - Represents the tag by which the videos will be filtered
  - **Name** - Tag Meta Name
  - **Value** - Tag Value
- **Condition** - Filtering condition: either with or without tag

### JSON views

<details>
  <summary>With Tag with None value type</summary>

```json
{
    "action": "filter_videos_by_tag",
    "src": [
        "$data_1"
    ],
    "dst": [
        "$filter_videos_by_tag_2__true",
        "$filter_videos_by_tag_2__false"
    ],
    "settings": {
        "tag": {
            "name": "animal present",
            "value": null
        },
        "condition": "with"
    }
}
```

</details>

<details>
  <summary>Without Tag with String value type</summary>

```json
{
    "action": "filter_videos_by_tag",
    "src": [
        "$data_1"
    ],
    "dst": [
        "$filter_videos_by_tag_2__true",
        "$filter_videos_by_tag_2__false"
    ],
    "settings": {
        "tag": {
            "name": "object",
            "value": "car",
        },
        "condition": "without"
    }
}
```

</details>
