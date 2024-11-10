from celery import shared_task
from .utils import classify_face

@shared_task
def classify_face_async(img_path):
    return classify_face(img_path)
