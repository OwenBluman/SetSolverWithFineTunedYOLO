'''
This program acts as the main driver for the novel YOLO-based image detection approach to solve Set
'''
import mss
import numpy as np
import cv2
import pyautogui
import time
from ultralytics import YOLO

class Table:
    def __init__(self, set_cards):
        self.cards = set_cards

    def findsets_gnt(self):
        for i, ci in enumerate(self.cards):
            for j, cj in enumerate(self.cards[i + 1:], i + 1):
                for k, ck in enumerate(self.cards[j + 1:], j + 1):
                    if ci.isset(cj, ck):
                        return ci, cj, ck
        return None

class Card:
    def __init__(self, *attrs):
        self.attrs = attrs

    def isset(self, card1, card2):
        def allsame(v0, v1, v2): return v0 == v1 and v1 == v2
        def alldifferent(v0, v1, v2): return len({v0, v1, v2}) == 3
        return all(allsame(v0, v1, v2) or alldifferent(v0, v1, v2)
                   for (v0, v1, v2) in zip(self.attrs, card1.attrs, card2.attrs))

def filename_to_card(filename):
    color_map = {"red": 0, "green": 1, "purple": 2}
    number_map = {"one": 0, "two": 1, "three": 2}
    shape_map = {"pill": 0, "tilda": 1, "diamond": 2}
    fill_map = {"empty": 0, "stripe": 1, "solid": 2}

    attributes = filename.rsplit(".", 1)[0].split("_")
    return Card(
        color_map[attributes[0]],
        number_map[attributes[1]],
        shape_map[attributes[2]],
        fill_map[attributes[3]]
    )

MODEL_PATH = "/Users/owenbluman/Downloads/best.pt"
CONFIDENCE_THRESHOLD = 0.8
DEVICE = 'cpu'
CAPTURE_REGION = {'top': 200, 'left': 420, 'width': 620, 'height': 660}

def load_model(path, device):
    model = YOLO(path)
    model.to(device)
    return model

def detect_cards(model):
    with mss.mss() as sct:
        img_bgra = np.array(sct.grab(CAPTURE_REGION))
        img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
        results = model.predict(img_bgr, verbose=False, conf=CONFIDENCE_THRESHOLD, device=DEVICE)
        boxes = results[0].boxes

        detections = []
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                card = filename_to_card(class_name)
                center_x = (x1 + x2) // 2 / 2 + CAPTURE_REGION['left']
                center_y = (y1 + y2) // 2 / 2 + CAPTURE_REGION['top']

                detections.append({
                    "card": card,
                    "filename": class_name,
                    "position": (center_x, center_y)
                })
        return detections

def find_card_positions(cards, detections):
    positions = []
    for target in cards:
        for d in detections:
            if d["card"].attrs == target.attrs:
                positions.append((d["position"], d["filename"]))
                break
    return positions

def click_positions(positions):
    for (x, y), fname in positions:
        pyautogui.click(x, y)

def main():
    model = load_model(MODEL_PATH, DEVICE)
    set_count = 0
    set_times = []
    start_time = time.time()

    try:
        while True:
            detections = detect_cards(model)
            cards = [d["card"] for d in detections]
            table = Table(cards)
            result = table.findsets_gnt()

            if result:
                positions = find_card_positions(result, detections)
                if len(positions) == 3:
                    click_positions(positions)
                    set_count += 1

                    elapsed_time = time.time() - start_time
                    set_times.append((set_count, elapsed_time))
                else:
                    print("Mapping Error")
            else:
                print("Set Detection Failure")

            time.sleep(0.3)


    except KeyboardInterrupt:

        print("Stopped.")

        if set_count > 0:
            total_time = time.time() - start_time
            average_time = total_time / set_count
            print(f"Total sets found: {set_count}")
            print(f"Total game time: {total_time:.2f} seconds")
            print(f"Average time per set: {average_time:.2f} seconds")

        else:

            print("No sets found.")


if __name__ == "__main__":
    time.sleep(1)
    main()
