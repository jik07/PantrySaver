from PIL import Image
from pytesseract import pytesseract
import numpy as np
import matplotlib.pyplot as plt

class TextExtractor():
    def __init__(self, process_img):
        self.process_img = process_img

        if self.process_img:
            import cv2

    def get_raw_text(self, img):
        if self.process_img:
            pil_image = img.convert('RGB')
            cv2_image = np.array(pil_image)
            cv2_image = cv2_image[:, :, ::-1].copy()

            cv2_gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)

            img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 15, 20)

        text = pytesseract.image_to_string(img)
        return text.split("\n")
