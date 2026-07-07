import streamlit as st
from src.screens.database.db import create_subject,enroll_student_to_subject
from src.screens.database.config import supabase
import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher:")
    join_code = st.text_input("Join Code", placeholder="Enter the join code here")

    st.button("Enroll Now", type="primary", width="stretch")
    if join_code:
        res= supabase.table('subjects').select('subject_id,name,subject_code').eq('subject_code', join_code).execute()
        if res.data:
            subject = res.data[0]
            student_id=st.session_state.student_data['student_id']

            check=supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
            if check.data:
                st.warning("You are already enrolled in this subject.")
            else:
                enroll_student_to_subject(student_id,subject['subject_id'])
                st.success(f"Successfully enrolled in {subject['name']}!")
                time.sleep(1)
                st.rerun()

    else:
        st.warning("Please enter a valid join code.")
        try:
            st.write("Enter the subject code provided by your teacher:")
            join_code = st.text_input("Join Code", placeholder="Enter the join code here")

            st.button("Enroll Now", type="primary", width="stretch")
            if join_code:
                res= supabase.table('subjects').select('subject_id,name,subject_code').eq('subject_code', join_code).execute()
                if res.data:
                    subject = res.data[0]
                    student_id=st.session_state.student_data['student_id']

                    check=supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                    if check.data:
                        st.warning("You are already enrolled in this subject.")
                    else:
                        enroll_student_to_subject(student_id,subject['subject_id'])
                        st.success(f"Successfully enrolled in {subject['name']}!")
                        time.sleep(1)
                        st.rerun()

            else:
                st.warning("Please enter a valid join code.")
        except Exception as _e:
            import traceback
            st.error(f"Dialog error: {_e}")
            st.text(traceback.format_exc())

   
            