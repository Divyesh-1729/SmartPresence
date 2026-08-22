import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.footer import footer_dashboard
from src.screens.components.header import header_dashboard
from PIL import Image
import numpy as np
from src.screens.pipelines.voice_pipeline import get_voice_embedding
from src.screens.pipelines.face_pipeline import predict_attendance, get_face_embedding, train_classifier
from src.screens.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_from_subject
import time
from src.screens.components.subject_card import subject_card
from src.screens.components.dialog_enroll import enroll_dialog


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}!", text_alignment="center")
        if st.button("Logout", type="secondary", key='student_logout_btn', shortcut="ctrl+h"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        st.header("Your Enrolled subjects")
    with c2:
        if st.button("Enroll in new subject", type="primary", use_container_width=True):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading the enrolled subjects"):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log.get('subject_id')
        if sid is None:
            sid = log.get('subjects', {}).get('subject_id') if isinstance(log.get('subjects'), dict) else None

        if sid is None:
            continue

        if sid not in stats_map:
            stats_map[sid] = {
                'total': 0,
                'attended': 0
            }

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.info("You are not enrolled in any subjects yet. Click 'Enroll in new subject' above to join a class!")
    else:
        cols = st.columns(2)
        for i, sub_mode in enumerate(subjects):
            sub = sub_mode.get('subjects') if isinstance(sub_mode, dict) else None
            if not sub:
                continue

            sid = sub.get('subject_id') or sub.get('id') or sub.get('subject_code')

            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            
            def unenroll_button(s_id=sid, s_sub=sub):
                if st.button("Unenroll from this course", type='tertiary', use_container_width=True, icon="🗑️", key=f"unenroll_{s_id}"):
                    unenroll_student_from_subject(student_id, s_id)
                    st.toast(f"Successfully unenrolled from {s_sub['name']}.", icon="✅")
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub.get('subject_code', ''),
                    section=sub.get('section', ''),
                    stats=[
                        ('🗓️', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended'])
                    ],
                    footer_callback=unenroll_button
                )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", type="secondary", key='studentloginbackbtn', shortcut="ctrl+h"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using faceID", text_alignment="center")
    st.write("")

    show_registeration = False
  
    photo_source = st.camera_input("Position your face in the centre")
    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI is Scanning..."):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("No face detected. Please try again.")

            elif num_faces > 1:
                st.warning("Multiple faces detected. Please ensure only your face is visible and try again.")
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if str(s.get('student_id') or s.get('id')) == str(student_id)), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = "student"
                        st.session_state.student_data = student
                        st.toast(f"Welcome, {student['name']}!")
                        time.sleep(1)
                        st.rerun()

                else:
                    st.info("Face not recognized. Please register below or try scanning again.")
                    show_registeration = True

    if show_registeration:
        with st.container(border=True):
            st.header("Register new profile")
            new_name = st.text_input("Enter your name")

            st.subheader("Optional: Voice enrollment")
            st.info("Enroll for voice only attendance:")

            audio_data = None

            try:
                audio_data = st.audio_input("Record your voice using a short phrase")
            except Exception as e:
                st.error(f"Audio input error: {e}")

            if st.button("Create account", type="primary"):
                if not new_name.strip():
                    st.error("Please enter your name.")
                else:
                    with st.spinner("Creating your account..."):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embedding(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            
                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = "student"
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Hi {new_name}, your account has been created successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to create student account in database.")
                        else:
                            st.error("Could not capture facial features for recognition. Please retake photo.")

    footer_dashboard()

    