import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.footer import footer_dashboard
from src.screens.components.header import header_dashboard, header_dashboard
from src.screens.database.db import check_teacher_exsits, create_teacher, teacher_login, get_teacher_subjects
from src.screens.components.dialog_create_subject import create_subject_dialog
from src.screens.components.subject_card import subject_card
from src.screens.components.dialog_share_subject import share_subject_dialog
from src.screens.components.dialog_add_photos import add_photos_dialog
from src.screens.pipelines.face_pipeline import predict_attendance
import numpy as np
from src.screens.database.config import supabase
from datetime import datetime
import pandas as pd
from src.screens.components.dialog_attendance_results import attendance_result_dialogue
from src.screens.components.dialog_voice_attendance import voice_attendance_dialog
from src.screens.database.db import get_attendance_for_teacher

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
    c1,c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}!", text_alignment="center")
        if st.button("Logout", type="secondary", key='loginbackbtn',shortcut="ctrl+h"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"
    tab1,tab2,tab3 = st.columns(3)

    with tab1:
        type1= "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("Take attendance", type=type1, width="stretch"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width="stretch"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance records", type=type3, width="stretch"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()



    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    st.header("Take Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("No subjects found. Please create a new subject.", icon="⚠️")
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1],vertical_alignment="bottom")
    with col1:
        selected_subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
    with col2:
        if st.button("Add photos 📸", type="primary", width="stretch"):
            add_photos_dialog()
    
    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header("Added the photos")
        gallery_cols = st.columns(4)

        for idx,img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width = 'stretch', use_column_width=True)
    has_photos = bool(st.session_state.attendance_images)
    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button('Clear Photos', type="tertiary", width="stretch", disabled=not has_photos, icon="🗑️"):
            st.session_state.attendance_images = []
            st.rerun()
    
    with c2:
        
        if st.button('Run Face Analysis', type="primary", width="stretch", disabled=not has_photos):
          with st.spinner("Deep scanning the photos of classroom.."):
            all_detected_id = {}

            for idx,img in enumerate(st.session_state.attendance_images):
                img_np = np.array(img.convert('RGB'))

                detected,_,_ = predict_attendance(img_np)

                if detected:
                    for sid in detected.keys():
                        student_id = int(sid)

                        all_detected_id.setdefault(student_id,[]).append(f"Photo {idx + 1}")

                    enrolled_res= supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                    enrolled_students = enrolled_res.data

                    if not enrolled_students:
                        st.warning("No students enrolled in this subject. Please enroll students first.", icon="⚠️")
                    else:
                        results, attendance_to_log =[],[]

                        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        for node in enrolled_students:
                            student = node['students']
                            sources = all_detected_id.get(int(student['student_id']), [])
                            is_present = len(sources) > 0
                            results.append({
                                "Name":student['name'],
                                "ID":student['student_id'],
                                "Source":".".join(sources) if is_present else "-",
                                "Status":"Present✅" if is_present else "❌Absent"

                            })

                            attendance_to_log.append({
                                "student_id": student['student_id'],
                                "subject_id": selected_subject_id,
                                "timestamp": current_timestamp,
                                "is_present": is_present
                            })  ##DB operation insertion


                    attendance_result_dialogue(pd.DataFrame(results), attendance_to_log)
            
    with c3:
        if st.button("Use voice attendance",type="primary",icon="🎤"):
            voice_attendance_dialog(selected_subject_id)







                        







def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1,col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects", width="stretch")
    with col2:
        if st.button("Create new subject", width="content"):
            create_subject_dialog(teacher_id)

    ##Listing all subjects
    subjects=get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥","Students",sub['total_students']),
                ("📅","Classes",sub['total_classes'])
            ]

        def share_btn():
            if st.button(f"Share Code: {sub['subject_code']}", key=f"share_{sub['subject_code']}", type="secondary", use_container_width=True, on_click=lambda: st.toast(f"Share link for {sub['subject_code']} copied to clipboard!", icon="✅")):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name=sub['name'],
            section=sub['section'],
            code=sub['subject_code'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("No subjects found. Please create a new subject.", icon="⚠️")



    

def teacher_tab_attendance_records():
    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return
    
    data =[]

    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group":ts.split(".")[0] if ts else "",
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "NA",
            "Subject":r['subjects']['name'],
            "Subject_Code":r['subjects']['subject_code'],
            "is_present":bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)

    summary = (df.groupby(['ts_group','Time','Subject','Subject_Code']).agg(
        Present_Count=('is_present', 'sum'),
        Total_Count=('is_present', 'count')
    ).reset_index()

    )


    
    summary['Attendance_Stats'] = ( "✅" + summary['Present_Count'].astype(str) + " / " + "👥" + summary['Total_Count'].astype(str))

    display_df= (summary.sort_values(by='ts_group', ascending=False)
                 [["Time","Subject","Subject_Code","Attendance_Stats"]])
    
    st.dataframe(display_df, width="stretch", hide_index=True)

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