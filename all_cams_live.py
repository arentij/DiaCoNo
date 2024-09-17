import cv2
import threading

def stream(device):
    # Open the video capture device
    cap = cv2.VideoCapture(device)

    if not cap.isOpened():
        print("Error: Unable to open the video capture device.")
        return

    # Set properties - adjust as needed
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Create a window to display the video stream
    window_name = 'USB Camera Stream_' + device
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if the frame is valid
        if not ret:
            print("Error: Unable to read frame from the video capture device.")
            break

        # Display the frame
        cv2.imshow(window_name, frame)

        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":

    device1 = '/dev/video4'
    device2 = '/dev/video10'
    # stream(device)
    cam1_worker = threading.Thread(target=stream, args=([device1]))
    cam1_worker.start()

    cam2_worker = threading.Thread(target=stream, args=([device2]))
    # cam2_worker.start()