# Main file for Overwatch-Auto-Hilights
# Author: William Kluge
# Date: 2017-10-25
import cv2
import numpy
import time

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from matplotlib import pyplot as plt

from src.grip import GripPipeline


def print_stats(fps, frame_count):
    print_string = str(round(fps, 2)) + "fps : Time Remaining: "
    time_remaining = frame_count / fps

    if time_remaining > 60:
        print_string += str(time_remaining / 60) + " minutes"
    else:
        print_string += str(time_remaining) + " seconds"


def main():
    # Show every selected frame
    FRAME_BY_FRAME = False
    # Time (in seconds) to select around each kill
    CLIP_SURROUND_TIME = 4
    # Image that holds the user's name
    name_image = cv2.imread("name.png")
    # Create the GRIP Pipeline for image processing
    pipline = GripPipeline(name_image)
    # Get the path of the video to edit
    input_path = input("Enter the path of the video to edit: ")
    input_path = input_path.replace("\"", "")  # Removes the "" around the path so that file paths can be copied as path
    # Read the path into memory as a video clip
    input_video = VideoFileClip(input_path)
    # Time this process started
    start = time.time()
    # Amount of frames processed
    processed_frames = 0
    # Video FPS
    video_fps = input_video.fps
    # Amount of frames in the video
    frame_count = int(video_fps * input_video.duration)
    # Clips that were found to fit the criteria
    selected_clips = []

    last_clip_end = -1

    for frame in input_video.iter_frames():
        # Iterates through the frames in a clip

        if processed_frames / video_fps < last_clip_end:
            processed_frames += 1
            continue
        else:
            last_clip_end = -1

        pipline.process(frame)  # Processes the frame using the GRIP filter

        if len(pipline.find_contours_output) > 0:
            # If the array is not none (there are contours)
            if FRAME_BY_FRAME:
                # show the associated images
                plt.subplot(121), plt.imshow(frame, cmap='gray')
                plt.title("Scanned Image"), plt.xticks([]), plt.yticks([])
                plt.subplot(122), plt.imshow(pipline.rgb_threshold_output, cmap='gray')
                plt.title("RGB Filter Output"), plt.xticks([]), plt.yticks([])
                plt.suptitle("Frame Analysis")
                plt.show()

            clip_start_time = processed_frames / video_fps - CLIP_SURROUND_TIME
            clip_end_time = processed_frames / video_fps + CLIP_SURROUND_TIME

            if clip_start_time < 0:
                clip_start_time = 1

            if clip_end_time > input_video.duration:
                # If the end of the clip would be past the end of the video
                clip_end_time = input_video.duration

            print("Selected video between", clip_start_time, "and", clip_end_time)

            selected_clips.append(input_video.subclip(clip_start_time, clip_end_time))
            last_clip_end = clip_end_time

        # Prints out stats
        processed_frames += 1
        print("Processed frame #" + str(processed_frames))
        if processed_frames % 10 == 0:
            fps = processed_frames / (time.time() - start)
            print_stats(fps, frame_count)

    # Writing video file
    final_clip = concatenate_videoclips(selected_clips)
    final_clip.write_videofile(input_path[:4] + "_highlights.mp4")

    print("Done.")


if __name__ == "__main__":
    main()
