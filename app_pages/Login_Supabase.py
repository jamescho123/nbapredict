"""
Login Page for NBA Prediction Website - Supabase Authentication
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_supabase_auth import (
    init_auth_session, login_user, register_user, 
    check_authentication, logout_user, reset_password
)

def app():
    """Main app function for Login page"""
    st.set_page_config(
        page_title="Login - NBA Predictions",
        page_icon="🏀",
        layout="wide"
    )
    
    # Initialize auth session
    init_auth_session()
    
    # Check if already authenticated
    if check_authentication():
        st.success(f"Welcome back, {st.session_state.user_data.get('username', st.session_state.user_data.get('email', 'User'))}!")
        st.info("You are already logged in. Navigate to other pages to use the NBA prediction system.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Logout", type="primary", use_container_width=True):
                logout_user()
                st.rerun()
        
        st.stop()

    # Login/Register tabs
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Reset Password"])

    with tab1:
        st.header("Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Logging in..."):
                        success, user_data, message = login_user(email, password)
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            # Set current_page to Home for redirect
                            st.session_state.current_page = 'Home'
                            st.info("Redirecting to Home...")
                            # Small delay to show success message
                            import time
                            time.sleep(1)
                            # Redirect will happen via rerun and Home page check
                            st.rerun()
                        else:
                            st.error(message)

    with tab2:
        st.header("Create Account")
        
        with st.form("register_form"):
            new_email = st.text_input("Email", key="reg_email",
                                      help="Valid email address")
            new_username = st.text_input("Username (optional)", key="reg_username",
                                        help="Display name (optional)")
            new_password = st.text_input("Password", type="password", key="reg_password",
                                        help="At least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                register = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if register:
                if not new_email or not new_password:
                    st.error("Please fill in email and password")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif not agree_terms:
                    st.error("Please agree to the Terms of Service")
                else:
                    with st.spinner("Creating account..."):
                        success, message = register_user(new_email, new_password, new_username if new_username else None)
                        
                        if success:
                            st.success(message)
                            st.info("Please check your email to verify your account before logging in.")
                            st.balloons()
                        else:
                            st.error(message)

    with tab3:
        st.header("Reset Password")
        st.info("Enter your email address and we'll send you a password reset link.")
        
        with st.form("reset_form"):
            reset_email = st.text_input("Email", key="reset_email")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                reset_submit = st.form_submit_button("Send Reset Link", type="primary", use_container_width=True)
            
            if reset_submit:
                if not reset_email:
                    st.error("Please enter your email address")
                else:
                    with st.spinner("Sending reset email..."):
                        success, message = reset_password(reset_email)
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

    # Footer
    st.markdown("---")
    st.caption("🏀 NBA Prediction System - Supabase Authentication")
    st.caption("🔐 Secure authentication powered by Supabase")

if __name__ == "__main__":
    app()

