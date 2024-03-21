# If Action

`if` layer is used to split input data to several flows with a specified criterion. By choosing one of the conditions, you can split data by probability, objects count, image height, tags, class presence, images names in range, and step.
All "true" data will be passed to the first branch (`$if_<id>__true`), all "false" data will be passed to the second branch (`$if_<id>__false`).

### Conditions

- **Condition** for splitting data. Possible following options:
  - **Probability** - input number of probability percentage to split data
  - **Min objects count** - input number of minimum objects count to split data
  - **Min height** - input number of minimum image height to split data
  - **Tags** - select one or more tags to split data
  - **Include classes** - select one or more classes to split data
  - **Name in range** - input names in range to split data:
    - **Name from** - input name from
    - **Name to** - input name to
    - **Step** - input frame step to split data

#### Split data by probability

It can be used in several scenarios. Split data to train and val subsets.
First scenario is when we are going to split data into train and validation sets by adding corresponding tag to each image.

For example, we are going to split data by probability 95%.
In this case input data (image + annotation) will go to the "left" branch (`$if_10__true`) with probability 95% and to the "right" branch (`$if_10__false`) with probability 5%.

#### Split data by objects count

This case allows you to split data by objects count (`min_objects_count` value).

For example, we are going to split data by objects count == 3.
So, images with equal or more than three objects will be passed to `$if_10__true` branch, other images — to the `$if_10__false` branch.

#### Split by image height

This option is useful when we are going to skip some small images after applying `Crop` layer.

For example, we are going to filter images by minimum image height 200 pixels and all images with height more than 200 pixels will be passed to `$if_10__true` branch, other images — to the `$if_10__false` branch.

#### Split by tags

This option is useful when we are going to split data by tags, for example, by existing tags "train" and "val" for train and validation subsets. It can be useful in neural networks training workflow.

#### Split by class presence

This option can be used for splitting data by class presence.

For example, if images contain any object of some required class (`person`) they will be passed to the `$if_10__true` branch, else to the `$if_10__false` branch.

#### Split by images names in range, and step

Option `name_in_range` allows you to split data by images names in range, and step.

**Names is ordered alphabetical (a, b, c ...).**

### JSON views

<details>
  <summary>Use case: split with probability</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "probability": 0.95
    }
  }
}
```

</details>

<details>
  <summary>Use case: split data by objects count</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "min_objects_count": 3
    }
  }
}
```

</details>

<details>
  <summary>Use case: split by image height</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "min_height": 200
    }
  }
}
```

</details>

<details>
  <summary>Use case: split by tags</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "tags": ["party", "dinner"]
    }
  }
}
```

</details>

<details>
  <summary>Use case: split by class presence</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "include_classes": ["person", "dog"]
    }
  }
}
```

</details>

<details>
  <summary>Use case: split by images names in range, and step</summary>

```json
{
  "action": "if",
  "src": ["$images_project_1"],
  "dst": ["$if_10__true", "$if_10__false"],
  "settings": {
    "condition": {
      "name_in_range": ["a0100", "a0105"],
      "frame_step": 2
    }
  }
}
```

Should pass images with names ["00100", "00102", "00104"] into first branch (`$if_10__true`) and else into (`$if_10__false`) branch.

</details>
