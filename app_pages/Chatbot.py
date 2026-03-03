import streamlit as st
import pandas as pd
import time
from query_processor import QueryProcessor
from database_prediction import predict_game_outcome, get_team_context_data, get_team_list, get_general_news_search
from nba_supabase_auth import check_authentication
from app_pages.llm_interface import OllamaChat

TEAM_LOGOS = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET", "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

def get_logo_url(team_name):
    abbr = TEAM_LOGOS.get(team_name)
    if abbr:
        return f"https://a.espncdn.com/i/teamlogos/nba/500/{abbr.lower()}.png"
    return None

def app():
    # Header and Auth Check
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_chat", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("🤖 NBA AI Assistant (with Ollama)")
    
    # Check authentication
    if not check_authentication():
        st.warning("🔒 Please login to use the AI Chatbot.")
        if st.button("Login"):
            st.session_state.current_page = 'Login'
            st.rerun()
        return

    # Initialize LLM (Ensure we use the latest settings)
    # We check if base_url matches our 127.0.0.1 fix, if not we reset
    if "llm" in st.session_state and getattr(st.session_state.llm, 'base_url', '') != "http://127.0.0.1:11434":
        del st.session_state.llm
        
    if "llm" not in st.session_state:
        st.session_state.llm = OllamaChat(model="llama3") # Auto-selects available model
    
    # Check LLM status
    if not st.session_state.llm.is_available:
        st.warning("⚠️ Local Ollama instance not detected. Chatbot will use basic rule-based responses.", icon="⚠️")
        if st.button("♻️ Retry Connection"):
            st.session_state.llm = OllamaChat(model="llama3")
            st.rerun()
    else:
        st.caption(f"🟢 Connected to Ollama ({st.session_state.llm.model})")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your NBA AI Assistant. I have access to your database stats and can use AI to answer your questions. Try asking:\n\n- *'Who will win, Lakers vs Celtics?'*\n- *'Show me stats for Golden State Warriors'*\n- *'Latest news about LeBron James'*"}
        ]
    
    # Initialize query processor (Force refresh to ensure latest logic)
    if "query_processor" not in st.session_state:
        st.session_state.query_processor = QueryProcessor()
    else:
        # Optional: Check if we need to reload (e.g. valid matchup logic was buggy)
        # For now, let's just use the existing one, assuming the user might refresh the page which clears session state?
        # Actually, st.session_state persists across reruns. We should reload it once.
        pass

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            elif isinstance(message["content"], dict):
                # Handle structured content (charts, dataframes, etc)
                render_structured_content(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about NBA games, stats, or news..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query and generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data and generating response..."):
                response_data = process_user_query(prompt)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_data})
                
                # Render response
                render_structured_content(response_data)

def process_user_query(query):
    """Process user query and return response content (str or dict)"""
    processor = st.session_state.query_processor
    result = processor.process_query(query)
    llm = st.session_state.llm
    
    query_type = result['query_type']
    
    # Auto-upgrade general queries about specific teams/players to news queries
    if query_type == 'general':
        entities = result.get('entities', [])
        has_team = bool(result.get('teams_found'))
        has_player = any(e.get('type') == 'player' or e.get('label') == 'PERSON' for e in entities)
        if has_team or has_player:
            query_type = 'news'

    # --- LLM Fallback for Extraction ---
    # If rule-based failed to find teams/intent but we have an interesting query, try LLM extraction
    if (query_type == 'general' or not result['is_valid_matchup']) and llm.is_available:
        try:
            # Ask LLM to extract intent and teams JSON
            extraction_prompt = """
            Analyze the user's NBA query. Return ONLY a JSON object with this format:
            {
                "intent": "prediction" or "stats" or "news" or "general",
                "team1": "Full Team Name 1" (or null),
                "team2": "Full Team Name 2" (or null)
            }
            Map abbreviations to full names (e.g. "Lakers" -> "Los Angeles Lakers").
            Query: """ + query
            
            llm_json_str = llm.generate_response(query, system_prompt=extraction_prompt)
            
            # Simple parsing attempt (robustness)
            import json
            import re
            
            # Try to find JSON block
            match = re.search(r'\{.*\}', llm_json_str, re.DOTALL)
            if match:
                extracted = json.loads(match.group(0))
                
                # Override if LLM found something useful
                if extracted.get('intent') in ['prediction', 'stats', 'news']:
                    query_type = extracted['intent']
                    
                    t1 = extracted.get('team1')
                    t2 = extracted.get('team2')
                    
                    # Resolve team names using processor's normalizer just to be safe/consistent
                    if t1:
                        norm_t1 = processor._normalize_team_name(t1)
                        if norm_t1: result['team1'] = norm_t1
                    if t2:
                        norm_t2 = processor._normalize_team_name(t2)
                        if norm_t2: result['team2'] = norm_t2
                        
                    # Fix teams_found list
                    result['teams_found'] = [t for t in [result.get('team1'), result.get('team2')] if t]
                    result['is_valid_matchup'] = bool(result['team1'] and result['team2'])
                    
        except Exception as e:
            # Silent fail on LLM extraction, proceed with whatever we have
            pass

    # 1. Prediction Query
    if query_type == 'prediction' and result['is_valid_matchup']:
        try:
            prediction = predict_game_outcome(result['team1'], result['team2'])
            if prediction:
                # Generate LLM commentary if available
                llm_text = llm.generate_response(
                    user_query=query,
                    context_data=prediction,
                    system_prompt="You are a sports analyst. Summarize this prediction data for the user. Mention the winner, confidence, key factors, and team strengths. Keep it encouraging but realistic."
                )
                
                return {
                    "type": "prediction",
                    "data": prediction,
                    "text": llm_text or f"Here is my prediction for **{result['team1']} vs {result['team2']}**:",
                    "is_llm": bool(llm_text)
                }
            else:
                return "I couldn't generate a prediction for that matchup. Please check the team names."
        except Exception as e:
            return f"Sorry, I encountered an error making that prediction: {str(e)}"

    # 1.5 Game Result Query (New)
    elif query_type == 'result' and result.get('teams_found'):
        teams = result['teams_found']
        t1 = teams[0]
        t2 = teams[1] if len(teams) > 1 else None
        
        try:
            from database_prediction import get_last_match_result
            match = get_last_match_result(t1, t2)
            
            if match:
                llm_text = llm.generate_response(
                    user_query=query,
                    context_data=match,
                    system_prompt="You are a sports announcer. Summarize the outcome of this game. Mention the final score, who won, the margin, and the date. Be energetic."
                )
                
                return {
                    "type": "game_result",
                    "data": match,
                    "text": llm_text or f"Here is the result of the last game for **{t1}**:",
                    "is_llm": bool(llm_text)
                }
            else:
                return f"I couldn't find a recent game result for {t1}" + (f" against {t2}" if t2 else "") + "."
        except Exception as e:
            return f"Error fetching game result: {str(e)}"

    # 2. Stats Query
    elif query_type == 'stats' and result['teams_found']:
        team = result['teams_found'][0]
        try:
            context = get_team_context_data(team)
            if context and context.get('team_stats'):
                # Prepare stats context for LLM
                stats_context = {
                    "team": team,
                    "season_stats": context['team_stats'],
                    "recent_form": context.get('recent_form', {})
                }
                
                llm_text = llm.generate_response(
                    user_query=query,
                    context_data=stats_context,
                    system_prompt="You are a stats analyst. Summarize the team's performance based on the provided stats. Highlight the win record, form, and any notable strengths/weaknesses."
                )

                return {
                    "type": "stats",
                    "team": team,
                    "stats": context['team_stats'],
                    "recent_form": context.get('recent_form', {}),
                    "text": llm_text or f"Here are the latest statistics for the **{team}**:",
                    "is_llm": bool(llm_text)
                }
            else:
                return f"I couldn't find detailed statistics for {team}."
        except Exception as e:
            return f"Error fetching stats: {str(e)}"

    # 2.5 Player Stats Query (New)
    elif query_type == 'stats' and (result.get('entities') or 'player' in query.lower()):
        # Try to find a player name in the query if no team was clearly the focus
        # This relies on the entity extractor identifying a person/player
        player_name = None
        
        # Check entities first
        for ent in result.get('entities', []):
            if ent.get('type') == 'player' or ent.get('label') == 'PERSON':
                player_name = ent.get('name')
                break
        
        # If no entity, check if LLM extracted it in previous step (if we add that logic)
        # Or simple fallback: take the whole query as name if short enough? 
        # Better: Use the new DB function to fuzzy search
        
        if not player_name and llm.is_available:
             # Ask LLM specifically for player name
             name_prompt = f"Extract the NBA player name from this query: '{query}'. Return ONLY the name, or 'None'."
             extracted = llm.generate_response(query, system_prompt=name_prompt)
             if extracted and 'None' not in extracted and len(extracted) < 50:
                 player_name = extracted.strip().replace('"', '').replace("'", "")

        if player_name:
            from database_prediction import get_specific_player_stats
            player_data = get_specific_player_stats(player_name)
            
            if player_data:
                llm_text = llm.generate_response(
                    user_query=query,
                    context_data=player_data,
                    system_prompt="You are a basketball expert. Summarize the key player details provided. Mention their team, position, and physical stats."
                )
                
                return {
                    "type": "player_stats",
                    "player": player_data['PlayerName'],
                    "data": player_data,
                    "text": llm_text or f"Here is the info for **{player_data['PlayerName']}**:",
                    "is_llm": bool(llm_text)
                }
            elif query_type == 'stats':
                 return f"I searched for player '{player_name}' but couldn't find them in the database."

    # 3. News Query
    elif query_type == 'news' or (query_type == 'general' and any(kw in query.lower() for kw in ['news', 'headlines', 'latest', 'status'])):
        try:
            news = []
            
            # 3.1 Try Vector Search if LLM/Embeddings available
            if llm.is_available:
                query_vector = llm.get_embedding(query)
                if query_vector:
                    from database_prediction import get_vector_news_search
                    # Get more results for better reranking context
                    news = get_vector_news_search(query_vector, limit=10)
            
            # 3.2 Fallback to keyword search if no vector results
            if not news:
                # Try to identify subject for keyword search
                subject = None
                if result.get('teams_found'):
                    subject = result['teams_found'][0]
                else:
                    name_prompt = f"Extract the NBA player or team name from this news query: '{query}'. Return ONLY the name."
                    if llm.is_available:
                        extracted = llm.generate_response(query, system_prompt=name_prompt)
                        if extracted and len(extracted) < 50:
                            subject = extracted.strip().replace('"', '').replace("'", "")
                
                if subject:
                    from database_prediction import get_general_news_search
                    news = get_general_news_search(subject, limit=5)

            if news:
                # 3.3 LLM Reranking & Summarization
                news_context = [
                    {
                        "title": a.get('Title'), 
                        "date": str(a.get('Date')), 
                        "summary": a.get('Content', '')[:400],
                        "similarity": a.get('similarity', 'N/A')
                    } 
                    for a in news
                ]
                
                sum_prompt = f"""You are a senior NBA sports analyst. 
                I will provide you with several news snippets retrieved via vector search.
                
                YOUR TASK:
                1. RERANK: Mentally evaluate which snippets most accurately answer the user's question: "{query}".
                2. SUMMARIZE: Provide a "Correct Answer" summary based on the most relevant facts.
                3. RELEVANCE: Ignore snippets that are outdated or not relevant to the specific intent.
                4. CITE: Mention the source/date briefly if it adds credibility.
                
                Keep the response concise, authoritative, and focused on the 'Correct Answer'.
                """
                
                llm_text = llm.generate_response(
                    user_query=query,
                    context_data=news_context,
                    system_prompt=sum_prompt
                )

                return {
                    "type": "news",
                    "subject": query, 
                    "articles": news,
                    "text": llm_text or "I found some news but couldn't generate a summary. See the sources below.",
                    "is_llm": bool(llm_text)
                }
            else:
                return f"No relevant news found for your query: '{query}'."
        except Exception as e:
            return f"Error processing news query: {str(e)}"

    # Default / Fallback / General Chat
    if llm.is_available:
        # If we failed to handle specific intent but LLM is available, just answer generally
        # We can try to fetch generic context if possible, but for now just general knowledge
        llm_response = llm.generate_response(
            user_query=query,
            system_prompt="You are a helpful NBA assistant. You don't have access to specific real-time data for this query (or couldn't identify the teams). Answer generally based on your knowledge. If it's a prediction request, explain that you need clear team names."
        )
        if llm_response and not llm_response.startswith("Error:"):
            return llm_response
        else:
            # LLM failed to generate response
            error_details = llm_response if llm_response else "Unknown error"
            return f"❌ I'm having trouble connecting to my AI brain.\n\nDetails: {error_details}\n\nPlease check if Ollama is running."

    # Rule-based fallback
    response_text = "I can help you with:"
    response_text += "\n- **Predictions**: 'Predict Lakers vs Warriors'"
    response_text += "\n- **Stats**: 'Stats for Celtics'"
    response_text += "\n- **News**: 'News about Suns'"
    
    if result.get('entities'):
        response_text += f"\n\nI recognized these entities: {', '.join([e['name'] for e in result['entities']])}"
    
    return response_text

def render_structured_content(content):
    """Render complex content types in the chat"""
    if isinstance(content, str):
        st.markdown(content)
        return
        
    if not isinstance(content, dict):
        st.write(content)
        return

    # Display introductory text (LLM generated or static)
    if "text" in content:
        if content.get("is_llm"):
             st.markdown(f"🤖 **AI Analysis:**\n\n{content['text']}")
        else:
             st.markdown(content["text"])

    content_type = content.get("type")

    # --- Render Prediction ---
    if content_type == "prediction":
        pred = content["data"]
        home = pred['home_team']
        away = pred['away_team']
        winner = pred['predicted_winner']
        conf = pred['confidence']
        
        # Result Card
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            logo = get_logo_url(winner)
            if logo:
                st.image(logo, width=150)
            st.metric("Predicted Winner", winner)
            st.progress(conf)
            st.caption(f"Confidence: {conf:.1%}")
            
        with col2:
            st.subheader("Win Probability")
            prob_df = pd.DataFrame({
                "Team": [home, away],
                "Probability": [pred.get('home_win_probability', 0.5), pred.get('away_win_probability', 0.5)]
            })
            st.bar_chart(prob_df.set_index("Team"), horizontal=True)
            
            # Show score prediction if available
            scores = pred.get('score_predictions', {})
            if scores:
                st.write(f"🏠 {home}: **{scores.get('home_score')}**")
                st.write(f"✈️ {away}: **{scores.get('away_score')}**")
        
        with st.expander("Detailed Analysis Metrics"):
            st.write("Strength Comparison")
            # Create comparison chart for strengths
            metrics = {
                "Overall Strength": [pred.get("home_strength", 0), pred.get("away_strength", 0)],
                "Data Quality": [pred.get("home_confidence", 0), pred.get("away_confidence", 0)]
            }
            st.bar_chart(pd.DataFrame(metrics, index=[home, away]))
            st.json(pred)

    # --- Render Stats ---
    elif content_type == "stats":
        stats = content["stats"]
        form = content.get("recent_form", {})
        
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            logo = get_logo_url(content["team"])
            if logo:
                st.image(logo, width=150)
            st.metric("Wins", stats.get("Wins", 0))
            st.metric("Losses", stats.get("Losses", 0))
            
        with col2:
            st.subheader("Seasonal Performance")
            # Calculate basics
            total = stats.get('Wins', 0) + stats.get('Losses', 0)
            win_pct = stats.get('Wins', 0) / max(1, total)
            
            st.metric("Win %", f"{win_pct*100:.1f}%")
            
            # Show chart of Points For vs Against if available
            p_df = pd.DataFrame({
                "Metric": ["PPG Scored", "PPG Allowed"],
                "Value": [stats.get("PointsFor", 0)/max(1, total), stats.get("PointsAgainst", 0)/max(1, total)]
            })
            st.bar_chart(p_df.set_index("Metric"))

        st.subheader("Detailed Performance Data")
        st.dataframe(pd.DataFrame([stats]).T, use_container_width=True)

    # --- Render Player Stats ---
    elif content_type == "player_stats":
        p = content["data"]
        st.markdown("---")
        st.subheader(f"👤 {p.get('PlayerName')}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Position", p.get('Position', 'N/A'))
        c2.metric("Team", p.get('TeamName', 'Free Agent'))
        c3.metric("Height", p.get('Height', 'N/A'))
        
        with st.expander("Full Details"):
            st.write(p)

    # --- Render News ---
    elif content_type == "news":
        # Note: Summary is already rendered above in the "text" block
        with st.expander("🔍 View Source Articles", expanded=False):
            st.info("These sources were used to generate the AI summary.")
            for article in content["articles"]:
                news_id = article.get('NewsID')
                title_text = article.get('Title', 'No Title')
                date_str = str(article.get('Date', ''))[:10]
                similarity = article.get('similarity')
                
                sim_text = f" | Relevance: {similarity:.1%}" if similarity is not None else ""
                
                if st.button(f"• {title_text} ({date_str}){sim_text}", key=f"chat_news_{news_id}"):
                    st.session_state.current_page = 'News Detail'
                    st.session_state.selected_news_id = news_id
                    st.rerun()
    
    # --- Render Game Result ---
    elif content_type == "game_result":
        match = content["data"]
        st.markdown("---")
        
        # Winner Banner
        st.success(f"🏆 **{match['winner']}** won by **{match['margin']}** points!")
        
        col1, col2 = st.columns(2)
        with col1:
            logo1 = get_logo_url(match['HomeTeamName'])
            if logo1: st.image(logo1, width=80)
            st.markdown(f"**🏠 Home**\n### {match['HomeTeamName']}\n# {match['HomeTeamScore']}")
        with col2:
            logo2 = get_logo_url(match['VisitorTeamName'])
            if logo2: st.image(logo2, width=80)
            st.markdown(f"**✈️ Away**\n### {match['VisitorTeamName']}\n# {match['VisitorPoints']}")
            
        st.caption(f"📅 Date: {match['Date']} | 📍 Venue: {match.get('Venue', 'N/A')}")
        
    else:
        # Fallback for dicts that aren't specific types
        st.write(content)

if __name__ == "__main__":
    app()
