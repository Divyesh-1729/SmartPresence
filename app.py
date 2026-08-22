
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import numpy as np
if not hasattr(np, 'long'):
    np.long = int
if not hasattr(np, 'ulong'):
    np.ulong = int

import streamlit as st



from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.home_screen import home_screen
from src.screens.components.header import header_home
from src.screens.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(page_title='SmartPresence', page_icon='🙌')
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()

    join_code = st.query_params.get('join_code')
    if join_code:
        if st.session_state.login_type!='student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') =='student':
            auto_enroll_dialog(join_code)
        


main()