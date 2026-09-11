import streamlit as st
import pandas as pd
from database import get_all_committees, get_all_users
from workload_engine import get_workload_breakdown

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
    [data-testid="stMetricValue"] { color: #1e1538 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📊 Reports Dashboard</h1>
    <p>View analytics and statistics</p>
</div>
""", unsafe_allow_html=True)

committees = get_all_committees()
df = pd.DataFrame(committees)

if not df.empty:
    # ==================== OVERVIEW METRICS ====================
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Committees", len(df))
    with col2: st.metric("Open", len(df[df['status'] == 'Open']))
    with col3: st.metric("Draft", len(df[df['status'] == 'Draft']))
    with col4: st.metric("Pending Approval", len(df[df['status'] == 'Pending Approval']))
    with col5: st.metric("Closed", len(df[df['status'] == 'Closed']))

    st.divider()

    # ==================== CHARTS ====================
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Committees by Type")
        if 'type' in df.columns:
            st.bar_chart(df['type'].value_counts())
    with col2:
        st.subheader("Committees by Urgency")
        if 'urgency' in df.columns:
            st.bar_chart(df['urgency'].value_counts())

    st.divider()

    # ==================== STATUS DISTRIBUTION ====================
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Committees by Status")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
    with col2:
        st.subheader("Committees by Level")
        if 'level' in df.columns:
            st.bar_chart(df['level'].value_counts())

    st.divider()

    # ==================== FILL RATE ANALYSIS ====================
    st.subheader("Fill Rate Analysis")
    df['fill_rate'] = df.apply(lambda x: round((x.get('filled_seats', 0) / x.get('total_seats', 1) * 100), 1) if x.get('total_seats', 0) > 0 else 0, axis=1)

    fill_cols = st.columns(4)
    with fill_cols[0]: st.metric("Avg Fill Rate", f"{df['fill_rate'].mean():.1f}%")
    with fill_cols[1]: st.metric("Fully Filled", len(df[df['fill_rate'] >= 100]))
    with fill_cols[2]: st.metric("Partially Filled", len(df[(df['fill_rate'] > 0) & (df['fill_rate'] < 100)]))
    with fill_cols[3]: st.metric("Empty", len(df[df['fill_rate'] == 0]))

    st.bar_chart(df.set_index('name')['fill_rate'] if len(df) <= 20 else df.head(20).set_index('name')['fill_rate'])

    st.divider()

    # ==================== ALL COMMITTEES DATA ====================
    st.subheader("All Committees Data")
    display_cols = ['name', 'type', 'level', 'status', 'hours_per_week', 'urgency', 'total_seats', 'filled_seats', 'deadline']
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

    st.divider()

    # ==================== FACULTY PARTICIPATION ====================
    st.subheader("Faculty Participation")
    faculty = get_all_users(role='Faculty')
    if faculty:
        participation_data = []
        for f in faculty:
            breakdown = get_workload_breakdown(f['id'])
            participation_data.append({
                'name': f['name'],
                'department': f.get('department', 'N/A'),
                'school': f.get('school', 'N/A'),
                'rank': f.get('rank', 'N/A'),
                'active_committees': breakdown['committees'],
                'hours_per_week': breakdown['total_hours']
            })

        part_df = pd.DataFrame(participation_data)
        st.dataframe(part_df, use_container_width=True, hide_index=True)

        st.subheader("Participation by Department")
        dept_part = part_df.groupby('department').agg({
            'active_committees': 'sum',
            'hours_per_week': 'sum'
        }).reset_index()
        st.bar_chart(dept_part.set_index('department')['active_committees'])
else:
    st.info("No committees found.")