# Create New Project

`Create New Project` layer stores results of data transformations to a new project in your workspace. Remember that you should specify a name to your output project.

### Settings

- **Project name** - Input the name of the output project. If the project with the same name already exists, the new project name will be generated automatically by adding a suffix to the specified name.

<details>
  <summary>JSON view</summary>

```json
{
  "action": "supervisely",
  "src": ["$images_project_1"],
  "dst": "result project",
  "settings": {}
}
```

</details>
