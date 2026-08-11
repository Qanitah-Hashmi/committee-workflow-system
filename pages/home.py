import streamlit as st
from database import get_user_notifications, mark_notifications_read, clear_notifications

st.set_page_config(
    page_title="Committee Workplace",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== COMPLETELY HIDE SIDEBAR ====================
st.markdown("""
<style>
    /* Hide sidebar completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    /* Hide any navigation elements */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] ul {
        display: none !important;
    }
    section[data-testid="stSidebar"] nav {
        display: none !important;
    }
    .st-emotion-cache-1cyp4cz, .st-emotion-cache-16txtl3, .st-emotion-cache-1jicfl2,
    .st-emotion-cache-vk3wp9, .st-emotion-cache-1rtdygy, .st-emotion-cache-1v0mbdj {
        display: none !important;
    }
    /* Hide the sidebar toggle button */
    .st-emotion-cache-1wmy9hl {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Redirect to login if not authenticated
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

# ==================== GET USER INFO ====================
raw_role = st.session_state.get('user_role')
user_role = str(raw_role).strip() if raw_role is not None else ''
user_name = st.session_state.get('user_name', 'User')
user_id = st.session_state.get('user_id')

# Role validation
VALID_ROLES = ['Faculty', 'Department Coordinator', 'HOD', 'Dean', 'Registrar', 'Rector', 'President', 'System Admin']
if user_role not in VALID_ROLES:
    st.error(f"⚠️ Invalid or missing role: '{user_role}'. Please logout and login again.")
    if st.button("🚪 Logout and Return to Login", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("login.py")
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

    /* ---- Tighten overall page padding & vertical rhythm ---- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1500px !important;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
        gap: 0.6rem !important;
    }
    hr {
        margin: 1.4rem 0 !important;
    }

    /* ---- Compact buttons ---- */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.9rem 1.1rem !important;
        min-height: 3.4rem !important;
        line-height: 1.2 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        white-space: normal !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6d28d9, #9333ea) !important;
        color: white !important; box-shadow: 0 3px 10px rgba(109, 40, 217, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
        transform: translateY(-1px) !important; box-shadow: 0 5px 16px rgba(109, 40, 217, 0.45) !important;
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #1e1538, #2d1b54) !important;
        color: white !important; box-shadow: 0 3px 8px rgba(30, 21, 56, 0.3) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #2d1b54, #3f2470) !important;
        transform: translateY(-1px) !important; box-shadow: 0 5px 14px rgba(30, 21, 56, 0.4) !important;
    }

    /* Logout button styling */
    .logout-btn-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 0.3rem;
    }
    .logout-btn-container .stButton button {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        padding: 0.4rem 1.2rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        min-height: 2.1rem !important;
    }
    .logout-btn-container .stButton button:hover {
        background: rgba(239, 68, 68, 0.25) !important;
        border-color: #ef4444 !important;
        transform: translateY(-1px) !important;
    }

    /* Compact section heading + subtitle */
    .section-heading {
        font-size: 1.45rem;
        color: #1e1538;
        margin-bottom: 0.25rem;
        font-weight: 700;
    }
    .section-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== WELCOME SECTION WITH LOGOUT BUTTON ====================
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.markdown(f"""
    <div style="padding: 0.2rem 0 0.1rem 0;">
        <h1 style="font-size: 1.9rem; color: #1e1538; font-family: 'Outfit', sans-serif; margin-bottom: 0.2rem;">Welcome, {user_name}</h1>
        <p style="font-size: 0.95rem; color: #64748b; margin: 0.1rem 0;">Role: <strong>{user_role}</strong></p>
        <p style="font-size: 0.85rem; color: #94a3b8; margin: 0.1rem 0;">Dept: {st.session_state.get('user_department', 'N/A')} &nbsp;|&nbsp; School: {st.session_state.get('user_school', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

with col_logout:
    st.markdown('<div class="logout-btn-container">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="logout_top"):
        st.session_state.logged_in = False
        st.switch_page("login.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==================== NOTIFICATIONS SECTION ====================
notifications = get_user_notifications(user_id)
unread_count = len([n for n in notifications if not n['read']])

if notifications:
    with st.expander(f"🔔 Notifications {f'({unread_count} unread)' if unread_count > 0 else ''}"):
        for notif in notifications[:10]:
            st.markdown(f"**{notif['message']}**")
            st.caption(f"{notif['created_at'][:16]}")
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_notifications(user_id)
            st.rerun()

    st.divider()


# ==================== HELPER: 2-BUTTONS-PER-ROW GRID ====================
def render_button_grid(buttons):
    """
    Render a list of buttons, two per row, regardless of how many
    buttons are passed in (keeps layout consistent across roles).

    buttons: list of dicts -> {"label": str, "key": str, "page": str}
    """
    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        cols = st.columns(2)
        for col, btn in zip(cols, row):
            with col:
                if st.button(btn["label"], use_container_width=True, key=btn["key"]):
                    st.switch_page(btn["page"])


# ==================== ROLE-BASED HOME BUTTONS ====================
if user_role == "Faculty":
    st.markdown('<div class="section-heading">👤 Faculty Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">View committees, apply, and track your applications.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "🔍 View Available Committees", "key": "fac_btn1", "page": "pages/faculty_dashboard.py"},
        {"label": "📝 My Applications", "key": "fac_btn2", "page": "pages/faculty_dashboard.py"},
        {"label": "📜 Service History", "key": "fac_btn3", "page": "pages/service_history_page.py"},
    ])

elif user_role == "Department Coordinator":
    st.markdown('<div class="section-heading">📝 Department Coordinator Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Create and manage committee records on behalf of academic authorities.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "coord_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "coord_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 View Applications", "key": "coord_btn3", "page": "pages/committee_management.py"},
        {"label": "📊 Workload Dashboard", "key": "coord_btn4", "page": "pages/workload_dashboard.py"},
        {"label": "📊 Reports Dashboard", "key": "coord_btn5", "page": "pages/reports_dashboard.py"},
        {"label": "📤 Export Reports", "key": "coord_btn6", "page": "pages/export_reports.py"},
    ])

elif user_role == "HOD":
    st.markdown('<div class="section-heading">🏛️ Head of Department Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Initiate department committees, review applicants, and monitor workload.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "hod_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "hod_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 Review Applications", "key": "hod_btn3", "page": "pages/committee_management.py"},
        {"label": "⚡ Direct Assignment", "key": "hod_btn4", "page": "pages/direct_assignment_page.py"},
        {"label": "📊 Workload Dashboard", "key": "hod_btn5", "page": "pages/workload_dashboard.py"},
        {"label": "📊 Reports Dashboard", "key": "hod_btn6", "page": "pages/reports_dashboard.py"},
    ])

elif user_role == "Dean":
    st.markdown('<div class="section-heading">🎓 Dean Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Initiate school committees, approve department committees, and oversee school operations.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "dean_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "dean_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 Review Applications", "key": "dean_btn3", "page": "pages/committee_management.py"},
        {"label": "⚡ Direct Assignment", "key": "dean_btn4", "page": "pages/direct_assignment_page.py"},
        {"label": "📊 Workload Dashboard", "key": "dean_btn5", "page": "pages/workload_dashboard.py"},
        {"label": "📊 Reports Dashboard", "key": "dean_btn6", "page": "pages/reports_dashboard.py"},
    ])

elif user_role == "Registrar":
    st.markdown('<div class="section-heading">📋 Registrar Office Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Process university-level committees, publish postings, and maintain official records.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "reg_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "reg_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 Review Applications", "key": "reg_btn3", "page": "pages/committee_management.py"},
        {"label": "⚡ Direct Assignment", "key": "reg_btn4", "page": "pages/direct_assignment_page.py"},
        {"label": "📊 Reports Dashboard", "key": "reg_btn5", "page": "pages/reports_dashboard.py"},
        {"label": "📤 Export Reports", "key": "reg_btn6", "page": "pages/export_reports.py"},
    ])

elif user_role == "Rector":
    st.markdown('<div class="section-heading">🏛️ Rector Office Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Authorize university-level committees and approve committee memberships.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "rect_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "rect_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 Review Applications", "key": "rect_btn3", "page": "pages/committee_management.py"},
        {"label": "⚡ Direct Assignment", "key": "rect_btn4", "page": "pages/direct_assignment_page.py"},
        {"label": "📊 Reports Dashboard", "key": "rect_btn5", "page": "pages/reports_dashboard.py"},
        {"label": "📤 Export Reports", "key": "rect_btn6", "page": "pages/export_reports.py"},
    ])

elif user_role == "President":
    st.markdown('<div class="section-heading">🏛️ President Office Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Authorize high-level institutional committees and direct university-wide matters.</div>', unsafe_allow_html=True)

    render_button_grid([
        {"label": "📋 Manage Committees", "key": "pres_btn1", "page": "pages/committee_management.py"},
        {"label": "➕ Create Committee", "key": "pres_btn2", "page": "pages/committee_management.py"},
        {"label": "👥 Review Applications", "key": "pres_btn3", "page": "pages/committee_management.py"},
        {"label": "⚡ Direct Assignment", "key": "pres_btn4", "page": "pages/direct_assignment_page.py"},
        {"label": "📊 Reports Dashboard", "key": "pres_btn5", "page": "pages/reports_dashboard.py"},
        {"label": "📤 Export Reports", "key": "pres_btn6", "page": "pages/export_reports.py"},
    ])

else:
    st.error(f"⚠️ Unhandled role detected: '{user_role}'")
    st.info("This is a system error. Please contact the administrator.")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("login.py")