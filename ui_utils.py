import streamlit as st

def load_global_styles():
    st.markdown("""
        <style>
        /* 1. Full Page & Sidebar Layout */
        .block-container {
            padding-top: 2rem !important;
            max-width: 95% !important;
        }
        
        [data-testid="stSidebar"] { 
            background-color: #F5F1ED !important; 
            border-right: 1px solid #E0D5CC; 
        }

        /* 2. Navigation Menu Fix (YAHAN CHANGES KIYE HAIN) */
        
        /* 2. Navigation Menu Fix (Ab har haal mein dikhega!) */
        
        /* Poore radio group ke text ko target kar rahe hain */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            color: #5C4033 !important; 
            font-size: 16px !important; 
            font-weight: 600 !important;
            display: block !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        /* Selected state mein text white hi rahega */
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p {
            color: "#3E2723" !important;
        }

        /* Radio circles ko hide karne ka pakka tareeka */
        [data-testid="stSidebar"] [data-baseweb="radio"] div:first-child {
            display: none !important;
        }

        /* Buttons ki styling */
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            padding: 10px 15px !important;
            margin-bottom: 8px !important;
            border: 1px solid #E0D5CC !important;
            display: flex !important;
            align-items: center !important;
            min-height: 45px !important;
        }

        /* 3. KPI Cards Hover Fix */
        .kpi-card {
            background: white !important;
            border: 1px solid #E0D5CC !important;
            border-radius: 15px !important;
            padding: 20px !important;
            text-align: center !important;
            transition: all 0.3s ease-in-out !important;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.02) !important;
            display: block !important;
        }
        
        .kpi-card:hover {
            transform: translateY(-8px) !important;
            border-color: #A67B5B !important;
            box-shadow: 0 10px 20px rgba(166, 123, 91, 0.15) !important;
        }

        /* 4. Resource Circles Fix */
        .neon-circle {
            width: 100px !important;
            height: 100px !important;
            border-radius: 50% !important;
            border: 3px solid #A67B5B !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            background-color: white !important;
            margin: 0 auto !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        }
        
        .neon-circle strong { color: #3E2723 !important; font-size: 22px !important; display: block !important; }
        .neon-circle small { color: #A67B5B !important; font-size: 12px !important; display: block !important; }

        /* 5. Dataframes */
        .stDataFrame {
            border: 1px solid #E0D5CC !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def display_sidebar_header(user_name, role):
    st.sidebar.markdown(f"""
        <div style="padding: 10px 5px 20px 5px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 25px;">
                <div style="background: #A67B5B; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 18px;">404</div>
                <h2 style="color: #3E2723; font-size: 22px; margin: 0;">Found Club</h2>
            </div>
            <div style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #E0D5CC;">
                <p style="color: #3E2723; font-weight: bold; margin: 0; font-size: 15px;">{user_name}</p>
                <p style="color: #A67B5B; font-size: 11px; margin: 0; text-transform: uppercase;">{role}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)