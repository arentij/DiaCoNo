import cv2
import glob

def capture_images_from_cameras():
    # Find all video devices
    video_devices = glob.glob('/dev/video*')

    for video_device in video_devices:
        # Open the video device
        cap = cv2.VideoCapture(video_device)

        # Check if the camera is opened successfully
        if not cap.isOpened():
            print(f"Could not open video device: {video_device}")
            continue

        # Read a frame from the camera
        ret, frame = cap.read()

        # Release the capture object
        cap.release()

        # Check if the frame is valid
        if not ret:
            print(f"Could not read frame from video device: {video_device}")
            continue

        # Get the name of the video source
        video_source_name = f"camera_{video_device.split('/')[-1]}"

        # Save the frame with the name of the video source
        image_filename = f"/CMFX/different_cameras/{video_source_name}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Saved image from {video_source_name} to {image_filename}")


if __name__ == "__main__":
    capture_images_from_cameras()
