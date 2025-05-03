from moviepy import VideoFileClip
from moviepy.video.fx import *
import pandas as pd
import os

clip_dir = "downloaded_clips/"
tracking_data_dir = "face_tracking_data/"

def crop_clip(clip: VideoFileClip, start_time, end_time, center_position):
    
    """
    This function crops a subclip of the given clip. Its duration is given by start and end time.
    The crop is centered around the passed center position. After cropping the clip is returned.
    """

    subclip = clip.subclipped(start_time, end_time).with_start(start_time).with_end(end_time)

    # Keep the crop in bounds
    if center_position[0] - 304 < 0:
        center_position = (304, center_position[1])
    elif center_position[0] + 304 > 1920:
        center_position = (1920 - 304, center_position[1])

    cropped_subclip = subclip.cropped(x_center=center_position[0], y_center=1080/2, width=608, height=1080)

    return cropped_subclip

def cropper_handler(return_cropped_clips=False):

    """
    Main function of this script. Likely to be called when imported as module.
    """

    # Loads the data from given directories
    clips, tracking_data = load_data()
    
    # Iterate through all found clips and crop them
    cropped_clips = []
    for i in range(len(clips)):

        # Pass the loaded data to an extra subclip creation handler that reads that data.
        # The cropped clips will get returned
        cropped_clips.append(handle_tracking_data(clip=clips[i], tracking_data=tracking_data[i]))
    
    if return_cropped_clips:
        return cropped_clips

def handle_tracking_data(clip: VideoFileClip, tracking_data: pd.DataFrame):

    """
    This function handles the given tracking data in a way, that it iterates through it and instructs
    the behaviour of the creation of subclips from the given clip.
    """

    cropped_clips = []
    last_start_time = 0
    last_center_pos = (0, 0)

    print("[ .. ] Creating cropped subclips (this may take a few seconds)..")

    # Iterate through all rows of tracking data
    for i, row in tracking_data.iterrows():

        # Get data of the current row
        x = row["x"]
        y = row["y"]
        frame = row["frame"]

        # If this is the first row, do the same as always, but start at time 0
        if i == 0:
            last_start_time = 0
            last_center_pos = (x, y)
            continue

        # Save this frame as the end time of the previous clip
        end_time = frame / clip.reader.fps

        # Crop the previous clip and append it to the list of all cropped clips
        cropped_clips.append(crop_clip(clip, last_start_time, end_time, last_center_pos))

        # Prepare the start time and center position for the next iteration
        last_start_time = end_time
        last_center_pos = (x, y)        

        # If this is the last row of data, just create a clip from here until the end
        if i == len(tracking_data) - 1:
            end_time = clip.duration
            cropped_clips.append(crop_clip(clip, last_start_time, end_time, last_center_pos))

    print("[ OK ] Finished creating cropped subclips.")

    return cropped_clips

def load_data():

    """
    Loads data (clips and tracking data) and returns it.
    """

    print("[ .. ] Loading data..")

    tracking_data_file_names = os.listdir(tracking_data_dir)
    tracking_data_file_names.sort()
    tracking_data = []
    clips = []


    if len(os.listdir(clip_dir)) != len(tracking_data_file_names):
        print("[ WARNING ] There is a mismatch in the amount of tracking data files and clips.")
        print("[ WARNING ] Please ensure first each clip was analyzed.")
        exit()
    
    print(f"[ NOTE ] Found {len(tracking_data_file_names)} clips and their tracking data.")

    for t in tracking_data_file_names:

        # Skip broken clips
        if "BROKEN" in t:
            print(f"[ NOTE ] Found broken clip ({t}), skipping.")
            continue    
        
        # Load and append clips and tracking data
        tracking_data.append(pd.read_xml(tracking_data_dir+t))
        clips.append(VideoFileClip(clip_dir+t[:len(t)-4]+".mkv"))

    print("[ OK ] Data successfully loaded.")

    return clips, tracking_data

if __name__ == "__main__":
    pass