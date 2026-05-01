import streamlit as st
from ui_utils import load_global_styles
load_global_styles()
from database import execute_query
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="404 FOUND CLUB", layout="wide")

# --- CUSTOM CSS FOR LAYOUT & BUTTON ---
st.markdown("""
    <style>
    /* Sidebar hide karne ke liye */
    section[data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Sponsor Button Styling - Darker & Bold */
    .stButton>button[kind="secondary"] {
        background-color: #0056b3 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 20px;
        border: none;
    }

   
    .footer {
        width: 100%;
        background-color: transparent;
        color: black;
        text-align: center;
        padding: 30px 0px; /* Thori spacing barha di */
        font-size: 18px;
        font-weight: bold;
        margin-top: 50px; /* Form se thora fasla */
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER & SPONSOR BUTTON ---
col_logo, col_sponsor = st.columns([4, 1.2])
with col_logo:
    # 404 FOUND CLUB ka size barha diya (h1 use kiya hai)
    st.markdown("<h1 style='color: #00D4FF; margin:0; font-size: 50px;'>🚀 404 FOUND CLUB</h1>", unsafe_allow_html=True)

# --- main.py mein "col_sponsor" wala hissa replace karein ---
with col_sponsor:
    st.write("") 
    if st.button("**APPLY AS A SPONSOR**", type="secondary"):
        st.switch_page("pages/sponsor_apply.py") # Naye page ka naam

st.write("---") # Header Line

# --- VALIDATION RULES ---
phone_formats = {
    "Pakistan (+92)": {"pattern": r"^03\d{2}-\d{7}$", "example": "03xx-xxxxxxx"},
    "USA/Canada (+1)": {"pattern": r"^\d{3}-\d{3}-\d{4}$", "example": "xxx-xxx-xxxx"},
    "UK (+44)": {"pattern": r"^07\d{3}-\d{6}$", "example": "07xxx-xxxxxx"},
    "UAE (+971)": {"pattern": r"^05\d{1}-\d{7}$", "example": "05x-xxxxxxx"}
}

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- MAIN UI ---
if not st.session_state.logged_in:
    # Form ko center karne ke liye columns ka use
    empty_l, center_col, empty_r = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown("<h3 style='text-align: center;'>Welcome to the Hub</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        # --- TAB 1: LOGIN ---
        with tab1:
            st.subheader("Login to your Dashboard")
            login_email = st.text_input("Email Address", placeholder="name@domain.com")
            login_pass = st.text_input("Password", type="password")
            
            if st.button("Sign In"):
                if login_email and login_pass:
                    query = "SELECT * FROM user_master WHERE email = %s AND password = %s"
                    user_data = execute_query(query, (login_email, login_pass), fetch=True)

                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data[0]
                        st.session_state.user_id = user_data[0]['user_id']
                        st.session_state.user_name = user_data[0]['user_name']
                        if user_data[0]['role'] == 'Admin Staff':
                            st.session_state.active_admin_id = user_data[0]['user_id']
                        st.success(f"Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Email or Password.")
                else:
                    st.warning("Please enter both email and password.")

        # --- TAB 2: SIGNUP ---
        with tab2:
            st.subheader("Join as a Participant")
            reg_name = st.text_input("Full Name").title()
            reg_email = st.text_input("Email Address")
            country_choice = st.selectbox("Select Country", list(phone_formats.keys()))
            fmt = phone_formats[country_choice]
            reg_contact = st.text_input(f"Contact Number (Format: {fmt['example']})")
            reg_pass = st.text_input("Set Password", type="password")

            if st.button("Create Account"):
                if not (reg_name and reg_email and reg_contact and reg_pass):
                    st.error("All fields are mandatory!")
                elif not is_valid_email(reg_email):
                    st.error("Invalid email address.")
                elif not re.match(fmt['pattern'], reg_contact):
                    st.error(f"Invalid phone format.")
                else:
                    try:
                        id_query = "SELECT user_id FROM user_master WHERE user_id LIKE 'U-%' ORDER BY user_id DESC LIMIT 1"
                        last_record = execute_query(id_query, fetch=True)
                        if last_record:
                            last_num = int(last_record[0]['user_id'].split('-')[1])
                            new_id = f"U-{str(last_num + 1).zfill(3)}"
                        else:
                            new_id = "U-001"

                        ins_query = "INSERT INTO user_master (user_id, user_name, email, phone_no, password, role) VALUES (%s, %s, %s, %s, %s, 'Participant')"
                        execute_query(ins_query, (new_id, reg_name, reg_email, reg_contact, reg_pass))
                        st.balloons()
                        st.success(f"Account Created! ID: {new_id}")
                    except Exception as e:
                        st.error(f"Database Error: {e}")

    # --- FOOTER (Bold & Larger) ---
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2026 **404 FOUND CLUB** | Empowering Innovation</div>", unsafe_allow_html=True)

else:
    # --- LOGGED IN AREA ---
    user = st.session_state.user
    if user['role'] == 'Admin Staff':
        st.switch_page("pages/admin.py")
    elif user['role'] == 'Participant':
        st.switch_page("pages/participant.py")
    elif user['role'] == 'Judge':
        st.switch_page("pages/judge.py")
    elif user['role'] == 'Mentor':
        st.switch_page("pages/mentor.py")
        
    if st.sidebar.button("🚪 Logout", key="main_logout"):
        st.session_state.clear()
        st.session_state.logged_in = False
        st.rerun()