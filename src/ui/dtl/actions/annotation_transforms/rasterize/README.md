# Rasterize

`Rasterize` layer converts all geometry figures to bitmaps and rasterizes objects on the image. (i.e. one pixel will belong to only one object)

During labeling objects are treated as layers. **Objects order matters and defines final visualization**.
This layer is useful when you need to prepare datasets for semantic segmentation model training (every pixel on the image have to belong to a single class).

### Settings

- **Classes** — Select classes to rasterize. If no classes are selected, all objects will be preserved.

### Example

Let's see the example below. First labeled object is `road`, second object is `car`. We labeled them separately. Now some image pixels (`car` object area) belong to two objects simultaneously (to `road` and `car`).

**Before**: 

<img src="https://media.giphy.com/media/xOUlIfGk7kXlmcWwKb/giphy.gif" width="600px"/>

In labeling inteface we label objects as layers and now we have the following order: `road` is above `car`.
Note that you should **specify the order of objects with intersections** in labeling tool (it is important for the result).
Select classes to rasterize in settings of `Rasterize` layer.
Next we apply `Rasterize` layer to rasterize objects, it means that **every pixel uder objects will belong to only one object**.  

**After rasterization**:

<img src="https://media.giphy.com/media/TRA1kpZolhegrlGTxM/giphy.gif" width="600px"/>

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "rasterize",
  "src": ["$images_project_7"],
  "dst": "$rasterize_6",
  "settings": {
    "classes_mapping": {
      "car": "car_rasterized",
      "road": "road_rasterized"
    }
  }
}
</pre>
</details>
