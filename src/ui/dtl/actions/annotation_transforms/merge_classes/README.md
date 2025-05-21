# Merge Classes

`Merge Classes` layer allows merging multiple source classes into target classes. Source classes will be converted to target classes and removed from the project meta.

- Only classes with the same shape type can be merged, e.g. bitmap -> bitmap, polygon -> polygon, rectangle -> rectangle, etc.
- Doesn't support `AnyShape` geometries

![merge-classes-demo](https://github.com/user-attachments/assets/0d5a7bac-1d64-4eb9-ab61-725f4f69ffda)

All object tags from source classes will be preserved.

<img src="https://github.com/user-attachments/assets/e0104732-a991-4ea8-9a80-e33eb3b1f413" width="300">

### Settings

- **Classes Mapping** — Select the source classes and specify the target classes into which they should be merged.

### Example

In this example we will merge several animal classes into a single class:

<details>
  <summary>JSON view</summary>

```json
{
	"action": "merge_classes",
	"src": ["$data_12"],
	"dst": "$merge_classes_22",
	"settings": {
		"classes_mapping": {
			"cat": "__merge__animal",
			"dog": "__merge__animal",
			"horse": "__merge__animal",
			"sheep": "__merge__animal",
			"squirrel": "__merge__animal"
		}
	}
}
```

</details>
