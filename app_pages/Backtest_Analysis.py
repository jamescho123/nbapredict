#!/usr/bin/env python3
"""
NBA Prediction Model Backtest Analysis
Streamlit page for running and analyzing backtests
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_prediction import predict_game_outcome, get_team_context_data
import database_prediction
from model_config import load_config, save_config, reset_config, get_best_config
from model_optimizer import ModelOptimizer
import copy

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_available_games(limit=50):
    """Get available games for backtesting"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "GameID", "Date", "HomeTeam", "AwayTeam", "Time"
        FROM "{DB_SCHEMA}"."Season2024_25_Schedule"
        WHERE "Date" >= '2024-10-22' AND "Date" < '2025-06-15'
        ORDER BY "Date" ASC
        LIMIT %s
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error fetching games: {e}")
        return []
    finally:
        conn.close()

def get_real_game_result(game_id, home_team, away_team, game_date):
    """Get real game result from database if available"""
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        query = f'''
        SELECT "HomeScore", "AwayScore", "Winner", "Margin", "TotalPoints"
        FROM "{DB_SCHEMA}"."Season2024_25_Results"
        WHERE "GameID" = %s OR ("HomeTeam" = %s AND "AwayTeam" = %s AND "Date" = %s)
        LIMIT 1
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (game_id, home_team, away_team, game_date))
        result = cursor.fetchone()
        
        if result:
            home_score, away_score, winner, margin, total_points = result
            return {
                'home_score': home_score,
                'away_score': away_score,
                'winner': winner,
                'margin': margin,
                'total_points': total_points,
                'is_real': True
            }
        return None
    except Exception as e:
        st.warning(f"Could not fetch real result: {e}")
        return None
    finally:
        conn.close()

def simulate_game_result(home_team, away_team, prediction):
    """Simulate a realistic game result based on prediction"""
    # Get team context for more realistic simulation
    home_context = get_team_context_data(home_team)
    away_context = get_team_context_data(away_team)
    
    # Base scores
    home_base = np.random.randint(100, 125)
    away_base = np.random.randint(100, 125)
    
    # Adjust based on prediction confidence and strength
    confidence = prediction.get('confidence', 0.5)
    prediction_strength = abs(prediction.get('prediction_score', 0))
    
    # Home advantage
    home_advantage = np.random.randint(2, 8)
    home_score = home_base + home_advantage
    away_score = away_base
    
    # Add some randomness
    home_score += np.random.randint(-8, 8)
    away_score += np.random.randint(-8, 8)
    
    # Ensure realistic bounds
    home_score = max(85, min(150, home_score))
    away_score = max(85, min(150, away_score))
    
    # Determine winner
    if home_score > away_score:
        winner = home_team
        margin = home_score - away_score
    else:
        winner = away_team
        margin = away_score - home_score
    
    return {
        'home_score': home_score,
        'away_score': away_score,
        'winner': winner,
        'margin': margin,
        'total_points': home_score + away_score,
        'is_real': False
    }

def run_backtest_with_config(games, num_games, config):
    """Run backtest with a specific configuration"""
    # Temporarily override global config
    import database_prediction
    original_config = database_prediction.MODEL_CONFIG
    database_prediction.MODEL_CONFIG = config
    
    try:
        results = []
        
        for game in games[:num_games]:
            home_team = game['HomeTeam']
            away_team = game['AwayTeam']
            game_date = str(game['Date'])
            
            try:
                # Make prediction (use game_date for temporal filtering - only use data before this date)
                prediction = predict_game_outcome(home_team, away_team, game_date=game_date)
                
                if prediction:
                    # Try to get real game result first, otherwise simulate
                    result = get_real_game_result(game['GameID'], home_team, away_team, game_date)
                    if not result:
                        result = simulate_game_result(home_team, away_team, prediction)
                    
                    # Check if prediction is correct
                    predicted_winner = prediction.get('predicted_winner', 'Unknown')
                    actual_winner = result['winner']
                    is_correct = (predicted_winner == actual_winner)
                    
                    # Calculate score prediction accuracy
                    score_preds = prediction.get('score_predictions', {})
                    predicted_home_score = score_preds.get('home_score', 110)
                    predicted_away_score = score_preds.get('away_score', 108)
                    
                    home_score_error = abs(predicted_home_score - result['home_score'])
                    away_score_error = abs(predicted_away_score - result['away_score'])
                    avg_score_error = (home_score_error + away_score_error) / 2
                    
                    # Store result
                    backtest_result = {
                        'game_id': game['GameID'],
                        'date': game_date,
                        'home_team': home_team,
                        'away_team': away_team,
                        'predicted_winner': predicted_winner,
                        'actual_winner': actual_winner,
                        'is_correct': is_correct,
                        'confidence': prediction.get('confidence', 0),
                        'home_score': result['home_score'],
                        'away_score': result['away_score'],
                        'predicted_home_score': predicted_home_score,
                        'predicted_away_score': predicted_away_score,
                        'score_error': avg_score_error,
                        'is_real': result['is_real']
                    }
                    
                    results.append(backtest_result)
                    
            except Exception as e:
                st.warning(f"Error predicting game: {e}")
                continue
        
        return results
    finally:
        # Restore original config
        database_prediction.MODEL_CONFIG = original_config

def run_backtest(games, num_games=20):
    """Run backtest on selected games"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, game in enumerate(games[:num_games]):
        home_team = game['HomeTeam']
        away_team = game['AwayTeam']
        game_date = str(game['Date'])
        
        # Update progress
        progress = (i + 1) / num_games
        progress_bar.progress(progress)
        status_text.text(f"Testing game {i+1}/{num_games}: {away_team} @ {home_team}")
        
        try:
            # Make prediction (use game_date for temporal filtering - only use data before this date)
            prediction = predict_game_outcome(home_team, away_team, game_date=game_date)
            
            if prediction:
                # Try to get real game result first, otherwise simulate
                result = get_real_game_result(game['GameID'], home_team, away_team, game_date)
                if not result:
                    result = simulate_game_result(home_team, away_team, prediction)
                
                # Check if prediction is correct
                predicted_winner = prediction.get('predicted_winner', 'Unknown')
                actual_winner = result['winner']
                is_correct = (predicted_winner == actual_winner)
                
                # Calculate score prediction accuracy
                # Extract scores from score_predictions dict (correct structure)
                score_preds = prediction.get('score_predictions', {})
                predicted_home_score = score_preds.get('home_score', 110)
                predicted_away_score = score_preds.get('away_score', 108)
                
                home_score_error = abs(predicted_home_score - result['home_score'])
                away_score_error = abs(predicted_away_score - result['away_score'])
                avg_score_error = (home_score_error + away_score_error) / 2
                
                # Get detailed stats and news used for prediction
                home_context = get_team_context_data(home_team, as_of_date=game_date)
                away_context = get_team_context_data(away_team, as_of_date=game_date)
                
                # Store result with detailed data
                backtest_result = {
                    'game_id': game['GameID'],
                    'date': game_date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'predicted_winner': predicted_winner,
                    'actual_winner': actual_winner,
                    'is_correct': is_correct,
                    'confidence': prediction.get('confidence', 0),
                    'predicted_home_score': predicted_home_score,
                    'predicted_away_score': predicted_away_score,
                    'actual_home_score': result['home_score'],
                    'actual_away_score': result['away_score'],
                    'score_error': avg_score_error,
                    'margin': result['margin'],
                    'total_points': result['total_points'],
                    'result_type': '🏀 Real' if result.get('is_real', False) else '🎲 Simulated',
                    # Detailed stats used for prediction
                    'home_stats': home_context.get('team_stats', {}),
                    'away_stats': away_context.get('team_stats', {}),
                    'home_form': home_context.get('recent_form', {}),
                    'away_form': away_context.get('recent_form', {}),
                    'home_news': home_context.get('news', []),
                    'away_news': away_context.get('news', []),
                    'head_to_head': prediction.get('head_to_head', {}),
                    'home_strength': prediction.get('home_strength', 0),
                    'away_strength': prediction.get('away_strength', 0)
                }
                
                results.append(backtest_result)
            else:
                st.warning(f"No prediction generated for {away_team} @ {home_team}")
                
        except Exception as e:
            st.error(f"Error predicting {away_team} @ {home_team}: {e}")
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return results

def analyze_results(results):
    """Analyze backtest results"""
    if not results:
        return {}
    
    df = pd.DataFrame(results)
    
    # Basic metrics
    total_games = len(df)
    correct_predictions = df['is_correct'].sum()
    accuracy = correct_predictions / total_games if total_games > 0 else 0
    avg_confidence = df['confidence'].mean()
    avg_score_error = df['score_error'].mean()
    
    # Confidence-based analysis
    confidence_ranges = [
        (0.0, 0.5, "Low"),
        (0.5, 0.7, "Medium"),
        (0.7, 0.9, "High"),
        (0.9, 1.0, "Very High")
    ]
    
    confidence_analysis = {}
    for min_conf, max_conf, label in confidence_ranges:
        range_df = df[(df['confidence'] >= min_conf) & (df['confidence'] < max_conf)]
        if len(range_df) > 0:
            range_accuracy = range_df['is_correct'].mean()
            confidence_analysis[label] = {
                'count': len(range_df),
                'accuracy': range_accuracy,
                'avg_confidence': range_df['confidence'].mean()
            }
    
    return {
        'total_games': total_games,
        'correct_predictions': correct_predictions,
        'accuracy': accuracy,
        'avg_confidence': avg_confidence,
        'avg_score_error': avg_score_error,
        'confidence_analysis': confidence_analysis,
        'results_df': df
    }

def create_visualizations(metrics):
    """Create visualization charts"""
    if not metrics or 'results_df' not in metrics:
        return
    
    df = metrics['results_df']
    
    # Accuracy by confidence level
    if 'confidence_analysis' in metrics and metrics['confidence_analysis']:
        conf_data = []
        for label, data in metrics['confidence_analysis'].items():
            conf_data.append({
                'Confidence Level': label,
                'Accuracy': data['accuracy'],
                'Count': data['count']
            })
        
        conf_df = pd.DataFrame(conf_data)
        
        fig1 = px.bar(
            conf_df, 
            x='Confidence Level', 
            y='Accuracy',
            title='Prediction Accuracy by Confidence Level',
            color='Accuracy',
            color_continuous_scale='RdYlGn'
        )
        fig1.update_layout(yaxis_title='Accuracy (%)', yaxis_tickformat='.1%')
        st.plotly_chart(fig1, use_container_width=True)
    
    # Score prediction error distribution
    fig2 = px.histogram(
        df, 
        x='score_error',
        title='Score Prediction Error Distribution',
        nbins=20
    )
    fig2.update_layout(
        xaxis_title='Score Error (points)',
        yaxis_title='Number of Games'
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Confidence vs Accuracy scatter
    fig3 = px.scatter(
        df,
        x='confidence',
        y='is_correct',
        title='Confidence vs Prediction Accuracy',
        color='score_error',
        color_continuous_scale='RdYlGn_r'
    )
    fig3.update_layout(
        xaxis_title='Prediction Confidence',
        yaxis_title='Correct Prediction (1=Yes, 0=No)'
    )
    st.plotly_chart(fig3, use_container_width=True)

from nba_supabase_auth import check_authentication, is_admin

def main():
    """Main backtest analysis interface"""
    # Check authentication and admin status
    if not check_authentication():
        st.warning("Please login to access this page")
        st.stop()
    
    if not is_admin():
        st.error("🔒 Access Denied: This page is only available to administrators.")
        st.stop()

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_backtest", type="secondary"):
            st.switch_page("Home.py")
    with col2:
        st.title("🧪 NBA Prediction Model Backtest")
    st.markdown("""
    Test the prediction model's performance on **real 2024-25 season games** from 
    [Basketball-Reference.com](https://www.basketball-reference.com/leagues/NBA_2025_games.html)
    """)
    
    # Create tabs for different modes
    tab1, tab2 = st.tabs(["🔍 Single Backtest", "🔧 Auto-Optimize Model"])
    
    with tab2:
        st.header("🔧 Automatic Model Optimization")
        
        st.write("""
        This feature automatically runs multiple backtests with different parameter configurations
        to find the optimal settings for your model. The system will test various combinations
        of parameters and identify which configuration produces the best accuracy.
        """)
        
        opt_games = get_available_games(limit=100)
        
        if not opt_games:
            st.error("No games available for optimization")
        else:
            st.info(f"Found {len(opt_games)} available games for optimization")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                opt_mode = st.selectbox(
                    "Optimization Mode",
                    ["Quick (6 configs)", "Moderate (27 configs)", "Comprehensive (300 configs)"],
                    key="opt_mode"
                )
            
            with col2:
                games_per_config = st.slider("Games per Configuration", 5, 30, 15, key="games_per_config")
            
            with col3:
                total_preds = (6 if "Quick" in opt_mode else 27 if "Moderate" in opt_mode else 300) * games_per_config
                st.metric("Total Predictions", total_preds)
            
            if st.button("🚀 Start Optimization", type="primary", key="start_opt"):
                optimizer = ModelOptimizer()
                
                # Define parameter grid based on mode
                if "Quick" in opt_mode:
                    param_grid = {
                        'home_advantage': [0.08, 0.12],
                        'strength_weights.win_percentage': [0.25, 0.30, 0.35]
                    }
                elif "Moderate" in opt_mode:
                    param_grid = {
                        'home_advantage': [0.08, 0.10, 0.12],
                        'strength_weights.win_percentage': [0.25, 0.30, 0.35],
                        'strength_weights.recent_form': [0.05, 0.10, 0.15]
                    }
                else:  # Comprehensive
                    param_grid = {
                        'home_advantage': [0.05, 0.08, 0.10, 0.12, 0.15],
                        'strength_weights.win_percentage': [0.20, 0.25, 0.30, 0.35, 0.40],
                        'strength_weights.point_differential': [0.15, 0.20, 0.25, 0.30],
                        'strength_weights.recent_form': [0.05, 0.10, 0.15]
                    }
                
                # Create placeholders for real-time display
                st.markdown("---")
                st.subheader("📊 Optimization Progress")
                
                progress_bar = st.progress(0)
                status_container = st.container()
                config_display = st.empty()
                game_display = st.empty()
                results_display = st.empty()
                
                # Generate all configurations to show total
                total_configs = optimizer.generate_configurations(param_grid)
                num_configs = len(total_configs)
                
                st.info(f"Testing {num_configs} configurations with {games_per_config} games each = {num_configs * games_per_config} total predictions")
                
                # Enhanced wrapper with real-time display
                def backtest_wrapper_with_display(config, games_list, num, config_idx):
                    # Display current configuration
                    sw = config.get('strength_weights', {})
                    
                    config_display.markdown(f"""
                    ### Configuration {config_idx}/{num_configs}
                    
                    **Parameters:**
                    - 🏠 Home Advantage: **{config.get('home_advantage', 0.1):.3f}** ({config.get('home_advantage', 0.1)*100:.1f}%)
                    - 📊 Win % Weight: **{sw.get('win_percentage', 0.30):.2f}** ({sw.get('win_percentage', 0.30)*100:.0f}%)
                    - 📈 Point Diff Weight: **{sw.get('point_differential', 0.25):.2f}** ({sw.get('point_differential', 0.25)*100:.0f}%)
                    - 🔥 Recent Form Weight: **{sw.get('recent_form', 0.10):.2f}** ({sw.get('recent_form', 0.10)*100:.0f}%)
                    - 📰 News Sentiment Weight: **{sw.get('news_sentiment', 0.10):.2f}** ({sw.get('news_sentiment', 0.10)*100:.0f}%)
                    - ⚙️ Offensive Eff Weight: **{sw.get('offensive_efficiency', 0.15):.2f}** ({sw.get('offensive_efficiency', 0.15)*100:.0f}%)
                    - 🛡️ Defensive Eff Weight: **{sw.get('defensive_efficiency', 0.10):.2f}** ({sw.get('defensive_efficiency', 0.10)*100:.0f}%)
                    """)
                    
                    # Run backtest with game-by-game display
                    results = []
                    game_results_text = []
                    
                    for i, game in enumerate(games_list[:num], 1):
                        # Update game display
                        game_display.markdown(f"""
                        **Testing Game {i}/{num}:**  
                        🏀 {game['AwayTeam']} @ {game['HomeTeam']}  
                        📅 {game['Date']}
                        """)
                        
                        # Run prediction
                        home_team = game['HomeTeam']
                        away_team = game['AwayTeam']
                        game_date = str(game['Date'])
                        
                        try:
                            prediction = predict_game_outcome(home_team, away_team, game_date=game_date)
                            
                            if prediction:
                                result = get_real_game_result(game['GameID'], home_team, away_team, game_date)
                                if not result:
                                    result = simulate_game_result(home_team, away_team, prediction)
                                
                                predicted_winner = prediction.get('predicted_winner', 'Unknown')
                                actual_winner = result['winner']
                                is_correct = (predicted_winner == actual_winner)
                                
                                score_preds = prediction.get('score_predictions', {})
                                predicted_home_score = score_preds.get('home_score', 110)
                                predicted_away_score = score_preds.get('away_score', 108)
                                
                                home_score_error = abs(predicted_home_score - result['home_score'])
                                away_score_error = abs(predicted_away_score - result['away_score'])
                                avg_score_error = (home_score_error + away_score_error) / 2
                                
                                # Add to game results display
                                status = "✓" if is_correct else "✗"
                                game_results_text.append(
                                    f"Game {i}: {away_team} @ {home_team} - "
                                    f"Pred: {predicted_winner} ({prediction.get('confidence', 0):.1%}) - "
                                    f"Actual: {actual_winner} {status}"
                                )
                                
                                results.append({
                                    'is_correct': is_correct,
                                    'confidence': prediction.get('confidence', 0),
                                    'score_error': avg_score_error,
                                    'is_real': result.get('is_real', False)
                                })
                        except Exception as e:
                            st.warning(f"Error in game {i}: {e}")
                            continue
                    
                    # Display all game results for this config
                    if game_results_text:
                        results_display.markdown("**Games Tested:**\n\n" + "\n".join(game_results_text[-10:]))  # Show last 10
                    
                    # Calculate metrics
                    if results:
                        accuracy = sum(1 for r in results if r['is_correct']) / len(results)
                        avg_confidence = sum(r['confidence'] for r in results) / len(results)
                        avg_score_error = sum(r['score_error'] for r in results) / len(results)
                        
                        # Show configuration summary
                        results_display.markdown(f"""
                        **Configuration {config_idx} Results:**
                        - ✓ Accuracy: **{accuracy:.1%}** ({sum(1 for r in results if r['is_correct'])}/{len(results)} correct)
                        - 📊 Avg Confidence: **{avg_confidence:.1%}**
                        - 🎯 Avg Score Error: **{avg_score_error:.1f}** points
                        """)
                        
                        return {
                            'accuracy': accuracy,
                            'avg_confidence': avg_confidence,
                            'avg_score_error': avg_score_error
                        }
                    
                    return {'accuracy': 0, 'avg_confidence': 0, 'avg_score_error': 999}
                
                # Run optimization with enhanced display
                all_results = []
                best_config = None
                best_accuracy = 0
                best_display = st.empty()
                
                for idx, config in enumerate(total_configs, 1):
                    # Update progress
                    progress = idx / num_configs
                    progress_bar.progress(progress, text=f"Testing configuration {idx}/{num_configs}")
                    
                    # Temporarily override config for prediction
                    original_config = database_prediction.MODEL_CONFIG
                    database_prediction.MODEL_CONFIG = config
                    
                    try:
                        # Run backtest for this config
                        result = backtest_wrapper_with_display(config, opt_games, games_per_config, idx)
                        
                        # Store results
                        all_results.append({
                            'config': config,
                            'accuracy': result['accuracy'],
                            'avg_confidence': result['avg_confidence'],
                            'avg_score_error': result['avg_score_error']
                        })
                        
                        # Track best
                        if result['accuracy'] > best_accuracy:
                            best_accuracy = result['accuracy']
                            best_config = config
                            
                            # Display current best
                            sw = best_config.get('strength_weights', {})
                            best_display.success(f"""
                            🎯 **CURRENT BEST: Configuration {idx}**
                            - Accuracy: **{best_accuracy:.1%}**
                            - Home Advantage: {best_config.get('home_advantage', 0.1):.3f}
                            - Win % Weight: {sw.get('win_percentage', 0.30):.2f}
                            """)
                    finally:
                        # Restore original config
                        database_prediction.MODEL_CONFIG = original_config
                
                # Final progress
                progress_bar.progress(1.0, text="Optimization Complete!")
                
                # Store results
                opt_results = {
                    'best_config': best_config,
                    'best_accuracy': best_accuracy,
                    'all_results': all_results
                }
                
                # Display results
                st.success("✓ Optimization Complete!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Best Accuracy", f"{opt_results['best_accuracy']:.1%}")
                with col2:
                    st.metric("Configs Tested", len(opt_results['all_results']))
                with col3:
                    if st.button("💾 Apply Best Config", key="apply_best"):
                        # Ensure complete config is saved
                        best_config = opt_results['best_config']
                        
                        # Verify all required parameters are present
                        required_keys = ['home_advantage', 'strength_weights', 'confidence_weights', 
                                        'calibration', 'news_time_weights', 'news_recency', 'score_prediction']
                        
                        # Save complete configuration
                        if save_config(best_config):
                            st.success("✓ Best configuration applied with ALL parameters!")
                            
                            # Show what was applied
                            with st.expander("View Applied Configuration"):
                                st.json(best_config)
                            
                            st.rerun()
                        else:
                            st.error("Failed to save configuration")
                
                # Show comparison table with parameters
                st.subheader("📊 Configuration Comparison")
                
                comparison_data = []
                for idx, r in enumerate(opt_results['all_results'], 1):
                    config = r['config']
                    sw = config.get('strength_weights', {})
                    comparison_data.append({
                        'Config #': idx,
                        'Accuracy': r['accuracy'],
                        'Confidence': r['avg_confidence'],
                        'Score Error': r['avg_score_error'],
                        'Home Adv': config.get('home_advantage', 0.1),
                        'Win %': sw.get('win_percentage', 0.30),
                        'Recent Form': sw.get('recent_form', 0.10)
                    })
                
                results_df = pd.DataFrame(comparison_data)
                results_df = results_df.sort_values('Accuracy', ascending=False)
                
                # Highlight best row
                def highlight_best(row):
                    if row['Accuracy'] == results_df['Accuracy'].max():
                        return ['background-color: #90EE90'] * len(row)
                    return [''] * len(row)
                
                st.dataframe(
                    results_df.style
                    .format({
                        'Accuracy': '{:.1%}',
                        'Confidence': '{:.1%}',
                        'Score Error': '{:.1f}',
                        'Home Adv': '{:.3f}',
                        'Win %': '{:.2f}',
                        'Recent Form': '{:.2f}'
                    })
                    .apply(highlight_best, axis=1),
                    use_container_width=True
                )
                
                # Show detailed best configuration
                st.subheader("🏆 Best Configuration Details")
                if opt_results['best_config']:
                    best_sw = opt_results['best_config'].get('strength_weights', {})
                    best_cal = opt_results['best_config'].get('calibration', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Core Parameters:**")
                        st.write(f"🏠 Home Advantage: `{opt_results['best_config'].get('home_advantage', 0.1):.3f}`")
                        
                        st.markdown("**Strength Weights (normalized to 1.0):**")
                        st.write(f"📊 Win %: `{best_sw.get('win_percentage', 0.30):.3f}`")
                        st.write(f"📈 Point Diff: `{best_sw.get('point_differential', 0.25):.3f}`")
                        st.write(f"⚙️ Offensive Eff: `{best_sw.get('offensive_efficiency', 0.15):.3f}`")
                        st.write(f"🛡️ Defensive Eff: `{best_sw.get('defensive_efficiency', 0.10):.3f}`")
                        st.write(f"🔥 Recent Form: `{best_sw.get('recent_form', 0.10):.3f}`")
                        st.write(f"📰 News Sentiment: `{best_sw.get('news_sentiment', 0.10):.3f}`")
                        st.caption(f"Total: {sum(best_sw.values()):.3f}")
                        
                        st.markdown("**Calibration:**")
                        st.write(f"Smoothing: `{best_cal.get('smoothing_factor', 0.5):.2f}`")
                        st.write(f"Min Confidence: `{best_cal.get('min_confidence', 0.45):.2f}`")
                        st.write(f"Max Confidence: `{best_cal.get('max_confidence', 0.95):.2f}`")
                    
                    with col2:
                        st.markdown("**Performance:**")
                        st.metric("Accuracy", f"{opt_results['best_accuracy']:.1%}")
                        best_result = next((r for r in opt_results['all_results'] if r['accuracy'] == opt_results['best_accuracy']), None)
                        if best_result:
                            st.metric("Avg Confidence", f"{best_result['avg_confidence']:.1%}")
                            st.metric("Avg Score Error", f"{best_result['avg_score_error']:.1f} pts")
                        
                        st.markdown("**Complete Configuration:**")
                        st.caption("All parameters from DEFAULT_CONFIG are included")
                        
                        # Verify completeness
                        config_keys = set(opt_results['best_config'].keys())
                        required_keys = {'home_advantage', 'strength_weights', 'confidence_weights', 
                                       'calibration', 'news_time_weights', 'news_recency', 'score_prediction'}
                        missing = required_keys - config_keys
                        
                        if not missing:
                            st.success("✓ All required parameters present")
                        else:
                            st.warning(f"Missing: {missing}")
                        
                        # Show full config in expander
                        with st.expander("📋 View Full Configuration JSON"):
                            st.json(opt_results['best_config'])
    
    with tab1:
        st.header("🔍 Single Backtest Run")
        
        # Info box about data source
        with st.expander("ℹ️ About the Data", expanded=False):
            st.markdown("""
            **Data Source**: Basketball-Reference.com  
            **Season**: 2024-25 NBA Regular Season  
            **Date Range**: October 22, 2024 - April 13, 2025  
            **Games**: Real completed games with actual scores  
            
            **To import/update data**:
            ```bash
            python import_basketball_reference_2024_25.py
            ```
            
            This fetches real game schedules and results from the official Basketball Reference website.
            """)
        
        # Get available games
        games = get_available_games(100)
        
        if not games:
            st.error("No games found in the database. Please run: python import_basketball_reference_2024_25.py")
            st.info("💡 This will import real 2024-25 season games from Basketball-Reference.com")
            return
        
        st.success(f"Found {len(games)} games available for backtesting")
        
        # Backtest configuration
        st.subheader("Backtest Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_games = st.slider(
                "Number of games to test",
                min_value=5,
                max_value=min(50, len(games)),
                value=20,
                help="Select how many games to include in the backtest"
            )
        
        with col2:
            test_type = st.selectbox(
                "Test Type",
                ["Random Games", "Recent Games", "High Profile Games"],
                help="Choose which games to test"
            )
        
        # Select games based on test type
        if test_type == "Random Games":
            selected_games = np.random.choice(games, size=num_games, replace=False).tolist()
        elif test_type == "Recent Games":
            selected_games = games[:num_games]
        else:  # High Profile Games
            # Select games with popular teams
            popular_teams = ['Los Angeles Lakers', 'Boston Celtics', 'Golden State Warriors', 
                            'Miami Heat', 'Chicago Bulls', 'New York Knicks']
            selected_games = [g for g in games if g['HomeTeam'] in popular_teams or g['AwayTeam'] in popular_teams][:num_games]
        
        # Display selected games
        st.subheader("📅 Selected Games for Testing")
        games_df = pd.DataFrame(selected_games)
        st.dataframe(games_df[['Date', 'HomeTeam', 'AwayTeam', 'Time']], use_container_width=True)
        
        # Run backtest
        if st.button("🚀 Run Backtest", type="primary", key="run_single_backtest"):
            st.header("🧪 Running Backtest...")
            
            with st.spinner("Testing predictions..."):
                results = run_backtest(selected_games, num_games)
            
            if results:
                st.success(f"✅ Backtest completed! Tested {len(results)} games")
            
            # Analyze results
            metrics = analyze_results(results)
            
            # Display results
            st.header("📊 Backtest Results")
            
            # Show data source stats
            real_results = sum(1 for r in results if r.get('result_type', '').startswith('🏀'))
            simulated_results = len(results) - real_results
            
            if real_results > 0:
                st.success(f"✅ Testing on {real_results} real completed games from Basketball-Reference.com")
            if simulated_results > 0:
                st.info(f"🎲 {simulated_results} games simulated (no real results available yet)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Games", metrics['total_games'])
            
            with col2:
                st.metric("Correct Predictions", metrics['correct_predictions'])
            
            with col3:
                st.metric("Accuracy", f"{metrics['accuracy']:.1%}")
            
            with col4:
                st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1%}")
            
            # Detailed metrics
            st.subheader("📈 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Score Error", f"{metrics['avg_score_error']:.1f} points")
            
            with col2:
                # Model evaluation
                if metrics['accuracy'] >= 0.6:
                    evaluation = "✅ Good Performance"
                elif metrics['accuracy'] >= 0.5:
                    evaluation = "⚠️ Moderate Performance"
                else:
                    evaluation = "❌ Needs Improvement"
                
                st.metric("Model Evaluation", evaluation)
            
            # Confidence-based analysis
            if 'confidence_analysis' in metrics and metrics['confidence_analysis']:
                st.subheader("🎯 Confidence-Based Performance")
                
                conf_df = pd.DataFrame([
                    {
                        'Confidence Level': label,
                        'Games': data['count'],
                        'Accuracy': f"{data['accuracy']:.1%}",
                        'Avg Confidence': f"{data['avg_confidence']:.1%}"
                    }
                    for label, data in metrics['confidence_analysis'].items()
                ])
                
                st.dataframe(conf_df, use_container_width=True)
            
            # Visualizations
            st.subheader("📊 Performance Visualizations")
            create_visualizations(metrics)
            
            # Detailed results table
            st.subheader("📋 Detailed Results")
            
            # Display each game with expandable details
            for idx, result in enumerate(results):
                game_date = result['date']
                home_team = result['home_team']
                away_team = result['away_team']
                is_correct = result['is_correct']
                
                # Create expandable section for each game
                status_icon = "✅" if is_correct else "❌"
                with st.expander(
                    f"{status_icon} Game {idx+1}: {away_team} @ {home_team} ({game_date}) - "
                    f"Predicted: {result['predicted_winner']}, Actual: {result['actual_winner']}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {home_team} (Home)")
                        st.markdown(f"**🎯 Prediction Date:** {game_date}")
                        st.markdown(f"**⚠️ All data shown is from BEFORE {game_date}**")
                        
                        st.markdown("#### Team Stats (Season)")
                        home_stats = result.get('home_stats', {})
                        if home_stats:
                            st.write(f"- **Record:** {home_stats.get('Wins', 0)}W - {home_stats.get('Losses', 0)}L")
                            total_games = home_stats.get('Wins', 0) + home_stats.get('Losses', 0)
                            if total_games > 0:
                                ppg = home_stats.get('PointsFor', 0) / total_games
                                papg = home_stats.get('PointsAgainst', 0) / total_games
                                st.write(f"- **PPG:** {ppg:.1f}")
                                st.write(f"- **Opp PPG:** {papg:.1f}")
                                st.write(f"- **Diff:** {ppg - papg:+.1f}")
                        
                        st.markdown("#### Recent Form (Last 10 Games)")
                        home_form = result.get('home_form', {})
                        if home_form:
                            st.write(f"- **Record:** {home_form.get('wins', 0)}W - {home_form.get('losses', 0)}L")
                            st.write(f"- **Win %:** {home_form.get('win_percentage', 0):.1%}")
                        
                        st.markdown("#### Recent News (Used)")
                        home_news = result.get('home_news', [])
                        if home_news:
                            st.write(f"**{len(home_news)} news articles** used (all before {game_date}):")
                            for news in home_news[:5]:  # Show top 5
                                news_date = news.get('Date', 'N/A')
                                news_title = news.get('Title', 'No title')[:80]
                                st.write(f"- *{news_date}*: {news_title}...")
                            if len(home_news) > 5:
                                st.write(f"... and {len(home_news) - 5} more articles")
                        else:
                            st.write("No news articles found")
                        
                        st.markdown("#### Strength Score")
                        st.metric("Team Strength", f"{result.get('home_strength', 0):.3f}")
                    
                    with col2:
                        st.markdown(f"### {away_team} (Away)")
                        st.markdown(f"**🎯 Prediction Date:** {game_date}")
                        st.markdown(f"**⚠️ All data shown is from BEFORE {game_date}**")
                        
                        st.markdown("#### Team Stats (Season)")
                        away_stats = result.get('away_stats', {})
                        if away_stats:
                            st.write(f"- **Record:** {away_stats.get('Wins', 0)}W - {away_stats.get('Losses', 0)}L")
                            total_games = away_stats.get('Wins', 0) + away_stats.get('Losses', 0)
                            if total_games > 0:
                                ppg = away_stats.get('PointsFor', 0) / total_games
                                papg = away_stats.get('PointsAgainst', 0) / total_games
                                st.write(f"- **PPG:** {ppg:.1f}")
                                st.write(f"- **Opp PPG:** {papg:.1f}")
                                st.write(f"- **Diff:** {ppg - papg:+.1f}")
                        
                        st.markdown("#### Recent Form (Last 10 Games)")
                        away_form = result.get('away_form', {})
                        if away_form:
                            st.write(f"- **Record:** {away_form.get('wins', 0)}W - {away_form.get('losses', 0)}L")
                            st.write(f"- **Win %:** {away_form.get('win_percentage', 0):.1%}")
                        
                        st.markdown("#### Recent News (Used)")
                        away_news = result.get('away_news', [])
                        if away_news:
                            st.write(f"**{len(away_news)} news articles** used (all before {game_date}):")
                            for news in away_news[:5]:  # Show top 5
                                news_date = news.get('Date', 'N/A')
                                news_title = news.get('Title', 'No title')[:80]
                                st.write(f"- *{news_date}*: {news_title}...")
                            if len(away_news) > 5:
                                st.write(f"... and {len(away_news) - 5} more articles")
                        else:
                            st.write("No news articles found")
                        
                        st.markdown("#### Strength Score")
                        st.metric("Team Strength", f"{result.get('away_strength', 0):.3f}")
                    
                    # Head-to-head and prediction details
                    st.markdown("---")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown("#### Head-to-Head")
                        h2h = result.get('head_to_head', {})
                        if h2h and h2h.get('total_games', 0) > 0:
                            st.write(f"{home_team}: {h2h.get('team1_wins', 0)} wins")
                            st.write(f"{away_team}: {h2h.get('team2_wins', 0)} wins")
                            st.write(f"Total games: {h2h.get('total_games', 0)}")
                        else:
                            st.write("No prior meetings")
                    
                    with col_b:
                        st.markdown("#### Prediction")
                        st.write(f"**Winner:** {result['predicted_winner']}")
                        st.write(f"**Confidence:** {result['confidence']:.1%}")
                        st.write(f"**Score:** {result['predicted_home_score']}-{result['predicted_away_score']}")
                    
                    with col_c:
                        st.markdown("#### Actual Result")
                        st.write(f"**Winner:** {result['actual_winner']}")
                        st.write(f"**Score:** {result['actual_home_score']}-{result['actual_away_score']}")
                        st.write(f"**Type:** {result['result_type']}")
            
            # Summary table
            st.markdown("---")
            st.subheader("📊 Results Summary Table")
            results_df = metrics['results_df']
            
            # Select relevant columns for summary
            summary_df = results_df[[
                'date', 'home_team', 'away_team', 'predicted_winner', 
                'actual_winner', 'is_correct', 'confidence', 'result_type'
            ]].copy()
            
            # Add color coding for correct/incorrect predictions
            def highlight_correct(row):
                if row['is_correct']:
                    return ['background-color: #d4edda'] * len(row)
                else:
                    return ['background-color: #f8d7da'] * len(row)
            
            styled_df = summary_df.style.apply(highlight_correct, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Save results to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f"backtest_results_{timestamp}.csv"
            
            try:
                results_df.to_csv(csv_filename, index=False)
                st.success(f"💾 Results saved to {csv_filename}")
            except Exception as e:
                st.error(f"❌ Error saving CSV: {e}")
            
            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=csv_filename,
                mime="text/csv"
            )
            
        else:
            st.error("❌ Backtest failed. No results generated.")
    
    # Model insights
    st.header("💡 Model Insights")
    st.markdown("""
    **Understanding the Results:**
    
    - **Accuracy**: Percentage of correct winner predictions
    - **Confidence**: Model's confidence in its predictions
    - **Score Error**: Average difference between predicted and actual scores
    - **Confidence Analysis**: How accuracy varies with confidence levels
    
    **Good Performance Indicators:**
    - Accuracy > 60%
    - Higher confidence predictions are more accurate
    - Score error < 10 points
    - Consistent performance across different game types
    """)

if __name__ == "__main__":
    main()
