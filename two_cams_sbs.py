import cv2

def main():
    # Open the video streams
    cap0 = cv2.VideoCapture('/dev/video5')
    cap2 = cv2.VideoCapture('/dev/video11')

    # Check if camera opened successfully
    if not (cap0.isOpened() and cap2.isOpened()):
        print("Error: Couldn't open one or both video streams.")
        return

    # Get the default resolutions of the cameras
    width = int(cap0.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap0.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a window to display the video
    cv2.namedWindow('Video Streams', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video Streams', 2 * width, height)

    while True:
        # Capture frame-by-frame
        ret0, frame0 = cap0.read()
        ret2, frame2 = cap2.read()

        if not (ret0 and ret2):
            print("Error: Couldn't read frames from one or both video streams.")
            break

        # Display the resulting frames side by side
        combined_frame = cv2.hconcat([frame0, frame2])
        cv2.imshow('Video Streams', combined_frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture objects
    cap0.release()
    cap2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
