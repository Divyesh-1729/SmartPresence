import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.footer import footer_dashboard
from src.screens.components.header import header_dashboard, header_dashboard
from PIL import Image
import numpy as np


def student_screen():
    style_background_dashboard()
    style_base_layout()
    c1,c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", type="secondary", key='studentloginbackbtn',shortcut="ctrl+h"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using faceID", text_alignment="center")
    st.space()
    st.space()
  
    photo_source = st.camera_input("Position your face in the centre")
    if photo_source:
        np.array(Image.open(photo_source))
    footer_dashboard()
    