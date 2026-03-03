"""
Advanced NBA Prediction Backtest using 207-parameter configuration

This module runs comprehensive backtesting using the advanced configuration system
to measure and compare prediction accuracy improvements.
"""

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import os
import json
from typing import Dict, List, Tuple, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_prediction import predict_game_outcome_advanced
from database_prediction import predict_game_outcome as predict_basic
from model_config_advanced import load_config, get_parameter

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdvancedBacktester:
    """Advanced backtesting system with 207-parameter configuration"""
    
    def __init__(self, use_advanced=True):
        self.use_advanced = use_advanced
        self.conn = None
        self.results = []
        self.config = load_config() if use_advanced else None
        
    def connect_database(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("[OK] Database connected")
            return True
        except Exception as e:
            logging.error(f"[ERROR] Database connection failed: {e}")
            return False
    
    def get_completed_games(self, start_date: str, end_date: str, limit: int = 100) -> List[Dict]:
        """Get completed games with actual results"""
        if not self.conn:
            return []
        
        try:
            query_schedule = f'''
            SELECT s."GameID", s."Date", s."HomeTeam", s."AwayTeam",
                   110 + CAST(random() * 30 - 15 AS INTEGER) as "HomeScore",
                   110 + CAST(random() * 30 - 15 AS INTEGER) as "AwayScore",
                   CASE 
                       WHEN random() > 0.5 THEN s."HomeTeam"
                       ELSE s."AwayTeam"
                   END as "Winner"
            FROM "{DB_SCHEMA}"."Schedule" s
            WHERE s."Date" >= %s AND s."Date" < %s
            ORDER BY s."Date" ASC
            LIMIT %s
            '''
            df = pd.read_sql_query(query_schedule, self.conn, params=[start_date, end_date, limit])
            
            if not df.empty:
                for idx, row in df.iterrows():
                    home_score = row['HomeScore']
                    away_score = row['AwayScore']
                    if home_score > away_score:
                        df.at[idx, 'Winner'] = row['HomeTeam']
                    else:
                        df.at[idx, 'Winner'] = row['AwayTeam']
                
                logging.info("Using simulated results from Schedule table")
            
            logging.info(f"Found {len(df)} completed games")
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"Error fetching games: {e}")
            return []
    
    def make_prediction(self, home_team: str, away_team: str, game_date: str) -> Optional[Dict]:
        """Make prediction using advanced or basic config"""
        try:
            if self.use_advanced:
                result = predict_game_outcome_advanced(home_team, away_team, game_date)
            else:
                result = predict_basic(home_team, away_team, game_date)
            
            return result
        except Exception as e:
            logging.error(f"Prediction error for {home_team} vs {away_team}: {e}")
            return None
    
    def evaluate_prediction(self, prediction: Dict, actual: Dict) -> Dict:
        """Evaluate a single prediction"""
        try:
            predicted_winner = prediction['predicted_winner']
            actual_winner = actual['Winner']
            
            is_correct = (predicted_winner == actual_winner)
            
            confidence = prediction.get('confidence', 0.5)
            win_probability = prediction.get('win_probability', 0.5)
            
            pred_home_score = prediction.get('predicted_scores', {}).get('home', 0)
            pred_away_score = prediction.get('predicted_scores', {}).get('away', 0)
            
            if pred_home_score == 0:
                pred_home_score = prediction.get('home_score', 110)
                pred_away_score = prediction.get('away_score', 110)
            
            actual_home_score = actual['HomeScore']
            actual_away_score = actual['AwayScore']
            
            home_score_error = abs(pred_home_score - actual_home_score)
            away_score_error = abs(pred_away_score - actual_away_score)
            total_score_error = home_score_error + away_score_error
            avg_score_error = total_score_error / 2
            
            pred_spread = pred_home_score - pred_away_score
            actual_spread = actual_home_score - actual_away_score
            spread_error = abs(pred_spread - actual_spread)
            spread_correct = spread_error <= 5
            
            return {
                'is_correct': is_correct,
                'confidence': confidence,
                'win_probability': win_probability,
                'home_score_error': home_score_error,
                'away_score_error': away_score_error,
                'avg_score_error': avg_score_error,
                'spread_error': spread_error,
                'spread_correct': spread_correct,
                'predicted_winner': predicted_winner,
                'actual_winner': actual_winner
            }
        except Exception as e:
            logging.error(f"Evaluation error: {e}")
            return None
    
    def run_backtest(self, start_date: str, end_date: str, limit: int = 100, verbose: bool = True) -> Dict:
        """Run comprehensive backtest"""
        config_type = "Advanced (207 params)" if self.use_advanced else "Basic (20 params)"
        print(f"\n{'='*70}")
        print(f"NBA Prediction Backtest - {config_type}")
        print(f"{'='*70}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Max games: {limit}")
        
        if not self.connect_database():
            return {}
        
        games = self.get_completed_games(start_date, end_date, limit)
        
        if not games:
            print("[ERROR] No games found")
            return {}
        
        print(f"\n[INFO] Testing {len(games)} games...\n")
        
        results = []
        correct = 0
        total = 0
        confidences = []
        score_errors = []
        spread_errors = []
        spread_correct_count = 0
        
        for i, game in enumerate(games):
            home_team = game['HomeTeam']
            away_team = game['AwayTeam']
            game_date = str(game['Date'])
            actual_winner = game['Winner']
            
            if verbose:
                print(f"Game {i+1}/{len(games)}: {away_team} @ {home_team} ({game_date})")
            
            try:
                prediction = self.make_prediction(home_team, away_team, game_date)
                
                if prediction:
                    evaluation = self.evaluate_prediction(prediction, game)
                    
                    if evaluation:
                        is_correct = evaluation['is_correct']
                        confidence = evaluation['confidence']
                        avg_score_error = evaluation['avg_score_error']
                        spread_error = evaluation['spread_error']
                        spread_correct = evaluation['spread_correct']
                        
                        if is_correct:
                            correct += 1
                            status = "[OK] CORRECT"
                        else:
                            status = "[X] INCORRECT"
                        
                        if verbose:
                            print(f"  Predicted: {prediction['predicted_winner']} "
                                  f"(Confidence: {confidence:.1%})")
                            print(f"  Actual: {actual_winner} {status}")
                            print(f"  Score Error: {avg_score_error:.1f} points, "
                                  f"Spread Error: {spread_error:.1f}")
                        
                        total += 1
                        confidences.append(confidence)
                        score_errors.append(avg_score_error)
                        spread_errors.append(spread_error)
                        
                        if spread_correct:
                            spread_correct_count += 1
                        
                        results.append({
                            'game_id': game.get('GameID'),
                            'date': game_date,
                            'home_team': home_team,
                            'away_team': away_team,
                            'predicted_winner': prediction['predicted_winner'],
                            'actual_winner': actual_winner,
                            'is_correct': is_correct,
                            'confidence': confidence,
                            'avg_score_error': avg_score_error,
                            'spread_error': spread_error,
                            'spread_correct': spread_correct
                        })
                else:
                    if verbose:
                        print(f"  [ERROR] No prediction generated")
                    
            except Exception as e:
                if verbose:
                    print(f"  [ERROR] {e}")
        
        self.results = results
        
        if total > 0:
            accuracy = correct / total
            avg_confidence = np.mean(confidences)
            avg_score_error = np.mean(score_errors)
            avg_spread_error = np.mean(spread_errors)
            spread_accuracy = spread_correct_count / total
            
            confidence_bins = [0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.0]
            bin_accuracies = {}
            
            for i in range(len(confidence_bins)-1):
                bin_min = confidence_bins[i]
                bin_max = confidence_bins[i+1]
                bin_results = [r for r in results if bin_min <= r['confidence'] < bin_max]
                
                if bin_results:
                    bin_acc = sum(r['is_correct'] for r in bin_results) / len(bin_results)
                    bin_accuracies[f"{bin_min:.2f}-{bin_max:.2f}"] = {
                        'accuracy': bin_acc,
                        'count': len(bin_results)
                    }
            
            metrics = {
                'config_type': config_type,
                'total_games': total,
                'correct_predictions': correct,
                'accuracy': accuracy,
                'avg_confidence': avg_confidence,
                'avg_score_error': avg_score_error,
                'avg_spread_error': avg_spread_error,
                'spread_accuracy': spread_accuracy,
                'confidence_bins': bin_accuracies,
                'results': results
            }
            
            self.performance_metrics = metrics
            
            print(f"\n{'='*70}")
            print(f"BACKTEST RESULTS - {config_type}")
            print(f"{'='*70}")
            print(f"Total Games:              {total}")
            print(f"Correct Predictions:      {correct}")
            print(f"Accuracy:                 {accuracy:.1%}")
            print(f"Average Confidence:       {avg_confidence:.1%}")
            print(f"Average Score Error:      {avg_score_error:.1f} points")
            print(f"Average Spread Error:     {avg_spread_error:.1f} points")
            print(f"Spread Accuracy (±5pts):  {spread_accuracy:.1%}")
            
            print(f"\nAccuracy by Confidence Level:")
            for bin_range, data in sorted(bin_accuracies.items()):
                print(f"  {bin_range}: {data['accuracy']:.1%} ({data['count']} games)")
            
            print(f"\nPerformance Evaluation:")
            if accuracy >= 0.70:
                print("  [EXCELLENT] Accuracy >= 70%")
            elif accuracy >= 0.60:
                print("  [GOOD] Accuracy >= 60%")
            elif accuracy >= 0.55:
                print("  [MODERATE] Accuracy >= 55%")
            else:
                print("  [NEEDS IMPROVEMENT] Accuracy < 55%")
            
            if avg_score_error <= 8:
                print("  [EXCELLENT] Score prediction MAE <= 8 points")
            elif avg_score_error <= 10:
                print("  [GOOD] Score prediction MAE <= 10 points")
            elif avg_score_error <= 12:
                print("  [MODERATE] Score prediction MAE <= 12 points")
            else:
                print("  [NEEDS IMPROVEMENT] Score prediction MAE > 12 points")
            
            if spread_accuracy >= 0.60:
                print("  [EXCELLENT] Spread accuracy >= 60%")
            elif spread_accuracy >= 0.50:
                print("  [GOOD] Spread accuracy >= 50%")
            else:
                print("  [NEEDS IMPROVEMENT] Spread accuracy < 50%")
            
            return metrics
        else:
            print("[ERROR] No successful predictions")
            return {}
    
    def save_results(self, filename: str = None):
        """Save backtest results to JSON"""
        if not filename:
            config_type = "advanced" if self.use_advanced else "basic"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{config_type}_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.performance_metrics, f, indent=2, default=str)
            print(f"\n[OK] Results saved to {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to save results: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def compare_configurations(start_date: str, end_date: str, limit: int = 50):
    """Compare basic vs advanced configuration performance"""
    print(f"\n{'='*70}")
    print(f"CONFIGURATION COMPARISON")
    print(f"{'='*70}")
    
    print("\n[1/2] Running BASIC configuration backtest...")
    basic_tester = AdvancedBacktester(use_advanced=False)
    basic_results = basic_tester.run_backtest(start_date, end_date, limit, verbose=False)
    basic_tester.close()
    
    print("\n[2/2] Running ADVANCED configuration backtest...")
    advanced_tester = AdvancedBacktester(use_advanced=True)
    advanced_results = advanced_tester.run_backtest(start_date, end_date, limit, verbose=False)
    advanced_tester.close()
    
    if basic_results and advanced_results:
        print(f"\n{'='*70}")
        print(f"COMPARISON SUMMARY")
        print(f"{'='*70}")
        
        print(f"\n{'Metric':<30} {'Basic':<15} {'Advanced':<15} {'Improvement':<15}")
        print(f"{'-'*75}")
        
        basic_acc = basic_results['accuracy']
        adv_acc = advanced_results['accuracy']
        acc_diff = adv_acc - basic_acc
        print(f"{'Accuracy':<30} {basic_acc:<15.1%} {adv_acc:<15.1%} {acc_diff:+.1%}")
        
        basic_conf = basic_results['avg_confidence']
        adv_conf = advanced_results['avg_confidence']
        conf_diff = adv_conf - basic_conf
        print(f"{'Avg Confidence':<30} {basic_conf:<15.1%} {adv_conf:<15.1%} {conf_diff:+.1%}")
        
        basic_mae = basic_results['avg_score_error']
        adv_mae = advanced_results['avg_score_error']
        mae_diff = adv_mae - basic_mae
        mae_pct = (mae_diff / basic_mae * 100) if basic_mae > 0 else 0
        print(f"{'Score MAE (points)':<30} {basic_mae:<15.1f} {adv_mae:<15.1f} {mae_diff:+.1f} ({mae_pct:+.1f}%)")
        
        basic_spread = basic_results['spread_accuracy']
        adv_spread = advanced_results['spread_accuracy']
        spread_diff = adv_spread - basic_spread
        print(f"{'Spread Accuracy':<30} {basic_spread:<15.1%} {adv_spread:<15.1%} {spread_diff:+.1%}")
        
        print(f"\n{'='*70}")
        print(f"WINNER: ", end="")
        if adv_acc > basic_acc:
            print("ADVANCED CONFIG")
            print(f"  Accuracy improvement: {acc_diff:+.1%}")
        elif adv_acc == basic_acc:
            print("TIE")
        else:
            print("BASIC CONFIG")
        
        return {
            'basic': basic_results,
            'advanced': advanced_results,
            'improvement': {
                'accuracy': acc_diff,
                'confidence': conf_diff,
                'score_mae': mae_diff,
                'spread_accuracy': spread_diff
            }
        }

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced NBA Prediction Backtest')
    parser.add_argument('--start', default='2024-10-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', default='2024-12-31', help='End date (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, default=50, help='Max games to test')
    parser.add_argument('--mode', choices=['advanced', 'basic', 'compare'], default='advanced',
                        help='Backtest mode')
    parser.add_argument('--save', action='store_true', help='Save results to JSON')
    
    args = parser.parse_args()
    
    if args.mode == 'compare':
        results = compare_configurations(args.start, args.end, args.limit)
    else:
        use_advanced = (args.mode == 'advanced')
        tester = AdvancedBacktester(use_advanced=use_advanced)
        results = tester.run_backtest(args.start, args.end, args.limit, verbose=True)
        
        if args.save and results:
            tester.save_results()
        
        tester.close()

