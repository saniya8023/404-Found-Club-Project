import streamlit as st
import mysql.connector

# --- 1. Database Connection ---
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",        # Apna username dalein
            password="izma123", # Apna password dalein
            database="hackathon_model"
        )
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# --- 2. Custom CSS for "NexusHack" Theme ---
st.set_page_config(page_title="NexusHack Portal", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #041122;
        color: white;
    }
    .stButton>button {
        background-color: #00D4FF;
        color: black;
        border-radius: 20px;
        font-weight: bold;
        width: 100%;
    }
    .login-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. Login Logic ---
def login_user(email, password):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Email, Password aur Role check karna
        query = "SELECT * FROM user_master WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        conn.close()
        return user
    return None

# --- 5. Main UI Flow ---
if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    st.markdown("<h1 style='text-align: center; color: #00D4FF;'>NexusHack Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Empowering Tech Minds, One Commit at a Time.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user['role_id'] # e.g., 'Admin', 'Judge', 'Participant'
                    st.session_state.user_name = user['user_name']
                    st.session_state.user_contact = user['contact_no']
                    st.success(f"Welcome back, {user['user_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sign up link for Participants
            st.markdown("<br><p style='text-align: center;'>New here? <a href='#'>Create Participant Account</a></p>", unsafe_allow_html=True)

else:
    # --- LOGOUT BUTTON IN SIDEBAR ---
    st.sidebar.title(f"Hi, {st.session_state.user_name}")
    st.sidebar.info(f"Role: {st.session_state.user_role}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ROUTING ---
    if st.session_state.user_role == 'Admin':
        st.title("Admin Dashboard")
        st.write(f"Welcome, {st.session_state.user_name}. You have full system control.")
        # Admin functions like Shortlisting Teams yahan ayengi

    elif st.session_state.user_role == 'Judge':
        st.title("Judge Evaluation Panel")
        st.write(f"Welcome, Judge {st.session_state.user_name}. Please evaluate the projects below.")
        # Scoring tables yahan ayenge

    elif st.session_state.user_role == 'Participant':
        st.title("Participant Workspace")
        st.write(f"Hello {st.session_state.user_name}! Manage your teams and workshops.")
        # Workshop join aur Team creation logic yahan ayengi

#         techclub_ui/
# ├── main.py              # Login Page aur Navigation
# ├── database.py          # SQL Connection ka common code
# ├── pages/               # Ye folder ka naam 'pages' hi hona chahiye
# │   ├── 1_Admin.py       # Admin ka poora logic
# │   ├── 2_Participant.py # Participant ka logic
# │   └── 3_Judge.py       # Judge ka logic
# └── assets/              # Logos aur Images