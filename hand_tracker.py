"""
CyberTrace - Python Hand & Fingertip Tracker (Reference Implementation)
Requires: pip install opencv-python mediapipe

This script illustrates the same 2-stage AI pipeline in Python:
1. Grabs frames from your webcam using OpenCV.
2. Passes each frame to Google MediaPipe Hands.
3. Isolates all 5 fingertips (landmarks 4, 8, 12, 16, 20).
4. Draws glowing colored trails following each fingertip in real-time.
"""

from collections import deque
import cv2
import mediapipe as mp
import numpy as np

def main():
    print("Initializing Camera & MediaPipe Hands Model...")

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5
    )

    # 5 Fingertip Indices and their BGR Neon Colors
    FINGERTIPS = {
        4: ("Thumb",  (0, 183, 255)),   # Gold / Amber
        8: ("Index",  (254, 242, 0)),   # Cyan
        12: ("Middle", (135, 255, 0)),  # Green
        16: ("Ring",   (239, 70, 217)), # Magenta
        20: ("Pinky",  (34, 87, 255))   # Coral
    }

    # Store trail coordinates for each fingertip (max 30 historical points)
    trails = {tip: deque(maxlen=30) for tip in FINGERTIPS}

    # Open Default Laptop Camera (0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("\n[STARTED] CyberTrace Running!")
    print("Press 'q' in the window to quit, or 'c' to clear trails.\n")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Flip horizontally for a natural mirror view
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert BGR (OpenCV format) to RGB (MediaPipe format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # If hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the full skeleton
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Track each fingertip
                for tip_idx, (name, color) in FINGERTIPS.items():
                    lm = hand_landmarks.landmark[tip_idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    # Add to trail history
                    trails[tip_idx].append((cx, cy))

                    # Draw glowing concentric ring on fingertip
                    cv2.circle(frame, (cx, cy), 10, color, 2)
                    cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)
        else:
            # Gradually decay trails when hand leaves the camera frame
            for tip in trails:
                if len(trails[tip]) > 0:
                    trails[tip].popleft()

        # Render trails on screen
        for tip_idx, pts in trails.items():
            _, color = FINGERTIPS[tip_idx]
            for i in range(1, len(pts)):
                if pts[i - 1] is None or pts[i] is None:
                    continue
                # Line thickness decreases for older points (comet effect)
                thickness = int(np.sqrt(30 / float(i + 1)) * 2.5)
                cv2.line(frame, pts[i - 1], pts[i], color, max(1, thickness))

        # Show live frame
        cv2.imshow("CyberTrace - Hand & Fingertip Tracker", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            for tip in trails:
                trails[tip].clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
