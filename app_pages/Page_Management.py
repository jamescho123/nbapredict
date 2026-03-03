import streamlit as st
from nba_supabase_auth import require_admin, get_page_visibility, update_page_visibility

@require_admin
def app():
    st.header("⚙️ Page Management")
    st.info("Control visibility and access levels for application pages.")
    
    settings = get_page_visibility()
    
    if not settings:
        st.warning("No page settings found or DB error.")
        # Default list for initialization if empty
        known_pages = [
            'Home', 'News', 'Ranking', 'Simple Predict', 
            'Hybrid Predict', 'Check Stats', 'Predict', 'Chatbot',
            'Entity Extraction', 'Profile', 'User_Management', 'Page_Management'
        ]
        settings = {p: {'visible': True, 'min_role': 'user'} for p in known_pages}
    
    # Sort pages
    pages = sorted(settings.keys())
    
    # Header row
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    c1.markdown("**Page Name**")
    c2.markdown("**Visible**")
    c3.markdown("**Min Role**")
    c4.markdown("**Action**")
    
    # List pages
    for page in pages:
        config = settings[page]
        
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            col1.write(page)
            
            # Key needs to be unique
            is_visible = col2.checkbox("Show", value=config['visible'], key=f"vis_{page}", label_visibility="collapsed")
            
            roles = ['guest', 'user', 'admin']
            try:
                role_idx = roles.index(config['min_role'])
            except:
                role_idx = 1
                
            min_role = col3.selectbox("Role", list(roles), index=role_idx, key=f"role_{page}", label_visibility="collapsed")
            
            if col4.button("Save", key=f"save_{page}"):
                if update_page_visibility(page, is_visible, min_role):
                    st.success(f"Saved {page}")
                    st.rerun()
                else:
                    st.error("Error saving")
            
            st.markdown("---")

if __name__ == "__main__":
    app()
