import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

texto = "Acentos: áéíóú ç ã õ ê ô â João José"
img = np.ones((120, 600, 3), dtype=np.uint8) * 255

font = ImageFont.load_default()
img_pil = Image.fromarray(img)
draw = ImageDraw.Draw(img_pil)
draw.text((10, 40), texto, font=font, fill=(0, 0, 0))

img_cv = np.array(img_pil)
cv2.imshow("Teste Fonte com Acentos", img_cv)
cv2.waitKey(0)
cv2.destroyAllWindows()