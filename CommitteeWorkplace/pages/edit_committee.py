import streamlit as st
from navigation import render_sidebar
from datetime import datetime
from database import get_committee_by_id, update_committee, log_audit

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

user_id = st.session_state.get('user_id')
user_role = st.session_state.get('user_role', '')
user_dept = st.session_state.get('user_department')

render_sidebar()

query_params = st.query_params
committee_id = query_params.get('id')

if not committee_id:
    st.error("No committee selected.")
    st.stop()

try:
    committee_id = int(committee_id)
except ValueError:
    st.error("Invalid committee ID.")
    st.stop()

committee = get_committee_by_id(committee_id)

if not committee:
    st.error("Committee not found.")
    st.stop()

# ==================== AUTHORIZATION CHECKS ====================

# 1. Only draft committees can be edited
if committee['status'] != 'Draft':
    st.error("❌ Only draft committees can be edited. This committee is currently: **" + committee['status'] + "**")
    st.info("Once a committee is submitted for approval, it can no longer be edited. Contact the approving authority if changes are needed.")
    st.stop()

# 2. Check if user is authorized to edit this committee
authorized = False
edit_reason = ""

if user_role in ['Rector', 'President', 'System Admin']:
    authorized = True
elif user_role == 'Registrar' and committee['level'] == 'University':
    authorized = True
elif user_role == 'Dean' and committee.get('school') == st.session_state.get('user_school'):
    authorized = True
elif user_role == 'HOD' and committee.get('department') == user_dept:
    authorized = True
elif user_role == 'Department Coordinator':
    # Coordinator can only edit committees they created
    if committee['created_by'] == user_id:
        authorized = True
    else:
        edit_reason = "You can only edit committees that you created."
else:
    edit_reason = "You do not have permission to edit this committee."

if not authorized:
    st.error(f"❌ Access denied. {edit_reason}")
    st.stop()

st.markdown(f"# ✏️ Edit: {committee['name']}")
st.caption(f"Status: {committee['status']} | Level: {committee['level']} | Created by: {committee.get('created_by', 'N/A')}")

with st.form("edit_committee_form"):
    name = st.text_input("Committee Name", value=committee['name'])
    description = st.text_area("Description", value=committee.get('description', ''))
    hours = st.number_input("Hours per Week", 1, 20, value=committee['hours_per_week'])
    duration = st.number_input("Duration (months)", 1, 36, value=committee['duration_months'])

    try:
        deadline_date = datetime.strptime(committee['deadline'], '%Y-%m-%d')
        deadline = st.date_input("Deadline", value=deadline_date)
    except:
        deadline = st.date_input("Deadline", value=datetime.now())

    requirements = st.text_area("Requirements", value=committee.get('requirements', ''))

    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("Level", ['University', 'School', 'Department'], 
                           index=['University', 'School', 'Department'].index(committee['level']))
    with col2:
        comm_type = st.text_input("Type", value=committee['type'])

    # Show "On Behalf Of" info (read-only)
    st.info(f"This committee was created on behalf of authority ID: {committee.get('on_behalf_of', 'N/A')}")

    if st.form_submit_button("💾 Save Changes"):
        if not name:
            st.error("Name is required!")
        else:
            data = {
                'name': name,
                'description': description,
                'hours': hours,
                'duration': duration,
                'deadline': deadline.strftime('%Y-%m-%d'),
                'requirements': requirements,
                'type': comm_type,
                'level': level,
                'school': committee.get('school'),
                'department': committee.get('department')
            }
            update_committee(committee_id, data, user_id)
            st.success("✅ Committee updated successfully!")
            st.balloons()
            st.switch_page("pages/committee_management.py")