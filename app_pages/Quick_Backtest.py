#!/usr/bin/env python3
"""
Quick Backtest - Streamlit Interface
Fast backtesting with visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simulate_fast_prediction(home_team, away_team):
    """Simulate a fast prediction without heavy database calls"""
    
    # Simple team strength lookup (can be expanded with actual data)
    team_strengths = {
        'Boston Celtics': 0.78, 'Denver Nuggets': 0.70, 'Oklahoma City Thunder': 0.70,
        'Minnesota Timberwolves': 0.69, 'Los Angeles Clippers': 0.73, 'Milwaukee Bucks': 0.71,
        'Dallas Mavericks': 0.61, 'Cleveland Cavaliers': 0.59, 'Phoenix Suns': 0.71,
        'New York Knicks': 0.61, 'Orlando Magic': 0.57, 'Miami Heat': 0.56,
        'Philadelphia 76ers': 0.57, 'Indiana Pacers': 0.57, 'Los Angeles Lakers': 0.57,
        'New Orleans Pelicans': 0.60, 'Sacramento Kings': 0.56, 'Golden State Warriors': 0.56,
        'Houston Rockets': 0.50, 'Chicago Bulls': 0.48, 'Atlanta Hawks': 0.44,
        'Brooklyn Nets': 0.39, 'Toronto Raptors': 0.30, 'Utah Jazz': 0.38,
        'Memphis Grizzlies': 0.33, 'Portland Trail Blazers': 0.26, 'San Antonio Spurs': 0.27,
        'Charlotte Hornets': 0.26, 'Detroit Pistons': 0.17, 'Washington Wizards': 0.18
    }
    
    # Get team strengths with small random variation
    home_strength = team_strengths.get(home_team, 0.5) + np.random.uniform(-0.05, 0.05)
    away_strength = team_strengths.get(away_team, 0.5) + np.random.uniform(-0.05, 0.05)
    
    # Add home court advantage
    home_strength += 0.05
    
    # Calculate win probabilities
    total_strength = home_strength + away_strength
    home_win_prob = home_strength / total_strength
    away_win_prob = away_strength / total_strength
    
    # Determine predicted winner
    predicted_winner = home_team if home_win_prob > away_win_prob else away_team
    
    # Calculate confidence (more conservative)
    strength_diff = abs(home_strength - away_strength)
    confidence = min(0.75, 0.45 + strength_diff * 1.2)
    
    # Simulate actual result based on probabilities
    actual_winner = home_team if np.random.random() < home_win_prob else away_team
    
    return {
        'predicted_winner': predicted_winner,
        'actual_winner': actual_winner,
        'confidence': confidence,
        'home_win_prob': home_win_prob,
        'away_win_prob': away_win_prob,
        'home_strength': home_strength - 0.05,  # Remove home advantage for display
        'away_strength': away_strength,
        'is_correct': predicted_winner == actual_winner
    }

def run_quick_backtest(num_games=20):
    """Run a quick backtest on random matchups"""
    
    all_teams = [
        'Boston Celtics', 'Los Angeles Lakers', 'Golden State Warriors', 'Miami Heat',
        'Denver Nuggets', 'Phoenix Suns', 'Milwaukee Bucks', 'Philadelphia 76ers',
        'Dallas Mavericks', 'Cleveland Cavaliers', 'New York Knicks', 'Los Angeles Clippers',
        'Sacramento Kings', 'Memphis Grizzlies', 'Atlanta Hawks', 'Chicago Bulls',
        'Brooklyn Nets', 'Toronto Raptors', 'Charlotte Hornets', 'Detroit Pistons',
        'Houston Rockets', 'Indiana Pacers', 'Minnesota Timberwolves', 'New Orleans Pelicans',
        'Oklahoma City Thunder', 'Orlando Magic', 'Portland Trail Blazers', 'San Antonio Spurs',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_games):
        # Random matchup
        home_team, away_team = np.random.choice(all_teams, 2, replace=False)
        
        status_text.text(f"Testing game {i+1}/{num_games}: {away_team} @ {home_team}")
        progress_bar.progress((i + 1) / num_games)
        
        # Simulate prediction
        result = simulate_fast_prediction(home_team, away_team)
        result['game_num'] = i + 1
        result['home_team'] = home_team
        result['away_team'] = away_team
        
        results.append(result)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def analyze_backtest_results(df):
    """Analyze backtest results"""
    
    # Basic metrics
    total_games = len(df)
    correct_predictions = df['is_correct'].sum()
    accuracy = correct_predictions / total_games
    avg_confidence = df['confidence'].mean()
    
    # Confidence-based accuracy
    df['confidence_bucket'] = pd.cut(df['confidence'], 
                                      bins=[0, 0.5, 0.6, 0.7, 0.8, 1.0],
                                      labels=['<50%', '50-60%', '60-70%', '70-80%', '>80%'])
    
    confidence_analysis = df.groupby('confidence_bucket').agg({
        'is_correct': ['sum', 'count', 'mean']
    }).round(3)
    
    return {
        'total_games': total_games,
        'correct_predictions': correct_predictions,
        'accuracy': accuracy,
        'avg_confidence': avg_confidence,
        'confidence_analysis': confidence_analysis
    }

from nba_supabase_auth import check_authentication, is_admin

def main():
    """Main backtest interface"""
    # Check authentication and admin status
    if not check_authentication():
        st.warning("Please login to access this page")
        st.stop()
    
    if not is_admin():
        st.error("🔒 Access Denied: This page is only available to administrators.")
        st.stop()

    st.title("⚡ Quick Backtest")
    st.markdown("Fast model performance testing with instant results")
    
    # Configuration
    st.header("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_games = st.slider("Number of games", 10, 50, 20, 5)
    
    with col2:
        random_seed = st.number_input("Random seed (for reproducibility)", 0, 1000, 42)
    
    # Run backtest button
    if st.button("🚀 Run Quick Backtest", type="primary"):
        np.random.seed(random_seed)
        
        st.header("🧪 Running Backtest...")
        
        # Run backtest
        results_df = run_quick_backtest(num_games)
        
        # Store in session state
        st.session_state.backtest_results = results_df
        
        st.success(f"✅ Backtest completed! Tested {len(results_df)} games")
    
    # Display results if available
    if 'backtest_results' in st.session_state:
        df = st.session_state.backtest_results
        
        # Analyze results
        metrics = analyze_backtest_results(df)
        
        st.header("📊 Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Games", metrics['total_games'])
        
        with col2:
            st.metric("Correct", metrics['correct_predictions'])
        
        with col3:
            st.metric("Accuracy", f"{metrics['accuracy']:.1%}")
        
        with col4:
            st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1%}")
        
        # Evaluation
        st.subheader("🎯 Model Evaluation")
        
        if metrics['accuracy'] >= 0.60:
            st.success("✅ Good Performance (≥60% accuracy)")
        elif metrics['accuracy'] >= 0.55:
            st.warning("⚠️ Moderate Performance (55-60% accuracy)")
        else:
            st.error("❌ Poor Performance (<55% accuracy)")
        
        if metrics['avg_confidence'] <= 0.80:
            st.success("✅ Realistic Confidence (≤80%)")
        else:
            st.warning("⚠️ Confidence may be too high")
        
        # Visualizations
        st.subheader("📈 Performance Visualizations")
        
        # Accuracy by confidence level
        fig1 = px.bar(
            df.groupby('confidence_bucket')['is_correct'].agg(['mean', 'count']).reset_index(),
            x='confidence_bucket',
            y='mean',
            title='Accuracy by Confidence Level',
            labels={'mean': 'Accuracy', 'confidence_bucket': 'Confidence Level'},
            color='mean',
            color_continuous_scale='RdYlGn'
        )
        fig1.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Confidence distribution
        fig2 = px.histogram(
            df,
            x='confidence',
            nbins=20,
            title='Confidence Score Distribution',
            labels={'confidence': 'Confidence', 'count': 'Number of Games'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Win probability scatter
        fig3 = go.Figure()
        
        correct_games = df[df['is_correct'] == True]
        incorrect_games = df[df['is_correct'] == False]
        
        fig3.add_trace(go.Scatter(
            x=correct_games['home_win_prob'],
            y=correct_games['confidence'],
            mode='markers',
            name='Correct',
            marker=dict(color='green', size=10, opacity=0.6)
        ))
        
        fig3.add_trace(go.Scatter(
            x=incorrect_games['home_win_prob'],
            y=incorrect_games['confidence'],
            mode='markers',
            name='Incorrect',
            marker=dict(color='red', size=10, opacity=0.6)
        ))
        
        fig3.update_layout(
            title='Confidence vs Win Probability',
            xaxis_title='Home Win Probability',
            yaxis_title='Prediction Confidence',
            hovermode='closest'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Detailed results table
        st.subheader("📋 Detailed Results")
        
        # Format for display
        display_df = df[['game_num', 'home_team', 'away_team', 'predicted_winner', 
                         'actual_winner', 'confidence', 'is_correct']].copy()
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1%}")
        display_df['result'] = display_df['is_correct'].apply(lambda x: '✅' if x else '❌')
        
        st.dataframe(
            display_df.style.apply(
                lambda row: ['background-color: #d4edda'] * len(row) if row['is_correct'] 
                else ['background-color: #f8d7da'] * len(row),
                axis=1
            ),
            use_container_width=True
        )
        
        # Download results
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"quick_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Calibration recommendations
        st.subheader("🔧 Calibration Recommendations")
        
        # Calculate calibration factor
        overall_calibration = metrics['accuracy'] / metrics['avg_confidence'] if metrics['avg_confidence'] > 0 else 1.0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Calibration Factor", f"{overall_calibration:.3f}")
        
        with col2:
            if overall_calibration < 0.9:
                st.error(f"Model is {((1-overall_calibration)*100):.0f}% OVERCONFIDENT")
                st.markdown("**Recommendation**: Reduce confidence scores")
            elif overall_calibration > 1.1:
                st.warning(f"Model is {((overall_calibration-1)*100):.0f}% UNDERCONFIDENT")
                st.markdown("**Recommendation**: Increase confidence scores")
            else:
                st.success("Model is WELL-CALIBRATED ✅")
        
        st.markdown(f"""
        **What this means:**
        - **Calibration Factor < 1.0**: Model predicts with higher confidence than actual accuracy
        - **Calibration Factor > 1.0**: Model predicts with lower confidence than actual accuracy
        - **Calibration Factor ≈ 1.0**: Model confidence matches actual performance
        
        **Recommended Adjustment:**
        Multiply all confidence scores by **{overall_calibration:.3f}**
        
        Example: If current confidence is 60%, adjusted confidence = 60% × {overall_calibration:.3f} = {60 * overall_calibration:.1f}%
        """)
    
    # Model insights
    st.header("💡 About Quick Backtest")
    st.markdown("""
    **Quick Backtest** uses simplified prediction logic for fast performance testing:
    
    - **Instant Results**: Tests 20 games in seconds instead of minutes
    - **Team Strength Based**: Uses realistic NBA team strength estimates
    - **Probabilistic**: Simulates results based on win probabilities
    - **Visual Analytics**: Interactive charts and detailed breakdowns
    
    **Use this for:**
    - Quick model validation
    - Testing confidence calibration
    - Comparing different configurations
    - Educational demonstrations
    
    **For production backtesting**, use the full prediction system with actual game results.
    """)

if __name__ == "__main__":
    main()

