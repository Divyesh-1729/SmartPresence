import streamlit as st
from src.screens.database.db import create_attendance
import pandas as pd


def show_attendance_results(df, logs):  ##Modularized
    try:
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button('Discard',width = 'stretch'):
                st.session_state.voice_attendance_results=None
                st.session_state.attendance_images = []
                st.rerun()

        with col2:
            if st.button('Confirm',type='primary',width = 'stretch'):
                try:
                    create_attendance(logs)
                    st.toast("Attendance recorded successfully!", icon="✅")
                    st.session_state.attendance_images = []
                    st.session_state.voice_attendance_results=None
                    st.rerun()
                except Exception as e:
                    st.error("Sync failed!")
    except Exception as _e:
        import traceback
        st.error(f"Dialog error: {_e}")
        st.text(traceback.format_exc())

@st.dialog("Attendance Results")
def attendance_result_dialogue(df,logs):
    show_attendance_results(df,logs)
    




        