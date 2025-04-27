import cv2
import pandas as pd

def append_eyes():
    """
    This function will just read the current set of detected eyes and appends its values 
    to the corresponding lists.
    """
    for (x, y, w, h) in eyes:
        eyes_x.append(x)
        eyes_y.append(y)
        eyes_w.append(w)
        eyes_h.append(h)
        eyes_frame.append(c) 

def detect_eyes(_frame, offset=0):
    
    """
    Check the given frame for eyes in it. If no eyes are found in this frame, the funtion 
    will call it self again to check neighboring frames until eyes are found.
    """
    
    print(f"[ .. ] Searching eyes with offset of {offset}..")

    # Convert to gray scale and start searching
    gray_frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
    _eyes = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=17, minSize=(10, 10))

    # Return eyes if detected
    if len(_eyes) > 0:
        print(f"[ OK ] Eyes found in frame {c + offset}.")
        global eyes
        eyes = _eyes
        return

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

    loaded_video.set(cv2.CAP_PROP_POS_FRAMES, c + offset)
    res, _frame = loaded_video.read()

    detect_eyes(_frame, offset=offset)

def face_tracker_handler(file_path: str):

    global loaded_video, loaded_video_length, c

    # Load video
    loaded_video = cv2.VideoCapture(filename=f)
    
    # Video length in frames
    loaded_video_length = int(loaded_video.get(cv2.CAP_PROP_FRAME_COUNT))

    print("[ .. ] Starting analysis..")

    c = 0
    while loaded_video.isOpened():

        print(f"[ .. ] {int(c/loaded_video_length * 100)}% [{c} / {loaded_video_length}] - Processing..")

        # Read the video
        res, frame = loaded_video.read()

        if not res:
            print("[ NOTE ] Finished reading the video file.")
            loaded_video.release()
            break

        # Detect all eyes in or around the current frame
        detect_eyes(frame)

        # Append the current set of eyes to storage
        append_eyes()

        # Advance 60 frames (2sec at 30fps)
        c += 60
        loaded_video.set(cv2.CAP_PROP_POS_FRAMES, c)
    
    print("[ OK ] Completed analysis.")

    print("[ .. ] Converting data..")
    eye_data = pd.DataFrame({
        "x": eyes_x,
        "y": eyes_y,
        "width": eyes_w,
        "height": eyes_h,
        "frame": eyes_frame,
    })
    print("[ OK ] Conversion complete.") 

    print(f"[ .. ] Storing data in {eye_data_filename}..")
    eye_data.to_xml(eye_data_filename, index=False)
    print("[ OK ] Stored successfully.")

def print_eye_information(_eyes):
    """
    This function takes detected eyes as input and nicely prints some information.
    """

    print()
    print("-- Information --")
    print(f"Amount of eyes detected: {len(_eyes)}")
    print()
    for i in range(0, len(_eyes)):
        print(f"Eye {i+1}")
        print(f"  Start: ({_eyes[i][0]} | {eyes[i][1]})")
        print(f"  End:   ({_eyes[i][0]+_eyes[i][2]} | {eyes[i][1]+_eyes[i][3]})")
    print("------ End ------")
    print()

# Global vars

f = "downloaded_clips/Papaplatte_Warum ohne Monte?_2245330192.mkv"
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

eyes = []   # Global variable to store the current set of detected eyes
eyes_x, eyes_y, eyes_w, eyes_h, eyes_frame = [], [], [], [], [] # Keep track of all detected eyes
eye_data_filename = "eye_data.xml"

loaded_video = None     # The video loaded by cv2
loaded_video_length = 0 # Length of loaded video
c = 0                   # Counter to keep track of frames

if __name__ == "__main__":
    face_tracker_handler(f)