import subprocess
import os
import re
from datetime import datetime

def get_video_resolution(input_path):
    ffprobe_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffprobe')
    cmd_resolution = [
        ffprobe_path, '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0:s=x',
        input_path
    ]

    try:
        res_out = subprocess.run(cmd_resolution, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
        return res_out
    except Exception as e:
        print(f"❌ Error getting resolution: {e}")
        return "unknown"

def get_video_codec(input_path):
    ffprobe_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffprobe')
    cmd_codec = [
        ffprobe_path, '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]
    try:
        codec = subprocess.run(cmd_codec, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
        return codec
    except:
        return None

def convert_h265_to_h264(input_path):
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg')

    input_path = input_path.strip('"')
    input_path = os.path.abspath(input_path)

    if not os.path.isfile(input_path):
        print(f"❌ Error: File '{input_path}' does not exist.")
        return

    input_dir = os.path.dirname(input_path)
    filename, ext = os.path.splitext(os.path.basename(input_path))

    resolution = get_video_resolution(input_path)
    codec = get_video_codec(input_path)

    if codec == "h264":
        print("✅ File is already H.264. Copying without re-encoding...")
        output_path = os.path.join(input_dir, f"{filename}-copy{ext}")
        command = [
            ffmpeg_path, '-y', '-i', input_path,
            '-c', 'copy',
            output_path
        ]
        subprocess.run(command)
        print(f"✅ Copied to: {output_path}")
        return

    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"{filename}-{resolution}-h264-{now}{ext}"
    output_path = os.path.join(input_dir, output_filename)

    print("\nChoose encoder:")
    print("[1] GPU (fast, good quality)")
    print("[2] CPU (slower, best quality)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '2':
        encoder_settings = [
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '20'
        ]
        encoder_type = "CPU (libx264)"
    else:
        encoder_settings = [
            '-c:v', 'h264_nvenc',
            '-profile:v', 'high',
            '-pix_fmt', 'yuv420p',
            '-rc', 'vbr',
            '-cq', '19',
            '-b:v', '0',
            '-preset', 'p5'
        ]
        encoder_type = "GPU (h264_nvenc)"

    command = [
        ffmpeg_path, '-y', '-i', input_path,
        *encoder_settings,
        '-c:a', 'copy',
        '-progress', 'pipe:1',
        '-nostats',
        output_path
    ]

    print(f"\n🎬 Converting with {encoder_type}...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}\n")

    log_dir = os.path.join(input_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{filename}-logs.log")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    with open(log_path, "w", encoding="utf-8") as log_file:
        for line in process.stdout:
            log_file.write(line)
            line = line.strip()
            if line.startswith("frame="):
                print(f"🧩 {line}", end='\r')
            elif line.startswith("fps="):
                print(f"⏩ {line}", end='\r')

    process.wait()
    print(f"\n✅ Conversion complete! File saved to:\n{output_path}")
    print(f"📝 Log saved to: {log_path}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    print("Please drag and drop your H.265 video file into the terminal window, and press Enter.")
    user_input = input("📂 Enter the absolute path to your H.265 video file: ").strip()
    convert_h265_to_h264(user_input)
