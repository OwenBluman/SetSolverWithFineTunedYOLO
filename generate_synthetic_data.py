'''
This program generates 500 synthetic boards for training a set detection model.
'''
from PIL import Image
import os
import random

CARD_IMAGES_FOLDER = "iconPics"
BACKGROUND_IMAGE_PATHS = ["bg_small.png"]
OUTPUT_IMAGE_DIR = "synthetic_dataset/images/train"
OUTPUT_LABEL_DIR = "synthetic_dataset/labels/train"
NUM_IMAGES_TO_GENERATE = 500
CARD_WIDTH = 359
CARD_HEIGHT = 214
FIXED_POSITIONS = [
    (36, 36), (423, 36), (810, 36),
    (36, 278), (423, 278), (810, 278),
    (36, 520), (423, 520), (810, 520),
    (36, 762), (423, 762), (810, 762),
]
NUM_CARDS_PER_IMAGE = 12

def get_yolo_format(class_id, box, img_width, img_height):
    x_min, y_min, x_max, y_max = box
    dw = 1.0 / img_width
    dh = 1.0 / img_height
    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    width = x_max - x_min
    height = y_max - y_min
    x_center_norm = x_center * dw
    y_center_norm = y_center * dh
    width_norm = width * dw
    height_norm = height * dh
    x_center_norm = max(0.0, min(1.0, x_center_norm))
    y_center_norm = max(0.0, min(1.0, y_center_norm))
    width_norm = max(0.0, min(1.0, width_norm))
    height_norm = max(0.0, min(1.0, height_norm))

    return f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"

all_card_filenames = sorted([f for f in os.listdir(CARD_IMAGES_FOLDER) if f.endswith('.png')])
class_id_to_filename = {i: filename for i, filename in enumerate(all_card_filenames)}
num_classes = len(all_card_filenames)

card_images_pil = {}
for i, filename in class_id_to_filename.items():
    try:
        path = os.path.join(CARD_IMAGES_FOLDER, filename)
        card_img = Image.open(path).convert("RGBA")
        if card_img.size != (CARD_WIDTH, CARD_HEIGHT):
             card_img = card_img.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
        card_images_pil[i] = card_img
    except FileNotFoundError:
         exit()

os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_LABEL_DIR, exist_ok=True)

generated_count = 0
bg_width, bg_height = 0, 0

try:
    bg_path = BACKGROUND_IMAGE_PATHS[0]
    print(f"Loading background image from: {os.path.abspath(bg_path)}")
    background_pil = Image.open(bg_path).convert("RGBA")
    bg_width, bg_height = background_pil.size
    print(f"Background size: {bg_width}x{bg_height}")
except FileNotFoundError:
    exit()

while generated_count < NUM_IMAGES_TO_GENERATE:
        chosen_class_ids = random.sample(list(card_images_pil.keys()), NUM_CARDS_PER_IMAGE)
        current_image_pil = background_pil.copy()
        annotations = []

        for i, class_id in enumerate(chosen_class_ids):
            card_pil = card_images_pil[class_id]
            pos_x, pos_y = FIXED_POSITIONS[i]
            pos_x, pos_y = int(pos_x), int(pos_y)
            current_image_pil.paste(card_pil, (pos_x, pos_y), card_pil)

            x_min = pos_x
            y_min = pos_y
            x_max = pos_x + CARD_WIDTH
            y_max = pos_y + CARD_HEIGHT

            yolo_annotation = get_yolo_format(class_id, (x_min, y_min, x_max, y_max), bg_width, bg_height)
            if yolo_annotation:
                 annotations.append(yolo_annotation)

        current_image_pil = current_image_pil.convert("RGB")

        output_image_filename = f"synthetic_set12_3x4_{generated_count:05d}.png"
        output_label_filename = f"synthetic_set12_3x4_{generated_count:05d}.txt"
        image_save_path = os.path.join(OUTPUT_IMAGE_DIR, output_image_filename)
        label_save_path = os.path.join(OUTPUT_LABEL_DIR, output_label_filename)

        current_image_pil.save(image_save_path)

        if annotations:
             with open(label_save_path, "w") as f:
                f.write("\n".join(annotations))
        generated_count += 1

