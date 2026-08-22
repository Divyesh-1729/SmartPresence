import streamlit as st
from PIL import Image

@st.dialog("Capture or Upload Photos")
def add_photos_dialog():
    try:
        st.write("Add classroom photos to scan for attendance:")

        if 'photo_tab' not in st.session_state:
            st.session_state.photo_tab = 'camera'

        t1, t2 = st.columns(2)

        with t1:
            type_camera = "primary" if st.session_state.photo_tab == 'camera' else "tertiary"
            if st.button("Camera", type=type_camera, use_container_width=True):
                st.session_state.photo_tab = 'camera'
                st.rerun()

        with t2:
            type_upload = "primary" if st.session_state.photo_tab == 'upload' else "tertiary"
            if st.button("Upload", type=type_upload, use_container_width=True):
                st.session_state.photo_tab = 'upload'
                st.rerun()

        if st.session_state.photo_tab == 'camera':
            cam_photo = st.camera_input("Take a photo", key='dialog_cam')
            if cam_photo:
                st.session_state.attendance_images.append(Image.open(cam_photo))
                st.toast("Photo added successfully!", icon="✅")
                st.rerun()

        if st.session_state.photo_tab == 'upload':
            uploaded_files = st.file_uploader("Upload photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key='dialog_upload')

            if uploaded_files:
                count = 0
                for f in uploaded_files:
                    img = Image.open(f)
                    if img not in st.session_state.attendance_images:
                        st.session_state.attendance_images.append(img)
                        count += 1

                if count > 0:
                    st.toast(f"{count} photo(s) added successfully!", icon="✅")

                st.divider()
                if st.button('Done', type="primary", use_container_width=True):
                    st.rerun()
    except Exception as _e:
        import traceback
        st.error(f"Dialog error: {_e}")
        st.text(traceback.format_exc())

