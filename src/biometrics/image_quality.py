"""Módulo para verificação da qualidade da imagem para reconhecimento facial."""

import cv2
import os
import numpy as np

# Carrega o classificador Haar Cascade para detecção facial
cascade_path = r'C:\haarcascades\haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

def is_image_quality_sufficient(image_np: np.ndarray) -> tuple[bool, str]:
    """Verifica a qualidade da imagem para reconhecimento facial.

    Args:
        image_np: A imagem como um array NumPy (BGR).

    Returns:
        Uma tupla (bool, str) indicando se a qualidade é suficiente e uma mensagem.
    """
    if image_np is None or image_np.size == 0:
        return False, "Imagem vazia ou inválida."

    gray_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    # 1. Detecção de Rosto
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    if len(faces) == 0:
        return False, "Nenhum rosto detectado na imagem."
    
    # Considerando apenas o maior rosto para análise de qualidade
    # (x, y, w, h)
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = faces[0]

    # 2. Verificação do Tamanho do Rosto
    min_face_size = 100 # pixels
    if w < min_face_size or h < min_face_size:
        return False, f"Rosto muito pequeno ({w}x{h} pixels). Tamanho mínimo é {min_face_size}x{min_face_size}."

    face_roi = gray_image[y:y+h, x:x+w]

    # 3. Análise de Iluminação (Brilho Médio)
    average_brightness = np.mean(face_roi)
    min_brightness = 50
    max_brightness = 200
    if average_brightness < min_brightness or average_brightness > max_brightness:
        return False, f"Iluminação inadequada (brilho médio: {average_brightness:.2f}). Ideal entre {min_brightness} e {max_brightness}."

    # 4. Análise de Borrão (Variância do Laplaciano)
    # Quanto maior o valor, mais nítida a imagem. Valores baixos indicam borrão.
    # É importante que a ROI tenha um tamanho mínimo para o Laplaciano ser significativo
    if face_roi.shape[0] < 3 or face_roi.shape[1] < 3: # Mínimo 3x3 para Laplaciano
        return False, "ROI do rosto muito pequena para análise de borrão."

    laplacian_var = cv2.Laplacian(face_roi, cv2.CV_64F).var()
    min_laplacian_var = 100.0 # Este valor pode precisar de ajuste com testes
    if laplacian_var < min_laplacian_var:
        return False, f"Imagem borrada (variância do Laplaciano: {laplacian_var:.2f}). Mínimo aceitável é {min_laplacian_var}."

    return True, "Qualidade da imagem suficiente."
