'''
This program outputs a visualization of a sample synthetic boards bounding boxes.
'''
import cv2

IMAGE_PATH = "synthetic_dataset/images/train/synthetic_set12_3x4_00000.png"
LABEL_PATH = "synthetic_dataset/labels/train/synthetic_set12_3x4_00000.txt"
DISPLAY_CLASS_NAMES = False
BOX_COLOR = (0, 255, 0)
BOX_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)
TEXT_SCALE = 0.5
TEXT_THICKNESS = 1

def draw_boxes_from_yolo(image_path, label_path):
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    with open(label_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        try:
            parts = line.strip().split()
            if len(parts) != 5:
                print(f"Warning: Skipping invalid line in label file: '{line.strip()}'")
                continue
            x_center_norm = float(parts[1])
            y_center_norm = float(parts[2])
            width_norm = float(parts[3])
            height_norm = float(parts[4])

            x_center_abs = x_center_norm * w
            y_center_abs = y_center_norm * h
            width_abs = width_norm * w
            height_abs = height_norm * h

            x_min = int(x_center_abs - (width_abs / 2))
            y_min = int(y_center_abs - (height_abs / 2))
            x_max = int(x_center_abs + (width_abs / 2))
            y_max = int(y_center_abs + (height_abs / 2))
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), BOX_COLOR, BOX_THICKNESS)
        except Exception as e:
            print("Error")

    return image


if __name__ == "__main__":
    image_with_boxes = draw_boxes_from_yolo(IMAGE_PATH, LABEL_PATH)
    save_path = "example_bounding.png"
    cv2.imwrite(save_path, image_with_boxes)