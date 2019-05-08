# Import libraries
import cv2 # opencv
import os #os specific stuff

## Vars

f_path = "/pfs/videos"
f_out = "/pfs/out"


## Functions

# Process video
def process_video(video):
    cap = cv2.VideoCapture(video)
    currentframe = 0

    # Get video name without extension for naming video
    vid_name = (os.path.splitext(os.path.basename(video))[0])

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # process the video into frames
        if ret:
            # Saves image of the current frame in jpg file
            name = str(vid_name) + "_" + str(currentframe) + '.jpg'
            cv2.imwrite(os.path.join(f_out, name), frame)

            # Iterate through the frames one by one
            currentframe += 1

        else:
            cap.release()
            break

## Body

# Read all the videos from the specified path and process them
for dirpath, dirs, files in os.walk(f_path):
    for file in files:
        process_video(os.path.join(dirpath, file))