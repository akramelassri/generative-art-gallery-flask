import cv2
import numpy as np

def process_image(img,type_process,name_process, value = None):
    match type_process:
        case "basic_adjustments":
            match name_process:
                case "brightness":
                    processed_image = cv2.convertScaleAbs(img, alpha=1, beta=value)
        case "color_adjustments":
            match name_process:
                case "grayscale":
                    processed_image= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                case "sepia":
                    sepia_filter = np.array([[0.272, 0.534, 0.131],
                         [0.349, 0.686, 0.168],
                         [0.393, 0.769, 0.189]])
                    
                    processed_image = cv2.transform(img, sepia_filter)
                    processed_image = np.clip(processed_image, 0, 255)
                case "color_inversion":
                    processed_image = cv2.bitwise_not(img)
        case "blur":
            match name_process:
                case "guassian":
                    processed_image = cv2.GaussianBlur(img,(5,5), value)
                case "pixelation":
                    pass
        case "transformation":
            match name_process:
                case "wraping":
                    rows, cols = img.shape[:2]
                    m = np.float32([[1, 0, 50], [0, 1, 50]])
                    processed_image = cv2.warpAffine(img, m, (cols, rows))
        case "artistic":
            match name_process:
                case "oil":
                    processed_image = cv2.xphoto.oilPainting(img, 7, 1)
                case "pencil":
                    if(value == 1):
                        processed_image = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[0]
                    else:
                        processed_image = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[1]
                case "water":
                    processed_image = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
                    
    return processed_image