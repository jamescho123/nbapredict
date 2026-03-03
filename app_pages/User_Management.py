import streamlit as st
import pandas as pd
from nba_supabase_auth import require_admin, get_all_users, update_user_status

@require_admin
def app():
    st.header("👥 User Management")
    st.info("Manage user accounts, roles, and access.")
    
    # Get all users
    users = get_all_users()
    
    if not users:
        st.warning("No users found.")
        return

    df = pd.DataFrame(users)
    
    # Display table
    st.dataframe(
        df,
        column_config={
            "UserID": st.column_config.TextColumn("ID", width="small"),
            "Email": "Email",
            "Username": "Username",
            "Role": "Role",
            "IsBanned": st.column_config.CheckboxColumn("Banned"),
            "CreatedAt": st.column_config.DatetimeColumn("Joined"),
            "LastLogin": st.column_config.DatetimeColumn("Last Login")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("### Update User Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Select User
        user_options = {f"{u['Username']} ({u['Email']})": u['UserID'] for u in users}
        selected_label = st.selectbox("Select User", options=list(user_options.keys()))
        selected_user_id = user_options[selected_label]
        
        # Get current status
        current_user = next((u for u in users if u['UserID'] == selected_user_id), None)
    
    if current_user:
        with col2:
            new_role = st.selectbox(
                "Role", 
                options=['user', 'admin'], 
                index=0 if current_user['Role'] == 'user' else 1
            )
        
        with col3:
            is_banned = current_user.get('IsBanned', False) if current_user else False
            new_ban_status = st.checkbox("🚫 Ban User", value=is_banned)
            
        if st.button("Update User", type="primary"):
            success, msg = update_user_status(selected_user_id, role=new_role, is_banned=new_ban_status)
            if success:
                st.success(f"Updated {current_user['Username']}: {msg}")
                st.rerun()
            else:
                st.error(f"Error: {msg}")

if __name__ == "__main__":
    app()
