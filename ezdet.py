import cv2
import torch
from ultralytics import YOLO
import serial
import time

ser = serial.Serial('COM8', 9600)
time.sleep(2)

model = YOLO("yolov10b.pt")

class_file = "coco.names"  
with open(class_file, "r") as f:
    class_names = [line.strip() for line in f.readlines()]

cap = cv2.VideoCapture(0)

def area(x1, x2, y1, y2):
    a = abs(x1-x2)*abs(y1-y2)
    return a


if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    resized_frame = cv2.resize(frame, (640, 640))
    
    with torch.no_grad():
        results = model(resized_frame)

    obstacle_in_front = False
    obstacle_in_left = False
    obstacle_in_right = False

    for detection in results:
        boxes = detection.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  
            confidence = box.conf[0]  
            if confidence < 0.5:  
                continue
            class_id = int(box.cls[0])  
            a = area(x1, x2, y1, y2)
            cv2.putText(resized_frame, "Area: " + str(a), (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            label = class_names[class_id] if class_id < len(class_names) else "Unknown"
            #label = int(box.cls[0])
            cv2.putText(resized_frame, str(label), (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            if label:
                if (x1 < 320 and x2 > 320):
                    obstacle_in_front = True
                if (x1 < 320 and x2 < 320):
                    obstacle_in_left = True
                if (x1 > 320 and x2 > 320):
                    obstacle_in_right = True
            label_text = f"{label}{confidence:.2f}"
    if obstacle_in_front and a > 50000 and label == 'person':
        cv2.putText(resized_frame, "Obstacle in front, stopping", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        ser.write(b'S')
    elif obstacle_in_left and a > 50000 and label == 'person':
        cv2.putText(resized_frame, "Obstacle in left, stopping", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        ser.write(b'R')
    elif obstacle_in_right and a > 50000 and label == 'person':
        cv2.putText(resized_frame, "Obstacle in right, stopping", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        ser.write(b'L')
    else:
        cv2.putText(resized_frame, "Path, clear, moving forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        ser.write(b'F')
    color = (0, 0, 0)
    cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)


    
    cv2.imshow("YOLOv10 Real-Time Detection", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("User requested exit.")
        break

cap.release()
cv2.destroyAllWindows()
