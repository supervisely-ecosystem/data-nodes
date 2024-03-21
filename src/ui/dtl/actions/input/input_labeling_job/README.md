# Input Labeling Job

The `Input Labeling Job` layer allows you to specify the data and annotations from labeling job that will participate in the transformation process. Only annotations from selected labeling job will be used in the transformation process.

> ✅ Don't worry, original labeling job will remain safe. Any changes you make using all the layers will affect the new resulting project, unless you select to save results with `Add to Existing Project` layer.

### How to use:

1. Add `Input Labeling Job` layer
2. Select labeling job in the sidebar
3. Press `SAVE`

### Settings:

- **Select labeling job** - select labeling job that will be used in data transformation processes

### Example

1. Add `Input Labeling Job` layer and select labeling job, e.g. `My labeling job #2`.
2. After selecting labeling job, you will see the information about it in the sidebar.
3. Press `SAVE` button to confirm selection.
4. All data from labeling job including it's classes, tags, entities and annotations will participate in the transformation process.

### JSON view

<details>
  <summary>Example</summary>
<pre>
{
    "action": "input_labeling_job",
    "src": ["Animals/dogs"],
    "dst": "$input_labeling_job_1",
    "settings": {
        "job_id": 847,
        "job_dataset_id": 80371,
        "entities_ids": [28424688, 28424689, 28424690, 28424691, 2842469,],
        "classes": ["dog"],
        "tags": ["dog"]
    }
}
</pre>
</details>
