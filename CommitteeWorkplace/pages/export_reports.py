import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_all_committees, get_all_users, get_user_applications, get_committee_applications
from export_engine import export_committees, export_users, export_audit_logs, generate_filename

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

if st.session_state.get('user_role') == 'Faculty':
    st.error("Access denied. Management roles only.")
    st.stop()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', 'Inter', sans-serif !important; }
    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(124, 58, 237, 0.10) 0%, transparent 38%),
            radial-gradient(circle at 92% 8%, rgba(217, 70, 239, 0.09) 0%, transparent 42%),
            radial-gradient(circle at 50% 105%, rgba(245, 158, 11, 0.07) 0%, transparent 50%),
            linear-gradient(135deg, #f8f7ff 0%, #f1edfb 45%, #eef1ff 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #150d2e 0%, #2a1654 50%, #3b1d6b 100%);
        padding: 2.2rem 2rem; border-radius: 22px; color: white;
        margin-bottom: 2rem; text-align: center;
        box-shadow: 0 16px 48px rgba(45, 16, 92, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .main-header h1 { margin: 0; font-size: 2.3rem; font-weight: 800; color: #fbbf24 !important; }
    .main-header p { margin: 6px 0 0 0; opacity: 0.85; font-size: 1.05rem; color: #d8d4ec; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📤 Export Reports</h1>
    <p>Export data for offline analysis</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Committees", "👥 Users", "📜 Applications", "📊 Audit Logs"])

# ==================== TAB 1: COMMITTEES ====================
with tab1:
    st.subheader("Export Committees")

    committees = get_all_committees()
    df = pd.DataFrame(committees)

    if not df.empty:
        # Add composition info
        from database import get_committee_composition
        for idx, row in df.iterrows():
            comp = get_committee_composition(row['id'])
            comp_str = ", ".join([f"{c['rank_required']}: {c['filled_slots']}/{c['total_slots']}" for c in comp])
            df.at[idx, 'composition'] = comp_str

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Committees CSV",
            data=csv,
            file_name=generate_filename("committees"),
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No committees to export.")

# ==================== TAB 2: USERS ====================
with tab2:
    st.subheader("Export Users")

    df = export_users()

    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Users CSV",
            data=csv,
            file_name=generate_filename("users"),
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No users to export.")

# ==================== TAB 3: APPLICATIONS ====================
with tab3:
    st.subheader("Export Applications")

    # Get all applications across all committees
    all_apps = []
    committees = get_all_committees()
    for c in committees:
        apps = get_committee_applications(c['id'])
        for app in apps:
            app['committee_name'] = c['name']
            app['committee_level'] = c['level']
            all_apps.append(app)

    df = pd.DataFrame(all_apps)

    if not df.empty:
        # Select relevant columns
        display_cols = ['name', 'email', 'rank', 'department', 'school', 'committee_name', 'committee_level', 'status', 'applied_date', 'updated_date', 'rejection_reason']
        available_cols = [c for c in display_cols if c in df.columns]
        df_display = df[available_cols]

        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Applications CSV",
            data=csv,
            file_name=generate_filename("applications"),
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No applications to export.")

# ==================== TAB 4: AUDIT LOGS ====================
with tab4:
    st.subheader("Export Audit Logs")

    df = export_audit_logs(limit=1000)

    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Audit Logs CSV",
            data=csv,
            file_name=generate_filename("audit_logs"),
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No audit logs to export.")