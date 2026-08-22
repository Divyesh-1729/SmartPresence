import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from src.screens.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
    facerec = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
    return detector, sp, facerec


def get_face_embedding(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)
    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)  # 128 embedding for each face
        encodings.append(np.array(face_descriptor))
    return encodings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None
    
    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    unique_classes = set(y)
    if len(unique_classes) < 2:
        return {'clf': None, 'X': X, 'y': y}

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')
    try:
        clf.fit(X, y)
    except ValueError:
        return {'clf': None, 'X': X, 'y': y}

    return {'clf': clf, 'X': X, 'y': y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    encodings = get_face_embedding(class_image_np)

    detected_student = {}
    model_data = get_trained_model()

    if not model_data or not isinstance(model_data, dict):
        return detected_student, [], len(encodings)

    clf = model_data.get('clf')
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))
    resemblance_threshold = 0.6

    for encoding in encodings:
        if clf is not None and len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
            student_embedding = X_train[y_train.index(predicted_id)]
            best_match_score = np.linalg.norm(student_embedding - encoding)
            if best_match_score <= resemblance_threshold:
                detected_student[predicted_id] = True
        else:
            # Nearest neighbor fallback when SVM is not fitted (e.g. 1 student)
            distances = [np.linalg.norm(emb - encoding) for emb in X_train]
            if distances:
                min_idx = int(np.argmin(distances))
                if distances[min_idx] <= resemblance_threshold:
                    predicted_id = int(y_train[min_idx])
                    detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)

    

