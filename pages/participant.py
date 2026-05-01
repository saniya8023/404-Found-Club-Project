import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from database import execute_query

# --- participant.py ke top par ye paste karein ---
st.markdown("""
    <style>
    /* Sirf default multipage menu ko hide karega, aapka custom sidebar rahega */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

def participant_page():
    if 'user' not in st.session_state:
        st.error("Please login first!")
        return

    user_data = st.session_state.user
    user_id = user_data.get('user_id')
    user_name = user_data.get('user_name')
    user_role = user_data.get('role')

    # --- SIDEBAR ---
    # --- SIDEBAR ---
    with st.sidebar:
        # 1. Club Branding
        st.markdown("""
            <div style='text-align: left;'>
                <h1 style='color: #8B4513; margin-bottom: 0; font-size: 40px; font-weight: 900;'>
                    404 FOUND
                </h1>
                <p style='font-size: 20px; font-weight: bold; margin-top: -15px; letter-spacing: 2px;'>
                    CLUB
                </h1>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        # 2. User Welcome & Styled Role Badge
        st.markdown(f"### Welcome, **{user_name}**")
        
        # Role ko aik rounded box (Badge) mein dikhane ke liye
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
                👤 {user_role}
            </div>
        """, unsafe_allow_html=True)
        
        # 3. Navigation Menu (Aapke original options)
        selected = option_menu(
            menu_title=None,
            options=["My Activities", "Team Hub", "Explore & Register", "Messages", "My Profile", "About Us"],
            icons=["list-task", "people", "search", "chat-dots", "person-circle", "info-circle"],
            default_index=0,
            styles={"nav-link-selected": {"background-color": "#8B4513"}}
        )
        
        st.write("---") # Visual divider before logout

        # 4. Fixed Logout Logic
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            # switch_page use karne se wo wapis main entry point (Login) par chala jayega
            st.switch_page("main.py")

    # --- 1. MY ACTIVITIES ---
    if selected == "My Activities":
        st.title("📋 Your Participation Status")
        query = """
            SELECT t.team_name, t.admin_approval, h.hackathon_name, w.workshop_url
            FROM team t
            JOIN team_members tm ON t.team_id = tm.team_id
            JOIN hackathon_table h ON t.hackathon_id = h.hackathon_id
            LEFT JOIN workshop_table w ON h.hackathon_id = w.hackathon_id
            WHERE tm.member_id = %s
        """
        results = execute_query(query, (user_id,), fetch=True)
        if results:
            for row in results:
                status = row['admin_approval']
                with st.container(border=True):
                    st.subheader(f"Team: {row['team_name']}")
                    st.write(f"**Hackathon:** {row['hackathon_name']}")
                    st.write(f"**Status:** {status}")
                    if status == "Accepted":
                        st.success(f"🔗 [Join Workshop]({row['workshop_url']})")
        else:
            st.info("You haven't joined any team yet.")

    # --- 2. TEAM HUB ---
    # --- 2. TEAM HUB ---
    elif selected == "Team Hub":
        st.title("👥 Team Management Hub")
        # Teeno tabs: Create, Join, aur Request handling
        tab1, tab2, tab3 = st.tabs(["➕ Create Team", "🤝 Join a Team", "🔔 Manage Requests"])
        
        with tab1:
            st.subheader("Start a New Team")
            new_team_name = st.text_input("Enter Team Name")
            h_data = execute_query("""
                 SELECT h.hackathon_name 
                 FROM hackathon_table h
                 JOIN status_master s ON h.status_id = s.status_id 
                 WHERE s.status_name = 'Upcoming'
            """ , fetch=True)
            
            h_choice = st.selectbox("Select Hackathon", [r['hackathon_name'] for r in h_data])
            
            if st.button("Create & Become Lead"):
                if new_team_name:
                    # --- Simple & Direct ID Logic ---
                    # Sabse bari ID uthao jo 'T-' se shuru hoti ho
                    # --- FOOLPROOF ID LOGIC ---
                    # Database se direct max number mangwaein jo 'T-' format mein ho
                    res = execute_query("""
                        SELECT MAX(CAST(SUBSTRING_INDEX(team_id, '-', -1) AS UNSIGNED)) as max_id 
                        FROM team 
                        WHERE team_id LIKE 'T-%'
                    """, fetch=True)
                    
                    if res and res[0]['max_id'] is not None:
                        new_id_num = res[0]['max_id'] + 1
                        new_id = f"T-{str(new_id_num).zfill(3)}"
                    else:
                        # Sirf tab jab table bilkul khali ho ya koi T- wali ID na ho
                        new_id = "T-001"

                    # --- INSERT LOGIC ---
                    h_res = execute_query("SELECT hackathon_id FROM hackathon_table WHERE hackathon_name=%s", (h_choice,), fetch=True)
                    if h_res:
                        h_id = h_res[0]['hackathon_id']
                        
                        # Team table mein entry (registration_status 0 ke sath)
                        execute_query("""
                            INSERT INTO team (team_id, team_name, lead_id, hackathon_id, admin_approval, registration_status) 
                            VALUES (%s, %s, %s, %s, 'Pending', 0)
                        """, (new_id, new_team_name, user_id, h_id))
                        
                        # Lead ki entry team_members mein (Accepted status ke sath)
                        execute_query("INSERT INTO team_members (team_id, member_id, status) VALUES (%s, %s, 'Accepted')", (new_id, user_id))
                        
                        st.success(f"Team created! ID: {new_id}")
                    else:
                        st.error("Hackathon details not found.")

        with tab2:
            st.subheader("Available Teams")
            # Query update: Apni team hide ki hai aur sirf wo dikhengi jinmein user member nahi hai
            available_teams = execute_query("""
                SELECT t.team_id, t.team_name, h.hackathon_name, u.user_name as lead_name, u.phone_no
                FROM team t 
                JOIN hackathon_table h ON t.hackathon_id = h.hackathon_id
                JOIN user_master u ON t.lead_id = u.user_id
                WHERE t.lead_id != %s 
                AND t.team_id NOT IN (SELECT team_id FROM team_members WHERE member_id = %s)
                GROUP BY t.team_id 
                HAVING (SELECT COUNT(*) FROM team_members WHERE team_id = t.team_id AND status = 'Accepted') < 3
             """, (user_id, user_id), fetch=True)

            if available_teams:
                for team in available_teams:
                    with st.container(border=True):
                        col1, col2 = st.columns([3,1])
                        col1.write(f"**Team:** {team['team_name']} ({team['hackathon_name']})")
                        col1.write(f"👤 **Lead:** {team['lead_name']} | 📞 **Contact:** {team['phone_no']}")
                        if col2.button("Request to Join", key=f"join_{team['team_id']}"):
                            # Request bhejte waqt status 'Pending' insert hoga
                            execute_query("INSERT INTO team_members (team_id, member_id, status) VALUES (%s, %s, 'Pending')", (team['team_id'], user_id))
                            st.toast("Join request sent!")
                            st.rerun()
            else:
                st.info("No other teams available right now.")

        with tab3:
            st.subheader("Pending Join Requests")
            # Lead ko apne team ki pending requests dikhayenge
            my_requests = execute_query("""
                SELECT tm.team_id, tm.member_id, u.user_name, t.team_name 
                FROM team_members tm
                JOIN team t ON tm.team_id = t.team_id
                JOIN user_master u ON tm.member_id = u.user_id
                WHERE t.lead_id = %s AND tm.status = 'Pending'
            """, (user_id,), fetch=True)

            if my_requests:
                for req in my_requests:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2,1,1])
                        c1.write(f"**{req['user_name']}** wants to join **{req['team_name']}**")
                        if c2.button("✅ Accept", key=f"acc_{req['member_id']}_{req['team_id']}"):
                            execute_query("UPDATE team_members SET status = 'Accepted' WHERE team_id = %s AND member_id = %s", (req['team_id'], req['member_id']))
                            
                            # Check agar team complete (3 members) ho gayi hai to registration_status 1 kar dein
                            count_res = execute_query("SELECT COUNT(*) as total FROM team_members WHERE team_id = %s AND status = 'Accepted'", (req['team_id'],), fetch=True)
                            if count_res[0]['total'] == 3:
                                execute_query("UPDATE team SET registration_status = 1 WHERE team_id = %s", (req['team_id'],))
                            
                            st.success(f"{req['user_name']} added!")
                            st.rerun()
                        if c3.button("❌ Reject", key=f"rej_{req['member_id']}_{req['team_id']}"):
                            execute_query("DELETE FROM team_members WHERE team_id = %s AND member_id = %s", (req['team_id'], req['member_id']))
                            st.warning("Request rejected and removed.")
                            st.rerun()
            else:
                st.info("No pending requests for your team.")
# --- 3. EXPLORE & REGISTER (Colored Square Cards) ---
    elif selected == "Explore & Register":
        st.title("🏆 Explore Hackathons")

        # 1. Query to get hackathons with status names
        hacks = execute_query("""
            SELECT h.*, s.status_name 
            FROM hackathon_table h 
            JOIN status_master s ON h.status_id = s.status_id
        """, fetch=True)

        sections = ["Upcoming", "Ongoing", "Evaluated"]
        
        for section in sections:
            section_hacks = [h for h in hacks if h['status_name'] == section]
            
            if section_hacks:
                st.header(f"✨ {section} Events")
                cols = st.columns(3)
                
                for idx, h in enumerate(section_hacks):
                    with cols[idx % 3]:
                        curr_status = h['status_name']
                        status_color = "#FFD700" if curr_status == 'Upcoming' else "#00FF00" if curr_status == 'Ongoing' else "#808080"

                        st.markdown(f"""
                            <div style="background-color: #262730; border: 2px solid #8B4513; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 10px;">
                                <p style="color: {status_color}; font-weight: bold; margin:0;">{curr_status.upper()}</p>
                                <h3 style="color: #CD7F32; margin: 10px 0;">{h['hackathon_name']}</h3>
                                <p style="color: #bbb; font-size: 0.8em;">{h['domain']}</p>
                                <h4 style="color: #FFD700;">💰 ${h['prize_pool']}</h4>
                            </div>
                        """, unsafe_allow_html=True)

                        if curr_status == 'Upcoming':
                            if st.button("Register Now", key=f"reg_{h['hackathon_id']}", use_container_width=True):
                                st.session_state.selected_h_id = h['hackathon_id']
                                st.session_state.selected_h_name = h['hackathon_name']
                                st.rerun()
                        elif curr_status == 'Ongoing':
                            st.button("Active Event", disabled=True, use_container_width=True, key=f"on_{h['hackathon_id']}")
                        else:
                            st.button("Completed", disabled=True, use_container_width=True, key=f"ev_{h['hackathon_id']}")
                st.markdown("---")

        # --- REGISTRATION FORM SECTION ---
        if 'selected_h_id' in st.session_state:
            st.markdown("---")
            
            if 'user' in st.session_state:
                user = st.session_state.user 
            else:
                st.error("Session expired. Please login again.")
                st.stop()

            with st.form("reg_form"):
                st.subheader(f"📝 Registration Form: {st.session_state.selected_h_name}")
                st.info(f"Registering with Hackathon ID: {st.session_state.selected_h_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    t_id_input = st.text_input("Confirm Team ID (e.g., T-001)")
                    t_name_input = st.text_input("Team Name")
                    st.text_input("Lead Name (You)", value=user['user_name'], disabled=True)
                
                with col2:
                    member2_name = st.text_input("Member 2 Name")
                    member3_name = st.text_input("Member 3 Name")
                
                st.markdown("---")
                p_name = st.text_input("Project Name / Title")
                p_idea = st.text_area("Project Idea & Solution Description")
                
                c1, c2 = st.columns([1, 4])
                with c1:
                    submit_btn = st.form_submit_button("Submit Registration")
                with c2:
                    if st.form_submit_button("Cancel"):
                        del st.session_state.selected_h_id
                        st.rerun()

                if submit_btn:
                    if t_id_input and t_name_input and p_name and p_idea and member2_name and member3_name:
                        
                        # --- VERIFICATION LOGIC (Handling H-001 String format) ---
                        verify_query = """
                            SELECT registration_status FROM team 
                            WHERE team_id = %s 
                            AND team_name = %s 
                            AND hackathon_id = %s 
                            AND lead_id = %s
                            AND registration_status = 1
                        """
                        
                        # params ko carefully string mein convert kiya hai
                        params = (
                            str(t_id_input).strip(), 
                            str(t_name_input).strip(), 
                            str(st.session_state.selected_h_id).strip(), 
                            user['user_id']
                        )
                        
                        # execute_query with fetch=True is mandatory for SELECT
                        verification = execute_query(verify_query, params, fetch=True)

                        if verification:
                            try:
                                # 1. Insert Project
                                project_query = """
                                    INSERT INTO project (team_id, project_title, project_description) 
                                    VALUES (%s, %s, %s)
                                """
                                execute_query(project_query, (t_id_input, p_name, p_idea))
                                
                                # 2. Update Team Approval Status
                                update_query = "UPDATE team SET admin_approval = 'Pending' WHERE team_id = %s"
                                execute_query(update_query, (t_id_input,))
                                
                                st.success(f"✅ Registration for '{t_name_input}' submitted successfully!")
                                del st.session_state.selected_h_id
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Submission Error: {e}")
                        else:
                            st.error("❌ Verification Failed! Details match nahi huin.")
                            st.warning("Puri details check karein: Team ID, Name, aur status '1' hona chahiye.")
                    else:
                        st.error("⚠️ Please fill all fields.")
    # --- 4. MESSAGES (Back to original) ---
    elif selected == "Messages":
        st.title("💬 Mentor Messaging")
        mentor_query = """
            SELECT u.user_name, u.user_id FROM workshop_table w
            JOIN user_master u ON w.mentor_id = u.user_id
            JOIN hackathon_table h ON w.hackathon_id = h.hackathon_id
            JOIN team t ON h.hackathon_id = t.hackathon_id
            JOIN team_members tm ON t.team_id = tm.team_id
            WHERE tm.member_id = %s
        """
        mentors = execute_query(mentor_query, (user_id,), fetch=True)
        if mentors:
            st.write(f"Chatting with Mentor: **{mentors[0]['user_name']}**")
            msg = st.text_input("Type your message...")
            if st.button("Send"):
                st.markdown(f'<div style="background:#8B4513; padding:10px; border-radius:10px; color:white;">{msg}</div>', unsafe_allow_html=True)
                st.toast("Message sent!")
        else: st.info("Mentor chat will open after team approval.")

    
    # --- 5. MY PROFILE ---
    elif selected == "My Profile":
        st.title("👤 Account Settings")
        
        # Database se user ka current data uthao
        u_data = execute_query("SELECT * FROM user_master WHERE user_id=%s", (user_id,), fetch=True)[0]
        
        with st.container(border=True):
            st.subheader("Edit Personal Information")
            new_name = st.text_input("Name", value=u_data['user_name'])
            # Email field add kar di (Aapke schema mein user_id hi email hai)
            new_email = st.text_input("Email ", value=u_data['email'])
            new_phone = st.text_input("Phone", value=u_data['phone_no'])
            
            if st.button("Save Changes"):
                # Query mein email (user_id) ko bhi shamil kar liya
                # NOTE: Agar user_id PK hai, to ye tabhi work karega jab CASCADE updates on hon
                execute_query("""
                    UPDATE user_master 
                    SET user_name=%s, email=%s, phone_no=%s 
                    WHERE user_id=%s
                """, (new_name, new_email, new_phone, user_id))
                
                # Session state update karein takay login barqarar rahe naye email ke sath
                st.session_state.user_id = new_email
                st.success("Profile & Email Updated!")
                st.rerun()

        st.divider()
        
        # Delete Account Section
        with st.expander("Deactivate Profile"):
            st.write("Deleting your account is permanent and cannot be undone.")
            if st.button(" Confirm Delete Account"):
                execute_query("DELETE FROM user_master WHERE user_id=%s", (user_id,))
                st.session_state.clear()
                st.rerun()
    # --- 6. ABOUT US ---
   
    elif selected == "About Us":
        st.title("🌟 About NexusHack")
        
        # --- Section 1: Club Introduction ---
        st.header("🚀 404 Found Club")
        st.markdown("""
        **404 Found** is the premier tech community at **NED University**. We are a group of AI enthusiasts, 
        developers, and dreamers dedicated to pushing the boundaries of innovation. 
        
        NexusHack is our flagship platform, designed to bridge the gap between talented students 
        and high-stakes AI hackathons. Our mission is to ensure no talent goes 'unfound'.
        """)
        
        st.divider()

        # --- Section 2: Why Trust Us? ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎯 Our Vision")
            st.write("To create an ecosystem where every student has the resources to build real-world AI solutions.")
        with col2:
            st.subheader("🛡️ Our Values")
            st.write("Transparency, Innovation, and Collaboration. We value your hard work and technical growth.")

        st.divider()

        # --- Section 3: Sponsors (Grid Layout) ---
        # --- Section 3: Sponsors (Organized Grid) ---
        st.header("🤝 Our Global Sponsors")
        st.info("We are proud to be supported by industry leaders who believe in student potential.")
        
        sponsors = [
            {"name": "Google", "url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"},
            {"name": "Apple", "url": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"},
            {"name": "Amazon", "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"},
            {"name": "NVIDIA", "url": "https://upload.wikimedia.org/wikipedia/sco/2/21/Nvidia_logo.svg"},
            # {"name": "OpenAI", "url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg"},
            {"name": "Meta", "url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg"}
        ]

        # 4 ya 3 columns per row (Aapki choice hai, maine 4 kar diye hain takay chotay lagain)
        cols = st.columns(4) 
        
        for i, sponsor in enumerate(sponsors):
            # Safe check takay KeyError na aaye
            if 'url' in sponsor:
                with cols[i % 4]:
                    # container use karne se images ek hi line mein alignment mein rahengi
                    with st.container():
                        st.image(sponsor['url'], use_container_width=True)
                        st.caption(f"<center>{sponsor['name']}</center>", unsafe_allow_html=True)
            else:
                continue # Agar url missing hai to error nahi dega, skip kar dega
        # --- Section 4: Contact & Socials ---
        st.header("📞 Get In Touch")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**📧 Email**")
            st.write("support@404found.ned.edu")
        with c2:
            st.markdown("**📍 Location**")
            st.write("NED University, Karachi, Pakistan")
        with c3:
            st.markdown("**🌐 LinkedIn**")
            st.write("[404 Found Official](https://linkedin.com)")

        # Footer message
        st.markdown("<br><center><i>Made with ❤️ by 404 Found Team</i></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    participant_page()