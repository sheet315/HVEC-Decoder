# H.265 to H.264 Video Converter

A simple Python tool to convert H.265 (HEVC) video files to H.264 (AVC) with support for **GPU** and **CPU encoding**, progress tracking, and automatic logging.

---

## Features

- **GPU or CPU Encoding**: Choose between faster GPU encoding using your NVIDIA graphics card (CUDA/NVENC) or CPU-based encoding (libx264) for better quality.
- **Progress Tracking**: Get a live percentage of conversion progress.
- **Automatic Logging**: All logs for each conversion are saved to a log file in the `logs/` directory.
- **Resolution Detection**: Automatically detects the video resolution and includes it in the output filename.
- **Codec Detection**: If the input is already H.264, it will skip re-encoding and copy the video file directly.
- **User-Friendly**: Simply drag and drop the video file into the terminal, choose the encoding option, and let the tool do the rest.

---

## Prerequisites

Make sure you have the following installed:

1. **Python 3.x**: This script requires Python to run.
2. **FFmpeg**: You need FFmpeg installed on your machine. It should be available in your system's PATH.
   - You can download it from [FFmpeg official website](https://ffmpeg.org/download.html).

3. **NVIDIA GPU (Optional)**: For hardware acceleration, you need a compatible NVIDIA GPU and the appropriate drivers for CUDA and NVENC.

---

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/h265-to-h264-converter.git
    cd h265-to-h264-converter
    ```

2. **Install Python dependencies**:

    If you don't have `subprocess` and `os` installed, they are part of the standard Python library, so no need for additional installation.

    For GPU encoding, make sure your **NVIDIA drivers** and **CUDA toolkit** are installed.

3. **Make sure FFmpeg is installed**:

    If FFmpeg isn't installed, use the following commands:
    
    - On **Windows**, you can install FFmpeg via `choco install ffmpeg`.
    - On **macOS** or **Linux**, use `brew install ffmpeg` (for macOS) or `sudo apt install ffmpeg` (for Ubuntu).

---

## Usage

1. **Drag and Drop Method**:

    After running the script, you will be prompted to drag and drop your H.265 video file into the terminal window.
    
    - The script will automatically detect the codec and resolution of the video.
    - You will be asked to choose between GPU (fast, using `h264_nvenc`) or CPU encoding (libx264 for better quality).
    
    The conversion progress will be shown, and the output file will be saved in the same directory with a `-processed` suffix.

2. **Output**:

    - Converted video file will be saved in the same directory as the original video.
    - The output filename will include the video resolution, H.264 encoding, and timestamp.
    - Logs will be saved to a `logs/` directory.

---

## Example

To use the script, simply run:

```bash
python convert.py
```