import streamlit as st
from datetime import datetime, date, timedelta
from importlib import import_module
import pandas as pd
from db_config import get_connection, DB_SCHEMA
from nba_supabase_auth import check_authentication, is_admin, logout_user


def render_page(module_name):
    """Import page modules lazily so one broken page does not stop the whole app."""
    try:
        module = import_module(f"app_pages.{module_name}")
        module.app()
    except Exception as e:
        st.error(f"Failed to load page '{module_name}': {e}")

def main():
    st.set_page_config(
        page_title="NBA Predict",
        page_icon="🏀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state for page navigation (before auth check)
    if 'current_page' not in st.session_state:
        # Default to Landing page for new visitors
        st.session_state.current_page = 'Landing'
        
    # Check for query parameters for navigation
    query_params = st.query_params
    if 'nav' in query_params:
        target_page = query_params['nav']
        if target_page in ['Home', 'Predict', 'Chatbot', 'News']:
            st.session_state.current_page = target_page
        # Clear param to avoid sticky navigation
        st.query_params.clear()

    # Check for News ID in query parameters
    if 'news_id' in query_params and st.session_state.current_page != 'News Detail':
        # Only switch if not already there, to avoid loops or state fighting
        st.session_state.current_page = 'News Detail'
        st.session_state.selected_news_id = query_params['news_id']
    
    # Get page visibility settings
    from nba_supabase_auth import get_page_visibility
    page_settings = get_page_visibility()
    
    # Defaults if DB fails
    if not page_settings:
        page_settings = {
            'Landing': {'visible': True, 'min_role': 'guest'},
            'Home': {'visible': True, 'min_role': 'guest'},
            'News': {'visible': False, 'min_role': 'guest'},
            'Ranking': {'visible': False, 'min_role': 'guest'},
            'Simple Predict': {'visible': False, 'min_role': 'guest'},
            'Hybrid Predict': {'visible': False, 'min_role': 'user'},
            'Check Stats': {'visible': False, 'min_role': 'user'},
            'News Search': {'visible': True, 'min_role': 'user'},
            'News Detail': {'visible': True, 'min_role': 'guest'},
            'Chatbot': {'visible': True, 'min_role': 'user'},
            'Predict': {'visible': True, 'min_role': 'guest'},
            'Profile': {'visible': True, 'min_role': 'admin'},
            'User_Management': {'visible': True, 'min_role': 'admin'},
            'Page_Management': {'visible': True, 'min_role': 'admin'},
            'News_Image_Manager': {'visible': True, 'min_role': 'admin'}
        }

    # Check authentication
    is_authenticated = check_authentication()
    
    user_role = 'guest'
    user_role = 'guest'
    if is_authenticated and st.session_state.user_data:
        user_role = st.session_state.user_data.get('role', 'user')

    # Security Check for Current Page
    current_page = st.session_state.current_page
    if current_page != 'Login':
        page_config = page_settings.get(current_page, {'visible': True, 'min_role': 'user'}) # Default to user restriction if unknown
        
        # Check permissions
        has_access = False
        allowed_roles = ['guest', 'user', 'admin']
        
        min_role_idx = allowed_roles.index(page_config['min_role'])
        current_role_idx = allowed_roles.index(user_role)
        
        if current_role_idx >= min_role_idx:
            has_access = True
            
        if not has_access:
            if not is_authenticated:
                st.session_state.current_page = 'Login'
                # Don't return, let it fall through to routing
            else:
                st.error("⛔ Access Denied: You do not have permission to view this page.")
                if st.button("🏠 Return Home"):
                    st.session_state.current_page = 'Home'
                    st.rerun()
                return

    # Custom CSS for ESPN/NBA style
    st.markdown("""
    <style>
    /* ESPN/NBA Inspired Styles */
    .main-header {
        background: linear-gradient(135deg, #C8102E 0%, #1D428A 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    .game-card {
        background: white;
        border-left: 4px solid #C8102E;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .game-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .news-card {
        background: #f8f9fa;
        border-left: 4px solid #1D428A;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .stat-box {
        background: linear-gradient(135deg, #1D428A 0%, #C8102E 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-box h3 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    .stat-box p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
    }
    .section-header {
        color: #1D428A;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #C8102E;
        padding-bottom: 0.5rem;
    }
    .ticker-container {
        background: #1D428A;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .feature-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
    }
    .feature-card:hover {
        border-color: #C8102E;
        box-shadow: 0 4px 12px rgba(200,16,46,0.2);
        transform: translateY(-2px);
    }
    .feature-card h4 {
        color: #1D428A;
        margin-top: 0.5rem;
    }
    .nav-button {
        background: linear-gradient(135deg, #1D428A 0%, #C8102E 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        margin: 0.5rem 0;
    }
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .page-nav-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar with user info and navigation
    if st.session_state.current_page != 'Landing':
        with st.sidebar:
            # User info
            if is_authenticated:
                user_data = st.session_state.user_data
                role = user_data.get('role', 'user')
                role_badge = "👑 Admin" if role == 'admin' else "👤 User"
                
                st.markdown(f"### {role_badge}")
                st.markdown(f"**{user_data.get('username', user_data.get('email', 'User'))}**")
                st.caption(f"Role: {role.upper()}")
                st.markdown("---")
                
                if st.button("🚪 Logout", use_container_width=True):
                    logout_user()
                    st.session_state.current_page = 'Home'
                    st.rerun()
            else:
                st.info("👋 Welcome Guest")
                if st.button("🔑 Login / Sign Up", use_container_width=True, type="primary"):
                    st.session_state.current_page = 'Login'
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Navigation")
            
            # Define Navigation Items based on access
            # Format: (Label, Page, RequiredRole)
            all_nav_items = [
                ("🚀 Welcome", "Landing", "guest"),
                ("🏠 Home", "Home", "guest"),
                ("📈 Predict", "Predict", "guest"),
                ("🤖 Chatbot", "Chatbot", "user"),
            ]
            
            # Filter visible items based on roles and DB visibility
            for label, page_name, default_role in all_nav_items:
                # Check DB visibility settings
                settings = page_settings.get(page_name, {'visible': True, 'min_role': default_role})
                
                if not settings['visible']:
                    continue
                    
                # Check role access
                min_role_idx = ['guest', 'user', 'admin'].index(settings['min_role'])
                current_role_idx = ['guest', 'user', 'admin'].index(user_role)
                
                if current_role_idx >= min_role_idx:
                    button_type = "primary" if st.session_state.current_page == page_name else "secondary"
                    if st.button(label, use_container_width=True, type=button_type):
                        st.session_state.current_page = page_name
                        st.rerun()

            # Admin Section
            if is_admin():
                st.markdown("---")
                st.markdown("### Admin")
                admin_pages = [
                    ("👑 Admin Profile", "Profile"),
                    ("👥 User Management", "User_Management"),
                    ("⚙️ Page Management", "Page_Management"),
                    ("🖼️ News Images", "News_Image_Manager")
                ]
                
                for label, page_name in admin_pages:
                     # Check access for admin pages too (e.g. if we want to hide them?)
                     # Usually always visible to admin, but check settings
                     settings = page_settings.get(page_name, {'visible': True})
                     if settings['visible']:
                        button_type = "primary" if st.session_state.current_page == page_name else "secondary"
                        if st.button(label, use_container_width=True, type=button_type):
                            st.session_state.current_page = page_name
                            st.rerun()

    # Route to appropriate page
    if st.session_state.current_page == 'Landing':
        landing_page_view()
    elif st.session_state.current_page == 'Home':
        home_page()
    elif st.session_state.current_page == 'Login':
        render_page("Login_Supabase")
    elif st.session_state.current_page == 'Profile':
        if is_admin():
            render_page("Profile")
    elif st.session_state.current_page == 'User_Management':
        if is_admin():
            render_page("User_Management")
    elif st.session_state.current_page == 'Page_Management':
        if is_admin():
            render_page("Page_Management")
    elif st.session_state.current_page == 'News_Image_Manager':
        if is_admin():
            render_page("News_Image_Manager")
    elif st.session_state.current_page == 'Check Stats':
        render_page("Check_Stats")
    elif st.session_state.current_page == 'News':
        render_page("News")
    elif st.session_state.current_page == 'News Detail':
        render_page("News_Detail")

    elif st.session_state.current_page == 'Entity Extraction':
        render_page("Entity_Extraction")
    elif st.session_state.current_page == 'Predict':
        render_page("Predict")
    elif st.session_state.current_page == 'Simple Predict':
        render_page("Simple_Predict")
    elif st.session_state.current_page == 'Hybrid Predict':
        render_page("Hybrid_Predict")
    elif st.session_state.current_page == 'Ranking':
        render_page("Ranking")
    elif st.session_state.current_page == 'Chatbot':
        render_page("Chatbot")


def landing_page_view():
    """Render the marketing landing page"""
    try:
        import os
        import streamlit.components.v1 as components
        
        # Performance/Visual Tweak: Remove Streamlit padding and hide sidebar/header
        st.markdown("""
            <style>
                #root > div:nth-child(1) > div > div > div > div > section > div {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
                [data-testid="stHeader"] {
                    display: none;
                }
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Read HTML and CSS
        with open('marketing_landing.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        with open('marketing.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # Inject CSS and tweak links for Streamlit routing
        html_content = html_content.replace('href="Home.py"', 'href="/?nav=Home"')
        
        # Combine CSS into HTML
        full_html = f"<style>{css_content}</style>\n{html_content}"
        
        # Render as component
        # Using a large height to ensure the content fits
        components.html(full_html, height=4500, scrolling=False)
        
    except Exception as e:
        st.error(f"Error loading landing page: {e}")
        # Fallback to home if landing fails
        st.session_state.current_page = 'Home'
        st.rerun()


def get_latest_news(limit=5):
    """Get latest news from database"""
    try:
        conn = get_connection()
        query = f'''
        SELECT "NewsID", "Title", "Content", "Date", "Source", "URL", "ImageURL"
        FROM "{DB_SCHEMA}"."News"
        ORDER BY "Date" DESC
        LIMIT %s
        '''
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def get_team_standings_preview(limit=5):
    """Get top teams for standings preview"""
    try:
        conn = get_connection()
        query = f'''
        SELECT "TeamName", "Wins", "Losses", 
               ROUND("Wins"::numeric / NULLIF("Wins" + "Losses", 0), 3) as "WinPct"
        FROM "{DB_SCHEMA}"."Teams"
        WHERE "Wins" IS NOT NULL AND "Losses" IS NOT NULL
        ORDER BY "WinPct" DESC, "Wins" DESC
        LIMIT %s
        '''
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        return []

def home_page():
    # User role indicator
    if check_authentication():
        user_data = st.session_state.user_data
        role = user_data.get('role', 'user')
        username = user_data.get('username', user_data.get('email', 'User'))
        
        if role == 'admin':
            st.info(f"👑 **Welcome, Administrator {username}!** You have full access to all features including the Admin Profile.")
        else:
            st.success(f"👤 **Welcome, {username}!** You are logged in as a regular user.")
    
    # Hero Section
    hero_col1, hero_col2 = st.columns([1, 5], gap="medium")
    with hero_col1:
        st.image("assets/logo.png", use_container_width=True)
    with hero_col2:
        st.markdown("""
        <div class="main-header" style="margin-bottom: 0;">
            <h1>🏀 NBA PREDICT</h1>
            <p>Your Ultimate Destination for NBA Statistics, News & AI-Powered Predictions</p>
        </div>
        """, unsafe_allow_html=True)

    # Platform Feature Overview
    with st.expander("📖 Platform Capabilities Overview", expanded=True):
        st.markdown("""
        ### Welcome to the NBA Predict Platform
        
        This application leverages state-of-the-art AI to provide deep insights into NBA games. Here is what you can do:
        
        **🎯 Hybrid Predictions**
        Our flagship prediction engine combines four distinct models to forecast game outcomes:
        - **Quantitative:** Time-series analysis of historical trends and advanced player/team statistics.
        - **Qualitative:** Sentiment analysis of news articles and LLM-based strategic reasoning.
        - **Vector Enhancement:** Finds historically similar matchups to refine probabilities.
        
        **🤖 AI Chatbot Assistant**
        Interact with your data using natural language. Ask questions like *"Who will win Lakers vs Warriors?"* or *"Stats for Curry"* and get:
        - **Real-time Answers:** Fetched directly from the latest database stats.
        - **Player Profiles:** Detailed cards for specific players.
        - **News Summaries:** AI-generated summaries of the latest team and player news.
        
        **📅 Live Dashboard**
        View today's schedule, upcoming games, and live scores (when connected to live data sources).
        """)
    
    st.markdown("---")
    
    # Today's Games Ticker
    st.markdown('<div class="section-header">📅 TODAY\'S GAMES</div>', unsafe_allow_html=True)
    
    try:
        from database_prediction import get_games_today
        today_games = get_games_today()
        
        if today_games:
            st.markdown('<div class="ticker-container">', unsafe_allow_html=True)
            cols = st.columns(min(len(today_games), 3))
            for idx, game in enumerate(today_games[:6]):
                col_idx = idx % 3
                with cols[col_idx]:
                    time_str = ""
                    if game.get('Time'):
                        try:
                            if isinstance(game['Time'], str):
                                time_str = game['Time'][:5] if len(game['Time']) >= 5 else game['Time']
                            else:
                                time_str = str(game['Time'])[:5]
                        except:
                            time_str = "TBD"
                    
                    st.markdown(f"""
                    <div class="game-card">
                        <strong>{game.get('AwayTeam', 'TBD')} @ {game.get('HomeTeam', 'TBD')}</strong><br>
                        <small>🕐 {time_str} | 📍 {game.get('Venue', 'TBD')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if len(today_games) > 6:
                with st.expander(f"View all {len(today_games)} games today"):
                    for game in today_games[6:]:
                        time_str = str(game.get('Time', 'TBD'))[:5] if game.get('Time') else "TBD"
                        st.write(f"**{game.get('AwayTeam', 'TBD')} @ {game.get('HomeTeam', 'TBD')}** - {time_str} | {game.get('Venue', 'TBD')}")
        else:
            st.info("No games scheduled for today. Check upcoming games below.")
            
            # Show upcoming games if no games today
            from database_prediction import get_upcoming_games
            upcoming = get_upcoming_games(5)
            if upcoming:
                st.subheader("Upcoming Games")
                for game in upcoming:
                    date_str = str(game.get('Date', ''))[:10] if game.get('Date') else "TBD"
                    time_str = str(game.get('Time', 'TBD'))[:5] if game.get('Time') else "TBD"
                    st.write(f"**{date_str}**: {game.get('AwayTeam', 'TBD')} @ {game.get('HomeTeam', 'TBD')} - {time_str}")
    except Exception as e:
        st.warning(f"Could not load games: {e}")
    
    # Main Content Grid - Sections removed as per request to hide News and Stats
    # Main Content - Latest News
    st.markdown("---")
    st.markdown('<div class="section-header">📰 LATEST NEWS</div>', unsafe_allow_html=True)
    
    news_items = get_latest_news(limit=4)
    if news_items:
        news_cols = st.columns(2)
        for idx, news in enumerate(news_items):
            with news_cols[idx % 2]:
                news_id = news.get('NewsID')
                title_text = news.get('Title', 'No Title')
                
                # Use Streamlit components for better state management (avoids reload/logout)
                with st.container(border=True):
                    # Image
                    image_url = news.get("ImageURL")
                    if image_url:
                        import os
                        if os.path.exists(image_url):
                            st.image(image_url, use_container_width=True)
                        elif image_url.startswith("http"):
                            st.image(image_url, use_container_width=True)
                        
                        # Also show the image URL text for visibility
                        st.caption(f"Image URL: {image_url}")
                    
                    # Title as Button (Styled roughly/simply)
                    if st.button(title_text, key=f"title_{news_id}", use_container_width=True):
                        st.session_state.current_page = 'News Detail'
                        st.session_state.selected_news_id = news_id
                        st.rerun()
 
                    # Metadata
                    st.caption(f"📅 {news.get('Date', '')} | 📰 {news.get('Source', 'Source')}")
                    
                    # Content Excerpt
                    st.write(news.get('Content', '')[:100] + "...")
                    
                    # Read More Button
                    if st.button("Read Full Story →", key=f"read_{news_id}"):
                          st.session_state.current_page = 'News Detail'
                          st.session_state.selected_news_id = news_id
                          st.rerun()
    else:
        st.info("No recent news available.")
    
    # Featured Sections with Navigation
    st.markdown("---")
    st.markdown('<div class="section-header">🌟 FEATURED FEATURES</div>', unsafe_allow_html=True)
    
    feat_col1, feat_col2 = st.columns(2)
    
    with feat_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1D428A 0%, #C8102E 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center; height: 100%;">
            <h3>🤖 Hybrid Predict</h3>
            <p><strong>AI-Powered Outcome Analysis</strong></p>
            <p style="font-size: 0.9rem; opacity: 0.9;">
                Combines four advanced models to predict game winners:
                <br>• <strong>Time Series:</strong> Analyzes historical trends and patterns.
                <br>• <strong>Statistical:</strong> Evaluates player and team performance metrics.
                <br>• <strong>Sentiment:</strong> Gauges team morale from recent news.
                <br>• <strong>LLM Reasoning:</strong> Uses AI to synthesize context and strategy.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Try Hybrid Predict", key="feat_hybrid", use_container_width=True):
            st.session_state.current_page = 'Predict'
            st.rerun()
            
    with feat_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #C8102E 0%, #1D428A 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center; height: 100%;">
            <h3>🤖 AI Chatbot</h3>
            <p><strong>Intelligent Basketball Assistant</strong></p>
            <p style="font-size: 0.9rem; opacity: 0.9;">
                Interact with your data using natural language:
                <br>• <strong>Real-time Stats:</strong> Ask for specific player or team statistics.
                <br>• <strong>Game Analysis:</strong> Get AI insights on upcoming matchups.
                <br>• <strong>News Context:</strong> Summaries of the latest team and player headlines.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬 Chat with AI", key="feat_chatbot", use_container_width=True):
            st.session_state.current_page = 'Chatbot'
            st.rerun()




    



if __name__ == "__main__":
    main() 
