import streamlit as st
from src.screens.components.header import header_home
from src.screens.components.footer import footer_home
from src.screens.ui.base_layout import style_base_layout, style_background_home
def home_screen():
    
    header_home()
    style_background_home()

    style_base_layout()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("I am Teacher")
        st.image("https://tse3.mm.bing.net/th/id/OIP.wkH8izDlFhMXb9D2c8rnQgHaHa?pid=Api&P=0&h=180", width=120)
        if st.button("Teacher portal", use_container_width=True, type="primary"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    with col2:
        st.header("I am Student")
        st.image("https://tse4.mm.bing.net/th/id/OIP.vas46v9gvknp29E2AZItagHaHa?pid=Api&P=0&h=180", width=120)
        if st.button("Student portal", use_container_width=True, type="primary"):
            st.session_state['login_type'] = 'student'
            st.rerun()
    footer_home()

    