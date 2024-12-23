import praw
import prawcore
import random
import platform
import os
import re

def fetch_thread_info():
    CLIENT_ID = 'TnYW6XrOUFOPglFVpMA0nQ'
    CLIENT_SECRET = 'wdm1I8VI3mR3iiRfEjTCXJruizOZ_w'
    USED_THREADS_FILE = 'used_threads.txt'

    SYSTEM_INFO = platform.system()
    RELEASE_INFO = platform.release()
    PYTHON_VERSION = platform.python_version()
    FILE_NAME = os.path.basename(__file__)

    subreddit_config = {
        "confession": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "confession": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "confessions": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "confessions": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "nosleep": {"thread_range": 150, "tone": "eerie", "time_range": "all", "nsfw": False},
        "tifu": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "tifu": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "AmItheAsshole": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "AmItheAsshole": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "AmItheAsshole": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "amiwrong": {"thread_range": 20, "tone": "normal", "time_range": "all", "nsfw": False},
        "AITAH": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "AITAH": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "relationships": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "relationships": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": False},
        "relationship_advice": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "relationship_advice": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "BreakUps": {"thread_range": 80, "tone": "normal", "time_range": "all", "nsfw": True},
        "BreakUps": {"thread_range": 80, "tone": "normal", "time_range": "all", "nsfw": False},
        "MaliciousCompliance": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "MaliciousCompliance": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": False},
        "pettyrevenge": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "pettyrevenge": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": False},
        "offmychest": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "offmychest": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": False},
        "TrueOffMyChest": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": True},
        "TrueOffMyChest": {"thread_range": 150, "tone": "normal", "time_range": "all", "nsfw": False},
        "TwoHotTakes": {"thread_range": 70, "tone": "normal", "time_range": "all", "nsfw": True},
        "TwoHotTakes": {"thread_range": 70, "tone": "normal", "time_range": "all", "nsfw": True},
        "TalesFromYourServer": {"thread_range": 60, "tone": "normal", "time_range": "all", "nsfw": False},
        "Glitch_in_the_Matrix": {"thread_range": 10, "tone": "eerie", "time_range": "month", "nsfw": False},
        "stories": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": True},
        "stories": {"thread_range": 200, "tone": "normal", "time_range": "all", "nsfw": False},
        "shortscarystories": {"thread_range": 10, "tone": "eerie", "time_range": "all", "nsfw": False},
        "Ghoststories": {"thread_range": 10, "tone": "eerie", "time_range": "month", "nsfw": False}
    }

    
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=f"{FILE_NAME}/1.0 ({SYSTEM_INFO}; {RELEASE_INFO}) Python/{PYTHON_VERSION}",
    )

    all_threads = []

    used_threads = load_existing_threads(USED_THREADS_FILE)

    try:
        for subreddit_name, config in subreddit_config.items():
            subreddit = reddit.subreddit(subreddit_name)
            thread_range = config["thread_range"]
            time_range = config["time_range"]
            nsfw = config["nsfw"]

            threads = list(subreddit.top(time_filter=time_range, limit=thread_range))

            if nsfw:
                nsfw_threads = [thread for thread in threads if thread.over_18]
                threads = nsfw_threads[:thread_range]

            threads = [
                thread for thread in threads
                if not thread.stickied
                and thread.id not in used_threads
                and len(thread.title) >= 30
                and len(thread.title) <= 150
                and is_ascii_text(thread.title)
                and is_ascii_text(thread.selftext)
                and not contains_links(thread.selftext)
                and not contains_links(thread.title)
                and not contains_parts(thread.selftext)
                and not contains_parts(thread.title)
                and len(fixed_length(thread.selftext)) >= 2000
                and len(fixed_length(thread.selftext)) <= 6000
                and "update" not in thread.title.lower()
                and "part" not in thread.title.lower() 
            ]

            all_threads.extend(threads)

        if not all_threads:
            print("No new threads available.")
            return None

        random_thread = random.choice(all_threads)
        subreddit_name = random_thread.subreddit.display_name
        title = random_thread.title
        content = random_thread.selftext
        tone = subreddit_config[subreddit_name]["tone"]

        upvotes = random_thread.score
        if upvotes >= 1000:
            upvotes = str(round(upvotes / 1000, 1)) + "k"
        else:
            upvotes = str(upvotes)

        comments = random_thread.num_comments
        if comments >= 1000:
            comments = str(round(comments / 1000, 1)) + "k"
        else:
            comments = str(comments)

        used_threads.add(random_thread.id)

        save_existing_threads(USED_THREADS_FILE, used_threads)

        print("Subreddit:", subreddit_name)
        print("Title:", title)
        print("Upvotes:", upvotes)
        print("Comments:", comments)
        print()

        return subreddit_name, title, content, upvotes, comments, tone

    except praw.exceptions.PRAWException as e:
        print("Error occurred during Reddit API request:", str(e))

def is_ascii_text(text):
    return all(ord(char) < 128 for char in text)

def contains_parts(text):
    parts_and_updates_pattern = re.compile(r"(?i)\b(?:part|update)\s+\d+\b")
    return bool(re.search(parts_and_updates_pattern, text))

def fixed_length(text):
    edit_pattern = re.compile(r"(?i)\b(?:edit[:;]|eta[:;])\b")
    match = re.search(edit_pattern, text)
    if match:
        return text[:match.start()]
    return text

def load_existing_threads(file_path):
    existing_threads = set()
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_threads = set(file.read().splitlines())
    return existing_threads

def save_existing_threads(file_path, existing_threads):
    with open(file_path, 'w') as file:
        file.write('\n'.join(existing_threads))

def contains_links(text):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return bool(re.search(url_pattern, text))