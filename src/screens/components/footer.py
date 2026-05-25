import streamlit as st


def footer_home():
 
    st.markdown(
        f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 32px;'>
        <p style="font-weight: bold; color:white">Created with ❤️ by Divyesh Puranik</p>
        </div>
        """, unsafe_allow_html=True
    )

def footer_dashboard():
 
    st.markdown(
        f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 32px;'>
        <p style="font-weight: bold; color:black">Created with ❤️ by Divyesh Puranik</p>
        </div>
        """, unsafe_allow_html=True
    )