import streamlit as st
from src.screens.database.db import create_subject

@st.dialog("Create new subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details for the new subject:")
    sub_id = st.text_input("Subject ID", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")


    if st.button("Create Subject Now", type="primary", width="stretch"):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject created successfully!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating subject: {e}")
        else:
            st.warning("Please fill in all the fields before creating the subject.")
            