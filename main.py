from textdoctorer import unabbreviate, remove_keywords, fixperiods
from threadfetcher import fetch_thread_info
from speechconverter import synthesize_speech
from videocompiler import compile_video
import os

# Define the number of videos to create.
NUM_VIDEOS = 1

# Declare list of thread titles.
thread_titles = []

# Indicate directories to be cleaned of temporary files.
directories = ['temp/ttsclips/', 'temp/images/', 'temp/subtitles/']

# Create videos to be scheduled
for i in range(NUM_VIDEOS):

    # Repeat until both synthesize_speech and compile_video succeed.
    while True:
        # Gather a thread title and content to be used.
        subreddit, title, thread_content, upvotes, comments, tone = fetch_thread_info()
        thread_titles.append(title)  # Append the title to the list of threads to be turned to videos.

        # Expand abbreviatons from known abbreviation list.
        thread_titles[i] = unabbreviate(thread_titles[i])
        unnabbreviated_content = unabbreviate(thread_content)

        # Fix grammatically incorrect periods.
        thread_titles[i] = fixperiods(thread_titles[i])
        unnabbreviated_content = fixperiods(unnabbreviated_content)

        # End content at tldr or update.
        unnabbreviated_content, content_length = remove_keywords(unnabbreviated_content)

        # Convert segments into TTS.
        synth_result = synthesize_speech(unnabbreviated_content, thread_titles[i])
        if synth_result == -1:
            print(f"Synthesize speech failed for video {i}, retrying...")
            continue  # Retry the same iteration.

        # Compile video into edited mp4 form.
        compile_result = compile_video(thread_titles[i], upvotes, comments, tone, subreddit, i)
        if compile_result == -1:
            print(f"Compile video failed for video {i}, retrying...")
            continue  # Retry the same iteration.

        # If both functions succeed, break the loop and proceed to the next video.
        break

    # Iterating through the provided directories, purge all no longer needed files.
    for directory in directories:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
