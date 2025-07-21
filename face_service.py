import os

from dotenv import load_dotenv

load_dotenv()

from deepface import DeepFace

DEEPFACE_MODEL = os.getenv("DEEPFACE_MODEL", "VGG-Face")
DEEPFACE_DETECTOR_BACKEND = os.getenv("DEEPFACE_DETECTOR_BACKEND", "fastmtcnn")
DEEPFACE_DISTANCE_METRIC = os.getenv("DEEPFACE_DISTANCE_METRIC", "cosine")


def verify_faces(
    img1_path: str,
    img2_path: str,
    model_name: str = DEEPFACE_MODEL,
    detector_backend: str = DEEPFACE_DETECTOR_BACKEND,
    distance_metric: str = DEEPFACE_DISTANCE_METRIC,
    enforce_detection: bool = True,
    anti_spoofing: bool = False,
):
    result = DeepFace.verify(
        img1_path=img1_path,
        img2_path=img2_path,
        model_name=model_name,
        detector_backend=detector_backend,
        distance_metric=distance_metric,
        enforce_detection=enforce_detection,
        anti_spoofing=anti_spoofing,
    )

    return result


def recognize_faces(
    img_path: str,
    db_path: str,
    model_name: str = DEEPFACE_MODEL,
    detector_backend: str = DEEPFACE_DETECTOR_BACKEND,
    distance_metric: str = DEEPFACE_DISTANCE_METRIC,
    enforce_detection: bool = True,
    anti_spoofing: bool = False,
):
    result = DeepFace.find(
        img_path=img_path,
        db_path=db_path,
        model_name=model_name,
        detector_backend=detector_backend,
        distance_metric=distance_metric,
        enforce_detection=enforce_detection,
        anti_spoofing=anti_spoofing,
    )

    return result
