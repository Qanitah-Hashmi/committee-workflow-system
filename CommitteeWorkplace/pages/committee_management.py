import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    get_all_committees, create_committee, update_committee_status,
    get_committee_applications, update_application_status,
    create_notification, get_user_applications,
    get_committee_by_id, get_committee_composition, get_all_users,
    get_committee_roster
)
from workflow import (
    submit_for_approval, approve_committee, publish_committee,
    close_committee, cancel_committee
)
from selection_engine import accept_application, reject_application, waitlist_application
from notifications_engine import (
    notify_application_accepted, notify_application_rejected,
    notify_waitlisted, notify_new_application_to_authority
)
from eligibility import check_eligibility
from workload_engine import get_workload_breakdown

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

user_id = st.session_state.get('user_id')
user_role = st.session_state.get('user_role', '')
user_dept = st.session_state.get('user_department')
user_school = st.session_state.get('user_school')

# Faculty cannot access management panel
if user_role == 'Faculty':
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
        position: relative; overflow: hidden;
    }
    .main-header h1 { margin: 0; font-size: 2.3rem; font-weight: 800; color: #fbbf24 !important; }
    .main-header p { margin: 6px 0 0 0; opacity: 0.85; font-size: 1.05rem; color: #d8d4ec; }
    .stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s ease !important; border: none !important; }
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
    .status-pending { background: #fef3c7; color: #92400e; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-accepted { background: #d1fae5; color: #065f46; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-rejected { background: #fee2e2; color: #991b1b; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-waitlisted { background: #e0e7ff; color: #3730a3; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-draft { background: #f3f4f6; color: #4b5563; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-pending-approval { background: #fef9c3; color: #854d0e; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    .status-approved { background: #dcfce7; color: #166534; padding: 2px 12px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #1e1538 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    .workflow-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-right: 8px; }
    .badge-draft { background: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; }
    .badge-pending { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .badge-approved { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-open { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    .badge-closed { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-cancelled { background: #f3f4f6; color: #9ca3af; border: 1px solid #d1d5db; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚙️ Committee Management Panel</h1>
    <p>Create, manage, and oversee committee operations</p>
</div>
""", unsafe_allow_html=True)

# ==================== ROLE-BASED ACCESS HELPERS ====================
def can_create_committee(role):
    return role in ['Department Coordinator', 'HOD', 'Dean', 'Registrar', 'Rector', 'President']

def can_approve_committee(role, committee_level, committee_dept, committee_school):
    if role == 'HOD' and committee_level == 'Department' and committee_dept == user_dept:
        return True
    if role == 'Dean' and committee_level == 'School' and committee_school == user_school:
        return True
    if role == 'Dean' and committee_level == 'Department' and committee_school == user_school:
        return True  # Dean can approve dept-level committees in their school
    if role == 'Registrar' and committee_level == 'University':
        return True
    if role in ['Rector', 'President'] and committee_level == 'University':
        return True
    return False

def can_publish_committee(role, committee_level):
    if role == 'Registrar' and committee_level == 'University':
        return True
    if role == 'Dean' and committee_level == 'School':
        return True
    if role == 'HOD' and committee_level == 'Department':
        return True
    if role in ['Rector', 'President'] and committee_level == 'University':
        return True
    return False

def can_review_applications(role, committee_level, committee_dept, committee_school):
    if role == 'HOD' and committee_level == 'Department' and committee_dept == user_dept:
        return True
    if role == 'Dean' and committee_level in ['School', 'Department'] and committee_school == user_school:
        return True
    if role == 'Registrar' and committee_level == 'University':
        return True
    if role in ['Rector', 'President'] and committee_level == 'University':
        return True
    return False

def can_close_committee(role, committee_level, committee_dept, committee_school):
    return can_approve_committee(role, committee_level, committee_dept, committee_school)

def get_committees_for_role(role, all_committees):
    """Filter committees based on user role and scope"""
    if role in ['Rector', 'President', 'System Admin']:
        return all_committees
    elif role == 'Registrar':
        return [c for c in all_committees if c['level'] == 'University' or c['status'] in ['Draft', 'Pending Approval']]
    elif role == 'Dean':
        return [c for c in all_committees if c['school'] == user_school or c['level'] == 'University']
    elif role == 'HOD':
        return [c for c in all_committees if c['department'] == user_dept or c['level'] == 'University']
    elif role == 'Department Coordinator':
        return [c for c in all_committees if c['created_by'] == user_id or c['department'] == user_dept]
    return []

# ==================== GET ALL COMMITTEES ====================
all_committees = get_all_committees()
my_committees = get_committees_for_role(user_role, all_committees)

# ==================== TABS ====================
tabs_list = ["📊 Overview"]
if can_create_committee(user_role):
    tabs_list.append("➕ Create Committee")
tabs_list.extend(["📋 Draft & Pending", "📊 Manage Committees", "👥 Review Applications"])

tabs = st.tabs(tabs_list)

tab_idx = 0

# ==================== TAB 0: OVERVIEW ====================
with tabs[tab_idx]:
    st.header("Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Committees", len(my_committees))
    with col2: st.metric("Draft", len([c for c in my_committees if c['status'] == 'Draft']))
    with col3: st.metric("Pending Approval", len([c for c in my_committees if c['status'] == 'Pending Approval']))
    with col4: st.metric("Open", len([c for c in my_committees if c['status'] == 'Open']))
    with col5: st.metric("Closed", len([c for c in my_committees if c['status'] == 'Closed']))

    st.divider()

    # Recent activity
    st.subheader("Recent Committees")
    recent = sorted(my_committees, key=lambda x: x['created_at'], reverse=True)[:5]
    if recent:
        for comm in recent:
            status_color = {
                'Draft': 'badge-draft', 'Pending Approval': 'badge-pending',
                'Approved': 'badge-approved', 'Open': 'badge-open',
                'Closed': 'badge-closed', 'Cancelled': 'badge-cancelled'
            }.get(comm['status'], 'badge-draft')

            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{comm['name']}**")
                    st.caption(f"{comm['type']} • {comm['level']} • {comm.get('department', 'N/A')} • {comm.get('school', 'N/A')}")
                with col2:
                    st.markdown(f'<span class="workflow-badge {status_color}">{comm["status"]}</span>', unsafe_allow_html=True)
                    st.caption(f"📅 {comm['deadline']}")
    else:
        st.info("No committees in your scope.")

tab_idx += 1

# ==================== TAB 1: CREATE COMMITTEE ====================
if can_create_committee(user_role):
    with tabs[tab_idx]:
        st.header("Create New Committee")

        templates = {
            'Custom': {},
            'Curriculum Review': {'type': 'Academic', 'hours': 5, 'duration': 12, 'seats': 5, 'urgency': 'Medium'},
            'Hiring Committee': {'type': 'Administrative', 'hours': 3, 'duration': 6, 'seats': 4, 'urgency': 'High'},
            'Accreditation Task Force': {'type': 'Strategic', 'hours': 8, 'duration': 18, 'seats': 3, 'urgency': 'Critical'}
        }
        template = st.selectbox("Choose Template", list(templates.keys()))
        template_data = templates.get(template, {})

        # Get authorities for "On Behalf Of" dropdown
        authority_roles = []
        if user_role == 'Department Coordinator':
            authority_roles = ['HOD', 'Dean']
        elif user_role == 'HOD':
            authority_roles = ['Dean']
        elif user_role == 'Dean':
            authority_roles = ['Rector', 'President']
        elif user_role == 'Registrar':
            authority_roles = ['Rector', 'President']
        elif user_role in ['Rector', 'President']:
            authority_roles = ['Rector', 'President']

        authorities = get_all_users()
        if authority_roles:
            authorities = [u for u in authorities if u['role'] in authority_roles]
        else:
            authorities = [u for u in authorities if u['role'] in ['HOD', 'Dean', 'Rector', 'President']]

        with st.form("create_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Committee Name*", value=template if template != 'Custom' else "")
                committee_type = st.selectbox("Type", ['Academic', 'Administrative', 'Strategic'])
                hours = st.slider("Hours per Week", 1, 20, template_data.get('hours', 5))
                duration = st.slider("Duration (months)", 1, 36, template_data.get('duration', 12))
            with col2:
                total_seats = st.number_input("Total Seats*", 1, 20, template_data.get('seats', 5))
                urgency = st.selectbox("Urgency", ['Low', 'Medium', 'High', 'Critical'])
                deadline = st.date_input("Deadline", value=datetime(2026, 8, 1))

                # On Behalf Of selection
                if authorities:
                    on_behalf_of = st.selectbox(
                        "On Behalf Of*",
                        options=[u['id'] for u in authorities],
                        format_func=lambda x: next((f"{u['name']} ({u['role']})" for u in authorities if u['id'] == x), "")
                    )
                else:
                    on_behalf_of = user_id
                    st.info("No authority found. Creating on your own behalf.")

            # Composition slots
            st.subheader("Committee Composition")
            st.caption("Specify how many slots for each rank. Total must equal Total Seats.")

            comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
            with comp_col1:
                prof_slots = st.number_input("Professor", 0, 20, 0)
            with comp_col2:
                assoc_slots = st.number_input("Associate Professor", 0, 20, 0)
            with comp_col3:
                asst_slots = st.number_input("Assistant Professor", 0, 20, 0)
            with comp_col4:
                any_slots = st.number_input("Any Rank", 0, 20, template_data.get('seats', 5))

            comp_total = prof_slots + assoc_slots + asst_slots + any_slots
            if comp_total != total_seats:
                st.error(f"⚠️ Composition total ({comp_total}) must equal Total Seats ({total_seats})")

            level = st.selectbox("Committee Level", ['University', 'School', 'Department'])

            dept_col, school_col = st.columns(2)
            with dept_col:
                department = st.text_input("Department", value=user_dept or "Academic Affairs")
            with school_col:
                school = st.text_input("School (if applicable)", value=user_school or "")

            description = st.text_area("Description", height=80)
            requirements = st.text_area("Requirements", height=60)

            # Auto-set department/school based on level
            if level == 'University':
                department = None
                school = None
            elif level == 'School':
                department = None

            submitted = st.form_submit_button("💾 Save as Draft", type="primary")

            if submitted:
                if not name:
                    st.error("Name is required!")
                elif comp_total != total_seats:
                    st.error("Composition slots must equal Total Seats!")
                else:
                    composition = {
                        'Professor': prof_slots,
                        'Associate Professor': assoc_slots,
                        'Assistant Professor': asst_slots,
                        'Any': any_slots
                    }

                    data = {
                        'name': name,
                        'level': level,
                        'type': committee_type,
                        'hours': hours,
                        'duration': duration,
                        'school': school if level == 'School' else (school if level == 'Department' else None),
                        'department': department if level == 'Department' else None,
                        'deadline': deadline.strftime("%Y-%m-%d"),
                        'description': description,
                        'requirements': requirements,
                        'composition': composition,
                        'on_behalf_of': on_behalf_of,
                        'initiating_auth': on_behalf_of,
                        'approving_auth': on_behalf_of,
                        'publishing_auth': on_behalf_of
                    }
                    committee_id = create_committee(data, user_id)
                    st.success(f"✅ Committee '{name}' saved as Draft!")
                    st.balloons()
                    st.rerun()

    tab_idx += 1

# ==================== TAB: DRAFT & PENDING ====================
with tabs[tab_idx]:
    st.header("Draft & Pending Approval Committees")

    draft_committees = [c for c in my_committees if c['status'] == 'Draft']
    pending_committees = [c for c in my_committees if c['status'] == 'Pending Approval']
    approved_committees = [c for c in my_committees if c['status'] == 'Approved']

    if draft_committees:
        st.subheader("📝 Draft Committees")
        for comm in draft_committees:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1.5, 1.5])
                with col1:
                    st.write(f"**{comm['name']}**")
                    st.caption(f"{comm['type']} • {comm['level']} • {comm.get('department', 'N/A')}")
                    st.caption(f"Created: {comm['created_at'][:16]}")
                with col2:
                    st.markdown('<span class="workflow-badge badge-draft">Draft</span>', unsafe_allow_html=True)
                with col3:
                    # Only creator or same-dept coordinator can submit for approval
                    if user_role == 'Department Coordinator' and comm['created_by'] == user_id:
                        if st.button("📤 Submit for Approval", key=f"submit_{comm['id']}"):
                            submit_for_approval(comm['id'], user_id)
                            st.success("Submitted for approval!")
                            st.rerun()
                    elif user_role in ['HOD', 'Dean', 'Registrar', 'Rector', 'President']:
                        if st.button("📤 Submit for Approval", key=f"submit_{comm['id']}"):
                            submit_for_approval(comm['id'], user_id)
                            st.success("Submitted for approval!")
                            st.rerun()

                    if st.button("✏️ Edit", key=f"edit_draft_{comm['id']}"):
                        st.query_params['id'] = str(comm['id'])
                        st.switch_page("pages/edit_committee.py")

    if pending_committees:
        st.subheader("⏳ Pending Approval")
        for comm in pending_committees:
            can_approve = can_approve_committee(user_role, comm['level'], comm.get('department'), comm.get('school'))
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1.5, 1.5])
                with col1:
                    st.write(f"**{comm['name']}**")
                    st.caption(f"{comm['type']} • {comm['level']} • {comm.get('department', 'N/A')}")
                    st.caption(f"Initiated by: {comm.get('initiating_authority', 'N/A')}")
                with col2:
                    st.markdown('<span class="workflow-badge badge-pending">Pending Approval</span>', unsafe_allow_html=True)
                with col3:
                    if can_approve:
                        if st.button("✅ Approve", key=f"approve_{comm['id']}"):
                            approve_committee(comm['id'], user_id)
                            st.success("Approved!")
                            st.rerun()
                        if st.button("❌ Reject", key=f"reject_{comm['id']}"):
                            update_committee_status(comm['id'], 'Rejected', user_id, "Rejected by authority")
                            st.success("Rejected!")
                            st.rerun()
                    else:
                        st.caption("Awaiting approval")

    if approved_committees:
        st.subheader("📢 Approved - Ready to Publish")
        for comm in approved_committees:
            can_pub = can_publish_committee(user_role, comm['level'])
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1.5, 1.5])
                with col1:
                    st.write(f"**{comm['name']}**")
                    st.caption(f"{comm['type']} • {comm['level']} • {comm.get('department', 'N/A')}")
                with col2:
                    st.markdown('<span class="workflow-badge badge-approved">Approved</span>', unsafe_allow_html=True)
                with col3:
                    if can_pub:
                        if st.button("🚀 Publish", key=f"publish_{comm['id']}"):
                            publish_committee(comm['id'], user_id)
                            st.success("Published! Now open for applications.")
                            st.rerun()
                    else:
                        st.caption("Awaiting publication")

    if not draft_committees and not pending_committees and not approved_committees:
        st.info("No draft, pending, or approved committees in your scope.")

tab_idx += 1

# ==================== TAB: MANAGE COMMITTEES ====================
with tabs[tab_idx]:
    st.header("Manage Committees")

    # Filter by status
    status_filter = st.multiselect(
        "Filter by Status",
        ['Open', 'Under Review', 'Filled', 'Active', 'Closed', 'Archived', 'Cancelled'],
        default=['Open', 'Under Review', 'Filled', 'Active']
    )

    filtered = [c for c in my_committees if c['status'] in status_filter] if status_filter else my_committees

    total_committees = len(filtered)
    total_seats = sum(c.get('total_seats', 0) for c in filtered)
    filled_seats = sum(c.get('filled_seats', 0) for c in filtered)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Committees", total_committees)
    with col2: st.metric("Total Seats", total_seats)
    with col3: st.metric("Filled Seats", filled_seats)
    with col4:
        fill_rate = round((filled_seats / total_seats * 100), 1) if total_seats > 0 else 0
        st.metric("Fill Rate", f"{fill_rate}%")

    st.divider()

    for comm in filtered:
        status_color = {
            'Open': 'badge-open', 'Under Review': 'badge-pending',
            'Filled': 'badge-approved', 'Active': 'badge-approved',
            'Closed': 'badge-closed', 'Archived': 'badge-draft',
            'Cancelled': 'badge-cancelled'
        }.get(comm['status'], 'badge-draft')

        urgency_icon = '🚨' if comm.get('urgency') == 'Critical' else ''

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2.5, 1, 1, 1.5])
            with col1:
                st.subheader(f"{urgency_icon} {comm['name']}")
                st.caption(f"{comm['type']} • {comm.get('department', 'N/A')} • {comm['hours_per_week']}h/wk")
                st.markdown(f'<span class="workflow-badge {status_color}">{comm["status"]}</span>', unsafe_allow_html=True)
            with col2:
                st.metric("Seats", f"{comm.get('filled_seats', 0)}/{comm.get('total_seats', 0)}")
            with col3:
                st.caption(f"📅 {comm['deadline']}")
                # Show composition
                comp = get_committee_composition(comm['id'])
                if comp:
                    for slot in comp:
                        st.caption(f"{slot['rank_required']}: {slot['filled_slots']}/{slot['total_slots']}")
            with col4:
                if st.button("👥 Applicants", key=f"apps_{comm['id']}"):
                    st.session_state.selected_committee = comm['id']
                    st.rerun()

                # Show roster button
                if st.button("📋 Roster", key=f"roster_{comm['id']}"):
                    st.session_state.view_roster = comm['id']
                    st.rerun()

                can_close = can_close_committee(user_role, comm['level'], comm.get('department'), comm.get('school'))
                if can_close and comm['status'] not in ['Closed', 'Archived', 'Cancelled']:
                    if st.button("🗑️ Close", key=f"close_{comm['id']}"):
                        close_committee(comm['id'], user_id)
                        st.rerun()

    # Show roster if selected
    if st.session_state.get('view_roster'):
        roster_comm_id = st.session_state.view_roster
        roster = get_committee_roster(roster_comm_id)
        comm = get_committee_by_id(roster_comm_id)

        st.divider()
        st.subheader(f"📋 Roster: {comm['name']}" if comm else "📋 Committee Roster")

        if roster:
            roster_df = pd.DataFrame(roster)
            st.dataframe(roster_df[['name', 'rank', 'department', 'role_in_committee', 'assignment_type', 'join_date', 'status']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No members in roster yet.")

        if st.button("Close Roster View"):
            del st.session_state.view_roster
            st.rerun()

tab_idx += 1

# ==================== TAB: REVIEW APPLICATIONS ====================
with tabs[tab_idx]:
    st.header("Review Applications")

    selected_comm_id = st.session_state.get('selected_committee')

    # Get committees that this user can review applications for
    reviewable_committees = [c for c in my_committees if can_review_applications(
        user_role, c['level'], c.get('department'), c.get('school')
    ) and c['status'] in ['Open', 'Under Review', 'Filled']]

    if not reviewable_committees:
        st.info("No committees available for application review in your scope.")
    else:
        comm_options = {c['id']: c['name'] for c in reviewable_committees}

        default_index = 0
        if selected_comm_id and selected_comm_id in comm_options:
            default_index = list(comm_options.keys()).index(selected_comm_id)

        selected_id = st.selectbox(
            "Select Committee",
            options=list(comm_options.keys()),
            format_func=lambda x: comm_options[x],
            index=default_index
        )

        applications = get_committee_applications(selected_id)
        applications = [app for app in applications if app['status'] not in ['Withdrawn', 'Closed without Selection']]

        if not applications:
            st.info("No applicants for this committee.")
        else:
            committee_name = comm_options[selected_id]

            # Show committee composition
            comp = get_committee_composition(selected_id)
            st.subheader("Available Slots")
            comp_cols = st.columns(len(comp) if comp else 1)
            if comp:
                for idx, slot in enumerate(comp):
                    with comp_cols[idx]:
                        available = slot['total_slots'] - slot['filled_slots']
                        st.metric(slot['rank_required'], f"{available}/{slot['total_slots']}")

            st.divider()

            for app in applications:
                with st.container(border=True):
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

                    with col1:
                        st.write(f"👤 {app['name']}")
                        st.caption(f"Rank: {app.get('rank', 'N/A')} | Dept: {app.get('department', 'N/A')}")
                        st.caption(f"Applied: {app['applied_date'][:16]}")

                        # Show current workload
                        workload = get_workload_breakdown(app['user_id'])
                        st.caption(f"Current Load: {workload['total_hours']}h/week | {workload['committees']} committees")

                    with col2:
                        status = app['status']
                        if status == 'Accepted':
                            st.markdown('<span class="status-accepted">✅ Accepted</span>', unsafe_allow_html=True)
                        elif status == 'Rejected':
                            st.markdown('<span class="status-rejected">❌ Rejected</span>', unsafe_allow_html=True)
                        elif status == 'Waitlisted':
                            st.markdown('<span class="status-waitlisted">⏳ Waitlisted</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="status-pending">⏳ Pending</span>', unsafe_allow_html=True)

                    with col3:
                        if status in ['Submitted', 'Under Review']:
                            # Check if accepting would violate composition
                            user_rank = app.get('rank', 'Any')
                            slot_available = False
                            for slot in comp:
                                if slot['filled_slots'] < slot['total_slots']:
                                    if slot['rank_required'] == 'Any' or slot['rank_required'] == user_rank:
                                        slot_available = True
                                        break

                            if not slot_available:
                                st.warning("No matching slot", icon="⚠️")

                            if st.button("✅ Accept", key=f"accept_{app['id']}"):
                                accept_application(app['id'], user_id, committee_name)
                                create_notification(app['user_id'], f"✅ Your application to '{committee_name}' has been ACCEPTED! 🎉", 'success')
                                st.rerun()

                    with col4:
                        if status in ['Submitted', 'Under Review']:
                            if st.button("⏳ Waitlist", key=f"waitlist_{app['id']}"):
                                waitlist_application(app['id'], user_id)
                                create_notification(app['user_id'], f"⏳ Your application to '{committee_name}' has been WAITLISTED.", 'info')
                                st.rerun()

                    with col5:
                        if status in ['Submitted', 'Under Review', 'Waitlisted']:
                            if st.button("❌ Reject", key=f"reject_{app['id']}"):
                                reject_application(app['id'], user_id, "Rejected by reviewer", committee_name)
                                create_notification(app['user_id'], f"❌ Your application to '{committee_name}' has been REJECTED.", 'error')
                                st.rerun()