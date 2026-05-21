import streamlit as st


def header_home():

    logo_url = "https://tse4.mm.bing.net/th/id/OIP.nRkNUDYhVXBKIAyf9McgEgHaHa?pid=Api&P=0&h=180"
    st.markdown(
        f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 30px; margin-top: 30px;'>
        <img src='{logo_url}' style='width: 100px; height: 100px; border-radius: 20%; border: 2px solid #000000; margin-bottom: 20px; object-fit: cover;' />
        <h1 style='text-align: center; color: #E0E3FF; margin: 0;'>SMART PRESENCE</h1>
        </div>
        """, unsafe_allow_html=True
    )