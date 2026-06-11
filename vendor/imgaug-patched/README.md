# imgaug 0.4.1 (patched)

This vendored build is based on `imgaug 0.4.0` and is used only for
`data-nodes`.

Patch scope:

- disable the deprecated `imgaug.multicore.BatchLoader`
- disable the deprecated `imgaug.multicore.BackgroundAugmenter`

Those code paths relied on unsafe pickle-based inter-process communication and
are not used by this app. The rest of the augmentation API is unchanged.
