# Images Project

The `Images Project` layer is a first and crucial component of the data transformation process you are need to configure.
It allows you to specify the project and datasets that will participate in the transformation process. Additionally, you can select the classes that will be used in the transformation process.

> ✅ Don't worry, all your original projects will remain safe in your workspace. Any changes you make using all the layers will affect the new resulting project, unless you select to save results with `Add to Existing Project` layer.

### How to use:

1. Add `Images Project` layer
2. Select project in the sidebar
3. Select one or more datasets in the sidebar (or all of them by clicking on checkbox near project name)
4. Press `SAVE`
5. Open another sidebar by clicking on `EDIT` button in classes section of the layer
6. Select one or more classes in the sidebar (or all of them by clicking on table header checkbox). You can also see additional information about classes in the sidebar (**number of images** and **number of objects**)
7. Press `SAVE`

### Settings:

- **Select project** - select project that will be used in data transformation processes:
    - `Project` - select project
    - `Select all datasets` - if this option is enabled, all datasets from the selected project will be used
    - `Dataset` - select one or more datasets from the selected project
- **Classes** - select classes that will be used in data transformation processes.

### Example

1. Add `Images Project` layer and select project `My project`. 
2. Select some dataset from this project. For example, `animals` dataset.
3. Select classes that will be used in the transformation process. For example, we will select `raccoon` class.

As a result, we will get all images from the `animals` dataset and all objects with the `raccoon` class.
This data will be used in the next layers of the transformation process.

![images_project-2](https://github.com/supervisely-ecosystem/ml-nodes/assets/79905215/4c6c66db-3197-4c76-add6-c1107cb0ecc5)

### JSON view

<details>
  <summary>Specific datasets and classes</summary>
<pre>
{
  "action": "images_project",
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