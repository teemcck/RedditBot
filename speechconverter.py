from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import json
import os
import sys
import time
import librosa

# Create a client using the credentials and region defined in the [adminuser].
session = Session(profile_name="default")
polly = session.client("polly")

def get_text_array():
    # Open an empty texxt file.
    with open('temp/ttsclips/content_speechmarks.txt', 'r') as file:
        # Initialize an empty list to store data.
        data = []

        # Read each line in the file.
        for line in file:
            # Parse the JSON object from the line.
            obj = json.loads(line)
            
            # Extract the necessary fields.
            word = obj['value']
            start_time = obj['time'] / 1000 # Convert milliseconds to seconds.
            
            # Append the extracted data to the list.
            data.append([word, start_time])

    # Initialize a new list to store the combined data.
    combined_data = []

    # Initialize index for iteration.
    i = 0
    while i < len(data):
        # Get the current word and start time.
        word, start_time = data[i]

        # Calculate the duration of the current word.
        if i + 1 < len(data):
            next_word, next_start_time = data[i + 1]
            duration = next_start_time - start_time
            
            # If the duration is less than 0.2 seconds, combine the words.
            while duration < 0.15 and i + 1 < len(data):
                word += " " + next_word
                i += 1
                if i + 1 < len(data):
                    next_word, next_start_time = data[i + 1]
                    duration = next_start_time - start_time

        # Append the word and start time to the combined list.
        combined_data.append([word, start_time])
        i += 1

    return combined_data

def get_audio_duration(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0

def synthesize_speech(content, title):
    try:
        # Request title speech synthesis.
        title_response = polly.synthesize_speech(
            TextType="ssml",
            Text=f"<speak><prosody rate='{1.2}'>{title}</prosody></speak>",
            OutputFormat="mp3",
            VoiceId="Matthew"
        )
        # Access the audio stream from the response.
        if "AudioStream" in title_response:
            output_path_title = os.path.join(os.getcwd(), "temp/ttsclips/title.mp3")

            try:
                # Open a file for writing the output as a binary stream.
                with open(output_path_title, "wb") as file:
                    file.write(title_response["AudioStream"].read())
                print(f"Title speech saved to {output_path_title}")
            except IOError as error:
                # Could not write to file, exit gracefully.
                print(error)
                sys.exit(-1)
        else:
            # The response didn't contain audio data, exit gracefully.
            print("Could not stream audio for title")
            sys.exit(-1)

    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully.
        print("Error during mp3 title synthesis API call:", error)
        sys.exit(-1)

    try:
        # Request content speech synthesis
        mp3_content_response = polly.start_speech_synthesis_task(
            TextType="ssml",
            Text=f"<speak><prosody rate='{1.2}'>{content}</prosody></speak>",
            OutputFormat="mp3",  # Save content as an mp3.
            OutputS3BucketName="redditcumbucket",
            VoiceId="Matthew"
        )
        task_id = mp3_content_response['SynthesisTask']['TaskId']
        print(f"Content synthesis task ID: {task_id}")

        # Wait for the synthesis task to finish.
        wait_for_synthesis_task(task_id)

        output_path_content_mp3 = os.path.join(os.getcwd(), "temp/ttsclips/content.mp3")
        output_uri = mp3_content_response['SynthesisTask']['OutputUri']

        # Download the MP3 file.
        download_file_from_s3(output_uri, output_path_content_mp3)
        print(f"Content speech saved to {output_path_content_mp3}")

        # Delete the file from the S3 bucket.
        delete_file_from_s3(output_uri)

    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully.
        print("Error during mp3 content synthesis API call:", error)
        return(-1)
    
    try:
        # Request content speech synthesis.
        json_content_response = polly.start_speech_synthesis_task(
            TextType="ssml",
            Text=f"<speak><prosody rate='{1.2}'>{content}</prosody></speak>",
            OutputFormat="json",  # Save content as a timestamp json.
            OutputS3BucketName="redditcumbucket",
            VoiceId="Matthew",
            SpeechMarkTypes=["word"]  # Request word-level timestamps.
        )
        task_id = json_content_response['SynthesisTask']['TaskId']
        print(f"Content synthesis task ID: {task_id}")

        # Wait for the synthesis task to finish.
        wait_for_synthesis_task(task_id)

        output_path_content_json = os.path.join(os.getcwd(), "temp/ttsclips/content_speechmarks.txt")
        output_uri = json_content_response['SynthesisTask']['OutputUri']

        # Download the JSON file.
        download_file_from_s3(output_uri, output_path_content_json)
        print(f"Content speech saved to {output_path_content_json}")

        # Delete the file from the S3 bucket.
        delete_file_from_s3(output_uri)

    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully.
        print("Error during JSON content synthesis API call:", error)
        sys.exit(-1)

def wait_for_synthesis_task(task_id):
    while True:
        try:
            response = polly.get_speech_synthesis_task(TaskId=task_id)
            task_status = response['SynthesisTask']['TaskStatus']
            print(f"Task status: {task_status}")

            if task_status == 'completed':
                break
            elif task_status == 'failed':
                print("Task failed")
                # Print additional details about the failure.
                print("Failure details:", response['SynthesisTask'])
                break

            time.sleep(5)  # Wait for 5 seconds before checking the status again.

        except (BotoCoreError, ClientError) as error:
            print("Error checking task status:", error)
            break

def download_file_from_s3(s3_uri, local_path):
    # Extract bucket and key from S3 URI.
    s3_uri_parts = s3_uri.split('/', 4)
    key = s3_uri_parts[4]

    # Download the file from S3.
    s3 = session.client('s3')
    s3.download_file("redditcumbucket", key, local_path)

def convert_to_json_and_delete(txt_path, json_path):
    # Read the lines from the text document.
    with open(txt_path, 'r') as txt_file:
        lines = txt_file.readlines()

    # Convert each line to a separate JSON object.
    data = [json.loads(line.strip()) for line in lines]

    # Save the list of dictionaries to a JSON file.
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    # Delete the original text document.
    os.remove(txt_path)

def delete_file_from_s3(s3_uri):
    # Extract bucket and key from S3 URI.
    s3_uri_parts = s3_uri.split('/', 4)
    key = s3_uri_parts[4]

    # Delete the file from S3.
    s3 = session.client('s3')
    try:
        s3.delete_object(Bucket="redditcumbucket", Key=key)
        print(f"File deleted from S3: {key}")
    except (BotoCoreError, ClientError) as error:
        print("Error deleting file from S3:", error)