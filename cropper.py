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

    # Check if start time is actually after the clip has finished. Could happen due to float estimation
    # when the last frame is the start time.
    if start_time >= clip.duration:
        start_time = clip.duration - 0.001

    subclip = clip.subclipped(start_time, end_time).with_start(start_time).with_end(end_time)

    # Keep the crop in bounds
    if center_position[0] - 304 < 0:
        center_position = (304, center_position[1])
    elif center_position[0] + 304 > 1920:
        center_position = (1920 - 304, center_position[1])

    cropped_subclip = subclip.cropped(x_center=center_position[0], y_center=1080/2, width=608, height=1080)

    return cropped_subclip

def cropper_handler(clip: VideoFileClip, tracking_data: pd.DataFrame):

    """
    This function handles the given tracking data in a way, that it iterates through it and instructs
    the behaviour of the creation of subclips from the given clip.
    """

    print("[ .. ] Starting cropper module..")

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

    print("[ OK ] cropper module has finished.")
    print()

    return cropped_clips

if __name__ == "__main__":
    pass