import streamlit as st

def get_navigation_items(user_role):
    """Get navigation items based on user role - per specification"""

    if user_role == 'Faculty':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('🔍 Committees', 'pages/faculty_dashboard.py'),
            ('📜 Service History', 'pages/service_history_page.py'),
        ]
    elif user_role == 'Department Coordinator':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('📋 Manage Committees', 'pages/committee_management.py'),
            ('📊 Workload Dashboard', 'pages/workload_dashboard.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
            ('📤 Export', 'pages/export_reports.py'),
        ]
    elif user_role == 'HOD':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('📋 Manage Committees', 'pages/committee_management.py'),
            ('⚡ Direct Assignment', 'pages/direct_assignment_page.py'),
            ('📊 Workload Dashboard', 'pages/workload_dashboard.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
        ]
    elif user_role == 'Dean':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('📋 Manage Committees', 'pages/committee_management.py'),
            ('⚡ Direct Assignment', 'pages/direct_assignment_page.py'),
            ('📊 Workload Dashboard', 'pages/workload_dashboard.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
        ]
    elif user_role == 'Registrar':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('📋 Manage Committees', 'pages/committee_management.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
            ('📤 Export', 'pages/export_reports.py'),
        ]
    elif user_role in ['Rector', 'President']:
        return [
            ('🏠 Home', 'pages/home.py'),
            ('📋 Manage Committees', 'pages/committee_management.py'),
            ('⚡ Direct Assignment', 'pages/direct_assignment_page.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
            ('📤 Export', 'pages/export_reports.py'),
        ]
    elif user_role == 'System Admin':
        return [
            ('🏠 Home', 'pages/home.py'),
            ('⚙️ System Settings', 'pages/system_settings.py'),
            ('📊 Reports', 'pages/reports_dashboard.py'),
            ('📤 Export', 'pages/export_reports.py'),
        ]
    else:
        return [('🏠 Home', 'pages/home.py')]

def render_sidebar():
    """Render the sidebar with user info and navigation"""

    # ==================== HIDE DEFAULT STREAMLIT NAVIGATION ====================
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] nav {
            display: none !important;
        }
        .st-emotion-cache-1v0mbdj {
            display: none !important;
        }
        .st-emotion-cache-1r6slb0 {
            display: none !important;
        }
        .st-emotion-cache-1wmy9hl {
            display: none !important;
        }
        .st-emotion-cache-1vscsi {
            display: none !important;
        }
        .st-emotion-cache-1pbsqtx {
            display: none !important;
        }
        .st-emotion-cache-1wivap2 {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==================== SIDEBAR STYLING ====================
    st.markdown("""
    <style>
        /* Sidebar container */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #140c2b 0%, #241346 55%, #140c2b 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }

        /* ==================== SCROLLBAR STYLING ==================== */
        section[data-testid="stSidebar"]::-webkit-scrollbar {
            width: 6px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #ec4899, #f472b6);
            border-radius: 10px;
        }
        section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #f472b6, #fbcfe8);
        }

        /* Sidebar title */
        .sidebar-title {
            text-align: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
            margin-bottom: 1rem;
        }
        .sidebar-title h2 {
            margin: 0;
            color: white !important;
            font-weight: 700;
            font-size: 1.5rem;
            font-family: 'Outfit', sans-serif !important;
        }
        .sidebar-title h2 span {
            background: linear-gradient(135deg, #fbbf24, #f472b6) !important;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sidebar-title p {
            color: #a78bfa !important;
            font-size: 0.8rem;
            margin: 2px 0 0 0;
        }

        /* User info card */
        .user-info-card {
            background: rgba(124, 58, 237, 0.12) !important;
            padding: 12px 14px !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
            border-left: 3px solid #7c3aed !important;
            backdrop-filter: blur(4px);
        }
        .user-info-card .user-name {
            color: #e2e8f0 !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
        }
        .user-info-card .user-role {
            color: #a78bfa !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }
        .user-info-card .user-detail {
            color: #94a3b8 !important;
            font-size: 0.75rem !important;
            margin-top: 2px !important;
        }

        /* Sidebar buttons */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            border: none !important;
            width: 100% !important;
            padding: 10px 12px !important;
            text-align: left !important;
            background: transparent !important;
            color: #cbd5e1 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
        }
        .stButton > button:hover {
            background: rgba(124, 58, 237, 0.2) !important;
            color: #e2e8f0 !important;
            transform: translateX(4px) !important;
            border-left: 2px solid #a855f7 !important;
        }
        .stButton > button:focus {
            outline: none !important;
        }
        .stButton > button:active {
            background: rgba(124, 58, 237, 0.3) !important;
        }

        /* Divider */
        .sidebar-divider {
            border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
            margin: 12px 0 !important;
        }

        /* Notification badge */
        .notification-badge {
            background: linear-gradient(135deg, #7c3aed, #c026d3) !important;
            color: white !important;
            padding: 2px 10px !important;
            border-radius: 12px !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
            margin-left: 5px !important;
        }

        /* Logout button - special styling */
        .logout-btn {
            background: rgba(239, 68, 68, 0.1) !important;
            border: 1px solid rgba(239, 68, 68, 0.2) !important;
            color: #f87171 !important;
        }
        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.2) !important;
            border-color: #ef4444 !important;
            color: #fca5a5 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    user_name = st.session_state.get('user_name', 'User')
    user_role = st.session_state.get('user_role', 'Faculty')
    user_department = st.session_state.get('user_department')
    user_school = st.session_state.get('user_school')

    with st.sidebar:
        # Title
        st.markdown("""
        <div class="sidebar-title">
            <h2 style="margin-top: -8px; color: #94a3b8 !important; font-size: 1rem;">🎓 <span>Committee</span></h2>
            <h2 style="margin-top: -8px; color: #94a3b8 !important; font-size: 1rem;">Marketplace</h2>
            <p>Find your perfect role</p>
        </div>
        """, unsafe_allow_html=True)

        # User info - SIMPLIFIED to avoid HTML rendering issues
        st.markdown(f"""
        <div class="user-info-card">
            <div class="user-name">👤 {user_name}</div>
            <div class="user-role">⚙️ {user_role}</div>
        </div>
        """, unsafe_allow_html=True)

        # Show department and school as separate plain text with white color
        if user_department:
            st.markdown(f'<span style="color: #e2e8f0; font-size: 0.8rem;">📁 Dept: {user_department}</span>', unsafe_allow_html=True)
        if user_school:
            st.markdown(f'<span style="color: #e2e8f0; font-size: 0.8rem;">🏫 School: {user_school}</span>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Navigation buttons - per role
        items = get_navigation_items(user_role)
        for label, page in items:
            if st.button(label, use_container_width=True):
                st.switch_page(page)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Notifications
        try:
            from database import get_user_notifications, mark_notifications_read, clear_notifications

            notifications = get_user_notifications(st.session_state.get('user_id'))
            unread_count = len([n for n in notifications if not n['read']])

            if st.button(f"🔔 Notifications {f'({unread_count})' if unread_count > 0 else ''}", use_container_width=True):
                st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
                if st.session_state.show_notifications:
                    mark_notifications_read(st.session_state.get('user_id'))
                st.rerun()

            if st.session_state.get('show_notifications'):
                if notifications:
                    for notif in notifications[:10]:
                        st.markdown(f"**{notif['message']}**")
                        st.caption(f"{notif['created_at'][:16]}")
                    if st.button("🗑️ Clear All", use_container_width=True):
                        clear_notifications(st.session_state.get('user_id'))
                        st.rerun()
                else:
                    st.info("No notifications")
        except Exception as e:
            pass

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.switch_page("login.py")

def render_navigation():
    """Render navigation in sidebar - called from home.py"""
    user_role = st.session_state.get('user_role', 'Faculty')
    items = get_navigation_items(user_role)

    for label, page in items:
        if st.button(label, use_container_width=True):
            st.switch_page(page)