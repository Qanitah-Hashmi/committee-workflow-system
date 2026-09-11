import streamlit as st
import re
from datetime import datetime
from database import verify_user, lock_user

st.set_page_config(
    page_title="Committee Marketplace - Login",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
section[data-testid="stSidebar"] { display: none !important; }
.st-emotion-cache-1r6slb0 { display: none !important; }

/* ---- Base background: same soft lavender as home.py, plus a faint dot-grid texture ---- */
.stApp {
    background:
        radial-gradient(circle, rgba(109, 40, 217, 0.07) 1px, transparent 1px) 0 0/26px 26px,
        radial-gradient(circle at 8% 12%, rgba(124, 58, 237, 0.10) 0%, transparent 38%),
        radial-gradient(circle at 92% 8%, rgba(217, 70, 239, 0.09) 0%, transparent 42%),
        radial-gradient(circle at 50% 105%, rgba(245, 158, 11, 0.07) 0%, transparent 50%),
        linear-gradient(135deg, #f8f7ff 0%, #f1edfb 45%, #eef1ff 100%);
    background-attachment: fixed;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* ---- Dark-purple decorative blobs, gently drifting, filling the empty left/right gutters ---- */
.stApp::before, .stApp::after {
    content: '';
    position: fixed;
    top: -20%;
    width: 42vw;
    height: 140vh;
    z-index: 0;
    pointer-events: none;
    filter: blur(45px);
    animation: driftBlob 16s ease-in-out infinite;
}
.stApp::before {
    left: -12vw;
    background: radial-gradient(circle, rgba(30, 21, 56, 0.42) 0%, rgba(45, 27, 84, 0.22) 45%, transparent 72%);
}
.stApp::after {
    right: -12vw;
    background: radial-gradient(circle, rgba(109, 40, 217, 0.32) 0%, rgba(147, 51, 234, 0.18) 45%, transparent 72%);
    animation-delay: 3s;
}
@keyframes driftBlob {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-26px) scale(1.05); }
}

/* ---- Floating academic icons + soft particles in the side gutters ---- */
.decor-layer {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.decor-icon {
    position: absolute;
    opacity: 0.15;
    animation: floatIcon 9s ease-in-out infinite;
}
.di-1 { top: 10%;  left: 6%;   font-size: 3rem;   animation-delay: 0s;   }
.di-2 { top: 66%;  left: 9%;   font-size: 2.3rem; animation-delay: 1.4s; }
.di-3 { top: 42%;  left: 3.5%; font-size: 1.9rem; animation-delay: 2.6s; }
.di-4 { top: 14%;  right: 7%;  font-size: 3.2rem; animation-delay: 0.7s; }
.di-5 { top: 46%;  right: 4.5%;font-size: 2.1rem; animation-delay: 2s;   }
.di-6 { top: 71%;  right: 8.5%;font-size: 2.5rem; animation-delay: 3.3s; }
@keyframes floatIcon {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-16px) rotate(6deg); }
}
.decor-dot {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(109,40,217,0.45), rgba(147,51,234,0.05));
    animation: pulseDot 5s ease-in-out infinite;
}
.dd-1 { width: 12px; height: 12px; top: 24%; left: 16%;  animation-delay: 0s;   }
.dd-2 { width: 9px;  height: 9px;  top: 58%; left: 21%;  animation-delay: 1.5s; }
.dd-3 { width: 11px; height: 11px; top: 30%; right: 18%; animation-delay: 0.8s; }
.dd-4 { width: 14px; height: 14px; top: 64%; right: 14%; animation-delay: 2.2s; }
@keyframes pulseDot {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.35); }
}

/* ---- Staggered fade-in for the main content ---- */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
.logo-section { animation: fadeInUp 0.6s ease-out both; }
.welcome-text { animation: fadeInUp 0.6s ease-out 0.12s both; }
.st-key-login_card { animation: fadeInUp 0.6s ease-out 0.24s both; }

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 430px !important;
    position: relative;
    z-index: 1;
}
main { padding: 0 !important; }
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
    gap: 0.25rem !important;
}

/* ---- Neutralize Streamlit's own form border so it doesn't double up with .login-card ---- */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-6px) rotate(3deg); }
}
.login-container {
    max-width: 430px;
    margin: 0 auto;
    padding: 0;
    animation: slideUp 0.5s ease-out;
    position: relative;
    z-index: 1;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.logo-section {
    text-align: center;
    margin-bottom: 0.3rem;
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 10px 22px rgba(109, 40, 217, 0.32); }
    50% { box-shadow: 0 10px 30px rgba(109, 40, 217, 0.55); }
}
.logo-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #6d28d9, #9333ea);
    border-radius: 18px;
    margin-bottom: 0.5rem;
    animation: float 6s ease-in-out infinite, glowPulse 3s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}
.logo-wrapper::before {
    content: '';
    position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
    transform: rotate(45deg); animation: shimmer 3s infinite;
}
@keyframes shimmer {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}
.logo-emoji { font-size: 2.1rem; z-index: 1; }

/* Using divs (not h1/h2) so Streamlit's own heading rules can't override the sizing */
.app-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    color: #1e1538;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.4px;
    white-space: nowrap;
}
.app-subtitle {
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 400;
    margin: 0;
}

.welcome-text {
    text-align: center;
    margin: 0.6rem 0 0.5rem 0;
}
.welcome-heading {
    font-family: 'Outfit', sans-serif;
    color: #1e1538;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 0.15rem 0;
}
.welcome-sub {
    color: #94a3b8;
    font-size: 0.78rem;
    margin: 0;
}

.st-key-login_card {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 1.1rem 1.4rem 1.2rem 1.4rem;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 16px 32px -12px rgba(124, 58, 237, 0.18);
    position: relative;
    z-index: 1;
}

.stTextInput { margin-bottom: 0.3rem; }
.stTextInput label {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.2rem !important;
}
.stTextInput input {
    height: 34px !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0 12px !important;
    font-size: 0.88rem !important;
    transition: all 0.3s ease !important;
    background: white !important;
}
.stTextInput input:focus {
    border-color: #6d28d9 !important;
    box-shadow: 0 0 0 4px rgba(109, 40, 217, 0.1) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: #94a3b8 !important; }

.stCheckbox label {
    color: #475569 !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
}

.stButton button {
    height: 36px !important;
    background: linear-gradient(135deg, #6d28d9, #9333ea) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 6px 16px rgba(109, 40, 217, 0.30) !important;
    letter-spacing: 0.3px !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(109, 40, 217, 0.4) !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
}
.stButton button:active { transform: translateY(0) !important; }

.demo-toggle { margin-top: 0.6rem; }
.demo-toggle button {
    height: 34px !important;
    background: linear-gradient(135deg, #1e1538, #2d1b54) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(30, 21, 56, 0.3) !important;
}
.demo-toggle button:hover {
    background: linear-gradient(135deg, #2d1b54, #3f2470) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(30, 21, 56, 0.4) !important;
}

.stAlert {
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    padding: 8px 12px !important;
    margin: 0.5rem 0 !important;
    border: none !important;
}

pre, code {
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_department' not in st.session_state:
        st.session_state.user_department = None
    if 'user_school' not in st.session_state:
        st.session_state.user_school = None
    if 'user_rank' not in st.session_state:
        st.session_state.user_rank = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'show_demo' not in st.session_state:
        st.session_state.show_demo = False
    if 'login_success' not in st.session_state:
        st.session_state.login_success = False

init_session_state()

# ==================== HELPER FUNCTIONS ====================
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(edu|ac\.\w{2}|university\.\w{2}|edu\.\w{2})$'
    return re.match(pattern, email) is not None

def logout():
    keys_to_clear = ['logged_in', 'user_id', 'user_email', 'user_name', 'user_role',
                     'user_department', 'user_school', 'user_rank', 'login_attempts', 'login_success']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ==================== MAIN LOGIN PAGE ====================
def show_login():

    st.markdown("""
    <div class="decor-layer">
        <span class="decor-icon di-1">🎓</span>
        <span class="decor-icon di-2">📚</span>
        <span class="decor-icon di-3">📝</span>
        <span class="decor-icon di-4">🏛️</span>
        <span class="decor-icon di-5">✒️</span>
        <span class="decor-icon di-6">📋</span>
        <span class="decor-dot dd-1"></span>
        <span class="decor-dot dd-2"></span>
        <span class="decor-dot dd-3"></span>
        <span class="decor-dot dd-4"></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="logo-section">
        <div class="logo-wrapper"><span class="logo-emoji">🎓</span></div>
        <div class="app-title">Committee Marketplace</div>
        <p class="app-subtitle">Find your perfect academic service role</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-text">
        <div class="welcome-heading">Welcome Back</div>
        <p class="welcome-sub">Sign in to continue your committee experience</p>
    </div>
    """, unsafe_allow_html=True)

    # ==================== Auto-redirect if already logged in ====================
    if st.session_state.logged_in:
        st.switch_page("pages/home.py")
        return

    # Handle login success redirect
    if st.session_state.login_success:
        st.session_state.login_success = False
        st.switch_page("pages/home.py")
        return

    with st.container(key="login_card"):
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="yourname@university.edu", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

            col1, col2 = st.columns([3, 1])
            with col1:
                remember = st.checkbox("Remember me", value=False)
            with col2:
                if st.form_submit_button("Forgot?", use_container_width=True):
                    st.info("📧 Contact your administrator for password reset")

            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("⚠️ Please enter both email and password.")
                    return

                if not is_valid_email(email):
                    st.error("⚠️ Please enter a valid university email address.")
                    return

                user = verify_user(email, password)

                if user:
                    # Set all session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['id']
                    st.session_state.user_email = user['email']
                    st.session_state.user_name = user['name']
                    st.session_state.user_role = user['role']
                    st.session_state.user_department = user.get('department')
                    st.session_state.user_school = user.get('school')
                    st.session_state.user_rank = user.get('rank')
                    st.session_state.login_attempts = 0
                    st.session_state.login_success = True

                    # Use rerun to trigger redirect
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error("❌ Invalid email or password. Please try again.")

                    if st.session_state.login_attempts >= 5:
                        lock_user(email)
                        st.error("🔒 Too many failed attempts. Account locked. Contact admin.")

    # Demo Toggle
    st.markdown('<div class="demo-toggle">', unsafe_allow_html=True)
    if st.button("🔑 Show Demo Credentials", key="demo_toggle", use_container_width=True):
        st.session_state.show_demo = not st.session_state.show_demo
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_demo:
        st.code("""
Faculty 1: faculty1@uni.edu / pass123 (CS Dept, Engineering, Asst. Prof)
Faculty 2: faculty2@uni.edu / pass123 (Business Dept, Business, Assoc. Prof)
Faculty 3: faculty3@uni.edu / pass123 (CS Dept, Engineering, Professor)
Coordinator: coord1@uni.edu / pass123 (CS Dept, Engineering)
HOD: hod1@uni.edu / pass123 (CS Dept, Engineering)
Dean: dean1@uni.edu / pass123 (Engineering)
Registrar: registrar@uni.edu / pass123
Rector: rector@uni.edu / pass123
President: president@uni.edu / pass123
        """, language="text")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN ====================
def main():
    if st.query_params.get("logout") == "true":
        logout()
    show_login()

if __name__ == "__main__":
    main()