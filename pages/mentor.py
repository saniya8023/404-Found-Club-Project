import streamlit as st
from streamlit_option_menu import option_menu
from database import execute_query
from datetime import datetime

st.markdown("""
    <style>
    /* Sirf default multipage menu ko hide karega, aapka custom sidebar rahega */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)
# --- PAGE CONFIG ---
st.set_page_config(page_title="Mentor Dashboard | 404 FOUND", layout="wide")

# CSS to hide default sidebar navigation
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.error("Please login first.")
    st.stop()

user = st.session_state.user 

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: left;'>
            <h1 style='color: #8B4513; margin-bottom: 0; font-size: 40px; font-weight: 900;'>404 FOUND</h1>
            <p style='font-size: 20px; font-weight: bold; margin-top: -15px; letter-spacing: 2px;'>CLUB</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown(f"### Welcome, **{user['user_name']}**")
    st.markdown(f"""<div style="background-color: #8B4513; color: white; padding: 2px 12px; border-radius: 15px; display: inline-block; font-size: 12px; font-weight: bold; margin-bottom: 20px;">👤 {user['role']}</div>""", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["My Activities", "Conducting Sessions", "My Profile"],
        icons=["list-check", "broadcast", "person-circle"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#8B4513"}}
    )
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("main.py")

# --- 1. MY ACTIVITIES SECTION ---
if selected == "My Activities":
    st.title("📋 My Mentorship Activities")
    st.subheader("Assigned Workshops & Participants")

    # Fixed Query: workshop_name use kiya hai jo aapke schema mein hai
    query = """
        SELECT w.workshop_id, w.workshop_name, 
               (SELECT COUNT(*) FROM workshop_attendees wa WHERE wa.workshop_id = w.workshop_id) as total_participants
        FROM workshop_table w
        WHERE w.mentor_id = %s
    """
    activities = execute_query(query, (user['user_id'],), fetch=True)

    if activities:
        for act in activities:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📍 **Workshop:** {act['workshop_name']}")
            with col2:
                st.metric("Participants", act['total_participants'])
    else:
        st.warning("No workshops assigned to you yet.")

# --- 2. CONDUCTING SESSIONS SECTION ---
elif selected == "Conducting Sessions":
    st.title("🎙️ Session Management")

    # Fixed Query: Columns match your schema
    query = """
        SELECT w.workshop_id, w.workshop_name, w.workshop_url, w.workshop_date, 
               w.start_time, w.end_time, h.hackathon_name, h.start_date as h_start_date, 
               sm.status_name 
        FROM workshop_table w
        JOIN hackathon_table h ON w.hackathon_id = h.hackathon_id
        JOIN status_master sm ON h.status_id = sm.status_id
        WHERE w.mentor_id = %s
    """
    sessions = execute_query(query, (user['user_id'],), fetch=True)

    if not sessions:
        st.info("No sessions to conduct.")
    else:
        current_date = datetime.now().date()

        for sess in sessions:
            # workshop_name use kiya title ki jagah
            with st.expander(f"📌 {sess['workshop_name']} - ({sess['hackathon_name']})", expanded=True):
                st.write(f"**Hackathon Status:** {sess['status_name']}")
                st.write(f"**Timing:** {sess['workshop_date']} | {sess['start_time']} to {sess['end_time']}")
                
                # Logic: Agar hackathon ki start date purani ho chuki hai
                if sess['h_start_date'] < current_date:
                    st.error("⚠️ This hackathon date has passed. Please upload the recording.")
                    
                    with st.form(key=f"upload_{sess['workshop_id']}"):
                        rec_url = st.text_input("Enter Recording URL", value=sess['workshop_url'] if sess['workshop_url'] else "")
                        if st.form_submit_button("Upload Recording"):
                            if rec_url:
                                execute_query("UPDATE workshop_table SET workshop_url = %s WHERE workshop_id = %s", (rec_url, sess['workshop_id']))
                                st.success("Recording URL updated!")
                                st.rerun()
                            else:
                                st.warning("Please enter a URL.")
                
                else:
                    st.success("✅ This session is upcoming/active.")
                    st.info(f"**Live Link Assigned by Admin:** {sess['workshop_url']}")
                    
                    if st.button("🚀 Go Live", key=f"live_{sess['workshop_id']}"):
                        if sess['workshop_url']:
                            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{sess["workshop_url"]}\'">', unsafe_allow_html=True)
                        else:
                            st.error("No URL assigned by admin yet.")

# --- 3. MY PROFILE SECTION ---
elif selected == "My Profile":  # Ab ye sirf tab chalega jab menu se select hoga
    st.markdown("---")
    st.subheader("👤 Profile Settings")
    with st.form("profile_edit"):
        u_name = st.text_input("Name", value=user['user_name'])
        u_phone = st.text_input("Phone", value=user['phone_no'])
        u_pass = st.text_input("Password", value=user['password'], type="password")
        st.text_input("Email", value=user['email'], disabled=True)
        st.text_input("Role", value=user['role'], disabled=True)
        
        if st.form_submit_button("Save Changes"):
            execute_query("UPDATE user_master SET user_name=%s, phone_no=%s, password=%s WHERE user_id=%s", 
                          (u_name, u_phone, u_pass, user['user_id']))
            st.success("Updated! Please Logout and Login again.")