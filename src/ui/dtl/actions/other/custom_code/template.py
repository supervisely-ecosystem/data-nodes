"""Custom Code node script (ML Pipelines).

process() is called once for every video that reaches the node. Return the frame ranges to keep
as inclusive (start, end) frame indexes:

- every range becomes a clip with its annotations;
- [] drops the video;
- [(0, video_info.frames_count - 1)] passes the video through unchanged.

params is the node's Parameters JSON. This example resizes every frame, applies an OpenCV
function (frame difference) and keeps the ranges where the picture moves.
"""

import cv2


def process(video_path, video_info, ann, params):
    width = params.get("width", 320)
    threshold = params.get("threshold", 5.0)
    min_length = params.get("min_length", 25)
    last_frame = video_info.frames_count - 1

    ranges = []
    start = None
    previous = None
    index = 0
    capture = cv2.VideoCapture(video_path)
    while index <= last_frame:
        ok, frame = capture.read()
        if not ok:
            break
        height = max(1, round(frame.shape[0] * width / frame.shape[1]))
        gray = cv2.cvtColor(cv2.resize(frame, (width, height)), cv2.COLOR_BGR2GRAY)
        moving = previous is not None and cv2.absdiff(gray, previous).mean() > threshold
        previous = gray
        if moving and start is None:
            start = index
        elif not moving and start is not None:
            if index - start >= min_length:
                ranges.append((start, index - 1))
            start = None
        index += 1
    capture.release()

    if start is not None and index - start >= min_length:
        ranges.append((start, index - 1))
    return ranges
