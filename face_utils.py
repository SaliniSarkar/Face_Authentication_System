import numpy as np
import face_recognition

from config import FACE_ENCODING_SIZE, FACE_MATCH_TOLERANCE


def load_rgb_array(image):
    image_array = np.asarray(image)

    if image_array.ndim != 3:
        raise ValueError("Image must be a color image.")

    if image_array.shape[2] == 4:
        image_array = image_array[:, :, :3]

    if image_array.shape[2] == 1:
        image_array = np.repeat(image_array, 3, axis=2)

    if image_array.dtype != np.uint8:
        image_array = image_array.astype(np.uint8)

    return image_array


def create_face_encoding(image):
    """
    Returns:
      np.ndarray for exactly one face
      None when no face is found
      'multiple' when more than one face is found
    """
    rgb_image = load_rgb_array(image)

    locations = face_recognition.face_locations(
        rgb_image,
        model="hog",
    )

    if len(locations) == 0:
        return None

    if len(locations) > 1:
        return "multiple"

    encodings = face_recognition.face_encodings(
        rgb_image,
        known_face_locations=locations,
        num_jitters=1,
    )

    if not encodings:
        return None

    encoding = np.asarray(
        encodings[0],
        dtype=np.float64,
    )

    if encoding.shape != (FACE_ENCODING_SIZE,):
        raise ValueError("Unexpected face encoding size.")

    return encoding


def decode_encoding(blob):
    if blob is None:
        return None

    try:
        encoding = np.frombuffer(
            blob,
            dtype=np.float64,
        ).copy()
    except (TypeError, ValueError):
        return None

    if encoding.shape != (FACE_ENCODING_SIZE,):
        return None

    return encoding


def find_duplicate_face(new_encoding, users, tolerance=None):
    if tolerance is None:
        tolerance = FACE_MATCH_TOLERANCE

    if new_encoding is None or isinstance(new_encoding, str):
        return None

    for user in users:
        stored_encoding = decode_encoding(user[4])

        if stored_encoding is None:
            continue

        distance = float(
            face_recognition.face_distance(
                [stored_encoding],
                new_encoding,
            )[0]
        )

        if distance <= tolerance:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "employee_id": user[3],
                "distance": distance,
            }

    return None


def recognize_face(image, users, tolerance=None):
    if tolerance is None:
        tolerance = FACE_MATCH_TOLERANCE

    current_encoding = create_face_encoding(image)

    # No face detected
    if current_encoding is None:
        return None

    # Multiple faces detected
    if isinstance(current_encoding, str) and current_encoding == "multiple":
        return "multiple"

    best_match = None
    best_distance = float("inf")

    for user in users:
        stored_encoding = decode_encoding(user[4])

        if stored_encoding is None:
            continue

        distance = float(
            face_recognition.face_distance(
                [stored_encoding],
                current_encoding,
            )[0]
        )

        if distance < best_distance:
            best_distance = distance

            best_match = {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "employee_id": user[3],
                "distance": distance,
            }

    # Face matched within tolerance
    if best_match is not None and best_distance <= tolerance:
        return best_match

    # No sufficiently close face
    return None
