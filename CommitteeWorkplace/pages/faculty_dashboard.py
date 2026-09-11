import streamlit as st
from database import (
    get_all_committees, get_user_applications, create_application,
    withdraw_application, get_committee_by_id, get_committee_composition
)
from visibility import get_visible_committees
from eligibility import check_eligibility
from notifications_engine import notify_application_submitted
from service_history import get_service_summary
from workload_engine import get_workload_breakdown

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

if st.session_state.get('user_role') != 'Faculty':
    st.error("Access denied. Faculty only.")
    st.stop()

user_id = st.session_state.get('user_id')
user_role = st.session_state.get('user_role', 'Faculty')
user_rank = st.session_state.get('user_rank')
user_dept = st.session_state.get('user_department')
user_school = st.session_state.get('user_school')

# Build user dict for visibility/eligibility engines
user_dict = {
    'id': user_id,
    'role': user_role,
    'department': user_dept,
    'school': user_school,
    'rank': user_rank
}

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
    .stButton > button {
        border-radius: 10px !important; font-weight: 600 !important;
        transition: all 0.2s ease !important; border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6d28d9, #9333ea) !important;
        color: white !important; box-shadow: 0 4px 14px rgba(109, 40, 217, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(109, 40, 217, 0.45) !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important; padding: 8px 20px !important;
        background: #f1f5f9 !important; color: #64748b !important; font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed, #c026d3) !important; color: white !important;
    }
    .urgent-badge {
        background: linear-gradient(135deg, #ffe1e6, #ffd0d8) !important;
        color: #be123c !important; padding: 3px 12px !important;
        border-radius: 12px !important; font-size: 11px !important;
        font-weight: 700 !important; margin-left: 8px !important;
        animation: pulse 1.5s ease-in-out infinite !important;
        display: inline-block !important; border: 1px solid #fda4af !important;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.35); }
        50% { transform: scale(1.05); box-shadow: 0 0 0 6px rgba(225, 29, 72, 0); }
    }
    .eligibility-reason {
        background: #fef3c7; color: #92400e; padding: 8px 12px;
        border-radius: 8px; font-size: 0.8rem; margin-top: 8px;
        border: 1px solid #fde68a;
    }
    .slot-info {
        background: #eff6ff; color: #1e40af; padding: 8px 12px;
        border-radius: 8px; font-size: 0.8rem; margin-top: 8px;
        border: 1px solid #bfdbfe;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border-radius: 18px !important;
        box-shadow: 0 4px 18px rgba(76, 29, 149, 0.07) !important;
        border: 1px solid rgba(226, 220, 248, 0.7) !important;
        padding: 20px !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
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
    <h1>👤 Faculty Dashboard</h1>
    <p>View and apply to available committees</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Available Committees", "📝 My Applications", "📜 Service History"])

# ==================== TAB 1: AVAILABLE COMMITTEES ====================
with tab1:
    st.subheader("Available Committees")

    # Use visibility engine instead of raw get_all_committees
    committees = get_visible_committees(user_dict)
    user_applications = get_user_applications(user_id)
    applied_committee_ids = [app['committee_id'] for app in user_applications if app['status'] not in ['Withdrawn', 'Rejected', 'Closed without Selection']]

    col_f1, col_f2, col_f3 = st.columns([2.5, 2, 1.5])
    with col_f1:
        search = st.text_input("🔍 Search", placeholder="Committee name...", label_visibility="collapsed")
    with col_f2:
        type_filter = st.multiselect("Type", ['Academic', 'Administrative', 'Strategic'], default=[], label_visibility="collapsed", placeholder="All types")
    with col_f3:
        show_only_available = st.toggle("Available only", value=True)

    filtered = []
    for c in committees:
        if search and search.lower() not in c['name'].lower(): continue
        if type_filter and c['type'] not in type_filter: continue
        if show_only_available and c.get('filled_seats', 0) >= c.get('total_seats', 0): continue
        filtered.append(c)

    urgency_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    filtered.sort(key=lambda x: urgency_order.get(x.get('urgency', 'Low'), 4))

    st.caption(f"Showing **{len(filtered)}** committee{'s' if len(filtered) > 1 else ''}")

    if not filtered:
        st.info("No committees match your filters.")
    else:
        cols = st.columns(2)

        for idx, comm in enumerate(filtered):
            with cols[idx % 2]:
                already_applied = comm['id'] in applied_committee_ids
                available = comm.get('total_seats', 0) - comm.get('filled_seats', 0)
                is_full = available == 0

                # Check eligibility using the engine
                eligible, reason = check_eligibility(user_dict, comm)

                urgency_badge = ""
                if comm.get('urgency') == 'Critical':
                    urgency_badge = '<span class="urgent-badge">🚨 URGENT</span>'

                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; font-size: 16px; color: #1e1538; line-height: 1.3;">{comm['name']}</h4>
                        {urgency_badge}
                    </div>
                    <div style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
                        {comm['type']} • {comm.get('department', 'N/A')} • {comm.get('level', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)

                    # Show composition slots
                    comp = get_committee_composition(comm['id'])
                    if comp:
                        slot_texts = []
                        for slot in comp:
                            if slot['total_slots'] > 0:
                                avail = slot['total_slots'] - slot['filled_slots']
                                slot_texts.append(f"{slot['rank_required']}: {avail}/{slot['total_slots']}")
                        if slot_texts:
                            st.markdown(f'<div class="slot-info">{" | ".join(slot_texts)}</div>', unsafe_allow_html=True)

                    seat_color = '#94a3b8' if is_full else '#7c3aed'
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; background: linear-gradient(135deg, #faf8ff, #f5f1ff); padding: 12px; border-radius: 10px; margin-bottom: 16px; border: 1px solid #ede9fe;">
                        <div><b style="color:#1e1538;">{comm['hours_per_week']}h</b> <span style="color:#64748b;">/wk</span></div>
                        <div><b style="color:#1e1538;">{comm['duration_months']}</b> <span style="color:#64748b;">mos</span></div>
                        <div><b style="color:{seat_color};">{available}</b> <span style="color:#64748b;">seats</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    if already_applied:
                        st.button("✅ Applied", disabled=True, use_container_width=True, key=f"apply_{comm['id']}")
                    elif is_full:
                        st.button("✕ Full", disabled=True, use_container_width=True, key=f"apply_{comm['id']}")
                    elif not eligible:
                        st.button("➕ Apply", disabled=True, use_container_width=True, key=f"apply_{comm['id']}", help=reason)
                        st.markdown(f'<div class="eligibility-reason">⚠️ {reason}</div>', unsafe_allow_html=True)
                    else:
                        if st.button("➕ Apply", type="primary", use_container_width=True, key=f"apply_{comm['id']}"):
                            app_id = create_application(user_id, comm['id'], user_rank)
                            if app_id:
                                notify_application_submitted(user_id, comm['name'])
                                st.success("Application submitted!")
                                st.rerun()
                            else:
                                st.error("Failed to submit application.")

# ==================== TAB 2: MY APPLICATIONS ====================
with tab2:
    st.subheader("My Applications")

    user_applications = get_user_applications(user_id)
    active_applications = [app for app in user_applications if app['status'] not in ['Withdrawn', 'Closed without Selection']]

    if not active_applications:
        st.info("You haven't applied to any committees yet.")
    else:
        for app in active_applications:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1.5, 1])

                with col1:
                    st.write(f"**{app['committee_name']}**")
                    st.caption(f"Applied: {app['applied_date'][:16]}")
                    st.caption(f"Level: {app.get('level', 'N/A')} | Hours: {app.get('hours_per_week', 0)}h/week")
                with col2:
                    status_display = {
                        'Submitted': '🟡 Submitted',
                        'Under Review': '🔍 Under Review',
                        'Accepted': '✅ Accepted 🎉',
                        'Rejected': '❌ Rejected',
                        'Waitlisted': '⏳ Waitlisted'
                    }.get(app['status'], app['status'])
                    st.caption(f"Status: {status_display}")
                with col3:
                    if app['status'] in ['Submitted', 'Under Review']:
                        if st.button("↩️ Withdraw", key=f"withdraw_{app['id']}"):
                            withdraw_application(user_id, app['committee_id'])
                            st.success("Application withdrawn.")
                            st.rerun()

# ==================== TAB 3: SERVICE HISTORY ====================
with tab3:
    st.subheader("Service History")

    summary = get_service_summary(user_id)

    if summary['total'] == 0:
        st.info("No service history found. Committees you are accepted to will appear here.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Committees", summary['total'])
        with col2: st.metric("Active", summary['active'])
        with col3: st.metric("Completed", summary['completed'])
        with col4: st.metric("Current Hours/Week", summary['current_hours'])

        st.divider()

        for record in summary['records']:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{record['committee_name']}**")
                    st.caption(f"Role: {record['role_in_committee']} | Type: {record['assignment_type']}")
                    st.caption(f"Joined: {record['join_date'][:10] if record['join_date'] else 'N/A'}")
                    if record['end_date']:
                        st.caption(f"Ended: {record['end_date'][:10]}")
                with col2:
                    st.caption(f"Status: {record['status']}")
                    st.caption(f"Hours: {record['hours_per_week']}h/week")
                    st.caption(f"Duration: {record['duration_months']} months")