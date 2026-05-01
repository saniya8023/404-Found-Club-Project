import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from database import execute_query
from ui_utils import load_global_styles, display_sidebar_header # Dono ek saath import


st.markdown("""
    <style>
    /* Sirf default multipage menu ko hide karega, aapka custom sidebar rahega */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)
# 1. Global Styles Load karein (Theme apply karne ke liye)
load_global_styles()

# --- ACCESS CONTROL ---
if 'logged_in' not in st.session_state or st.session_state.user['role'] != 'Admin Staff':
    st.error("Access Denied.")
    st.stop()

user = st.session_state.user

# --- SIDEBAR NAVIGATION ---
# --- SIDEBAR NAVIGATION (With Professional Icons) ---
with st.sidebar:
    # 1. Club Branding (Exact same as participant.py)
    st.markdown("""
        <div style='text-align: left;'>
            <h1 style='color: #8B4513; margin-bottom: 0; font-size: 40px; font-weight: 900;'>
                404 FOUND
            </h1>
            <p style='font-size: 20px; font-weight: bold; margin-top: -15px; letter-spacing: 2px;'>
                CLUB
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # 2. User Welcome & Styled Role Badge
    # 'user' dictionary se data nikal rahe hain jo login se aa raha hai
    st.markdown(f"### Welcome, **{user['user_name']}**")
    
    st.markdown(f"""
        <div style="
            background-color: #8B4513; 
            color: white; 
            padding: 2px 12px; 
            border-radius: 15px; 
            display: inline-block; 
            font-size: 12px; 
            font-weight: bold;
            margin-bottom: 20px;">
            👤 {user['role']}
        </div>
    """, unsafe_allow_html=True)
    
    # 3. Navigation Menu (Admin specific options with icons)
    # Variable ka naam 'selected' rakha hai takay niche logic mein use ho sakay
    selected = option_menu(
        menu_title=None,
        options=["Dashboard Overview", "Hackathons", "Workshops", "Teams & Participants", "Finance & Sponsors", "My Profile"],
        icons=["speedometer2", "trophy", "journal-bookmark", "people", "cash-stack", "person-circle"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#8B4513"}}
    )
    
    st.write("---") 

    # 4. Logout Logic
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("main.py")

# --- 1. DASHBOARD OVERVIEW ---
if selected == "Dashboard Overview":
    st.title("📊 System Analytics Overview")
    
    # Data fetch logic (Aapka logic bilkul sahi hai)
    t_teams = execute_query("SELECT COUNT(*) as total FROM team", fetch=True)[0]['total']
    t_funds = execute_query("SELECT SUM(funding_amount) as total FROM sponsor_hackathon", fetch=True)[0]['total'] or 0
    t_hacks = execute_query("SELECT COUNT(*) as total FROM hackathon_table", fetch=True)[0]['total']
    t_projs = execute_query("SELECT COUNT(*) as total FROM project", fetch=True)[0]['total']

    # --- Row 1: Stylish KPI Cards ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f'<div class="kpi-card"><small>Total Teams</small><h2>{t_teams}</h2></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="kpi-card"><small>Total Funding</small><h2>PKR {t_funds:,.0f}</h2></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="kpi-card"><small>Live Hackathons</small><h2>{t_hacks}</h2></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="kpi-card"><small>Total Projects</small><h2>{t_projs}</h2></div>', unsafe_allow_html=True)

    # --- Row 2: Dynamic Graphs ---
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Hackathons by Domain")
        df_domain = pd.DataFrame(execute_query("SELECT domain, COUNT(*) as count FROM hackathon_table GROUP BY domain", fetch=True))
        if not df_domain.empty:
            fig1 = px.pie(df_domain, values='count', names='domain', hole=0.4, 
                          template="plotly_white", 
                          color_discrete_sequence=['#A67B5B', '#D2B48C', '#E0D5CC', '#8B7E74'])
            st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Sponsor Contributions")
        df_sponsor = pd.DataFrame(execute_query("""
            SELECT s.sponsor_name, SUM(sh.funding_amount) as total 
            FROM sponsor_table s JOIN sponsor_hackathon sh ON s.sponsor_id = sh.sponsor_id 
            GROUP BY s.sponsor_name""", fetch=True))
        if not df_sponsor.empty:
            fig2 = px.bar(df_sponsor, x='sponsor_name', y='total', template="plotly_white",
                          color_discrete_sequence=['#A67B5B'])
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Row 3: Resource Summary (Circles) ---
    st.markdown("---")
    st.subheader("Resource Summary")
    c_judges = execute_query("SELECT COUNT(*) as total FROM user_master WHERE role='Judge'", fetch=True)[0]['total']
    c_mentors = execute_query("SELECT COUNT(*) as total FROM user_master WHERE role='Mentor'", fetch=True)[0]['total']
    c_parts = execute_query("SELECT COUNT(*) as total FROM user_master WHERE role='Participant'", fetch=True)[0]['total']
    c_spons = execute_query("SELECT COUNT(*) as total FROM sponsor_table", fetch=True)[0]['total']

    st.markdown(f"""
        <div style="display: flex; justify-content: space-around; padding: 20px 0;">
            <div class="neon-circle"><strong>{c_judges}</strong><small>Judges</small></div>
            <div class="neon-circle"><strong>{c_mentors}</strong><small>Mentors</small></div>
            <div class="neon-circle"><strong>{c_parts}</strong><small>Participants</small></div>
            <div class="neon-circle"><strong>{c_spons}</strong><small>Sponsors</small></div>
        </div>
    """, unsafe_allow_html=True)

    # --- Row 4: Tables ---
    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        st.subheader("⚖️ Judge Task Table")
        judge_data = execute_query("""
            SELECT u.user_name as Judge, t.team_name as Team 
            FROM user_master u 
            JOIN scores e ON u.user_id = e.judge_id 
            JOIN team t ON e.team_id = t.team_id""", fetch=True)
        st.table(pd.DataFrame(judge_data) if judge_data else pd.DataFrame(columns=["Judge", "Team"]))

    with t2:
        st.subheader("👨‍🏫 Mentor Status Table")
        mentor_data = execute_query("""
            SELECT u.user_name as Mentor, w.workshop_name as Workshop 
            FROM user_master u 
            JOIN workshop_table w ON u.user_id = w.mentor_id""", fetch=True)
        st.table(pd.DataFrame(mentor_data) if mentor_data else pd.DataFrame(columns=["Mentor", "Workshop"]))








# --- 2. HACKATHONS MANAGEMENT ---
# --- 2. HACKATHONS MANAGEMENT ---
# elif menu == "🏆 Hackathons":
#     st.title("🏆 Hackathon Management")s
    
#     # --- 1. CREATE SECTION ---
#     with st.expander("➕ Create New Hackathon"):
#         with st.form("new_hack_form"):
#             col1, col2 = st.columns(2)
#             h_name = col1.text_input("Hackathon Name")
#             h_domain = col2.selectbox("Domain", ["Web development", "AI", "Blockchain", "Cybersecurity","Data Science","Devops","Mobile app development"])
            
#             reg_d = st.date_input("Registration Deadline")
#             start_d = st.date_input("Start Date")
#             end_d = st.date_input("End Date")
            
#             prize = st.number_input("Prize Pool (PKR)", min_value=0, step=5000)
            
#             if st.form_submit_button("Launch Hackathon"):
                
#                 # 🔥 FIXED ID GENERATION (NO DUPLICATES)
#                 last_id_res = execute_query(
#                     "SELECT hackathon_id FROM hackathon_table ORDER BY hackathon_id DESC LIMIT 1",
#                     fetch=True
#                 )

#                 if last_id_res:
#                     last_id = last_id_res[0]['hackathon_id']   # e.g., H-025
#                     num = int(last_id.split('-')[1])
#                     new_h_id = f"H-{num+1:03d}"
#                 else:
#                     new_h_id = "H-001"

#                 default_status_id = 1 
                
#                 insert_query = """
#                     INSERT INTO hackathon_table (hackathon_id, hackathon_name, admin_id, domain, 
#                     reg_date, start_date, end_date, prize_pool, status_id) 
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """

#                 execute_query(insert_query, (
#                     new_h_id, h_name, user['user_id'], h_domain,
#                     reg_d, start_d, end_d, prize, default_status_id
#                 ))
                
#                 st.success(f"Hackathon '{h_name}' Created with ID {new_h_id}")
#                 st.rerun()

#     # --- 2. VIEW TABLE ---
#     st.subheader("Manage Existing Hackathons")
    
#     hacks = execute_query("""
#         SELECT h.hackathon_id, h.hackathon_name, h.domain, h.reg_date, 
#                h.start_date, h.end_date, h.prize_pool,
#                s.status_name, h.admin_id 
#         FROM hackathon_table h 
#         JOIN status_master s ON h.status_id = s.status_id
#     """, fetch=True)
    
#     if hacks:
#         h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1,2,2,1,1])
#         h_col1.markdown("**ID**")
#         h_col2.markdown("**Name**")
#         h_col3.markdown("**Status**")
#         h_col4.markdown("**Edit**")
#         h_col5.markdown("**Delete**")
#         st.markdown("---")

#         for h in hacks:
#             col_id, col_name, col_status, col_edit, col_del = st.columns([1,2,2,1,1])
#             col_id.write(h['hackathon_id'])
#             col_name.write(h['hackathon_name'])
#             col_status.write(f"🟢 {h['status_name']}")

#             # EDIT BUTTON
#             if col_edit.button("📝", key=f"edit_{h['hackathon_id']}"):
#                 st.session_state.editing_hack = h['hackathon_id']

#             # DELETE BUTTON
#             is_creator = (h['admin_id'] == user['user_id'])
#             if col_del.button("🗑️", key=f"del_{h['hackathon_id']}", disabled=not is_creator):
#                 execute_query("DELETE FROM hackathon_table WHERE hackathon_id = %s", (h['hackathon_id'],))
#                 st.warning(f"{h['hackathon_id']} Deleted")
#                 st.rerun()

#     else:
#         st.info("No hackathons found")

# #     # --- 🔥 EDIT FORM ---
# #     # --- EDIT HACKATHON LOGIC ---
# # if "editing_hack" in st.session_state:
# #     st.markdown("---")
# #     st.subheader(f"📝 Edit Hackathon: {st.session_state.editing_hack}")
    
# #     # Fetch existing data for this hackathon
# #     hack_data_list = execute_query(
# #         "SELECT * FROM hackathon_table WHERE hackathon_id = %s", 
# #         (st.session_state.editing_hack,), 
# #         fetch=True
# #     )
    
# #     if hack_data_list:
# #         hack_data = hack_data_list[0]
        
# #         with st.form("edit_hack_form"):
# #             e_name = st.text_input("Name", value=hack_data['hackathon_name'])
            
# #             # FIX: Convert Decimal to float to avoid StreamlitMixedNumericTypesError
# #             current_prize = float(hack_data['prize_pool']) if hack_data['prize_pool'] else 0.0
# #             e_prize = st.number_input("Prize", value=current_prize)
            
# #             e_domain = st.selectbox("Domain", 
# #                                   ["Web", "AI", "Blockchain", "Cybersecurity"],
# #                                   index=["Web", "AI", "Blockchain", "Cybersecurity"].index(hack_data['domain']))
            
# #             # Form ka apna Submit button (Lazmi hai)
# #             save_btn = st.form_submit_button("Update Details")
# #             cancel_btn = st.form_submit_button("Cancel Edit") # Optional second submit button

# #             if save_btn:
# #                 update_query = """
# #                     UPDATE hackathon_table
# #                     SET hackathon_name=%s, prize_pool=%s, domain=%s 
# #                     WHERE hackathon_id=%s
# #                 """
# #                 execute_query(update_query, (e_name, e_prize, e_domain, st.session_state.editing_hack))
# #                 st.success("Details Updated!")
# #                 del st.session_state.editing_hack # Edit mode khatam karne ke liye
# #                 st.rerun()
                
# #             if cancel_btn:
# #                 del st.session_state.editing_hack
# #                 st.rerun()
# # --- EDIT HACKATHON LOGIC (FIXED) ---
# if "editing_hack" in st.session_state:
#     st.markdown("---")
#     st.subheader(f"📝 Editing: {st.session_state.editing_hack}")
    
#     # Data fetch karein
#     hack_data_list = execute_query(
#         "SELECT * FROM hackathon_table WHERE hackathon_id = %s", 
#         (st.session_state.editing_hack,), 
#         fetch=True
#     )
    
#     if hack_data_list:
#         hack_data = hack_data_list[0]
        
#         # Form start
#         with st.form("edit_hackathion_form_unique"):
#             col1, col2 = st.columns(2)
            
#             # Fields
#             e_name = col1.text_input("Hackathon Name", value=hack_data['hackathon_name'])
            
#             # Numeric conversion fix
#             current_prize = float(hack_data['prize_pool']) if hack_data['prize_pool'] else 0.0
#             e_prize = col2.number_input("Prize Pool", value=current_prize)
            
#             # Domain selection
#             domains = ["Web development", "AI", "Blockchain", "Cybersecurity","Data Science","DevOps","Mobile app development","Cloud Computing"]
#             try:
#                 d_index = domains.index(hack_data['domain'])
#             except:
#                 d_index = 0
#             e_domain = st.selectbox("Domain", domains, index=d_index)
            
#             # Dates
#             e_reg = st.date_input("Registration Deadline", value=hack_data['reg_date'])
#             e_start = st.date_input("Start Date", value=hack_data['start_date'])
#             e_end = st.date_input("End Date", value=hack_data['end_date'])

#             # CRITICAL: Ye button form ke block ke andar hona lazmi hai
#             submitted = st.form_submit_button("Save All Changes", use_container_width=True)
            
#             if submitted:
#                 update_q = """
#                     UPDATE hackathon_table
#                     SET hackathon_name=%s, prize_pool=%s, domain=%s, 
#                         reg_date=%s, start_date=%s, end_date=%s 
#                     WHERE hackathon_id=%s
#                 """
#                 execute_query(update_q, (e_name, e_prize, e_domain, e_reg, e_start, e_end, st.session_state.editing_hack))
#                 st.success("Changes saved successfully!")
#                 del st.session_state.editing_hack
#                 st.rerun()

#         # Cancel button form ke bahar bhi rakh sakte hain ya andar bhi
#         if st.button("Cancel & Close"):
#             del st.session_state.editing_hack
#             st.rerun()





            # --- 2. HACKATHONS MANAGEMENT ---
elif selected == "Hackathons":
    st.title("🏆 Hackathon Management")

    # --- HELPER FUNCTION FOR DYNAMIC STATUS ---
    # --- HELPER FUNCTION FOR DYNAMIC STATUS ---
    # --- HELPER FUNCTION FOR DYNAMIC STATUS ---
    # --- HELPER FUNCTION FOR DYNAMIC STATUS ---
    def get_status_id_by_date(start_d, end_d):
        import datetime
        today = datetime.date.today()
        
        if start_d > today:
            status_text = "Upcoming"
        elif start_d == today:
            status_text = "Ongoing"
        elif end_d < today:
            status_text = "Evaluated"
        else:
            status_text = "Pending"

        last_status = execute_query("SELECT MAX(status_id) as last_id FROM status_master", fetch=True)
        new_status_id = (last_status[0]['last_id'] + 1) if last_status[0]['last_id'] is not None else 1
        
        execute_query("INSERT INTO status_master (status_id, status_name) VALUES (%s, %s)", (new_status_id, status_text))
        return new_status_id

    if "editing_hack" in st.session_state:
        st.markdown("---")
        st.subheader(f"📝 Editing: {st.session_state.editing_hack}")
        
        hack_data_list = execute_query("SELECT * FROM hackathon_table WHERE hackathon_id = %s", (st.session_state.editing_hack,), fetch=True)
        judges_list = execute_query("SELECT user_id, user_name FROM user_master WHERE role = 'Judge'", fetch=True)
        judge_map = {j['user_name']: j['user_id'] for j in judges_list}
        
        if hack_data_list:
            hack_data = hack_data_list[0]
            with st.form("edit_hackathion_form_unique"):
                col1, col2 = st.columns(2)
                e_name = col1.text_input("Hackathon Name", value=hack_data['hackathon_name'])
                e_prize = col2.number_input("Prize Pool", value=float(hack_data['prize_pool']), step=5000.0)
                
                domains = ["Web development", "AI", "Blockchain", "Cybersecurity","Data Science","DevOps","Mobile app development"]
                e_domain = st.selectbox("Domain", domains)
                
                j_names = list(judge_map.keys())
                e_judge = st.selectbox("Assign Judge", j_names)

                e_reg = st.date_input("Registration Deadline", value=hack_data['reg_date'])
                e_start = st.date_input("Start Date", value=hack_data['start_date'])
                e_end = st.date_input("End Date", value=hack_data['end_date'])

                if st.form_submit_button("Save All Changes"):
                    # Step 1: Current status_id leli jo hack_data mein pehle se hai
                    current_status_id = hack_data['status_id']

                    # Step 2: Naya status_text decide kiya dates ke mutabiq
                    import datetime
                    today = datetime.date.today()
                    if e_start > today:
                        new_status_text = "Upcoming"
                    elif e_start <= today <= e_end:
                        new_status_text = "Ongoing"
                    else:
                        new_status_text = "Evaluated"

                    # Step 3: status_master table mein isi ID ka naam update kiya
                    execute_query(
                        "UPDATE status_master SET status_name = %s WHERE status_id = %s",
                        (new_status_text, current_status_id)
                    )

                    # Step 4: Hackathon table mein baqi saari details update ki (status_id wahi rahi)
                    update_q = """
                        UPDATE hackathon_table
                        SET hackathon_name=%s, prize_pool=%s, domain=%s, 
                            reg_date=%s, start_date=%s, end_date=%s, 
                            judge_id=%s
                        WHERE hackathon_id=%s
                    """
                    execute_query(update_q, (e_name, e_prize, e_domain, e_reg, e_start, e_end, judge_map[e_judge], st.session_state.editing_hack))
                    
                    st.success("Changes saved successfully!")
                    del st.session_state.editing_hack
                    st.rerun()

    with st.expander("➕ Create New Hackathon"):
        judges_data = execute_query("SELECT user_id, user_name FROM user_master WHERE role = 'Judge'", fetch=True)
        judge_options = {j['user_name']: j['user_id'] for j in judges_data}

        with st.form("new_hack_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            h_name = col1.text_input("Hackathon Name")
            h_domain = col2.selectbox("Domain", ["Web development", "AI", "Blockchain", "Cybersecurity","Data Science","Devops"])
            h_judge = st.selectbox("Assign Judge", list(judge_options.keys()))
            h_problem = st.text_area("Problem Statement")
            
            reg_d = st.date_input("Registration Deadline")
            start_d = st.date_input("Start Date")
            end_d = st.date_input("End Date")
            prize = st.number_input("Prize Pool (PKR)", min_value=0, step=5000)
            
            if st.form_submit_button("Launch Hackathon"):
                if not h_name or not h_problem:
                    st.error("Please fill Name and Problem Statement.")
                else:
                    last_id_res = execute_query("SELECT hackathon_id FROM hackathon_table ORDER BY hackathon_id DESC LIMIT 1", fetch=True)
                    new_h_id = f"H-{int(last_id_res[0]['hackathon_id'].split('-')[1])+1:03d}" if last_id_res else "H-001"
                    
                    calc_status_id = get_status_id_by_date(start_d, end_d)

                    insert_q = """
                        INSERT INTO hackathon_table (hackathon_id, hackathon_name, admin_id, domain, reg_date, start_date, end_date, prize_pool, status_id, judge_id, problem_statement) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    execute_query(insert_q, (new_h_id, h_name, user['user_id'], h_domain, reg_d, start_d, end_d, prize, calc_status_id, judge_options[h_judge], h_problem))
                    st.success(f"✅ Launched {new_h_id}!")
                    st.rerun()
    # --- 2. VIEW TABLE ---
    st.subheader("Manage Existing Hackathons")
    
    hacks = execute_query("""
        SELECT h.hackathon_id, h.hackathon_name, h.domain, h.reg_date, 
               h.start_date, h.end_date, h.prize_pool,
               s.status_name, h.admin_id, u.user_name as judge_name
        FROM hackathon_table h 
        JOIN status_master s ON h.status_id = s.status_id
        LEFT JOIN user_master u ON h.judge_id = u.user_id
    """, fetch=True)
    
    if hacks:
        h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1,2,2,1,1])
        h_col1.markdown("**ID**")
        h_col2.markdown("**Name / Judge**")
        h_col3.markdown("**Status**")
        h_col4.markdown("**Edit**")
        h_col5.markdown("**Delete**")
        st.markdown("---")

        for h in hacks:
            col_id, col_name, col_status, col_edit, col_del = st.columns([1,2,2,1,1])
            col_id.write(h['hackathon_id'])
            col_name.write(f"**{h['hackathon_name']}**\n\n👨‍⚖️ {h['judge_name']}")
            col_status.write(f"{h['status_name']}")

            if col_edit.button("EDIT", key=f"edit_{h['hackathon_id']}"):
                st.session_state.editing_hack = h['hackathon_id']
                st.rerun()

            is_creator = (h['admin_id'] == user['user_id'])
            if col_del.button("DELETE", key=f"del_{h['hackathon_id']}", disabled=not is_creator):
                # STEP 1: Pehle database se pucho ke is hackathon ki status_id kya hai
                # Kyunki 'h' variable mein shayad status_id missing ho
                res = execute_query(
                    "SELECT status_id FROM hackathon_table WHERE hackathon_id = %s", 
                    (h['hackathon_id'],), 
                    fetch=True
                )
                
                if res:
                    s_id = res[0]['status_id']

                    # STEP 2: Hackathon delete karo
                    execute_query("DELETE FROM hackathon_table WHERE hackathon_id = %s", (h['hackathon_id'],))
                    
                    # STEP 3: Status Master se uski specific ID delete karo
                    execute_query("DELETE FROM status_master WHERE status_id = %s", (s_id,))
                    
                    st.warning(f"✅ {h['hackathon_id']} aur uska Status (ID: {s_id}) delete hogaye!")
                    st.rerun()
                else:
                    st.error("Status not match")
    else: 
         st.info("No hackathons found")
# --- 3. WORKSHOPS ---
# --- 3. WORKSHOPS MANAGEMENT (Finalized with Fixed Edit Form) ---
elif selected == "Workshops":
    st.title("📚 Workshop Management")

    # --- EDIT LOGIC (Uper display hoga jese Hackathon mein tha) ---
    if "editing_workshop" in st.session_state:
        st.info(f"📝 Editing Workshop: {st.session_state.editing_workshop}")
        w_to_edit = execute_query("SELECT * FROM workshop_table WHERE workshop_id = %s", (st.session_state.editing_workshop,), fetch=True)[0]
        
        with st.form("edit_workshop_form"):
            e_name = st.text_input("Workshop Title", value=w_to_edit['workshop_name'])
            e_url = st.text_input("Meeting URL", value=w_to_edit['workshop_url'])
            
            c1, c2 = st.columns(2)
            e_date = c1.date_input("Date", value=w_to_edit['workshop_date'])
            # Mentors and hacks for re-selection
            mentors_e = execute_query("SELECT user_id, user_name FROM user_master WHERE role='Mentor'", fetch=True)
            m_opts_e = {m['user_name']: m['user_id'] for m in mentors_e}
            e_mentor = c2.selectbox("Mentor", list(m_opts_e.keys()))
            
            # Form ke andar buttons
            btn_col1, btn_col2 = st.columns([1, 4])
            update_submit = btn_col1.form_submit_button("Update")
            cancel_submit = btn_col2.form_submit_button("Cancel Edit") # st.button ki jagah form_submit_button

            if update_submit:
                update_q = """
                    UPDATE workshop_table 
                    SET workshop_name=%s, workshop_url=%s, workshop_date=%s, mentor_id=%s 
                    WHERE workshop_id=%s
                """
                execute_query(update_q, (e_name, e_url, e_date, m_opts_e[e_mentor], st.session_state.editing_workshop))
                st.success("Workshop Updated!")
                del st.session_state.editing_workshop
                st.rerun()
            
            if cancel_submit:
                del st.session_state.editing_workshop
                st.rerun()

    # --- CREATE SECTION ---
    with st.expander("➕ Schedule New Workshop"):
        mentors = execute_query("SELECT user_id, user_name FROM user_master WHERE role='Mentor'", fetch=True)
        hacks_list = execute_query("SELECT hackathon_id, hackathon_name FROM hackathon_table", fetch=True)
        
        if not mentors or not hacks_list:
            st.warning("Mentors aur Hackathons ka hona lazmi hai.")
        else:
            with st.form("new_workshop_form"):
                w_name = st.text_input("Workshop Title")
                w_url = st.text_input("Workshop Meeting URL")
                
                col1, col2 = st.columns(2)
                w_date = col1.date_input("Workshop Date")
                mentor_options = {m['user_name']: m['user_id'] for m in mentors}
                selected_mentor_name = col2.selectbox("Assign Mentor", list(mentor_options.keys()))
                
                t1, t2 = st.columns(2)
                s_time = t1.time_input("Start Time")
                e_time = t2.time_input("End Time")
                
                hack_options = {h['hackathon_name']: h['hackathon_id'] for h in hacks_list}
                selected_hack_name = st.selectbox("Link to Hackathon", list(hack_options.keys()))
                
                if st.form_submit_button("Create Workshop"):
                    w_count = execute_query("SELECT COUNT(*) as c FROM workshop_table", fetch=True)[0]['c']
                    new_w_id = f"W-{w_count + 1:03d}"
                    
                    execute_query("""
                        INSERT INTO workshop_table 
                        (workshop_id, workshop_name, workshop_url, workshop_date, start_time, end_time, admin_id, mentor_id, hackathon_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (new_w_id, w_name, w_url, w_date, s_time.strftime('%H:%M:%S'), e_time.strftime('%H:%M:%S'), 
                          user['user_id'], mentor_options[selected_mentor_name], hack_options[selected_hack_name]))
                    
                    st.success("Workshop Created!")
                    st.rerun()

    st.markdown("---")

    # --- VIEW SECTION WITH HACKATHON STATUS ---
    st.subheader("📋 Scheduled Workshops")
    
    workshops_data = execute_query("""
        SELECT w.workshop_id, w.workshop_name, u.user_name as mentor_name, 
               h.hackathon_name, sm.status_name as hack_status, 
               w.workshop_date, w.start_time, w.workshop_url, w.admin_id
        FROM workshop_table w 
        JOIN user_master u ON w.mentor_id = u.user_id
        JOIN hackathon_table h ON w.hackathon_id = h.hackathon_id
        JOIN status_master sm ON h.status_id = sm.status_id
    """, fetch=True)

    if workshops_data:
        cols = st.columns([1, 2, 1.5, 2, 1, 1])
        headers = ["ID", "Workshop", "Mentor", "Hackathon/Status", "Edit", "Delete"]
        for col, h in zip(cols, headers): col.markdown(f"**{h}**")
        st.divider()

        for w in workshops_data:
            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1.5, 2, 1, 1])
            c1.write(w['workshop_id'])
            c2.markdown(f"**{w['workshop_name']}**")
            c2.caption(f"[Meeting Link]({w['workshop_url']})")
            c3.write(w['mentor_name'])
            
            c4.write(w['hackathon_name'])
            c4.caption(f"Status: {w['hack_status']} | 📅 {w['workshop_date']}")
            
            if c5.button("📝", key=f"ed_{w['workshop_id']}"):
                st.session_state.editing_workshop = w['workshop_id']
                st.rerun()

            is_owner = (w['admin_id'] == user['user_id'])
            if c6.button("🗑️", key=f"dl_{w['workshop_id']}", disabled=not is_owner, help="Sirf creator hi delete kar sakta hai"):
                execute_query("DELETE FROM workshop_attendees WHERE workshop_id = %s", (w['workshop_id'],))
                execute_query("DELETE FROM workshop_table WHERE workshop_id = %s", (w['workshop_id'],))
                st.warning("Deleted!")
                st.rerun()
# --- 4. TEAMS & SUBMISSIONS ---
elif selected == "Teams & Participants":
        st.title("👥 Idea Review & Shortlisting")
        
        # --- 1. DATA FETCHING (Filtering: Pending & Must have Project) ---
        # Humne GROUP_CONCAT use kiya hai taaki members ke naam ek line mein aa jayein
        pending_requests_query = """
         SELECT 
             t.team_id, 
             t.team_name, 
             t.admin_approval,
             h.hackathon_name,
             h.problem_statement,
             p.project_title,
             p.project_description,
             u_lead.user_name AS lead_name,
    -- Yahan tm_inner.user_id ko tm_inner.member_id se replace kiya hai
             (SELECT GROUP_CONCAT(u_m.user_name SEPARATOR ', ') 
             FROM team_members tm_inner
             JOIN user_master u_m ON tm_inner.member_id = u_m.user_id
              WHERE tm_inner.team_id = t.team_id) AS members_list
         FROM team t
         JOIN hackathon_table h ON t.hackathon_id = h.hackathon_id
         JOIN project p ON t.team_id = p.team_id
         JOIN user_master u_lead ON t.lead_id = u_lead.user_id
         WHERE t.admin_approval = 'Pending'
         LIMIT 0, 1000;
    """
        requests = execute_query(pending_requests_query, fetch=True)

        if not requests:
            st.success("No pending registration requests at the moment! 🎉")
        else:
            st.info(f"You have {len(requests)} pending ideas to review.")

            for req in requests:
                with st.expander(f"📌 Request from Team: {req['team_name']} (ID: {req['team_id']})"):
                    # Layout inside expander
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**🏆 Hackathon:** {req['hackathon_name']}")
                        st.markdown(f"**🎯 Problem Statement:**")
                        st.caption(req['problem_statement'])
                        st.markdown(f"**👤 Lead:** {req['lead_name']}")
                        st.markdown(f"**👥 Members:** {req['members_list']}")

                    with col2:
                        st.markdown(f"**💡 Project Title:** {req['project_title']}")
                        st.markdown(f"**📝 Idea Description:**")
                        st.write(req['project_description'])

                    # --- Action Buttons ---
                    b1, b2, _ = st.columns([1, 1, 2])
                    
                    with b1:
                        if st.button("✅ Approve", key=f"app_{req['team_id']}"):
                            execute_query("UPDATE team SET admin_approval = 'Accepted' WHERE team_id = %s", (req['team_id'],))
                            st.success(f"Team {req['team_name']} shortlisted!")
                            st.rerun()
                            
                    with b2:
                        if st.button("❌ Reject", key=f"rej_{req['team_id']}"):
                            execute_query("UPDATE team SET admin_approval = 'Rejected' WHERE team_id = %s", (req['team_id'],))
                            st.warning(f"Team {req['team_name']} rejected.")
                            st.rerun()

        st.markdown("---")
        
        # --- 2. SHORTLISTED TEAMS LIST (By Hackathon) ---
        # --- 2. SHORTLISTED TEAMS LIST (Categorized by Status) ---
        # --- 2. SHORTLISTED TEAMS LIST (Categorized by Status) ---
        # st.subheader("📋 Finalized Shortlists (By Category)")
        
        # # Query to get all accepted teams
        # shortlisted_data = execute_query("""
        #     SELECT t.team_id, t.team_name, h.hackathon_name, h.status 
        #     FROM team t 
        #     JOIN hackathon_table h ON t.hackathon_id = h.hackathon_id 
        #     WHERE t.admin_approval = 'Accepted'
        # """, fetch=True)

        # if shortlisted_data:
        #     # 1. Categories initialize karein exactly wese hi jese aapke dataset mein hain
        #     # Dictionary structure: { 'Status': { 'Hackathon Name': [Teams] } }
        #     categories = {
        #         "Upcoming": {},
        #         "Ongoing": {},
        #         "Evaluated": {}
        #     }
            
        #     # 2. Data ko Status aur phir Hackathon Name ke hisaab se group karein
        #     for row in shortlisted_data:
        #         status = row['status'].strip() # Extra spaces khatam karne ke liye
        #         h_name = row['hackathon_name']
                
        #         # Check karein ke status hamari predefined categories mein hai ya nahi
        #         if status in categories:
        #             if h_name not in categories[status]:
        #                 categories[status][h_name] = []
        #             categories[status][h_name].append(row)
        #         else:
        #             # Agar koi naya status mil jaye (optional debugging)
        #             if status not in categories:
        #                 categories[status] = {h_name: [row]}

        #     # 3. UI par sections display karein (Order: Upcoming -> Ongoing -> Evaluated)
        #     display_order = ["Upcoming", "Ongoing", "Evaluated"]
            
        #     for status in display_order:
        #         if status in categories and categories[status]: 
        #             st.markdown(f"## 📅 {status} Hackathons")
                    
        #             for h_name, teams in categories[status].items():
        #                 # Sirf 'Upcoming' wale expanders ko by default khula rakhein
        #                 is_expanded = (status == "Upcoming")
                        
        #                 with st.expander(f"🚀 {h_name} - ({len(teams)} Teams Shortlisted)", expanded=is_expanded):
        #                     import pandas as pd
        #                     df = pd.DataFrame(teams)[['team_id', 'team_name']]
        #                     df.columns = ['ID', 'Shortlisted Team Name']
        #                     st.table(df)
        #             st.markdown("---")
        # else:
        #     st.info("No teams have been shortlisted yet (Status: 'Accepted' teams only).")



# --- 2. SHORTLISTED TEAMS LIST (Categorized by Status) ---
        # --- 2. SHORTLISTED TEAMS LIST (Categorized by Status) ---
        st.subheader("📋 Finalized Shortlists (By Category)")
        
        # Updated Query with status_master join
        shortlisted_data = execute_query("""
            SELECT 
                t.team_id, 
                t.team_name, 
                h.hackathon_name, 
                sm.status_name AS status 
            FROM team t 
            JOIN hackathon_table h ON t.hackathon_id = h.hackathon_id 
            JOIN status_master sm ON h.status_id = sm.status_id
            WHERE t.admin_approval = 'Accepted'
        """, fetch=True)

        if shortlisted_data:
            # Baqi logic wahi rahega jo pehle tha
            categories = {
                "upcoming": {},
                "ongoing": {},
                "evaluated": {}
            }
            
            for row in shortlisted_data:
                # status_name ko check kar rahe hain
                db_status = str(row['status']).strip().lower()
                h_name = row['hackathon_name']
                
                if db_status in categories:
                    if h_name not in categories[db_status]:
                        categories[db_status][h_name] = []
                    categories[db_status][h_name].append(row)
                else:
                    if db_status not in categories:
                        categories[db_status] = {h_name: [row]}

            display_order = ["upcoming", "ongoing", "evaluated"]
            found_match = False

            for status_key in display_order:
                if status_key in categories and categories[status_key]:
                    found_match = True
                    st.markdown(f"## 📅 {status_key.capitalize()} Hackathons")
                    
                    for h_name, teams in categories[status_key].items():
                        is_expanded = (status_key == "upcoming")
                        with st.expander(f"🚀 {h_name} - ({len(teams)} Teams)", expanded=is_expanded):
                            import pandas as pd
                            df = pd.DataFrame(teams)[['team_id', 'team_name']]
                            df.columns = ['ID', 'Shortlisted Team Name']
                            st.table(df)
                    st.markdown("---")

            if not found_match:
                st.warning("Teams accepted hain lekin status match nahi ho raha.")
                st.write("Milne wale status:", [row['status'] for row in shortlisted_data])
        else:
            st.info("Abhi tak koi team 'Accepted' nahi hui hai.")





# # --- 5. FINANCE & SPONSORS ---
elif selected == "Finance & Sponsors":
    if 'active_admin_id' not in st.session_state:
        st.error("Access Denied: Admin session not found.")
        st.stop()

    st.title("💰 Finance & Sponsorship Management")
    st.markdown("---")

    # Styling for Request Cards
    st.markdown("""
        <style>
        .request-card {
            background-color: #FDF5E6;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #8D6E63;
            margin-bottom: 20px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("📩 Pending Funding Requests")
    
    # 1. Fetching Pending Requests
    query = "SELECT * FROM sponsor_table WHERE status = 'Pending'"
    pending_reqs = execute_query(query, fetch=True)

    if not pending_reqs:
        st.info("No pending sponsorship requests at the moment.")
    else:
        for req in pending_reqs:
            with st.container():
                st.markdown(f"""
                <div class="request-card">
                    <h4>Sponsor: {req['sponsor_name']}</h4>
                    <p><b>Email:</b> {req['email']}</p>
                    <p><b>Request Details:</b> {req['website_url']}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, _ = st.columns([1, 1, 3])
                
                # --- APPROVE LOGIC ---
                if col1.button("✅ Approve", key=f"app_{req['sponsor_id']}"):
                    try:
                        raw_info = req['website_url']
                        final_url = raw_info 
                        
                        # A. Check and Parse Funding Data
                        if "|" in raw_info and "Amt:" in raw_info:
                            parts = raw_info.split("|")
                            final_url = parts[0].strip() # Clean URL
                            funding_part = parts[1].strip() # "Amt: 5000 for AI Hackathon"
                            
                            # Safely split amount and hackathon name
                            if "for" in funding_part:
                                amt_str = funding_part.split("for")[0].replace("Amt:", "").strip()
                                h_name = funding_part.split("for")[1].strip()
                                
                                # Hackathon ID dhoondna
                                h_res = execute_query("SELECT hackathon_id FROM hackathon_table WHERE hackathon_name = %s", (h_name,), fetch=True)
                                
                                if h_res:
                                    hid = h_res[0]['hackathon_id']
                                    # Sponsor_Hackathon mein insertion (Pehle ye karein)
                                    execute_query(
                                        "INSERT INTO sponsor_hackathon (sponsor_id, hackathon_id, funding_amount) VALUES (%s, %s, %s)",
                                        (req['sponsor_id'], hid, float(amt_str))
                                    )
                                    st.toast(f"Finance Record Added: ${amt_str}")
                                else:
                                    st.error(f"Hackathon '{h_name}' not found. Check spelling!")
                        
                        # B. Update Sponsor Table (Hamesha hoga)
                        update_q = """
                            UPDATE sponsor_table 
                            SET status = 'Accepted', admin_id = %s, website_url = %s 
                            WHERE sponsor_id = %s
                        """
                        execute_query(update_q, (st.session_state.active_admin_id, final_url, req['sponsor_id']))
                        
                        st.success(f"Sponsor {req['sponsor_name']} approved and records updated!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error during approval: {e}")

                # --- REJECT LOGIC ---
                if col2.button("❌ Reject", key=f"rej_{req['sponsor_id']}"):
                    execute_query(
                        "UPDATE sponsor_table SET status = 'Rejected', admin_id = %s WHERE sponsor_id = %s",
                        (st.session_state.active_admin_id, req['sponsor_id'])
                    )
                    st.warning(f"Request {req['sponsor_id']} rejected.")
                    st.rerun()
    st.markdown("---")
    
    # 2. Financial Overview
    st.subheader("📊 Confirmed Sponsorships")
    finance_query = """
        SELECT sh.sponsor_id, s.sponsor_name, h.hackathon_name, sh.funding_amount 
        FROM sponsor_hackathon sh
        JOIN sponsor_table s ON sh.sponsor_id = s.sponsor_id
        JOIN hackathon_table h ON sh.hackathon_id = h.hackathon_id
    """
    confirmed_data = execute_query(finance_query, fetch=True)
    
    if confirmed_data:
        import pandas as pd
        df = pd.DataFrame(confirmed_data)
        st.dataframe(df, use_container_width=True)
        
        total_funds = df['funding_amount'].sum()
        st.metric("Total Revenue Generated", f"${total_funds:,.2f}")
    else:
        st.write("No confirmed funding records yet.")


# --- MY PROFILE SETTINGS ---
# --- MY PROFILE SETTINGS ---
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