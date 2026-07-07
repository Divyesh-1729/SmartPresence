import streamlit as st

def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
    <div style="background:white;border-left:8px solid #EB459E;border-radius:20px;padding:25px;margin-bottom:20px;">
    <h3 style="margin: 0; color: #1e293b; font-size:1.3rem">{name}</h3>
    <p style="margin:10px 0; color: #64748b;">
        Code:
        <span style="border-radius:4px; background:#E0E3FF; font-weight:bold; color:#5865F2; padding:2px 8px;">{code}</span>
        |
        Section:
        <span style="border-radius:4px; background:#E0E3FF; font-weight:bold; color:#5865F2; padding:2px 8px;">{section}</span>
    </p>
    """

    if stats:
        html += """
        <div style="display:flex; gap:20px; flex-wrap:wrap; margin-top:10px;">
        """

        for icon, label, value in stats:
            html += f"""
            <div style="background:#EB459E10; padding:5px 12px; border-radius:12px; font-size:0.9rem;">
                {icon} <b>{label}: {value}</b>
            </div>
            """

        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()