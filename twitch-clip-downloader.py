"""
This script's purpose is to download and store Twitch clips using twitch-dl.
"""

import json
import os

# Constant Vars
max_clip_limit = 10
target_clip_dir = "downloaded_clips/"
temporary_info_file_filename = "tmp_download_info.json"

# Working Vars
channel: str

def clean_up():
    
    """
    Remove all temporary files, that may have been created.
    """
    
    print("[ .. ] Starting clean up..")

    if os.path.exists(temporary_info_file_filename):
        os.remove(temporary_info_file_filename)

    print("[ OK ] Clean up finished.")

def download_clips(valid_clips: list):
    
    """
    Download all given clips. Each clip will be stored in {target_clip_dir} once it is sucessfully downloaded.
    The name of each clip consists of three parts:
        1. channel name
        2. clip title
        3. clip id  
    """

    if len(valid_clips) == 0:
        print("[ NOTE ] All clips up to date, not downloading.")
        return

    print(f"[ .. ] Downloading {len(valid_clips)} clips..")

    i = 1
    for clip in valid_clips:
        print(f"{i} / {len(valid_clips)} - {int(i / len(valid_clips) * 100)}%")
        clip_name = f'{channel}_{clip["title"]}_{clip["id"]}.mkv'
        os.system(f"twitch-dl download -o '{clip_name}' -q source {clip["url"]}")
        os.rename(clip_name, target_clip_dir+clip_name)
        i += 1

    print("[ OK ] Download complete.")

def fetch_clip_information():

    """
    Fetch clip information of the given channel and store it as {temporary_info_file_filename}.
    """

    print("[ .. ] Fetching clip information..")

    os.system(f"twitch-dl clips -l {max_clip_limit} --json {channel} > {temporary_info_file_filename}")
    
    print(f"[ OK ] Done.")

def prepare_clips():

    """
    Return a list of clips that needs to be downloaded. A reason why a clip will not be downloaded could be
    that a clip is already downloaded and is recognized as so.
    """

    print("[ .. ] Preparing clips..")

    with open(temporary_info_file_filename) as f:
        clip_information = json.load(f)
    stored_clips = os.listdir(target_clip_dir)
    
    _valid_clips = []
    for clip in clip_information:
        expected_clip_name = f'{channel}_{clip["title"]}_{clip["id"]}.mkv'
        if not (expected_clip_name in stored_clips):
            _valid_clips.append(clip)
    
    print(f"[ OK ] {len(_valid_clips)} can be downloaded.")
    
    return _valid_clips

def twitch_clip_downloader_handler():
    # Get channel name through user input
    print("[ DOWNLOAD ] Please enter the channel name")
    global channel
    channel = input(">> ")

    # Get clip information and store as {temporary_info_file_filename}
    fetch_clip_information()

    # Extract all clips, that need to be downloaded
    valid_clips = prepare_clips()

    # Download clips and store in {target_clip_dir}
    download_clips(valid_clips=valid_clips)

    clean_up()

if __name__ == "__main__":
    twitch_clip_downloader_handler()