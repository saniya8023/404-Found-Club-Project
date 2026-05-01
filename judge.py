import streamlit as st
from streamlit_option_menu import option_menu
from database import execute_query # Aapka database helper
import datetime  # Yeh line lazmi honi chahiye


st.markdown("""
    <style>
    /* Sirf default multipage menu ko hide karega, aapka custom sidebar rahega */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Page Config
st.set_page_config(page_title="404 FOUND | Judge Dashboard", layout="wide")

# CSS Load karna
with open("assets/judge_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# User session check (Dummy for now, login se aayega)
if 'user' not in st.session_state:
    st.error("Please Login first")
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
    
    st.markdown(f"""
        <div style="background-color: #8B4513; color: white; padding: 2px 12px; border-radius: 15px; 
        display: inline-block; font-size: 12px; font-weight: bold; margin-bottom: 20px;">
            👤 {user['role']}
        </div>
    """, unsafe_allow_html=True)
    
    # Judge specific menu
    selected = option_menu(
        menu_title=None,
        options=["Assigned Tasks", "Evaluate Submissions", "Results Overview", "My Profile"],
        icons=["list-task", "pencil-square", "trophy", "person-circle"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#8B4513"}}
    )
    
    st.write("---") 

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("main.py")

# --- MAIN CONTENT LOGIC ---

if selected == "Assigned Tasks":
    st.title("📅 Your Assigned Hackathons")
    st.info("💡 **Note:** Please evaluate all projects within **two days** of the hackathon's end date to finalize results timely.")

    # 1. Database se judge ki assigned hackathons uthana
    # Hum 'status_master' join kar rahe hain taake current status (Ongoing/Upcoming) bhi dikha saken
    assigned_hacks = execute_query("""
        SELECT h.hackathon_id, h.hackathon_name, h.domain, h.start_date, h.end_date, s.status_name
        FROM hackathon_table h
        JOIN status_master s ON h.status_id = s.status_id
        WHERE h.judge_id = %s
        ORDER BY h.start_date ASC
    """, (user['user_id'],), fetch=True)

    if assigned_hacks:
        # 2. Layout create karna (Cards ke liye)
        for h in assigned_hacks:
            with st.container():
                # Custom HTML/CSS Card for each Hackathon
                st.markdown(f"""
                    <div style="
                        background-color: white; 
                        padding: 20px; 
                        border-radius: 15px; 
                        border-left: 8px solid #8B4513; 
                        box-shadow: 2px 4px 12px rgba(0,0,0,0.1); 
                        margin-bottom: 20px;
                        color: #5d3412;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h2 style="margin: 0; color: #8B4513;">🏆 {h['hackathon_name']}</h2>
                            <span style="
                                background-color: {'#e1f5fe' if h['status_name'] == 'Upcoming' else '#e8f5e9'}; 
                                color: {'#01579b' if h['status_name'] == 'Upcoming' else '#2e7d32'}; 
                                padding: 4px 12px; 
                                border-radius: 20px; 
                                font-size: 14px; 
                                font-weight: bold;">
                                {h['status_name']}
                            </span>
                        </div>
                        <p style="margin: 10px 0; font-size: 16px;"><b>Domain:</b> {h['domain']}</p>
                        <hr style="border: 0.5px solid #eee;">
                        <div style="display: flex; gap: 40px;">
                            <div>
                                <p style="margin: 0; font-size: 12px; color: #888;">START DATE</p>
                                <p style="margin: 0; font-weight: bold;">{h['start_date'].strftime('%d %b, %Y')}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 12px; color: #888;">END DATE</p>
                                <p style="margin: 0; font-weight: bold; color: #d32f2f;">{h['end_date'].strftime('%d %b, %Y')}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 12px; color: #888;">DEADLINE FOR RESULTS</p>
                                <p style="margin: 0; font-weight: bold; color: #8B4513;">
                                    {(h['end_date'] + datetime.timedelta(days=2)).strftime('%d %b, %Y')}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.empty()
        st.warning("No hackathons have been assigned to you yet.")

elif selected == "Evaluate Submissions":
    st.title("📝 Evaluate Submissions")
    
    # 1. Judge ki assigned hackathons fetch karna
    assigned_hacks = execute_query("""
        SELECT hackathon_id, hackathon_name, reg_date, start_date, end_date 
        FROM hackathon_table 
        WHERE judge_id = %s
    """, (user['user_id'],), fetch=True)
    
    if assigned_hacks:
        hack_options = {h['hackathon_name']: h for h in assigned_hacks}
        selected_h_name = st.selectbox("🎯 Select Hackathon to Review", list(hack_options.keys()))
        h_info = hack_options[selected_h_name]
        h_id = h_info['hackathon_id']

        # --- HACKATHON DETAILS HEADER ---
        st.markdown(f"""
            <div style="background-color: #fdf5e6; padding: 15px; border-radius: 10px; border: 1px solid #8B4513; margin-bottom: 25px;">
                <h4 style="margin:0; color: #8B4513;">📋 Hackathon Schedule: {selected_h_name}</h4>
                <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 14px;">
                    <span><b>📌 Reg Deadline:</b> {h_info['reg_date']}</span>
                    <span><b>🚀 Start Date:</b> {h_info['start_date']}</span>
                    <span><b>🏁 End Date:</b> {h_info['end_date']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. TEAMS CHECKING LOGIC - Updated for stability
        # Hum pehle team table se data lenge, phir project aur scores ko link karenge
        teams_query = """
            SELECT 
                t.team_id, t.team_name, 
                p.project_title, p.project_description, p.github_link,
                s.technical_score, s.innovative_score, s.evaluative_score
            FROM team t
            LEFT JOIN project p ON t.team_id = p.team_id
            LEFT JOIN scores s ON t.team_id = s.team_id AND t.hackathon_id = s.hackathon_id
            WHERE t.hackathon_id = %s
        """
        teams_data = execute_query(teams_query, (h_id,), fetch=True)

        if teams_data:
            for team in teams_data:
                # Value check (Handling None safely)
                t_score = team.get('technical_score')
                g_link = team.get('github_link')
                
                has_scores = t_score is not None
                has_submission = g_link is not None

                with st.expander(f"👥 Team: {team['team_name']}"):
                    col_info, col_status = st.columns([3, 1])

                    # SCENARIO 1: Evaluated
                    if has_scores:
                        col_status.markdown("#### <span style='color:green;'>✅ Evaluated</span>", unsafe_allow_html=True)
                        total = (team['technical_score'] or 0) + (team['innovative_score'] or 0) + (team['evaluative_score'] or 0)
                        st.write(f"**Final Score:** {total}/30")
                        st.write(f"(Tech: {team['technical_score']}, Inno: {team['innovative_score']}, Exec: {team['evaluative_score']})")

                    # SCENARIO 2: Submitted (Ready for marking)
                    elif has_submission:
                        col_status.markdown("#### <span style='color:blue;'>📥 Submitted</span>", unsafe_allow_html=True)
                        st.write(f"**Project:** {team['project_title'] or 'No Title'}")
                        st.link_button("📂 View GitHub Repository", g_link)
                        
                        with st.form(key=f"mark_form_{team['team_id']}"):
                            st.markdown("##### 🔢 Mark Scores")
                            c1, c2, c3 = st.columns(3)
                            ts = c1.number_input("Tech", 0, 10, key=f"ts_{team['team_id']}")
                            ins = c2.number_input("Inno", 0, 10, key=f"ins_{team['team_id']}")
                            es = c3.number_input("Exec", 0, 10, key=f"es_{team['team_id']}")
                            
                            if st.form_submit_button("Submit Evaluation"):
                                save_score_query = """
                                    INSERT INTO scores (team_id, hackathon_id, judge_id, technical_score, innovative_score, evaluative_score)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE 
                                    technical_score=%s, innovative_score=%s, evaluative_score=%s
                                """
                                execute_query(save_score_query, (
                                    team['team_id'], h_id, user['user_id'], ts, ins, es,
                                    ts, ins, es
                                ))
                                st.success("Marks saved!")
                                st.rerun()

                    # SCENARIO 3: Registered but No Submission
                    else:
                        col_status.markdown("#### <span style='color:orange;'>⏳ No Project</span>", unsafe_allow_html=True)
                        st.warning("Team registered but project not submitted yet.")
        else:
            st.info("No teams are currently registered for this hackathon.")
    else:
        st.error("No hackathons assigned to you.")

elif selected == "Results Overview":
    st.title("🏆 Finalized Standings")
    st.info("Showing results based on scores submitted by you.")

    # 1. Judge ki assigned hackathons fetch karna (taake unka result dikha saken)
    assigned_hacks = execute_query("""
        SELECT hackathon_id, hackathon_name 
        FROM hackathon_table 
        WHERE judge_id = %s
    """, (user['user_id'],), fetch=True)

    if assigned_hacks:
        hack_options = {h['hackathon_name']: h['hackathon_id'] for h in assigned_hacks}
        selected_h_name = st.selectbox("📊 Select Hackathon to View Results", list(hack_options.keys()))
        h_id = hack_options[selected_h_name]

        # 2. Leaderboard Query (Summing up all three scores)
        leaderboard_query = """
            SELECT 
                t.team_name, 
                s.technical_score, 
                s.innovative_score, 
                s.evaluative_score,
                (s.technical_score + s.innovative_score + s.evaluative_score) AS final_score
            FROM scores s
            JOIN team t ON s.team_id = t.team_id
            WHERE s.hackathon_id = %s
            ORDER BY final_score DESC
        """
        results = execute_query(leaderboard_query, (h_id,), fetch=True)

        if results:
            # Result ko table format mein dikhana
            st.write(f"### Leaderboard: {selected_h_name}")
            
            # Formatting for a better look
            import pandas as pd
            df = pd.DataFrame(results)
            df.index = df.index + 1  # 1-based ranking
            
            # Displaying with highlighting the winner
            st.table(df)
            
            st.success(f"🥇 Winner: **{results[0]['team_name']}** with {results[0]['final_score']} points!")
        else:
            st.warning("No scores have been submitted for this hackathon yet.")
    else:
        st.error("No hackathons assigned.")
        
# --- MY PROFILE SETTINGS ---
elif selected == "My Profile":  
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