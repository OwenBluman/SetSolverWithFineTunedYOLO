'''
This program outputs a sample prediction of the fine-tuned model on a 3x5 Set board.
'''
import cv2
from ultralytics import YOLO

MODEL_PATH = "/Users/owenbluman/Downloads/best.pt"
IMAGE_TO_TEST_PATH = "/Users/owenbluman/Desktop/Screenshot 2025-05-15 at 1.05.43 AM.png"
CONFIDENCE_THRESHOLD = 0.4
DEVICE = 'cpu'
OUTPUT_IMAGE_PATH = "example_yolo_output.png"


model = YOLO(MODEL_PATH)
model.to(DEVICE)
image_bgr = cv2.imread(IMAGE_TO_TEST_PATH)
results = model.predict(image_bgr, verbose=False, conf=CONFIDENCE_THRESHOLD, device=DEVICE)
boxes = results[0].boxes

detected_items_count = 0
if boxes is not None:
    detected_items_count = len(boxes)
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        class_name = model.names[cls]
        cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{class_name}: {conf:.2f}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_x, text_y = x1, y1 - 10
        if text_y < h:
            text_y = y1 + h + 5

        cv2.rectangle(image_bgr, (text_x, text_y - h - 2), (text_x + w, text_y + 2), (0, 255, 0), -1)
        cv2.putText(image_bgr, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
else:
    print("Detection failure")

cv2.imwrite(OUTPUT_IMAGE_PATH, image_bgr)
