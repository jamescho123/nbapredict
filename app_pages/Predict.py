import streamlit as st
from app_pages import Simple_Predict, Hybrid_Predict
from nba_supabase_auth import check_authentication

def legacy_manual_app():
    col1, col2 = st.columns([1, 5])
    with col2:
        st.subheader("Manual Game Selection")

    # Game selection
    st.subheader("Select Teams")
    col1, col2 = st.columns(2)

    with col1:
        home_team = st.selectbox("Home Team:", 
            ['Lakers', 'Celtics', 'Warriors', 'Bucks', 'Heat', 'Nuggets', 'Suns'])

    with col2:
        away_team = st.selectbox("Away Team:", 
            ['Lakers', 'Celtics', 'Warriors', 'Bucks', 'Heat', 'Nuggets', 'Suns'])

    if st.button("Predict Winner"):
        st.subheader("Prediction Results")
        st.write("Based on current team performance and historical data:")
        # Add prediction logic here
        st.write(f"Predicted Winner: {home_team} (65% confidence)")
        st.write("Key Factors:")
        st.write("- Home Court Advantage")
        st.write("- Recent Performance")
        st.write("- Head-to-Head Record")
        st.write("- Team Injuries")

def app():
    # Header
    st.title("🎯 NBA Prediction Center")
    
    # Check authentication
    is_authenticated = check_authentication()
    
    # Mode selection
    modes = {
        "Simple": "📊 Simple Predict (Database Stats)",
        "Hybrid": "🚀 Hybrid Predict (AI Powered)",
        "Manual": "🎲 Manual Demo"
    }
    
    # Selection using radio or tabs
    # Using pills/radio for clean look
    mode_selection = st.radio(
        "Select Prediction Mode:",
        options=list(modes.keys()),
        format_func=lambda x: modes[x],
        horizontal=True
    )
    
    st.markdown("---")
    
    if mode_selection == "Simple":
        # Simple Predict (Available to Guest)
        Simple_Predict.app()
        
    elif mode_selection == "Hybrid":
        # Hybrid Predict (Restricted to User)
        if not is_authenticated:
            st.warning("🔒 **Access Restricted**")
            st.info("Hybrid Predict is an advanced AI feature available only to registered users.")
            if st.button("🔑 Login / Sign Up", type="primary"):
                st.session_state.current_page = 'Login'
                st.rerun()
        else:
            Hybrid_Predict.app()
            
    elif mode_selection == "Manual":
        # Manual/Legacy (Restricted to User)
        if not is_authenticated:
            st.warning("🔒 **Access Restricted**")
            st.info("Manual Demo Mode is available only to registered users.")
            if st.button("🔑 Login / Sign Up", type="primary"):
                st.session_state.current_page = 'Login'
                st.rerun()
        else:
            legacy_manual_app() 