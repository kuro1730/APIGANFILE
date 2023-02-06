import os
import sys
import bz2
from PIL import Image
import io
sys.path.append('utils')
import webFunction as web
from gan.interfacegan.face_align.ffhq_dataset.face_alignment import image_align
from gan.interfacegan.face_align.ffhq_dataset.landmarks_detector import LandmarksDetector

LANDMARKS_MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'


def unpack_bz2(src_path):
    data = bz2.BZ2File(src_path).read()
    dst_path = src_path[:-4]
    with open(dst_path, 'wb') as fp:
        fp.write(data)
    return dst_path


def align_image(IMAGE):
    """
    Extracts and aligns all faces from images using DLib and a function from original FFHQ dataset preparation step
    python align_images.py /raw_images /aligned_images
    """
    
    RAW_IMAGES_DIR = '/content/interfacegan/img/test_out.png'
    try: Image.open(IMAGE).save(RAW_IMAGES_DIR, format='PNG')
    except: IMAGE.save(RAW_IMAGES_DIR, format='PNG')
    IMAGE = Image.open(RAW_IMAGES_DIR)

    landmarks_model_path = unpack_bz2('/content/interfacegan/models/shape_predictor_68_face_landmarks.dat.bz2')

    landmarks_detector = LandmarksDetector(landmarks_model_path)

    for i, face_landmarks in enumerate(landmarks_detector.get_landmarks(RAW_IMAGES_DIR), start=1):
            ori = image_align(IMAGE, face_landmarks)
            new = web.image_to_buffer(image_align(IMAGE, face_landmarks))
            return ori, new 