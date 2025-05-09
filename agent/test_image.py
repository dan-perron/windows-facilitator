import cv2
import os

image_path = os.path.join('agent', 'images', 'ootp_window.png')
print(f"Trying to load image from: {os.path.abspath(image_path)}")
print(f"File exists: {os.path.exists(image_path)}")

try:
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image with OpenCV")
    else:
        print(f"Successfully loaded image. Shape: {img.shape}")
except Exception as e:
    print(f"Error loading image: {str(e)}") 