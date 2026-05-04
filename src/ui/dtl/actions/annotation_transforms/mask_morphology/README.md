# Mask Morphology

Mask Morphology applies mathematical morphology operations to bitmap masks.

This layer is useful before converting masks to polygons. It smooths or regularizes the raster mask first, so `Mask to Polygon` extracts contours from a less noisy mask instead of simplifying an already corrupted vector contour.

### Settings

- **Classes** - Choose bitmap classes to process. Only objects with `bitmap` geometry are supported. Objects of other classes are kept unchanged.

- **Operation** - Select the morphology operation:
    - `open` - erodes the mask and then dilates it back. Use it to remove small isolated pixels, thin spikes, and tiny protrusions from object borders.
    - `close` - dilates the mask and then erodes it back. Use it to fill small holes, close narrow gaps, connect very close mask parts, and smooth jagged borders before polygon extraction.
    - `erode` - shrinks the mask. Use it when masks are slightly oversized or when you need to remove thin border artifacts. It can delete small objects entirely.
    - `dilate` - expands the mask. Use it when masks are slightly undersized or when nearby components should be connected. It can merge close objects.

- **Kernel shape** - Select the shape of the structuring element:
    - `ellipse` - the best default for smoothing natural object contours. It changes corners less aggressively than a rectangle.
    - `rectangle` - affects horizontal, vertical, and diagonal neighbors inside a square window. It is stronger and can make contours look more blocky.
    - `cross` - affects mostly horizontal and vertical neighbors. It is useful for thin orthogonal structures, but usually weaker for contour smoothing.

- **Kernel size** - Size of the structuring element in pixels. Larger values produce stronger changes. Start with `3` for light cleanup and `5` for more visible smoothing. Values like `7` or higher can noticeably change object shape, remove narrow parts, or merge nearby objects.

- **Iterations** - Number of times to apply the selected operation. Increasing iterations has a similar effect to increasing kernel size. Start with `1`; use `2` only when one pass is not enough.

Recommended starting points:

- Smooth masks before `Mask to Polygon`: `operation = close`, `kernel_shape = ellipse`, `kernel_size = 3` or `5`, `iterations = 1`.
- Remove small noisy fragments or border spikes: `operation = open`, `kernel_shape = ellipse`, `kernel_size = 3`, `iterations = 1`.
- Slightly shrink masks: `operation = erode`, `kernel_shape = ellipse`, `kernel_size = 3`, `iterations = 1`.
- Slightly expand masks: `operation = dilate`, `kernel_shape = ellipse`, `kernel_size = 3`, `iterations = 1`.

> Be careful with large `kernel_size` and `iterations`: morphology changes the raster mask itself, so it can intentionally alter object area and topology before polygons are created.

Typical chains:

- Remove tiny protrusions before polygonization: `Mask Morphology` with `open`, then `Mask to Polygon`.
- Fill small holes and gaps before polygonization: `Mask Morphology` with `close`, then `Mask to Polygon`.
- Convert vector objects to cleaner polygons after rasterization: `Rasterize`, then `Mask Morphology`, then `Mask to Polygon`.

### Examples

#### Close: fill small holes and narrow gaps

Use `close` when a bitmap mask has small holes or thin gaps that should be closed before polygonization.

| Before | After `close` |
| --- | --- |
| ![before](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/02_before_close_holes.png) | ![after](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/03_after_close_ellipse_13.png) |

Settings used:

```json
{
  "operation": "close",
  "kernel_shape": "ellipse",
  "kernel_size": 13,
  "iterations": 1
}
```

#### Open: remove tiny exterior fragments and protrusions

Use `open` when a bitmap mask has small isolated fragments or tiny protrusions outside the main object.

| Before | After `open` |
| --- | --- |
| ![before](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/04_before_open_noise.png) | ![after](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/05_after_open_ellipse_7.png) |

Settings used:

```json
{
  "operation": "open",
  "kernel_shape": "ellipse",
  "kernel_size": 7,
  "iterations": 1
}
```

#### Open then close: clean fragments, then repair holes

For masks that contain both exterior fragments and small holes, use two `Mask Morphology` layers in sequence: first `open`, then `close`.

| Before | After `open` + `close` |
| --- | --- |
| ![before](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/06_before_open_close.png) | ![after](https://github.com/supervisely-ecosystem/data-nodes/releases/download/v0.0.2/07_after_open_close.png) |

### JSON view

<details>
  <summary>JSON view</summary>
<pre>
{
  "action": "mask_morphology",
  "src": ["$rasterize_1"],
  "dst": "$mask_morphology_2",
  "settings": {
    "classes": ["Road"],
    "operation": "close",
    "kernel_shape": "ellipse",
    "kernel_size": 5,
    "iterations": 1
  }
}
</pre>
</details>
