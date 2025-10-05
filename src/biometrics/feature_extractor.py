import os
from src.biometrics.image_quality import is_image_quality_sufficient
 # from src.biometrics.liveness_detection import detect_liveness_blink_haar, analyze_texture_lbp
import cv2
import os
import numpy as np
from typing import List
import math


def _imread_unicode(path):
    """Tenta ler uma imagem de forma robusta em Windows com caminhos Unicode.

    Primeiro tenta cv2.imread. Se retornar None (comum em caminhos com
    acentos no Windows para algumas builds do OpenCV), tenta usar
    numpy.fromfile + cv2.imdecode como fallback.
    """
    try:
        img = cv2.imread(path)
        if img is not None:
            return img
    except Exception:
        img = None

    # fallback: ler bytes via numpy.fromfile e decodificar
    try:
        arr = np.fromfile(path, dtype=np.uint8)
        if arr.size == 0:
            return None
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _rotate_image(img, angle, center=None):
    (h, w) = img.shape[:2]
    if center is None:
        center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR)
    return rotated


def _align_and_preprocess(img, size=(64, 64)):
    """Detecta rosto, alinha pelos olhos quando possível, aplica CLAHE e normaliza.

    Recebe uma imagem BGR (numpy array) e retorna vetor L2-normalizado ou None.
    """
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detectar rosto com Haar Cascade
    cascade_path = r'C:\haarcascades\haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = []
    # Se o cascade não carregou (paths com caracteres especiais podem quebrar), evitar chamar detectMultiScale
    if not face_cascade.empty():
        try:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        except Exception:
            faces = []

    if len(faces) > 0:
        # escolher o maior rosto detectado
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        (x, y, w, h) = faces[0]
        # margem para incluir um pouco além do rosto
        pad_w = int(0.2 * w)
        pad_h = int(0.2 * h)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(img.shape[1], x + w + pad_w)
        y2 = min(img.shape[0], y + h + pad_h)
        face_img = img[y1:y2, x1:x2]

        # tentar alinhar pelos olhos
        eye_cascade_path = r'C:\haarcascades\haarcascade_eye.xml'
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        if eye_cascade.empty():
            raise FileNotFoundError(f"Cascade não encontrado: {eye_cascade_path}. Copie o arquivo haarcascade_eye.xml para C:/haarcascades e ajuste o código se necessário.")
        gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        eyes = []
        if not eye_cascade.empty():
            try:
                eyes = eye_cascade.detectMultiScale(gray_face)
            except Exception:
                eyes = []
        if len(eyes) >= 2:
            # pegar dois olhos com maior largura
            eyes = sorted(eyes, key=lambda e: e[2], reverse=True)[:2]
            eye_centers = []
            for (ex, ey, ew, eh) in eyes:
                eye_centers.append((ex + ew/2.0, ey + eh/2.0))
            # ordenar por x
            eye_centers = sorted(eye_centers, key=lambda c: c[0])
            (xL, yL), (xR, yR) = eye_centers[0], eye_centers[1]
            # calcular ângulo entre olhos
            dy = yR - yL
            dx = xR - xL
            angle = math.degrees(math.atan2(dy, dx))
            # rotacionar o face_img para alinhar olhos horizontalmente
            face_img = _rotate_image(face_img, angle)

        # fallback: central crop sempre definido
        h, w = img.shape[:2]
        side = min(w, h)
        cx, cy = w // 2, h // 2
        x1 = max(0, cx - side // 2)
        y1 = max(0, cy - side // 2)
        x2 = x1 + side
        y2 = y1 + side
        face_img = img[y1:y2, x1:x2]

    try:
        # redimensionar
        face_img = cv2.resize(face_img, size)
    except Exception:
        return None

    # converter para gray
    face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

    # aplicar CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    face_gray = clahe.apply(face_gray)

    # vetor e normalização
    vec = face_gray.flatten().astype('float32') / 255.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def _image_to_vector(img_path_or_array, size=(64, 64)):
    # permite receber caminho ou numpy array
    if isinstance(img_path_or_array, str):
        img = _imread_unicode(img_path_or_array)
    else:
        img = img_path_or_array
    return _align_and_preprocess(img, size)


def extract_features_from_folder(folder_path: str) -> List[float]:
    """Carrega todas as imagens de um diretório, aplica pré-processamento (CLAHE)
    e retorna vetores L2-normalizados por imagem.

    Args:
        folder_path: diretório com imagens (ex: data/images_to_register/<user>/...)

    Returns:
        lista de vetores (cada vetor é uma lista de floats). Retorna [] se nenhuma imagem.
    """
    if not os.path.exists(folder_path):
        return []
    vecs = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                p = os.path.join(root, f)
                img = _imread_unicode(p)
                if img is None:
                    # não conseguiu ler essa imagem; pula
                    continue
                # original
                v = _image_to_vector(img)
                if v is not None:
                    vecs.append(v)
                # augmentations: flip
                vflip = _image_to_vector(cv2.flip(img, 1))
                if vflip is not None:
                    vecs.append(vflip)
                # small rotations and brightness variants
                for angle in (-6, 6):
                    rimg = _rotate_image(img, angle)
                    vr = _image_to_vector(rimg)
                    if vr is not None:
                        vecs.append(vr)
                for alpha in (0.9, 1.1):
                    # alterar brilho multiplicando em RGB e clip
                    bimg = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
                    vb = _image_to_vector(bimg)
                    if vb is not None:
                        vecs.append(vb)

    if not vecs:
        return []

    # Retorna todos os vetores. O matcher fará a comparação
    # com cada amostra individualmente para reduzir falsos positivos.
    return [v.tolist() for v in vecs]


def extract_feature_from_image(image_np: np.ndarray):
    """Extrai um vetor de features de uma única imagem.
    Aplica o mesmo pré-processamento que `extract_features_from_folder`.

    Args:
        image_np: A imagem como um array NumPy (BGR).

    Returns:
        lista de floats (vetor de features) se a imagem for válida e passar nas verificações, caso contrário, lista vazia.
    """
    if image_np is None or image_np.size == 0:
        return []

    # 1. Verificação de Qualidade da Imagem
    quality_ok, quality_message = is_image_quality_sufficient(image_np)
    if not quality_ok:
        print(f"[Feature Extractor] Qualidade da imagem insuficiente: {quality_message}")
        return []


    # Se todas as verificações passarem, extrair as features
    v = _image_to_vector(image_np)
    if v is None:
        return []
    return v.tolist()
