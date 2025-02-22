import cv2
import math
import serial
import mediapipe as mp

# Arduino serial communication setup
arduino = serial.Serial('COM8', 9600)  # Replace 'COM8' with the appropriate port

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# OpenCV setup
cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

# Servo limits and scaling
servo_min = 0
servo_max = 180
x_scale = (servo_max - servo_min) / cap.get(3)
y_scale = (servo_max - servo_min) / cap.get(4)

# Initialize servo positions
servo_x = 90
servo_y = 90

# Smoothing variables (increase alpha for smoother movements)
alpha = 0.9  # Adjust this value to control the level of smoothing
prev_servo_x = 90
prev_servo_y = 90

# Wrist point
wrist_x = 0
wrist_y = 0

with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        if not ret:
            break

        # Convert the image to RGB and perform hand tracking
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get wrist landmark (landmark 0)
                wrist_landmark = hand_landmarks.landmark[0]
                wrist_x, wrist_y = int(wrist_landmark.x * frame.shape[1]), int(wrist_landmark.y * frame.shape[0])

                # Draw bounding box around the hand region
                hand_region = hand_landmarks.landmark
                min_x, min_y, max_x, max_y = frame.shape[1], frame.shape[0], 0, 0
                for landmark in hand_region:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)

                # Draw hand landmarks and connections
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Calculate servo positions based on wrist position
        wrist_x_deg = int(servo_min + wrist_x * x_scale)
        wrist_y_deg = int(servo_min + wrist_y * y_scale)

        # Smooth the servo movements
        servo_x = int(alpha * wrist_x_deg + (1 - alpha) * prev_servo_x)
        servo_y = int(alpha * wrist_y_deg + (1 - alpha) * prev_servo_y)

        # Send the wrist position to Arduino for servo control
        arduino.write(f"1:{servo_x},{servo_y}\n".encode())

        # Display the frame with annotations
        cv2.imshow("Hand Gesture Control", frame)

        # Exit loop by pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
arduino.close()