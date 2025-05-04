import cv2
import pandas as pd
import os

def append_eye_data():
    """
    This function will just read the current set of detected eyes and appends its values 
    to the corresponding lists.
    """

    if len(eye_data) == 0:
        print("[ NOTE ] No eye information passed to store.")
        return

    eye_x.append(eye_data[0])
    eye_y.append(eye_data[1])
    eye_frame.append(c) 

def detect_eyes(_frame, offset=0):
    
    """
    Check the given frame for eyes in it. If no eyes are found in this frame, the funtion 
    will call it self again to check neighboring frames until eyes are found.
    """

    # print(f"[ .. ] Looking for eyes in frame {c} with offset {offset}..")

    global eye_data

    # Convert to gray scale and start searching
    gray_frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
    _eye_data = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

    # --- Return scenarios ---

    # Case one eye detected
    if len(_eye_data) == 1:
        # print(f"[ OK ] One eye found in frame {c + offset}.")
        x_center = _eye_data[0][0] + _eye_data[0][2]
        y_center = _eye_data[0][1] + _eye_data[0][3]
        eye_data = [int(x_center), int(y_center)]
        return
    
    # Case more than one eye detected
    elif len(_eye_data) > 1:
        # print(f"[ OK ] Multiple eyes found in frame {c + offset}.")
        x_center_sum = 0    # Sum of all x center values
        y_center_sum = 0    # Sum of all y center values
        for (x, y, w, h) in _eye_data:
            x_center_sum += x + 0.5 * w
            y_center_sum += y + 0.5 * h
        x_center_avg = x_center_sum // len(_eye_data)
        y_center_avg = y_center_sum // len(_eye_data)
        eye_data = [int(x_center_avg), int(y_center_avg)]  
        return


    # --- Offset management and increasement ---

    # Advance one frame to the right from the start
    if offset == 0:
        offset += 1

    # Check if it is possible to move either left or right within the videos bounds
    elif offset > 0 and -offset + c >= 0:
        offset = -offset
    elif offset < 0 and -(offset - 1) + c <= loaded_video_length:
        offset = -(offset - 1) 
    
    # If left boundary is reached advance further to the right instead
    elif offset > 0 and -offset + c < 0 and offset + 1 + c <= loaded_video_length:
        offset += 1

    # Quit if no eyes were found in the whole video file
    else:
        print("[ WARNING ] Was NOT able to find any eyes in the given video file.")
        exit()

    # Load next frame to check
    loaded_video.set(cv2.CAP_PROP_POS_FRAMES, c + offset)
    res, _frame = loaded_video.read()

    # Check if a frame could not be loaded, if so mark the process as broken
    if not res:
        global broken
        broken = True
        eye_data = []
        print("[ CRITICAL WARNING ] There was trouble reading a frame.")
        return

    # Check for time out
    elif offset >= step_size:
        eye_data = []
        print("[ WARNING ] Time out :/")
        return

    detect_eyes(_frame, offset)

def detect_duplicate_files(file_names):
    
    """
    This function takes all file paths of the video files were the script should look for eyes.
    The function will only return non-duplicates to prevent multiple analysis on one file. 
    """
    
    print("[ .. ] Checking for duplicates..")

    already_tracked = os.listdir(face_tracking_data_dir)
    valids = []
    duplicates = []

    for f in file_names:
        if not any(f[:len(f)-4] in already for already in already_tracked):
            valids.append(f)
        else:
            duplicates.append(f)
    
    print(f"[ OK ] Done. {len(valids)} valid, {len(duplicates)} duplicate.")
    return valids

def face_tracker_handler(file_dir="downloaded_clips/"):

    """
    Main function to start the face tracker. Needs a path to video file it shall track faces from
    """

    print("[ .. ] Starting face_tracker module..")

    global loaded_video, loaded_video_length, c, eye_data, eye_x, eye_y, eye_frame, broken, clip_dir

    # Set the global clip directory
    clip_dir = file_dir

    # Get only the valid file paths (non duplicates) 
    valid_file_names = detect_duplicate_files(os.listdir(clip_dir))

    for v in valid_file_names:

        print(f"[ .. ] Handling {clip_dir+v} now..")

        # Reset global vars
        eye_data = []
        eye_x, eye_y, eye_frame = [], [], []
        broken = False

        # Load video
        loaded_video = cv2.VideoCapture(filename=clip_dir+v)
        
        # Video length in frames
        loaded_video_length = int(loaded_video.get(cv2.CAP_PROP_FRAME_COUNT))

        print("[ .. ] Starting analysis..")

        c = 0
        while loaded_video.isOpened():

            # Read the video
            res, frame = loaded_video.read()

            # Handling when end of file is reached
            if not res:
                print("[ NOTE ] Finished reading the video file.")
                loaded_video.release()
                break
            elif c > loaded_video_length:
                print("[ WARNING ] The frame count exceeded the valid limit, reading done.")
                loaded_video.release()
                break

            print(f"[ .. ] {int(c/loaded_video_length * 100)}% [{c} / {loaded_video_length}] - Processing..")

            # Detect all eyes in or around the current frame
            detect_eyes(frame)

            # Append the current eye data
            append_eye_data()

            # Advance 60 frames (2sec at 30fps)
            c += step_size
            loaded_video.set(cv2.CAP_PROP_POS_FRAMES, c)
        
        print("[ OK ] Completed analysis.")

        print("[ .. ] Converting data..")
        eye_data = pd.DataFrame({
            "x": eye_x,
            "y": eye_y,
            "frame": eye_frame,
        })
        print("[ OK ] Conversion complete.") 

        # Change name wether a file was analzed successfully or not
        if broken:
            eye_data_filename = f"{face_tracking_data_dir}BROKEN_{v[:len(v)-4]}.xml"
        else:
            eye_data_filename = f"{face_tracking_data_dir}{v[:len(v)-4]}.xml"

        # Export as .xml
        print(f"[ .. ] Storing data in {eye_data_filename}..")
        eye_data.to_xml(eye_data_filename, index=False)
        print("[ OK ] Stored successfully.")
        
        print()
    
    print("[ OK ] face_tracker module has finished.")
    print()

# Global vars

# Standard directory where downloaded clips are stored.
# If a different directiory is passed this value gets overwritten.
clip_dir = "downloaded_clips/" 

face_tracking_data_dir = "face_tracking_data/"
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

eye_data = []       # Global variable to store the current detected eye position in
eye_x, eye_y, eye_frame = [], [], []    # Store all the eye information in
broken = False  # Wether a file had trouble getting analyzed

loaded_video = None     # The video loaded by cv2
loaded_video_length = 0 # Length of loaded video
c = 0                   # (C)ounter to keep track of frames
step_size = 120         # Number of frames which c gets increased by (new default 120)

if __name__ == "__main__":
    pass