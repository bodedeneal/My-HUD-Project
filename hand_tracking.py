import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a "selfie" view
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        result = hands.process(rgb_frame)

        # Draw hand landmarks
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get fingertip position (e.g., index finger tip)
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x, y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])

                # Draw a circle on the fingertip to represent a cursor
                cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

        cv2.imshow("Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
