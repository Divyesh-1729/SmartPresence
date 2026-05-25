from src.screens.database.db import create_teacher
import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.footer import footer_dashboard
from src.screens.components.header import header_dashboard, header_dashboard
from src.screens.database.db import check_teacher_exsits, create_teacher,teacher_login 

def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == 'login':
        teacher_screen_login()
    elif st.session_state.teacher_login_type == 'register':
        teacher_screen_register()
    

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    st.header(f"Welcome, {teacher_data['name']}!", text_alignment="center")

def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
    return False




def teacher_screen_login():
    c1,c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type="secondary", key='loginbackbtn',shortcut="ctrl+h"):
            st.session_state['login_type'] = None
            st.rerun()
    
    st.header("Please login to your account", text_alignment="center")
    st.space()
    teacher_username = st.text_input("Enter Username", placeholder="vaidehi parshurami")
    teacher_pass = st.text_input("Enter Password", placeholder="Enter password", type="password")
    st.divider()

    btnc1,btnc2 = st.columns(2, gap="large")
    with btnc1:
        if st.button("🔐 Login", shortcut = "ctrl+enter", use_container_width=True):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Login successful", icon="✅")
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'
                st.rerun()
            else:
                st.error("Invalid username or password", icon="❌")
    with btnc2:
        if st.button("📝 Register Instead", type="primary", shortcut = "ctrl+enter", use_container_width=True):
            st.session_state.teacher_login_type = 'register'
            st.rerun()
    footer_dashboard()

def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "Please fill all the fields"
    
    if check_teacher_exsits(teacher_username):
        return False, "Teacher with this username already exists"
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Teacher profile created successfully"
    except Exception as e:
        print(f"Error creating teacher: {str(e)}")
        return False, f"An error occurred: {str(e)}"
    

def teacher_screen_register():
    c1,c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type="secondary", key='loginbackbtn',shortcut="ctrl+h"):
            st.session_state['login_type'] = None
            st.rerun()


    st.header("Register your teacher profile")

    st.space()
    st.space()

    teacher_username = st.text_input("Enter Username", placeholder="vaidehi_parshurami")
    teacher_name = st.text_input("Enter Name", placeholder="Vaidehi Parshurami")
    teacher_pass = st.text_input("Enter Password", placeholder="Enter password", type="password")
    teacher_pass_confirm = st.text_input("Confirm Password", placeholder="Confirm password", type="password")
    st.divider()

    btnc1,btnc2 = st.columns(2, gap="large")
    with btnc2:
        if st.button("📝 Register now", type="primary", shortcut = "ctrl+enter", use_container_width=True):
            # Handle registration logic here
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'
                st.rerun()
            else:
                st.error(message)
    with btnc1:
        if st.button("🔐 Login Instead", shortcut = "ctrl+enter", use_container_width=True):
            if teacher_login(teacher_username, teacher_pass):
                st.toast("Login successful", icon="✅")
                import time
                time.sleep(2)
                st.rerun()

            else:
                st.error("Invalid username or password", icon="❌")
                

            st.session_state.teacher_login_type = 'login'
            st.rerun()
    
    footer_dashboard()