import streamlit as st
import io
import segno

@st.dialog("Share subject")
def share_subject_dialog(subject_name,subject_code):
    app_domain= "smartpresence-india.streamlit.app"
    join_url = f"{app_domain}/?join-code={subject_code}"

    st.header("SScan to join")
    st.write(f"Share this link with your students: {join_url}")

    qr=segno.make(join_url)

    out= io.BytesIO()
    qr.save(out, kind='png', scale=10)

    col1,col2 = st.columns(2)

    with col1:
        st.markdown('###Copy link')
        st.code(join_url, language='text')
        st.code(subject_code, language='text')
        st.info("You can also share the subject code with your students to join the subject.")


    with col2:
        st.markdown('###Scan QR code')
        st.image(out.getvalue(), caption='Scan this QR code to join the subject', use_column_width=True)
        
