import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION & STATE MANAGEMENT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Program Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'saved_programs' not in st.session_state:
    st.session_state.saved_programs = set()
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        "gpa": 3.5,
        "sat": 1100,
        "interests": ["Computer & IT", "Engineering"],
        "max_tuition": 25000,
        "loc": ["In-State"]
    }

# Custom CSS for "Pill" Badges
st.markdown("""
<style>
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
    }
    .badge-reach { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
    .badge-match { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .badge-safety { background-color: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .badge-neutral { background-color: #f5f5f5; color: #616161; border: 1px solid #e0e0e0; }
    
    /* Tweaking metric labels */
    [data-testid="stMetricLabel"] { font-size: 0.85rem; color: #666; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MOCK DATA GENERATION
# -----------------------------------------------------------------------------
@st.cache_data
def get_mock_programs():
    institutions = [
        {"name": "Tech State University", "type": "Public", "state": "CA", "setting": "Urban"},
        {"name": "Lincoln Private College", "type": "Private non-profit", "state": "NY", "setting": "Suburban"},
        {"name": "Midwest Polytech", "type": "Public", "state": "IL", "setting": "Rural"},
        {"name": "Coastal City College", "type": "Public (2-year)", "state": "FL", "setting": "Urban"},
        {"name": "Elite Research Inst.", "type": "Private non-profit", "state": "MA", "setting": "Urban"},
        {"name": "Southern A&M", "type": "Public", "state": "TX", "setting": "Rural"},
    ]
    
    programs = [
        {"name": "Computer Science", "field": "Computer & IT"},
        {"name": "Nursing (BSN)", "field": "Health & Medicine"},
        {"name": "Business Admin", "field": "Business"},
        {"name": "Mech Engineering", "field": "Engineering"},
        {"name": "Graphic Design", "field": "Arts & Design"},
        {"name": "Data Analytics", "field": "Computer & IT"},
    ]
    
    recommendations = []
    
    for i in range(20): 
        inst = random.choice(institutions)
        prog = random.choice(programs)
        
        # Correlate cost/earnings slightly
        net_price = random.randint(8000, 55000)
        base_earnings = 40000 if "Arts" in prog['field'] else 60000
        median_earnings = base_earnings + random.randint(-10000, 25000)
        
        match_score = random.randint(70, 99)
        fit_type = random.choice(["Reach", "Match", "Safety"])
        
        rec = {
            "id": i, # Unique ID for saving
            "program_name": prog["name"],
            "degree_level": "Bachelor's",
            "institution": inst["name"],
            "location": f"{inst['setting']}, {inst['state']}",
            "type": inst["type"],
            "match_score": match_score,
            "fit_type": fit_type,
            "net_price": net_price,
            "earnings_10yr": median_earnings,
            "debt_at_grad": random.randint(12000, 32000),
            "grad_rate": random.randint(45, 95),
            "field": prog["field"],
            "reason": f"Strong alignment with your interest in {prog['field']}."
        }
        recommendations.append(rec)
        
    return pd.DataFrame(recommendations).sort_values(by="match_score", ascending=False)

# -----------------------------------------------------------------------------
# 3. UI LAYOUT FUNCTIONS
# -----------------------------------------------------------------------------

def render_header():
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        st.title("AI Program Recommender")
        st.markdown("### Find the perfect college program based on your unique profile.")
    with c2:
        # Simple sidebar summary of saved items
        saved_count = len(st.session_state.saved_programs)
        st.metric("Shortlist", f"{saved_count}", help="Programs you have saved")

def render_input_tab():
    c_title, c_btn = st.columns([3, 1])
    with c_title:
        st.markdown("#### 📝 Step 1: Your Profile")
    with c_btn:
        if st.button("⚡ Quick Fill (Demo Persona)"):
            st.session_state.form_data = {
                "gpa": 3.8,
                "sat": 1350,
                "interests": ["Engineering", "Computer & IT"],
                "max_tuition": 45000,
                "loc": ["In-State", "Out-of-State"]
            }
            st.rerun()

    # Access current values from state
    defaults = st.session_state.form_data

    with st.form("profile_form"):
        with st.container(border=True):
            st.markdown("##### 👤 Who are you?")
            c1, c2, c3 = st.columns(3)
            with c1: st.radio("Current Status", ["High School Student", "Transfer", "Adult Learner"])
            with c2: st.selectbox("Citizenship", ["US Citizen", "International"])
            with c3: st.selectbox("Home State", ["California", "New York", "Texas", "Other"])

        with st.container(border=True):
            st.markdown("##### 📚 Academics & Interests")
            c1, c2 = st.columns(2)
            with c1:
                st.slider("GPA (Weighted)", 0.0, 5.0, defaults["gpa"], 0.1)
                st.multiselect("Interests", ["Computer & IT", "Business", "Health", "Engineering", "Arts"], default=defaults["interests"])
            with c2:
                st.number_input("SAT Score", 400, 1600, defaults["sat"])
                st.text_input("Dream Job / Keywords", placeholder="e.g. Robotics, AI, Sustainable Energy")

        with st.container(border=True):
            st.markdown("##### 💰 Budget")
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Max Annual Net Price ($)", 0, 90000, defaults["max_tuition"], step=1000, help="Tuition minus grants/scholarships")
            with c2:
                st.multiselect("Location Preference", ["In-State", "Out-of-State", "Anywhere"], default=defaults["loc"])

        submitted = st.form_submit_button("Generate Recommendations 🚀", type="primary", use_container_width=True)
        
        if submitted:
            st.session_state['has_run'] = True
            with st.spinner("Crunching numbers against IPEDS & College Scorecard database..."):
                time.sleep(1.2) # UX pause
            st.rerun()

def render_results_tab(df):
    st.markdown("#### 📊 Step 2: Recommendations")
    
    # 3.1 Data Vis: High Level View
    with st.expander("📈 View Cost vs. Earnings Analysis", expanded=True):
        st.caption("Programs in the top-left offer the best financial ROI (Low Cost, High Earnings).")
        st.scatter_chart(
            df,
            x='net_price',
            y='earnings_10yr',
            color='fit_type',
            size='match_score',
            height=300,
            use_container_width=True
        )

    st.divider()

    # 3.2 List of Cards
    # Filter/Sort Bar
    col_filter, col_sort = st.columns([3, 1])
    with col_filter:
        st.caption(f"Showing top {len(df)} matches based on your profile.")
    with col_sort:
        sort_opt = st.selectbox("Sort By", ["Best Match", "High Earnings", "Low Cost"], label_visibility="collapsed")
    
    # Sorting Logic
    if sort_opt == "High Earnings": df = df.sort_values("earnings_10yr", ascending=False)
    elif sort_opt == "Low Cost": df = df.sort_values("net_price", ascending=True)

    # Render Cards
    for index, row in df.iterrows():
        # Badge logic
        fit_style = "badge-match"
        if row['fit_type'] == "Reach": fit_style = "badge-reach"
        if row['fit_type'] == "Safety": fit_style = "badge-safety"

        # Native Container for the Card
        with st.container(border=True):
            # Top Row: Title + Match Score
            top_c1, top_c2 = st.columns([0.8, 0.2])
            with top_c1:
                st.markdown(f"""
                    <div style='display:flex; align-items:center;'>
                        <h4 style='margin:0; padding-right:10px;'>{row['program_name']}</h4>
                        <span class='badge {fit_style}'>{row['fit_type']}</span>
                    </div>
                    <span style='color:gray; font-size:0.9em;'>🏫 {row['institution']} • {row['location']}</span>
                """, unsafe_allow_html=True)
            with top_c2:
                st.metric("Match", f"{row['match_score']}%")

            st.markdown("---")

            # Middle Row: Contextual Metrics (Green/Red Deltas)
            # Benchmarks: Avg Cost ~$25k, Avg Earnings ~$50k
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Net Price", f"${row['net_price']:,}", 
                      delta=f"${25000 - row['net_price']:,}" if row['net_price'] < 25000 else f"-${row['net_price'] - 25000:,}",
                      help="Annual cost after aid. Green is cheaper than national avg.")
            
            m2.metric("Median Earnings", f"${row['earnings_10yr']:,}", 
                      delta=f"${row['earnings_10yr'] - 50000:,}",
                      help="10 years after entry. Green is higher than national avg.")
            
            m3.metric("Grad Rate", f"{row['grad_rate']}%", f"{row['grad_rate'] - 60}%")
            
            # Action Row
            is_saved = row['id'] in st.session_state.saved_programs
            save_label = "❤️ Saved" if is_saved else "🤍 Save to Shortlist"
            
            # Collapsible Details (First one opens by default)
            with st.expander("Why this recommendation?", expanded=(index == 0)):
                st.write(f"**AI Analysis:** {row['reason']}")
                st.info(f"💡 **Career Insight:** This program feeds into high-demand roles in the {row['field']} sector, where regional growth is +12%.")
                
                btn_col1, btn_col2 = st.columns([1, 4])
                if btn_col1.button(save_label, key=f"save_{row['id']}"):
                    if is_saved:
                        st.session_state.saved_programs.remove(row['id'])
                    else:
                        st.session_state.saved_programs.add(row['id'])
                    st.rerun()

# -----------------------------------------------------------------------------
# 4. MAIN APP LOGIC
# -----------------------------------------------------------------------------

def main():
    render_header()
    
    # Initialize session state for data persistence
    if 'data' not in st.session_state:
        st.session_state['data'] = get_mock_programs()
    if 'has_run' not in st.session_state:
        st.session_state['has_run'] = False

    tab1, tab2, tab3 = st.tabs(["📝 Step 1: Input Profile", "🚀 Step 2: Results", "⚙️ Data View"])

    with tab1:
        render_input_tab()
        
    with tab2:
        if st.session_state['has_run']:
            render_results_tab(st.session_state['data'])
        else:
            # Smart Empty State (Pre-search value)
            st.info("👈 Please complete your profile in Step 1 to see recommendations.")
            st.markdown("#### National Trends (Live Data Preview)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg. Public Tuition", "$10,500", "+2.1%")
            c2.metric("Highest Demand Field", "Healthcare", "Growing")
            c3.metric("Avg. Starting Salary", "$55,000", "+4.5%")
            st.caption("Complete your profile to see how you compare to these benchmarks.")

    with tab3:
        st.markdown("### ⚙️ Raw Data Warehouse")
        st.dataframe(st.session_state['data'])

    st.markdown("---")
    st.caption("v3.0 | AI Program Recommender Demo")

if __name__ == "__main__":
    main()