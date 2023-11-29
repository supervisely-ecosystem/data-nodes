# Videos Project

The `Video Project` layer allows you to specify the project and datasets that will participate in the transformation process. Additionally, you can select the classes that will be used in the transformation process.

> ✅ Don't worry, all your original projects will remain safe in your workspace. Any changes you make using all the layers will affect the new resulting project.

### How to use:

1. Add `Video Project` layer
2. Select project in the sidebar
3. Select one or more datasets in the sidebar (or all of them by clicking on checkbox near project name)
4. Press `SAVE`
5. Open another sidebar by clicking on `EDIT` button in classes section of the layer
6. Select one or more classes in the sidebar (or all of them by clicking on table header checkbox). You can also see additional information about classes in the sidebar (**number of videos** and **number of objects**)
7. Press `SAVE`

### Settings:

- **Select project** - select a project that will be used in data transformation processes:
    - `Project` - select a project
    - `Select all datasets` - if this option is enabled, all datasets from the selected project will be used
    - `Dataset` - select one or more datasets from the selected project
- **Classes** - select classes that will be used in data transformation processes.

### Example

1. Add `Videos Project` layer and select project `My project`. 
2. Select some dataset from this project. For example, `animals` dataset.
3. Select classes that will be used in the transformation process. For example, we will select `raccoon` class.

As a result, we will get all videos from the `animals` dataset and all objects with the `raccoon` class.
This data will be used in the next layers of the transformation process.

### JSON view

<details>
  <summary>Specific datasets and classes</summary>
<pre>
{
  "action": "data",
  "src": ["My project/animals"],
  "dst": "$data_15",
  "settings": {
    "classes_mapping": {
      "blueberries": "__ignore__",
      "raccoon": "raccoon",
      "dog": "__ignore__",
      "plants": "__ignore__",
      "tree": "__ignore__"
    }
  }
}
</pre>
</details>