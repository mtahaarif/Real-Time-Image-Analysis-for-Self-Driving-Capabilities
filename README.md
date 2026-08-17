# Real-Time Image Analysis for Self-Driving Capabilities

A real-time computer vision pipeline built with **OpenCV** and **NumPy** that simulates core perception and decision-making components of a self-driving system: **lane detection**, **obstacle detection**, and **rule-based directional decision-making**. The system processes a video stream frame-by-frame, overlays the detected drivable lane region and obstacles, and simulates a navigation agent moving through the free space it detects.

This project was developed as a **Digital Image Processing (DIP)** course project, 6th Semester, Department of Computer & Software Engineering, College of E&ME, **NUST**, Rawalpindi, Pakistan.

> Sample output: yellow overlay = detected drivable lane region, green boxes = detected obstacles, red square = simulated navigation agent.

---

## Table of Contents

- [Overview](#overview)
- [Authors](#authors)
- [How It Works](#how-it-works)
  - [1. Obstacle Detection](#1-obstacle-detection)
  - [2. Lane Highlighting](#2-lane-highlighting)
  - [3. Directional Decision-Making](#3-directional-decision-making)
  - [4. Real-Time Processing Loop](#4-real-time-processing-loop)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Parameters](#configuration-parameters)
- [Results & Evaluation](#results--evaluation)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [References](#references)
- [License](#license)

---

## Overview

Autonomous navigation requires reliable real-time perception to ensure safe motion. This project implements a lightweight, classical (non-machine-learning) computer vision pipeline that:

1. **Detects the most prominent lane region** in a road scene using edge detection and connected-component analysis.
2. **Detects red-colored obstacles** using HSV color segmentation and contour filtering.
3. **Simulates directional decision-making** for a virtual agent, choosing between **forward, right, left, or backward** movement based on which direction has free (lane-colored) space available.

The entire system runs on a single video file, processing it frame-by-frame and rendering two live windows: an edge map and the final annotated frame (lane + obstacles + agent).

## Authors

- Muhammad Muhtashim
- Muhammad Taha
- Muhammad Sohaib Afzal
- Muhammad Hashir Ashraf Awan

Department of Computer & Software Engineering, College of E&ME, NUST, Rawalpindi, Pakistan
Course: Digital Image Processing
Submitted to: Mam LE Sundas Ashraf, Dr. Asad Khan

Full write-up available in [`Project Report.pdf`](./Project%20Report.pdf).

---

## How It Works

The pipeline is implemented entirely in [`project.py`](./project.py) as four functions.

### 1. Obstacle Detection

`detect_obstacles(frame)`

- Converts the BGR frame to **HSV** color space.
- Thresholds pixels within a fixed HSV range tuned for **red/reddish-orange** objects (`H: 0–15, S: 45–255, V: 50–255`).
- Extracts contours from the resulting binary mask via `cv2.findContours`.
- Filters out noise by discarding contours with area `<= 150` pixels.
- Draws a green bounding box and an `"Object"` label around each valid detection.
- Returns the annotated frame and a list of bounding boxes `(x, y, width, height)`.

### 2. Lane Highlighting

`highlight_largest_lane_region(frame, edge_pixel_thresh=100)`

Identifies the most likely drivable lane/road region using classical edge + region analysis rather than a fixed color mask, making it more robust to varying road surfaces:

1. Convert the frame to grayscale and run **Canny edge detection** (`50, 150` thresholds).
2. Apply **morphological closing** (5×5 kernel) to bridge small gaps between edge segments.
3. Invert the edge map and crop to the **bottom half** of the frame (the road is assumed to occupy the lower portion of the image).
4. Binarize the cropped region and compute **connected components** (`cv2.connectedComponentsWithStats`).
5. Score each candidate component using:
   - a **minimum area threshold** (`min_area = 4000`) to reject small regions,
   - **edge pixel density** within the component (must exceed `edge_pixel_thresh`) to reject overly "flat"/noisy regions,
   - **proximity to the horizontal image center** (closer = higher score),
   - **vertical extent** (taller components — i.e., regions extending further into the distance — score higher).

   ```
   score = area - 5 * distance_from_center + height
   ```
6. The highest-scoring component is selected as the lane region, filled with a **yellow overlay**, and alpha-blended (`0.4`/`0.6`) with the original frame for a semi-transparent highlight.
7. Returns the overlay frame, the raw edge map, and the blended visualization.

### 3. Directional Decision-Making

`directional_decision_making(road, highlighted_frame, object, x1, x2, y1, y2)`

Simulates a small navigation agent (a colored square) that "walks" within the highlighted lane region:

- The agent occupies a bounding box `[x1:x2, y1:y2]` on the frame.
- The function checks, in priority order, whether the adjacent pixels in each direction are lane-colored (`[0, 255, 255]`, i.e., the yellow overlay):
  1. **Forward (up)** — checked first; if the full width of the agent's leading edge is lane-colored, move up.
  2. **Right** — if forward is blocked, check whether the space to the right is free.
  3. **Left** — if right is also blocked, check the left side.
  4. **Backward (down)** — last resort if left is blocked too.
- The agent's coordinates are updated for the first direction found to be free, and it is redrawn on the frame — producing a simple rule-based reactive navigation simulation.

### 4. Real-Time Processing Loop

`process_video_realtime(video_path)`

Ties everything together:

1. Opens the input video with `cv2.VideoCapture`.
2. Initializes a 20×20 red-colored agent sprite and its starting position.
3. For every frame:
   - Resize to `640×480`.
   - Run obstacle detection.
   - Run lane highlighting to get the edge map and lane overlay.
   - Run directional decision-making to update and render the agent.
   - Display two live windows: `"Edge Map"` and `"Lane and Obstacle Detection"`.
4. Loop until the video ends or the user presses `q`.
5. Release the video capture and destroy all display windows.

---

## Project Structure

```
.
├── project.py            # Full pipeline: obstacle detection, lane detection, decision logic, main loop
├── Project Report.pdf     # Full academic write-up (methodology, evaluation, sample output)
└── README.md              # Project documentation (this file)
```

This is a single-script project — there is no package layout, config file, or test suite.

---

## Requirements

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/) (`opencv-python`)
- [NumPy](https://pypi.org/project/numpy/)

## Installation

```bash
git clone https://github.com/<your-username>/Real-Time-Image-Analysis-for-Self-Driving-Capabilities.git
cd Real-Time-Image-Analysis-for-Self-Driving-Capabilities

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install opencv-python numpy
```

## Usage

The video path is currently **hardcoded** at the bottom of [`project.py`](./project.py):

```python
process_video_realtime('E:/Documents/6th Semester/DIP/Lab/Project/DIP Project Videos/q1.mp4')
```

To run the project:

1. Open `project.py` and replace the path in the final line with the path to your own road/driving video (`.mp4`, `.avi`, etc.).
2. Run the script:

   ```bash
   python project.py
   ```
3. Two windows will open:
   - **Edge Map** — the Canny edge output used for lane detection.
   - **Lane and Obstacle Detection** — the annotated frame showing the yellow lane overlay, green obstacle boxes, and the red navigation agent.
4. Press **`q`** at any time to stop playback and close the windows.

> For best results, use footage of a road/pathway that is visually distinct from its surroundings (for lane detection) and contains red or reddish-orange objects (for obstacle detection), since the color thresholds are tuned specifically for red hues.

## Configuration Parameters

These constants can be tuned directly in `project.py` to adapt the pipeline to different footage:

| Parameter | Location | Default | Purpose |
|---|---|---|---|
| `color_range_min` / `color_range_max` | `detect_obstacles` | `[0,45,50]` – `[15,255,255]` | HSV range for obstacle color (currently red) |
| Contour area threshold | `detect_obstacles` | `150` | Minimum obstacle contour area to filter noise |
| Canny thresholds | `highlight_largest_lane_region` | `50, 150` | Edge detection sensitivity |
| Morphological kernel | `highlight_largest_lane_region` | `5×5` | Gap-closing strength for broken edges |
| `min_area` | `highlight_largest_lane_region` | `4000` | Minimum area for a valid lane region candidate |
| `edge_pixel_thresh` | `highlight_largest_lane_region` | `100` | Minimum edge density required within a lane candidate |
| Frame resize | `process_video_realtime` | `640×480` | Processing resolution |
| Agent start position (`x1,x2,y1,y2`) | `process_video_realtime` | `400,420 / 240,260` | Initial bounding box of the simulated navigation agent |

---

## Results & Evaluation

As reported in the accompanying paper:

- **Lane Highlighting** — robust under partial occlusions, thanks to the connected-component scoring approach (area + edge density + centrality + vertical extent) rather than a single naive threshold.
- **Obstacle Detection** — effective at detecting red objects, with area-based filtering suppressing small false positives.
- **Decision-Making** — provides a simple but functional rule-based navigation simulation, prioritizing forward motion and falling back to right → left → backward as space allows.

A pre-recorded demo of the system output is referenced in the original report.

---

## Known Limitations

- **Color-specific obstacle detection**: only red/reddish-orange objects are recognized as obstacles; other-colored obstacles (vehicles, pedestrians, etc.) are not detected. This is a classical thresholding approach, not a general object detector.
- **Heuristic lane detection**: relies on edge density and region geometry rather than true road/lane semantics; it can be fooled by other large, edge-dense regions in a scene (e.g., pavement patterns, sidewalks).
- **Rule-based decisions only**: the directional decision-making logic is reactive and simplistic (checks a single strip of pixels per direction); it does not account for velocity, obstacle trajectories, or path planning.
- **Hardcoded video path**: the entry point at the bottom of `project.py` points to a local file path and must be edited before running.
- **No dynamic obstacle avoidance integration**: obstacle detection and directional decision-making run independently — detected obstacles are drawn on the frame but not currently factored into the movement logic.
- **No automated tests**: this is a demonstration/prototype script, not production-grade or unit-tested software.

## Future Improvements

As suggested in the original report, this system can be extended by:

- Incorporating **multi-color / multi-class object detection** (e.g., via a trained model such as YOLO) instead of fixed HSV thresholds.
- Building a more **robust lane model** (e.g., Hough Transform-based lane line fitting, perspective/bird's-eye transforms, or a learned segmentation model).
- Replacing the rule-based decision module with a **learning-based or planning-based** navigation policy that accounts for obstacle positions, agent velocity, and path history.
- Adding configurability (CLI arguments / config file) instead of hardcoded paths and constants.

---

## References

Full methodology, implementation listing, and evaluation are documented in [`Project Report.pdf`](./Project%20Report.pdf):

> M. Muhtashim, M. Taha, M. S. Afzal, M. H. A. Awan, "Real-time Image Analysis for Self Driving Capabilities," Digital Image Processing Course Project, Department of Computer & Software Engineering, College of E&ME, NUST, Rawalpindi, Pakistan.

## License

No license has been specified for this repository. All rights reserved by the authors unless otherwise stated.
