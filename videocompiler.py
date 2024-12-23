from moviepy.editor import ImageClip, CompositeVideoClip, VideoFileClip, AudioFileClip
from audioeditor import concatenate_audios
from speechconverter import get_text_array
from imagegenerator import draw_subtitles, draw_title
import moviepy.config as cfg
import re
import soundfile as sf
import numpy as np
import random
import librosa
import os

# Configure imagemagick binary
cfg.change_settings(
    {
        "IMAGEMAGICK_BINARY": "magick/magick.exe"
    }
)

VIDEO_FADE_DURATION = 0.4
TEXT_WIDTH = 600
MINIMUM_FONT_SIZE = 75
MAXIMUM_FONT_SIZE = 110
FONT_COLOR = "white"
OUTLINE_COLOR = "black"
TITLE_ANIMATION_DURATION = 0.25
SUBTITLE_ANIMATION_DURATION = 0.1
ANIMATION_DURATION = 0.2
SUBTITLE_FONT = "fonts/Invisible-ExtraBold.otf"
POPUP_ANIMATION_DURATION = 0.1

# Set video parameters such as duration, width, and height (unchanged)
duration = 0.5
width = 1080
height = 1920

# Set footage background (unchanged)
background_path = "saved_videos/mcparkournormal.mp4"
subtitle_path = "temp/subtitles/"

background = VideoFileClip(background_path, audio=False)
background_duration = background.duration + .05
random_start = random.uniform(0, background_duration - len(os.listdir(subtitle_path)) * duration)
background = background.subclip(random_start, random_start + len(os.listdir(subtitle_path)) * duration)

# Function to create an image clip with vertical movement
def create_image_clip(image_path, duration, width, height, start_time, start_offset=45):
    img_clip = ImageClip(image_path)

    # Define the Positioning Function to Move the Image Up
    def translate(t):
        # Constants
        fixed_period = 0.1  # Time in seconds for the translation to complete

        # Initial and final y positions
        initial_y = (height - img_clip.h) / 2 + start_offset
        final_y = (height - img_clip.h) / 2 + 10

        # Move the image up by start_offset pixels over the fixed period
        if t < fixed_period:
            y = initial_y - (initial_y - final_y) * (t / fixed_period)
        else:
            y = final_y

        x = (width - img_clip.w) / 2
        return (x, y)

    # Apply Positioning Effect to the Image
    img_moving = img_clip.set_position(translate).set_duration(duration).set_start(start_time)

    return img_moving

# Function to overlap audio files
def overlap_audio_files(audio_path1, audio_path2):
    # Load both audio files
    audio1, sr1 = librosa.load(audio_path1, sr=None)
    audio2, sr2 = librosa.load(audio_path2, sr=None)

    # Ensure both audio files have the same sample rate
    if sr1 != sr2:
        raise ValueError("Sample rates of the two audio files must be the same.")

    # Calculate the duration of audio2
    audio2_duration = len(audio2)

    # Tile and trim audio1 to match the duration of audio2
    audio1 = np.tile(audio1, int(np.ceil(audio2_duration / len(audio1))))
    audio1 = audio1[:audio2_duration]

    # Combine the audio files by superimposing them then save to new file
    combined_audio = audio1 + audio2

    output_path = "temp/ttsclips/combined_audio.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, combined_audio, sr1)

    return output_path

def ease_out(t):
    return 1 - (1 - t) ** 2

# Compile video function
def compile_video(title_content, upvotes, comments, tone, subreddit, video_num):
    # Create concatenated TTS clip .mp3 file
    concatenate_audios()

    concatenated_audio_path = "temp/ttsclips/concatenated_audio.mp3"
    title_audio_path = "temp/ttsclips/title.mp3"

    title_audio = AudioFileClip(title_audio_path)
    concatenated_audio = AudioFileClip(concatenated_audio_path)

    # Calculate for video duration
    title_duration = title_audio.duration + 1
    duration = concatenated_audio.duration

    # Release the title audio
    title_audio.close()

    # Set background depending on the selected tone
    if tone == "eerie":
        background_path = "saved_videos/mcparkoureerie.mp4"
    else:
        background_path = "saved_videos/mcparkournormal.mp4"

    background = VideoFileClip(background_path, audio=False)
    background_duration = background.duration + 2
    random_start = random.uniform(0, background_duration - duration)
    background = background.subclip(random_start, random_start + background_duration) 

    # Generate the background image with rounded corners
    background_image_path = draw_title(title_content, upvotes, comments, subreddit)

    # Load the background image with rounded corners
    background_image = ImageClip(background_image_path)

    # Set the start of the animated title clip
    animated_background_clip = background_image.set_start(0)

    # Set the initial and final position of the title textbox for animation
    initial_position = (131, 1800)
    final_position = (131, 765)

    # Animate the title clip to slide up over the course of the animation duration
    animated_background_clip = animated_background_clip.set_position(
        lambda t: (
            initial_position[0],
            initial_position[1]
            - (initial_position[1] - final_position[1])
            * ease_out(t / TITLE_ANIMATION_DURATION),
        )
    )

    # Set the duration of the animated title clip
    animated_background_clip = animated_background_clip.set_duration(TITLE_ANIMATION_DURATION)

    # Assign start times to title image
    stationary_background_clip = background_image.set_start(TITLE_ANIMATION_DURATION)

    # Assign positions to stationary title image
    stationary_background_clip = stationary_background_clip.set_position(final_position)

    # Assign durations to stationary title image
    stationary_background_clip = stationary_background_clip.set_duration(title_duration - TITLE_ANIMATION_DURATION)

    # Select background music based on the tone
    if tone == "normal":
        music_options = [
            "Anguish", "Garden", "Limerence", "Lost", "NoWayOut", "Summer",
            "Never", "Miss", "Touch", "Stellar"
        ]
        background_music_choice = random.choice(music_options)
        background_music_path = f"music/chillmusic/{background_music_choice}.mp3"
    else:
        music_options = [
            "Creepy", "Scary", "Spooky", "Space", "Suspense"
        ]
        background_music_choice = random.choice(music_options)
        background_music_path = f"music/eeriemusic/{background_music_choice}.mp3"

    # Create final audio by overlapping background music and concatenated audio
    final_audio = AudioFileClip(overlap_audio_files(background_music_path, concatenated_audio_path))

    # Release the concatenated audio
    concatenated_audio.close()

    # Retrieve subtitle information (if needed)
    subtitle_textclips = get_text_array()
    
    # Draw subtitles
    draw_subtitles(subtitle_textclips)

    # Create image file paths # WRONG ORDER HERE
    image_files = [subtitle_path + f for f in sorted([f for f in os.listdir(subtitle_path) if f.endswith('.png')], key=lambda x: int(re.search(r'\d+', x).group()))]

    subtitle_images = []

    # Find correct duration for and create each imageclip
    for i in range(len(subtitle_textclips)):
        start_time = subtitle_textclips[i][1] - .02
        end_time = subtitle_textclips[i + 1][1] - .02 if i + 1 < len(subtitle_textclips) else background_duration - .05
        subtitle_duration = end_time - start_time
        
        # Create a list of subtitle image clips
        clip = create_image_clip(image_files[i], subtitle_duration, width, height, start_time + title_duration)
        subtitle_images.append(clip)

    # Overlay image clips and subtitles on the continuous background
    final_clip = CompositeVideoClip([background, animated_background_clip, stationary_background_clip] + subtitle_images)

    # Set the final video dimensions and write video file
    final_clip = final_clip.set_duration(duration)
    final_clip = final_clip.set_audio(final_audio)

    final_clip.write_videofile(
        f"temp/videos/{video_num}.mp4",
        codec="libx264",
        fps=30,
        bitrate="7000k",
        audio_codec="aac",
        audio_bitrate="164k",
        preset="slow",
        threads=5
    )

    # Release unneeded memory
    final_clip.close()
    background.close()
    final_audio.close()
