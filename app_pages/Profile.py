"""
User Profile Page for NBA Prediction Website
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_supabase_auth import (
    check_authentication, get_user_preferences, update_user_preferences,
    get_user_prediction_history, get_user_stats, logout_user, is_admin
)

def app():
    if st.button("← Back to Home", key="back_profile", type="secondary"):
         st.session_state.current_page = 'Home'
         st.rerun()

    # Check authentication
    if not check_authentication():
        st.warning("Please login to access your profile")
        st.stop()

    # Admin check removed to allow regular users to access their profile
    # if not is_admin():
    #     st.error("🔒 Access Denied: This page is only available to administrators.")
    #     ...


    user_data = st.session_state.user_data
    
    st.title(f"👤 {user_data['username']}'s Profile")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Account", "Statistics", "Prediction History"])
    
    with tab1:
        st.header("Account Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Profile")
            st.write(f"**Username:** {user_data['username']}")
            st.write(f"**Email:** {user_data['email']}")
            st.write(f"**User ID:** {user_data['user_id']}")
        
        with col2:
            st.subheader("Preferences")
            
            # Get current preferences
            prefs = get_user_preferences(user_data['user_id'])
            
            if prefs is None:
                prefs = {
                    'favorite_team': None,
                    'theme': 'light',
                    'email_notifications': False
                }
            
            teams = [
                'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
                'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
                'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
                'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
                'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
                'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
                'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
                'Utah Jazz', 'Washington Wizards'
            ]
            
            current_team = prefs.get('favorite_team') or ""
            team_index = teams.index(current_team) + 1 if current_team in teams else 0
            
            # Personal Details
            st.markdown("##### Personal Details")
            
            favorite_teams = st.multiselect(
                "Favorite Teams",
                teams,
                default=prefs.get('favorite_teams', [])
            )
            
            # Primary favorite team (optional, can be selected from the list above or separate)
            favorite_team = st.selectbox(
                "Primary Favorite Team",
                [""] + teams,
                index=team_index,
                help="Select your main team for dashboard highlights"
            )
            
            age = st.number_input("Age", min_value=0, max_value=120, value=prefs.get('age') or 0)
            
            gender = st.selectbox(
                "Gender",
                ["", "Male", "Female", "Non-binary", "Other", "Prefer not to say"],
                index=["", "Male", "Female", "Non-binary", "Other", "Prefer not to say"].index(prefs.get('gender') or "")
            )
            
            col_loc1, col_loc2, col_loc3 = st.columns(3)
            with col_loc1:
                country = st.text_input("Country", value=prefs.get('country') or "")
            with col_loc2:
                state = st.text_input("State/Province", value=prefs.get('state') or "")
            with col_loc3:
                city = st.text_input("City", value=prefs.get('city') or "")

            st.markdown("##### App Settings")
            theme = st.selectbox(
                "Theme",
                ["light", "dark"],
                index=0 if prefs.get('theme', 'light') == 'light' else 1
            )
            
            email_notif = st.checkbox(
                "Email Notifications",
                value=prefs.get('email_notifications', False)
            )
            
            if st.button("Save Preferences", type="primary"):
                if update_user_preferences(
                    user_data['user_id'],
                    favorite_team=favorite_team if favorite_team else None,
                    theme=theme,
                    email_notifications=email_notif,
                    favorite_teams=favorite_teams,
                    age=age if age > 0 else None,
                    country=country if country else None,
                    state=state if state else None,
                    city=city if city else None,
                    gender=gender if gender else None
                ):
                    st.success("Preferences updated!")
                    st.rerun()
                else:
                    st.error("Failed to update preferences")
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", type="secondary"):
            logout_user()
            st.success("Logged out successfully!")
            st.session_state.current_page = 'Home'
            st.rerun()
    
    with tab2:
        st.header("Your Prediction Statistics")
        
        stats = get_user_stats(user_data['user_id'])
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Predictions", stats['total_predictions'])
            
            with col2:
                st.metric("Correct Predictions", stats['correct_predictions'])
            
            with col3:
                st.metric("Accuracy", f"{stats['accuracy']:.1f}%")
            
            with col4:
                st.metric("Avg Confidence", f"{stats['avg_confidence']:.1f}%")
            
            if stats['total_predictions'] > 0:
                # Show accuracy over time (if enough data)
                st.subheader("Performance Overview")
                
                if stats['accuracy'] >= 70:
                    st.success(f"Excellent! Your {stats['accuracy']:.1f}% accuracy is above average.")
                elif stats['accuracy'] >= 60:
                    st.info(f"Good job! Your {stats['accuracy']:.1f}% accuracy is solid.")
                elif stats['accuracy'] >= 50:
                    st.warning(f"Your {stats['accuracy']:.1f}% accuracy has room for improvement.")
                else:
                    st.error(f"Keep practicing! Your {stats['accuracy']:.1f}% accuracy will improve over time.")
            else:
                st.info("Make some predictions to see your statistics!")
        else:
            st.info("No statistics available yet. Start making predictions!")
    
    with tab3:
        st.header("Prediction History")
        
        history = get_user_prediction_history(user_data['user_id'], limit=50)
        
        if history:
            for pred in history:
                with st.expander(
                    f"{pred['game_date']} - {pred['away_team']} @ {pred['home_team']}",
                    expanded=False
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Your Prediction:** {pred['predicted_winner']}")
                        st.write(f"**Confidence:** {pred['confidence']:.1f}%")
                    
                    with col2:
                        if pred['actual_winner']:
                            st.write(f"**Actual Winner:** {pred['actual_winner']}")
                            if pred['is_correct']:
                                st.success("✓ Correct!")
                            else:
                                st.error("✗ Incorrect")
                        else:
                            st.info("Game not played yet")
                    
                    st.caption(f"Predicted on: {pred['created_at']}")
        else:
            st.info("No prediction history yet. Make your first prediction!")
    
    st.markdown("---")
    st.caption("🏀 NBA Prediction System - User Profile")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Profile - NBA Predictions",
        page_icon="👤",
        layout="wide"
    )
    app()
