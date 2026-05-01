import streamlit as st
from database import execute_query
from datetime import date

st.set_page_config(page_title="Sponsor Portal", layout="wide")

# UI Styling
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #8D6E63; color: white; }
    .center-card { background-color: #FDF5E6; padding: 40px; border-radius: 20px; border: 2px solid #D2B48C; margin-top: 50px; }
    .main-card { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

if 'sponsor_view' not in st.session_state:
    st.session_state.sponsor_view = 'verify'

# Helper function to generate New Sponsor ID (S-001 format)
def generate_new_id():
    id_q = "SELECT sponsor_id FROM sponsor_table ORDER BY sponsor_id DESC LIMIT 1"
    last = execute_query(id_q, fetch=True)
    if last and '-' in last[0]['sponsor_id']:
        num = int(last[0]['sponsor_id'].split('-')[1]) + 1
        return f"S-{num:03d}"
    return "S-001"

# --- STEP 1: LOGIN / VERIFICATION ---
if st.session_state.sponsor_view == 'verify':
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='center-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #5D4037;'>Sponsor Login</h2>", unsafe_allow_html=True)
        v_name = st.text_input("Sponsor Name").strip()
        v_email = st.text_input("Registered Email").strip()
        
        if st.button("Access My Funding Details"):
            if v_name and v_email:
                query = """
                    SELECT sponsor_id, sponsor_name, status 
                    FROM sponsor_table 
                    WHERE LOWER(TRIM(sponsor_name)) = LOWER(%s) 
                    AND LOWER(TRIM(email)) = LOWER(%s)
                """
                res = execute_query(query, (v_name, v_email), fetch=True)
                
                if res:
                    status_val = res[0]['status'].strip().lower()
                    if status_val in ['approved', 'accepted']:
                        st.session_state.active_sponsor_id = res[0]['sponsor_id']
                        st.session_state.active_sponsor_name = res[0]['sponsor_name']
                        st.session_state.sponsor_view = 'dashboard'
                        st.rerun()
                    else:
                        st.warning(f"Account status is '{res[0]['status']}'. Waiting for Admin approval.")
                else:
                    st.error("Credentials not found.")
            else:
                st.warning("Please fill all fields.")
        
        st.write("---")
        if st.button("New Partner? Apply Here"):
            st.session_state.sponsor_view = 'apply_new'
            st.rerun()
        
        if st.button("⬅️ Back to Home"):
            st.switch_page("main.py")
        st.markdown("</div>", unsafe_allow_html=True)

# --- STEP 2: SPONSOR DASHBOARD ---
elif st.session_state.sponsor_view == 'dashboard':
    st.title(f"💰 Welcome, {st.session_state.active_sponsor_name}")
    
    tab1, tab2 = st.tabs(["📊 My Funding History", "🚀 New Funding Request"])
    
    with tab1:
        st.subheader("Your Funding Records")
        history_q = """
            SELECT h.hackathon_name, sh.funding_amount, h.start_date
            FROM sponsor_hackathon sh 
            JOIN hackathon_table h ON sh.hackathon_id = h.hackathon_id 
            WHERE sh.sponsor_id = %s
        """
        history = execute_query(history_q, (st.session_state.active_sponsor_id,), fetch=True)
        
        if history:
            st.table(history)
        else:
            st.info("No active funding records found.")

    with tab2:
        st.subheader("Request to Fund a New Hackathon")
        today_str = date.today().strftime('%Y-%m-%d')
        h_query = "SELECT hackathon_id, hackathon_name, prize_pool FROM hackathon_table WHERE start_date > %s"
        h_data = execute_query(h_query, (today_str,), fetch=True)
        
        if h_data:
            h_map = {h['hackathon_name']: h for h in h_data}
            sel_h_name = st.selectbox("Select Upcoming Hackathon", list(h_map.keys()))
            target_h = h_map[sel_h_name]
            p_pool = float(target_h['prize_pool'])
            min_required = p_pool * 2
            
            st.info(f"Prize Pool: ${p_pool:,.2f} | Min. Sponsorship: ${min_required:,.2f}")
            st.warning("Note: Funding must be at least double the prize pool.")

            with st.form("existing_sponsor_new_req"):
                amount = st.number_input("Funding Amount ($)", min_value=min_required)
                if st.form_submit_button("Submit Request"):
                    # LOGIC: Create a NEW request in sponsor_table with a NEW ID for Admin to approve
                    new_req_id = generate_new_id()
                    # We store the intended amount in a way admin can see (e.g., website_url field or a custom note)
                    # For now, following your logic: Create new record in sponsor_table
                    ins_q = """
                        INSERT INTO sponsor_table (sponsor_id, sponsor_name, email, status, website_url) 
                        VALUES (%s, %s, %s, 'Pending', %s)
                    """
                    # Storing amount in website_url temporarily so admin knows how much was offered
                    execute_query(ins_q, (new_req_id, st.session_state.active_sponsor_name, f"REQ_{amount}", f"Funding for {sel_h_name}"))
                    st.success("Your request has been sent to Admin for approval!")
        else:
            st.info("No upcoming hackathons found.")

    if st.button("Logout"):
        st.session_state.clear()
        st.session_state.sponsor_view = 'verify'
        st.rerun()

# --- STEP 3: NEW SPONSOR REGISTRATION ---
elif st.session_state.sponsor_view == 'apply_new':
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.header("New Sponsorship Application")
        with st.form("new_reg_form"):
            reg_name = st.text_input("Company Name")
            reg_email = st.text_input("Contact Email")
            reg_url = st.text_input("Website URL")
            
            if st.form_submit_button("Send Application"):
                if reg_name and reg_email:
                    new_id = generate_new_id()
                    ins_q = """
                        INSERT INTO sponsor_table (sponsor_id, sponsor_name, email, website_url, status) 
                        VALUES (%s, %s, %s, %s, 'Pending')
                    """
                    execute_query(ins_q, (new_id, reg_name, reg_email, reg_url))
                    st.success(f"Application Sent! Your ID is {new_id}. Please wait for approval.")
                else:
                    st.error("Name and Email are required.")
        
        if st.button("⬅️ Back to Login"):
            st.session_state.sponsor_view = 'verify'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)