import subprocess
import os

# Specify the full path to ffmpeg executable.
ffmpeg_path = "/venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win64-v4.2.2.exe"

# Specify the relative path for the output file.
output_path = "temp/ttsclips/concatenated_audio.mp3"

def concatenate_audios():
    try:
        # Use relative file paths.
        with open('temp/concatenation_list.txt', 'w') as file:
            file.write(f"file ttsclips/title.mp3\n")
            file.write(f"file saved_audio_needsfix/1sec.mp3\n")
            file.write(f"file ttsclips/content.mp3\n")

        # Run FFmpeg to concatenate the WAV files with delays.
        ffmpeg_command = [
            ffmpeg_path,  # Use the full path to ffmpeg executable.
            "-f", "concat",
            "-i", "temp/concatenation_list.txt",
            "-c", "copy",
            output_path
        ]

        process = subprocess.Popen(ffmpeg_command)
        process.wait()  # Wait for the process to finish.

        # Check the return code of the process.
        if process.returncode != 0:
            print("FFmpeg process failed.")
            return None

        # Remove the temporary text file.
        os.remove("temp/concatenation_list.txt")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None