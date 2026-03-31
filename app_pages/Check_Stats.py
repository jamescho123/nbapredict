import streamlit as st
import pandas as pd
import plotly.express as px
from db_config import get_connection, DB_SCHEMA


def _read_sql(query, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

def get_player_list():
    return _read_sql(f'SELECT * FROM "{DB_SCHEMA}"."Players" ORDER BY "PlayerName"')

def get_player_stats(player_id):
    query = '''
        SELECT mp.*, p.*
        FROM "{schema}"."MatchPlayer" mp
        JOIN "{schema}"."Players" p ON mp."PlayerID" = p."PlayerID"
        WHERE mp."PlayerID" = %s
    '''.format(schema=DB_SCHEMA)
    return _read_sql(query, params=(player_id,))

def get_team_list():
    return _read_sql(f'SELECT * FROM "{DB_SCHEMA}"."Teams" ORDER BY "TeamName"')

def get_team_matches(team_id):
    query = '''
        SELECT m.*, ht."TeamName" AS "HomeTeam", vt."TeamName" AS "VisitorTeam"
        FROM "{schema}"."Matches" m
        JOIN "{schema}"."Teams" ht ON m."HomeTeamID" = ht."TeamID"
        JOIN "{schema}"."Teams" vt ON m."VisitorTeamID" = vt."TeamID"
        WHERE m."HomeTeamID" = %s OR m."VisitorTeamID" = %s
        ORDER BY m."Date" DESC
    '''.format(schema=DB_SCHEMA)
    return _read_sql(query, params=(team_id, team_id))

def get_match_by_id(match_id):
    query = '''
        SELECT m.*, ht."TeamName" AS "HomeTeam", vt."TeamName" AS "VisitorTeam"
        FROM "{schema}"."Matches" m
        JOIN "{schema}"."Teams" ht ON m."HomeTeamID" = ht."TeamID"
        JOIN "{schema}"."Teams" vt ON m."VisitorTeamID" = vt."TeamID"
        WHERE m."MatchID" = %s
    '''.format(schema=DB_SCHEMA)
    return _read_sql(query, params=(match_id,))

def get_match_by_date(date):
    query = '''
        SELECT m.*, ht."TeamName" AS "HomeTeam", vt."TeamName" AS "VisitorTeam"
        FROM "{schema}"."Matches" m
        JOIN "{schema}"."Teams" ht ON m."HomeTeamID" = ht."TeamID"
        JOIN "{schema}"."Teams" vt ON m."VisitorTeamID" = vt."TeamID"
        WHERE m."Date" = %s
    '''.format(schema=DB_SCHEMA)
    return _read_sql(query, params=(date,))

def get_match_player_stats(match_id):
    query = '''
        SELECT mp.*, p."PlayerName", t."TeamName"
        FROM "{schema}"."MatchPlayer" mp
        JOIN "{schema}"."Players" p ON mp."PlayerID" = p."PlayerID"
        JOIN "{schema}"."TeamPlayer" tp ON mp."PlayerID" = tp."PlayerID"
        JOIN "{schema}"."Teams" t ON tp."TeamID" = t."TeamID"
        WHERE mp."MatchID" = %s
    '''.format(schema=DB_SCHEMA)
    return _read_sql(query, params=(match_id,))

def app():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_stats", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("NBA Statistics")
    
    stat_type = st.selectbox("Select Statistics Type:", ["Player Stats", "Team Stats", "Game Stats"])
    
    if stat_type == "Player Stats":
        st.subheader("Player Statistics")
        players_df = get_player_list()
        search = st.text_input("Search Player Name:")
        if search:
            filtered_players = players_df[players_df["PlayerName"].str.contains(search, case=False, na=False)]
            if filtered_players.empty:
                st.warning("No players found matching your search.")
            elif len(filtered_players) > 1:
                st.dataframe(filtered_players, hide_index=True)
                st.info("Multiple players found. Please refine your search.")
            else:
                player_id = filtered_players.iloc[0]["PlayerID"]
                player_name = filtered_players.iloc[0]["PlayerName"]
                with st.spinner("Fetching player stats from database..."):
                    df = get_player_stats(player_id)
                    if df is not None and not df.empty:
                        st.dataframe(df, hide_index=True)
                        # Show aggregate stats
                        agg_cols = [
                            "MP", "FG", "FGA", "FGPercentage", "3P", "3PA", "3PPercentage", "FT", "FTPercentage", "TRB", "AST", "BLK", "TOV", "PF", "PTS", "PlusMinus"
                        ]
                        agg_df = df[agg_cols].sum().to_frame().T
                        st.subheader("Aggregated Stats (Sum)")
                        st.dataframe(agg_df, hide_index=True)
                        # Visualization: Points per game
                        if "PTS" in df.columns:
                            fig = px.line(df, y="PTS", title=f'Points per Game for {player_name}')
                            st.plotly_chart(fig)
                    else:
                        st.warning("No stats found for the selected player.")
        else:
            st.info("Please enter a player name to search.")
    elif stat_type == "Team Stats":
        st.subheader("Team Statistics")
        teams_df = get_team_list()
        search = st.text_input("Search Team Name:")
        if search:
            filtered_teams = teams_df[teams_df["TeamName"].str.contains(search, case=False, na=False)]
            if filtered_teams.empty:
                st.warning("No teams found matching your search.")
            elif len(filtered_teams) > 1:
                st.dataframe(filtered_teams, hide_index=True)
                st.info("Multiple teams found. Please refine your search.")
            else:
                team_id = filtered_teams.iloc[0]["TeamID"]
                team_name = filtered_teams.iloc[0]["TeamName"]
                with st.spinner("Fetching team matches from database..."):
                    df = get_team_matches(team_id)
                    if df is not None and not df.empty:
                        st.dataframe(df, hide_index=True)
                        # Visualization: Points for and against
                        fig = px.bar(df, x="Date", y=["HomeTeamScore", "VisitorPoints"], barmode="group", title=f'Scores for {team_name}')
                        st.plotly_chart(fig)
                    else:
                        st.warning("No matches found for the selected team.")
        else:
            st.info("Please enter a team name to search.")
    elif stat_type == "Game Stats":
        st.subheader("Game Statistics")
        match_id_input = st.text_input("Enter Match ID (or leave blank to search by date):")
        date_input = st.text_input("Enter Match Date (YYYY-MM-DD, optional):")
        match_df = None
        if match_id_input:
            try:
                match_id = int(match_id_input)
                match_df = get_match_by_id(match_id)
            except Exception:
                st.warning("Invalid Match ID.")
        elif date_input:
            try:
                match_df = get_match_by_date(date_input)
            except Exception:
                st.warning("Invalid date format. Use YYYY-MM-DD.")
        if match_df is not None:
            if match_df.empty:
                st.warning("No matches found.")
            elif len(match_df) > 1:
                st.dataframe(match_df, hide_index=True)
                st.info("Multiple matches found. Please refine your search.")
            else:
                match_id = match_df.iloc[0]["MatchID"]
                st.write("### Match Info")
                st.dataframe(match_df, hide_index=True)
                with st.spinner("Fetching player stats for this match..."):
                    df = get_match_player_stats(match_id)
                    if df is not None and not df.empty:
                        st.dataframe(df, hide_index=True)
                    else:
                        st.warning("No player stats found for this match.")
        else:
            st.info("Please enter a Match ID or Date to search.")

if __name__ == "__main__":
    app()
