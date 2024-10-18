import face_recognition as fr
import numpy as np
from profiles.models import Employe


def get_encoded_faces():
    """
    This function loads all user profile images and encodes their faces
    """
    # Retrieve all employee profiles from the database
    qs = Employe.objects.all()

    # Create a dictionary to hold the encoded face for each employee
    encoded = {}

    for p in qs:
        try:
            # Load the user's profile image
            face = fr.load_image_file(p.photo.path)

            # Encode the face (if detected)
            face_encodings = fr.face_encodings(face)

            if len(face_encodings) > 0:
                encoding = face_encodings[0]
                # Add the user's encoded face to the dictionary
                encoded[p.user.username] = encoding
            else:
                print(f"No face found in the image for {p.user.username}")

        except Exception as e:
            # Log any error that occurs while encoding the image
            print(f"Error processing {p.user.username}'s image: {e}")

    # Return the dictionary of encoded faces
    return encoded

def classify_face(img):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    try:
        # Load all the known faces and their encodings
        faces = get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())

        # Load the input image
        img = fr.load_image_file(img)

        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        # Initialize a list to hold identified face names
        face_names = []

        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, label the face with the known name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        # Return the name of the first face in the input image (or None if no faces found)
        if face_names:
            return face_names[0]
        else:
            return "Unknown"

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error during face classification: {e}")
        return False
