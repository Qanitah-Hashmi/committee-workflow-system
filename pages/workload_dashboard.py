import streamlit as st
import pandas as pd
from database import get_all_users, get_all_committees
from workload_engine import get_workload_breakdown

from navigation import render_sidebar
render_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

if st.session_state.get('user_role') == 'Faculty':
    st.error("Access denied. Management roles only.")
    st.stop()

user_role = st.session_state.get('user_role', '')
user_dept = st.session_state.get('user_department')
user_school = st.session_state.get('user_school')

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
    [data-testid="stMetricValue"] { color: #1e1538 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    .workload-high { background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.8rem; }
    .workload-medium { background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.8rem; }
    .workload-low { background: #d1fae5; color: #065f46; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📊 Workload Dashboard</h1>
    <p>Monitor committee workload across faculty</p>
</div>
""", unsafe_allow_html=True)

# ==================== GET ALL FACULTY WORKLOADS ====================
all_faculty = get_all_users(role='Faculty')
all_committees = get_all_committees()

workload_data = []
for faculty in all_faculty:
    breakdown = get_workload_breakdown(faculty['id'])
    workload_data.append({
        'id': faculty['id'],
        'name': faculty['name'],
        'email': faculty['email'],
        'department': faculty.get('department', 'N/A'),
        'school': faculty.get('school', 'N/A'),
        'rank': faculty.get('rank', 'N/A'),
        'current_hours': breakdown['total_hours'],
        'active_committees': breakdown['committees'],
        'committees_list': ", ".join([c['name'] for c in breakdown['breakdown']]) if breakdown['breakdown'] else "None"
    })

df = pd.DataFrame(workload_data)

# ==================== OVERVIEW METRICS ====================
st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Faculty", len(all_faculty))
with col2: st.metric("Faculty with Active Service", len([w for w in workload_data if w['active_committees'] > 0]))
with col3: st.metric("Total Active Committees", len([c for c in all_committees if c['status'] in ['Open', 'Under Review', 'Filled', 'Active']]))
with col4: 
    avg_hours = sum(w['current_hours'] for w in workload_data) / len(workload_data) if workload_data else 0
    st.metric("Avg Hours/Faculty", f"{avg_hours:.1f}h")

st.divider()

# ==================== FACULTY WORKLOAD TABLE ====================
st.subheader("Faculty Workload Breakdown")

if not df.empty:
    # Add workload level indicator
    def get_workload_level(hours):
        if hours > 15: return '<span class="workload-high">High</span>'
        elif hours > 8: return '<span class="workload-medium">Medium</span>'
        elif hours > 0: return '<span class="workload-low">Low</span>'
        return '<span style="color:#94a3b8;">None</span>'

    # Display as styled dataframe
    display_df = df[['name', 'rank', 'department', 'school', 'current_hours', 'active_committees', 'committees_list']].copy()
    display_df.columns = ['Name', 'Rank', 'Department', 'School', 'Hours/Week', 'Committees', 'Active Committees']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # ==================== CHARTS ====================
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Workload by Department")
        dept_df = df.groupby('department').agg({
            'current_hours': 'sum',
            'active_committees': 'sum'
        }).reset_index()
        dept_df.columns = ['Department', 'Total Hours', 'Total Committees']
        st.bar_chart(dept_df.set_index('Department')['Total Hours'])

    with col2:
        st.subheader("Workload by School")
        school_df = df.groupby('school').agg({
            'current_hours': 'sum',
            'active_committees': 'sum'
        }).reset_index()
        school_df.columns = ['School', 'Total Hours', 'Total Committees']
        st.bar_chart(school_df.set_index('School')['Total Hours'])

    st.divider()

    # ==================== HIGHEST/LOWEST LOAD ====================
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Highest Workload")
        highest = df.nlargest(5, 'current_hours')
        for _, row in highest.iterrows():
            with st.container(border=True):
                st.write(f"**{row['name']}** ({row['rank']})")
                st.caption(f"{row['current_hours']}h/week | {row['active_committees']} committees | {row['department']}")

    with col2:
        st.subheader("❄️ Lowest Workload")
        lowest = df.nsmallest(5, 'current_hours')
        for _, row in lowest.iterrows():
            with st.container(border=True):
                st.write(f"**{row['name']}** ({row['rank']})")
                st.caption(f"{row['current_hours']}h/week | {row['active_committees']} committees | {row['department']}")
else:
    st.info("No faculty data found.")