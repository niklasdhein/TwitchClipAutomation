# Custom modules
import cropper
import face_tracker as tracker
import subtitle_creator as subtitles
import twitch_clip_downloader as downloader

# other
from moviepy import VideoFileClip, CompositeVideoClip
import pandas as pd
import os

download_dir = "downloaded_clips/"
face_tracking_data_dir = "face_tracking_data/"
export_dir = "exported_clips/"

def get_and_process_data():

    # Download clips
    downloader.twitch_clip_downloader_handler()

    # Process downloaded clips and extract face tracking data
    tracker.face_tracker_handler()

def get_non_duplicate_files_in_dir(files: list, dir: str):

    valid_files = []
    for file in files:
        target_file_name = file[:len(file)-4]+".mp4"
        if not os.path.exists(dir+target_file_name):
            valid_files.append(file)
    
    print(f"[ NOTE ] {len(valid_files)} files ready to export. {len(files)-len(valid_files)} out of {len(files)} are duplicates.")
    return valid_files

if __name__ == "__main__":

    print("[ .. ] Initializing pipeline..")

    # Pre pipeline data gathering and processing
    get_and_process_data()

    
    # --- Actual pipeline procedure starts here ---

    # Check if export directory exists
    if not os.path.exists(export_dir):
        os.mkdir(export_dir)
        print(f"[ NOTE ] Created directory {export_dir}.")

    non_duplicate_clips = get_non_duplicate_files_in_dir(os.listdir(download_dir), export_dir)

    # Load only non broken tracking data files
    valid_face_tracking_data = []
    for data in os.listdir(face_tracking_data_dir):
        if not "BROKEN" in data:
            valid_face_tracking_data.append(data)
    
    # Handle all ready to crop and export clips
    for clip in non_duplicate_clips:

        # Skip non duplicate but broken clips 
        if not (clip[:len(clip)-4] in data for data in valid_face_tracking_data):
            continue

        # Import as VideoFileClip and DataFrame
        video_file_clip = VideoFileClip(download_dir+clip)
        dataframe = pd.read_xml(face_tracking_data_dir+clip[:len(clip)-4]+".xml")


        # Get cropped VideoFileClips 
        cropped_clips = cropper.cropper_handler(video_file_clip, dataframe)

        # Get SubtitleClips
        subtitle_clips = subtitles.subtitle_creator_handler(download_dir+clip)

        # Add all clips together in one list
        all_clips = cropped_clips + subtitle_clips

        # Export
        filename = clip[:len(clip)-4]+".mp4"
        print(f"[ .. ] Starting export of {filename}..")
        CompositeVideoClip(all_clips).write_videofile(filename=export_dir+filename, fps=24, threads=24, preset="ultrafast")
        print("[ OK ] Export finished.")

    print("[ OK ] Complete pipeline has finished.")