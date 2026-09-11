import streamlit as st
from database import (
    get_all_users, get_all_committees, get_committee_by_id, 
    get_committee_composition, get_committee_roster
)
from workload_engine import get_workload_breakdown
from eligibility import check_eligibility
from direct_assignment import assign_member

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

user_id = st.session_state.get('user_id')
user_role = st.session_state.get('user_role', '')
user_dept = st.session_state.get('user_department')
user_school = st.session_state.get('user_school')

# Only authorized roles can direct assign
if user_role not in ['HOD', 'Dean', 'Registrar', 'Rector', 'President']:
    st.error("Access denied. Only HOD, Dean, Registrar, Rector, and President can directly assign members.")
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
    .workload-card {
        background: linear-gradient(135deg, #faf8ff, #f5f1ff);
        padding: 16px; border-radius: 12px; border: 1px solid #ede9fe;
        margin-bottom: 12px;
    }
    .workload-card h4 { margin: 0 0 8px 0; color: #1e1538; font-size: 1rem; }
    .workload-card p { margin: 0; color: #64748b; font-size: 0.85rem; }
    .eligibility-match { background: #d1fae5; color: #065f46; padding: 8px 12px; border-radius: 8px; font-size: 0.85rem; }
    .eligibility-mismatch { background: #fee2e2; color: #991b1b; padding: 8px 12px; border-radius: 8px; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚡ Direct Assignment</h1>
    <p>Directly assign faculty members to committees</p>
</div>
""", unsafe_allow_html=True)

st.info("This feature allows authorized academic authorities to directly assign faculty members to committees. The faculty member will receive a notification.")

# ==================== FILTER COMMITTEES BY ROLE SCOPE ====================
all_committees = get_all_committees()

# Filter committees based on user role
if user_role == 'HOD':
    eligible_committees = [c for c in all_committees if c['level'] == 'Department' and c.get('department') == user_dept and c['status'] in ['Open', 'Under Review', 'Filled', 'Active']]
elif user_role == 'Dean':
    eligible_committees = [c for c in all_committees if c['level'] in ['School', 'Department'] and c.get('school') == user_school and c['status'] in ['Open', 'Under Review', 'Filled', 'Active']]
elif user_role == 'Registrar':
    eligible_committees = [c for c in all_committees if c['level'] == 'University' and c['status'] in ['Open', 'Under Review', 'Filled', 'Active']]
elif user_role in ['Rector', 'President']:
    eligible_committees = [c for c in all_committees if c['level'] == 'University' and c['status'] in ['Open', 'Under Review', 'Filled', 'Active']]
else:
    eligible_committees = []

if not eligible_committees:
    st.warning("No committees available for direct assignment in your scope.")
    st.stop()

# ==================== GET ELIGIBLE USERS ====================
# Get users based on assigning user's role
if user_role in ['Rector', 'President']:
    eligible_users = get_all_users()
    # Exclude System Admin and self
    eligible_users = [u for u in eligible_users if u['role'] != 'System Admin' and u['id'] != user_id]
elif user_role == 'Registrar':
    eligible_users = [u for u in get_all_users() if u['role'] in ['Faculty', 'HOD', 'Dean']]
elif user_role == 'Dean':
    eligible_users = [u for u in get_all_users() if u['role'] in ['Faculty', 'HOD'] and u.get('school') == user_school]
elif user_role == 'HOD':
    eligible_users = [u for u in get_all_users() if u['role'] == 'Faculty' and u.get('department') == user_dept]
else:
    eligible_users = []

if not eligible_users:
    st.warning("No eligible users available for direct assignment.")
    st.stop()

# ==================== SELECTION FORM ====================
st.subheader("Select User to Assign")

selected_user_id = st.selectbox(
    "User",
    options=[u['id'] for u in eligible_users],
    format_func=lambda x: next((f"{u['name']} ({u['role']}) — {u.get('department', 'N/A')}" for u in eligible_users if u['id'] == x), ""),
    key="da_user"
)

# Show selected user details
if selected_user_id:
    user_selected = next((u for u in eligible_users if u['id'] == selected_user_id), None)
    if user_selected:
        workload = get_workload_breakdown(selected_user_id)

        st.markdown("#### Current Workload")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Active Committees", workload['committees'])
        with col2: st.metric("Hours/Week", workload['total_hours'])
        with col3: st.metric("Department", user_selected.get('department', 'N/A'))

        if workload['breakdown']:
            st.markdown("**Active Committee Load:**")
            for item in workload['breakdown']:
                st.markdown(f'<div class="workload-card"><h4>{item["name"]}</h4><p>{item["hours"]} hours/week</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="workload-card"><p>No active committees</p></div>', unsafe_allow_html=True)

st.divider()

st.subheader("Select Committee")

selected_committee_id = st.selectbox(
    "Committee",
    options=[c['id'] for c in eligible_committees],
    format_func=lambda x: next((f"{c['name']} ({c['level']}) — {c.get('filled_seats', 0)}/{c.get('total_seats', 0)} filled" for c in eligible_committees if c['id'] == x), ""),
    key="da_committee"
)

# Show committee details when selected
if selected_committee_id:
    committee = get_committee_by_id(selected_committee_id)
    if committee:
        comp = get_committee_composition(selected_committee_id)
        roster = get_committee_roster(selected_committee_id)

        st.markdown("#### Committee Details")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Seats", committee.get('total_seats', 0))
        with col2: st.metric("Filled", committee.get('filled_seats', 0))
        with col3: st.metric("Hours/Week", committee.get('hours_per_week', 0))

        if comp:
            st.markdown("**Available Slots:**")
            comp_cols = st.columns(len(comp))
            for idx, slot in enumerate(comp):
                with comp_cols[idx]:
                    available = slot['total_slots'] - slot['filled_slots']
                    st.metric(slot['rank_required'], f"{available}/{slot['total_slots']}")

        if roster:
            st.markdown("**Current Roster:**")
            for member in roster:
                st.caption(f"• {member['name']} ({member['rank']}) — {member['role_in_committee']}")

        # Check eligibility
        if selected_user_id and user_selected:
            user_dict = {
                'id': user_selected['id'],
                'role': user_selected['role'],
                'department': user_selected.get('department'),
                'school': user_selected.get('school'),
                'rank': user_selected.get('rank')
            }
            eligible, reason = check_eligibility(user_dict, committee)

            if eligible:
                st.markdown('<div class="eligibility-match">✅ User is eligible for this committee</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="eligibility-mismatch">⚠️ {reason}</div>', unsafe_allow_html=True)
                st.warning("This user may not be eligible. You can still assign with justification.")

st.divider()

st.subheader("Assignment Details")

role_in_committee = st.selectbox(
    "Role in Committee",
    ['Chair', 'Convener', 'Secretary', 'Member', 'Ex-officio'],
    index=3,
    key="da_role"
)

assignment_reason = st.text_area(
    "Reason for Direct Assignment",
    placeholder="Explain why this user is being directly assigned (e.g., expertise required, mandatory service, etc.)",
    height=100,
    key="da_reason"
)

st.divider()

# ==================== ASSIGN BUTTON ====================
# NOTE: the button is intentionally NOT disabled via the `disabled=` param.
# A disabled button can't be clicked at all, which made the page look broken.
# Validation happens inside the click handler instead.
if st.button("⚡ Assign to Committee", type="primary", use_container_width=True):
    if not selected_user_id or not selected_committee_id:
        st.error("Please select both a user and a committee.")
    elif not assignment_reason.strip():
        st.error("Please provide a reason for the direct assignment.")
    else:
        with st.spinner("Assigning..."):
            success, message = assign_member(
                committee_id=selected_committee_id,
                user_id=selected_user_id,
                role=role_in_committee,
                assigner_id=user_id,
                reason=assignment_reason
            )

        if success:
            committee = get_committee_by_id(selected_committee_id)
            user = next((u for u in eligible_users if u['id'] == selected_user_id), None)
            # Notification is created inside assign_member() — no extra call needed here.
            st.success(f"✅ {user['name']} has been directly assigned to '{committee['name']}' as {role_in_committee}!")
            st.balloons()

            # Show updated workload
            workload = get_workload_breakdown(selected_user_id)
            st.info(f"📊 {user['name']}'s updated workload: {workload['total_hours']} hours/week across {workload['committees']} committees.")
        else:
            st.error(f"❌ Assignment failed: {message}")