import streamlit as st
from service_history import get_service_summary
from database import get_user_applications

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

user_id = st.session_state.get('user_id')

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
    .applied-badge { background: #dbeafe; color: #1e40af; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .direct-badge { background: #fce7f3; color: #be185d; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .active-badge { background: #d1fae5; color: #065f46; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .completed-badge { background: #e5e7eb; color: #374151; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border-radius: 18px !important;
        box-shadow: 0 4px 18px rgba(76, 29, 149, 0.07) !important;
        border: 1px solid rgba(226, 220, 248, 0.7) !important;
        padding: 20px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 100%; display: flex; flex-direction: column;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(91, 33, 182, 0.16) !important;
        border-color: #a855f7 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📜 Service History</h1>
    <p>View your current and past committee memberships</p>
</div>
""", unsafe_allow_html=True)

# ==================== SERVICE HISTORY FROM ROSTER ====================
summary = get_service_summary(user_id)

if summary['total'] == 0:
    st.info("No service history found. Committees you are accepted to will appear here.")
else:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Committees", summary['total'])
    with col2: st.metric("Active", summary['active'])
    with col3: st.metric("Completed", summary['completed'])
    with col4: st.metric("Current Hours/Week", summary['current_hours'])

    st.divider()

    # Active committees
    active_records = [r for r in summary['records'] if r['status'] == 'Active']
    if active_records:
        st.subheader("🟢 Active Committees")
        for record in active_records:
            assignment_badge = '<span class="applied-badge">Applied</span>' if record['assignment_type'] == 'Applied' else '<span class="direct-badge">Direct Assignment</span>'
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{record['committee_name']}** {assignment_badge}")
                    st.caption(f"Role: {record['role_in_committee']} | Level: {record['level']}")
                    st.caption(f"Joined: {record['join_date'][:10] if record['join_date'] else 'N/A'}")
                with col2:
                    st.markdown('<span class="active-badge">Active</span>', unsafe_allow_html=True)
                    st.caption(f"Hours: {record['hours_per_week']}h/week")
                    st.caption(f"Duration: {record['duration_months']} months")

    # Completed committees
    completed_records = [r for r in summary['records'] if r['status'] == 'Completed']
    if completed_records:
        st.subheader("✅ Completed Committees")
        for record in completed_records:
            assignment_badge = '<span class="applied-badge">Applied</span>' if record['assignment_type'] == 'Applied' else '<span class="direct-badge">Direct Assignment</span>'
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{record['committee_name']}** {assignment_badge}")
                    st.caption(f"Role: {record['role_in_committee']} | Level: {record['level']}")
                    st.caption(f"Joined: {record['join_date'][:10] if record['join_date'] else 'N/A'} | Ended: {record['end_date'][:10] if record['end_date'] else 'N/A'}")
                with col2:
                    st.markdown('<span class="completed-badge">Completed</span>', unsafe_allow_html=True)
                    st.caption(f"Hours: {record['hours_per_week']}h/week")
                    st.caption(f"Duration: {record['duration_months']} months")

    # Removed committees
    removed_records = [r for r in summary['records'] if r['status'] == 'Removed']
    if removed_records:
        st.subheader("❌ Removed from Committee")
        for record in removed_records:
            with st.container(border=True):
                st.write(f"**{record['committee_name']}**")
                st.caption(f"Role: {record['role_in_committee']} | Removed on: {record['end_date'][:10] if record['end_date'] else 'N/A'}")
                if record.get('removal_reason'):
                    st.caption(f"Reason: {record['removal_reason']}")