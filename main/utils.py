import face_recognition as fr
import numpy as np
from profiles.models import Employe
import json
import os
from django.core.cache import cache

cache.clear()
CACHE_PATH = "encoded_faces.json"

def save_encoded_faces(encoded_faces):
    with open(CACHE_PATH, 'w') as f:
        json.dump(encoded_faces, f)

def load_encoded_faces():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)
    return None

def get_encoded_faces():
    encoded = load_encoded_faces()
    if encoded is not None:
        return encoded

    encoded = {}
    for employe in Employe.objects.all():
        try:
            face = fr.load_image_file(employe.photo.path)
            face_encodings = fr.face_encodings(face)
            if face_encodings:
                encoded[employe.user.username] = face_encodings[0].tolist()
            else:
                print(f"No face found for {employe.user.username}")
        except Exception as e:
            print(f"Error processing {employe.user.username}'s image: {e}")

    save_encoded_faces(encoded)
    return encoded

def get_cached_encoded_faces():
    encoded_faces = cache.get("encoded_faces")
    if encoded_faces is None:
        encoded_faces = {}
        for employe in Employe.objects.all():
            try:
                face_image = fr.load_image_file(employe.photo.path)
                encodings = fr.face_encodings(face_image)
                if encodings:
                    encoded_faces[employe.user.username] = encodings[0].tolist()
            except Exception as e:
                print(f"Error encoding {employe.user.username}: {e}")
        cache.set("encoded_faces", encoded_faces, timeout=86400)
    return {name: np.array(enc) for name, enc in encoded_faces.items()}

FACE_MATCH_THRESHOLD = 0.45  # Seuil plus strict pour réduire les erreurs

def classify_face(img_path):
    faces = get_cached_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    try:
        img = fr.load_image_file(img_path)
        face_locations = fr.face_locations(img)

        if len(face_locations) != 1:
            print("Either no face or multiple faces detected, rejecting recognition.")
            return "Unknown"

        unknown_face_encodings = fr.face_encodings(img, face_locations)

        for face_encoding in unknown_face_encodings:
            distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(distances)
            if distances[best_match_index] < FACE_MATCH_THRESHOLD:
                return known_face_names[best_match_index]
            else:
                print("No match found.")
        return "Unknown"
    except Exception as e:
        print(f"Error during face classification: {e}")
        return "Unknown"
