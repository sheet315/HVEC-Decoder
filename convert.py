import subprocess
import os
import re
from fractions import Fraction
from datetime import datetime

def get_video_info(input_path):
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg')
    cmd_fps = [
        ffmpeg_path, '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]

    cmd_duration = [
        ffmpeg_path, '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]

    cmd_resolution = [
        ffmpeg_path, '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0:s=x',
        input_path
    ]

    try:
        fps_out = subprocess.run(cmd_fps, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
        duration_out = subprocess.run(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
        res_out = subprocess.run(cmd_resolution, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

        fps = float(Fraction(fps_out))
        duration = float(duration_out)
        resolution = res_out
        return duration * fps, resolution
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def get_video_codec(input_path):
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg')
    cmd_codec = [
        ffmpeg_path, '-v', 'error',
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

    total_frames, resolution = get_video_info(input_path)
    if total_frames is None:
        return

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
        '-nostats', '-loglevel', 'error',
        output_path
    ]

    print(f"\n🎬 Converting with {encoder_type}...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}\n")

    log_dir = os.path.join(input_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{filename}-logs.log")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    frames_processed = 0

    with open(log_path, "w", encoding="utf-8") as log_file:
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            log_file.write(line)
            if line.startswith('frame='):
                match = re.search(r'frame=(\d+)', line)
                if match:
                    frames_processed = int(match.group(1))
                    percentage = (frames_processed / total_frames) * 100
                    print(f"Progress: {percentage:.2f}% completed", end='\r')

    process.wait()
    print(f"\n✅ Conversion complete! File saved to:\n{output_path}")
    print(f"📝 Log saved to: {log_path}")

    # Add pause so the window doesn't close instantly
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    print("Please drag and drop your H.265 video file into the terminal window, and press Enter.")
    user_input = input("📂 Enter the absolute path to your H.265 video file: ").strip()
    convert_h265_to_h264(user_input)
