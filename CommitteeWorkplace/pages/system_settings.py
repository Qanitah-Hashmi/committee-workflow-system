import streamlit as st

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', 'Inter', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(124, 58, 237, 0.10) 0%, transparent 38%),
            radial-gradient(circle at 92% 8%, rgba(217, 70, 239, 0.09) 0%, transparent 42%),
            radial-gradient(circle at 50% 105%, rgba(245, 158, 11, 0.07) 0%, transparent 50%),
            linear-gradient(135deg, #f8f7ff 0%, #f1edfb 45%, #eef1ff 100%);
    }

    .main-header {
        background: linear-gradient(135deg, #150d2e 0%, #2a1654 50%, #3b1d6b 100%);
        padding: 2.2rem 2rem;
        border-radius: 22px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 16px 48px rgba(45, 16, 92, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.07);
        position: relative;
        overflow: hidden;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.3rem;
        font-weight: 800;
        position: relative;
        color: #fbbf24 !important;
        font-family: 'Outfit', sans-serif !important;
        display: inline-block;
    }
    .main-header p {
        margin: 6px 0 0 0;
        opacity: 0.85;
        font-size: 1.05rem;
        color: #d8d4ec;
        position: relative;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚙️ System Settings</h1>
    <p>System configuration and administration</p>
</div>
""", unsafe_allow_html=True)

st.info("""
**System Admin Module**

The System Admin module is reserved for technical administrators who manage:
- User accounts
- Roles and permissions
- Schools and departments
- Academic ranks
- System configuration

This module is **not part of the current development scope**.
""")

st.markdown("### Current System Information")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Database:** committee_workplace.db")
    st.markdown("**Version:** 1.0.0")
with col2:
    st.markdown("**Last Updated:** July 2026")
    st.markdown("**Status:** Active")