# Doodle Deduction

An automation tool designed to create, render, and upload character-based doodle videos to YouTube. `Doodle Deduction` automates the entire workflow, from sourcing images to rendering outline-based frames and scheduling video uploads. Built using Python's robust image processing and automation libraries, this project is ideal for creating engaging, scheduled content for YouTube channels.

## **Features**

- **Automated Image Sourcing**: Downloads transparent background character images from Bing with `bing_image_downloader`.
- **Dynamic Outline Rendering**: Processes images using OpenCV to create outline effects, generating frames for animated doodles.
- **Video Sequence Generation**: Combines frames into videos with background music using MoviePy, saving to local storage.
- **YouTube Upload Automation**: Leverages Selenium to automate YouTube Studio uploads with customized schedules and titles.

## **Requirements**

- **Python** 3.x
- **OpenCV** `cv2`
- **Pillow (PIL)** for image processing
- **Selenium** for web automation
- **MoviePy** for video generation
- **PyGame** for GUI handling
- **Bing Image Downloader** for image sourcing

Install dependencies via `pip`:
    
```bash
pip install opencv-python-headless pillow selenium moviepy pygame bing-image-downloader
```
## **Setup**
1. **Download ChromeDriver**:

    - Install ChromeDriver for Selenium and ensure it matches your Chrome version.
    - Specify the path to ChromeDriver in the script (found in `DoodleDeduction.py`).

2. **Configuration**:

    - Add target characters to Input/characters.txt.
    - Store music files in the Music/ directory for background use.

3. **Execution**:
    - Run `DoodleDeduction.py` to start the automation. Images will be sourced, processed, and uploaded as videos based on queue and scheduling parameters.

## **Usage**
1. **Launching the GUI**:
    - Execute `ImageLoader.py` to open the character selection window.
    - Click on the displayed images to select characters for the next video.

2. **Scheduling Uploads**:
    - `DoodleDeduction.py` queues videos based on scheduling data and automatically uploads them using Selenium.

## **Notes**
- Modify `timeOffset` and `hourOffset` in the script to adjust upload times as needed.
- Ensure YouTube Studio credentials are configured for Selenium to work with Chrome’s user data.
- The following folders need to be added and configured properly:
    - `Frames/`
    - `Images/`
    - `Input/`
    - `Music/`
    - `Output/`
