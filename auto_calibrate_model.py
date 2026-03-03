#!/usr/bin/env python3
"""
Automatic Model Calibration Based on Backtest Results
Analyzes backtest performance and adjusts model parameters
"""

import json
import os
from datetime import datetime
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModelCalibrator:
    """Automatically calibrate prediction model based on backtest results"""
    
    def __init__(self):
        self.calibration_params = {}
        self.backtest_results = None
        
    def load_latest_backtest(self):
        """Load the most recent backtest results"""
        backtest_files = [f for f in os.listdir('.') if f.startswith('2024_25_season_backtest_') and f.endswith('.json')]
        
        if not backtest_files:
            logging.error("No backtest results found")
            return False
        
        # Get most recent file
        latest_file = max(backtest_files, key=os.path.getctime)
        
        try:
            with open(latest_file, 'r') as f:
                self.backtest_results = json.load(f)
            
            logging.info(f"Loaded backtest results from {latest_file}")
            return True
        except Exception as e:
            logging.error(f"Error loading backtest results: {e}")
            return False
    
    def analyze_performance(self) -> Dict:
        """Analyze backtest performance"""
        if not self.backtest_results:
            return {}
        
        metrics = self.backtest_results.get('performance_metrics', {})
        detailed_results = self.backtest_results.get('detailed_results', [])
        
        analysis = {
            'accuracy': metrics.get('accuracy', 0),
            'avg_confidence': metrics.get('avg_confidence', 0),
            'avg_score_error': metrics.get('avg_score_error', 0),
            'avg_margin_error': metrics.get('avg_margin_error', 0),
            'total_games': metrics.get('total_games', 0)
        }
        
        # Calculate confidence calibration
        confidence_vs_accuracy = []
        for result in detailed_results:
            confidence_vs_accuracy.append({
                'confidence': result['confidence'],
                'correct': result['is_correct']
            })
        
        analysis['confidence_calibration'] = self.calculate_confidence_calibration(confidence_vs_accuracy)
        
        # Calculate score bias
        score_biases = []
        for result in detailed_results:
            home_bias = result['predicted_home_score'] - result['actual_home_score']
            away_bias = result['predicted_away_score'] - result['actual_away_score']
            score_biases.append({'home_bias': home_bias, 'away_bias': away_bias})
        
        analysis['avg_home_bias'] = np.mean([b['home_bias'] for b in score_biases])
        analysis['avg_away_bias'] = np.mean([b['away_bias'] for b in score_biases])
        
        return analysis
    
    def calculate_confidence_calibration(self, confidence_data: List[Dict]) -> float:
        """Calculate how well confidence matches actual accuracy"""
        if not confidence_data:
            return 1.0
        
        # Group by confidence ranges
        ranges = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
        calibration_errors = []
        
        for min_conf, max_conf in ranges:
            range_data = [d for d in confidence_data if min_conf <= d['confidence'] < max_conf]
            if range_data:
                avg_confidence = np.mean([d['confidence'] for d in range_data])
                actual_accuracy = np.mean([d['correct'] for d in range_data])
                calibration_errors.append(abs(avg_confidence - actual_accuracy))
        
        # Overall calibration factor
        avg_confidence = np.mean([d['confidence'] for d in confidence_data])
        actual_accuracy = np.mean([d['correct'] for d in confidence_data])
        
        if avg_confidence > 0:
            calibration_factor = actual_accuracy / avg_confidence
        else:
            calibration_factor = 1.0
        
        return calibration_factor
    
    def calculate_adjustments(self, analysis: Dict) -> Dict:
        """Calculate model adjustments based on analysis"""
        adjustments = {}
        
        # 1. Confidence calibration factor
        calibration_factor = analysis.get('confidence_calibration', 1.0)
        adjustments['confidence_multiplier'] = calibration_factor
        
        # 2. Score prediction adjustments
        home_bias = analysis.get('avg_home_bias', 0)
        away_bias = analysis.get('avg_away_bias', 0)
        adjustments['home_score_adjustment'] = -home_bias  # Negative to correct bias
        adjustments['away_score_adjustment'] = -away_bias
        
        # 3. Home advantage adjustment
        # If model is overconfident in home teams, reduce home advantage
        accuracy = analysis.get('accuracy', 0.5)
        if accuracy < 0.5:
            # Model is worse than random, need more conservative home advantage
            adjustments['home_advantage_multiplier'] = 0.8
        elif accuracy < 0.55:
            adjustments['home_advantage_multiplier'] = 0.9
        else:
            adjustments['home_advantage_multiplier'] = 1.0
        
        # 4. Strength calculation adjustment
        # If overall accuracy is low, reduce confidence in strength differences
        if accuracy < 0.5:
            adjustments['strength_variance_multiplier'] = 0.7
        elif accuracy < 0.55:
            adjustments['strength_variance_multiplier'] = 0.85
        else:
            adjustments['strength_variance_multiplier'] = 1.0
        
        # 5. Margin of error adjustment
        score_error = analysis.get('avg_score_error', 0)
        if score_error > 15:
            adjustments['score_prediction_reliability'] = 0.6
        elif score_error > 10:
            adjustments['score_prediction_reliability'] = 0.8
        else:
            adjustments['score_prediction_reliability'] = 1.0
        
        return adjustments
    
    def save_calibration(self, adjustments: Dict):
        """Save calibration parameters to file"""
        calibration_data = {
            'timestamp': datetime.now().isoformat(),
            'adjustments': adjustments,
            'backtest_source': 'auto_calibration',
            'version': '1.0'
        }
        
        try:
            with open('model_calibration.json', 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            logging.info("Calibration parameters saved to model_calibration.json")
            return True
        except Exception as e:
            logging.error(f"Error saving calibration: {e}")
            return False
    
    def print_calibration_report(self, analysis: Dict, adjustments: Dict):
        """Print calibration report"""
        print("\n" + "=" * 80)
        print("MODEL CALIBRATION REPORT")
        print("=" * 80)
        
        print("\nCurrent Performance:")
        print(f"  Accuracy: {analysis['accuracy']:.1%}")
        print(f"  Average Confidence: {analysis['avg_confidence']:.1%}")
        print(f"  Average Score Error: {analysis['avg_score_error']:.1f} points")
        print(f"  Games Analyzed: {analysis['total_games']}")
        
        print("\nDiagnostics:")
        calibration = analysis.get('confidence_calibration', 1.0)
        if calibration < 0.9:
            print(f"  WARNING: Model is OVERCONFIDENT by {(1-calibration)*100:.0f}%")
        elif calibration > 1.1:
            print(f"  NOTE: Model is UNDERCONFIDENT by {(calibration-1)*100:.0f}%")
        else:
            print(f"  OK: Model confidence is well-calibrated")
        
        home_bias = analysis.get('avg_home_bias', 0)
        if abs(home_bias) > 2:
            print(f"  WARNING: Home score predictions biased by {home_bias:+.1f} points")
        
        away_bias = analysis.get('avg_away_bias', 0)
        if abs(away_bias) > 2:
            print(f"  WARNING: Away score predictions biased by {away_bias:+.1f} points")
        
        print("\nRecommended Adjustments:")
        print(f"  Confidence Multiplier: {adjustments['confidence_multiplier']:.3f}")
        print(f"  Home Score Adjustment: {adjustments['home_score_adjustment']:+.1f} points")
        print(f"  Away Score Adjustment: {adjustments['away_score_adjustment']:+.1f} points")
        print(f"  Home Advantage Multiplier: {adjustments['home_advantage_multiplier']:.2f}")
        print(f"  Strength Variance Multiplier: {adjustments['strength_variance_multiplier']:.2f}")
        
        print("\nImpact:")
        if adjustments['confidence_multiplier'] < 1.0:
            print(f"  - Reduce all confidence scores by {(1-adjustments['confidence_multiplier'])*100:.0f}%")
        elif adjustments['confidence_multiplier'] > 1.0:
            print(f"  - Increase all confidence scores by {(adjustments['confidence_multiplier']-1)*100:.0f}%")
        
        if adjustments['home_advantage_multiplier'] < 1.0:
            print(f"  - Reduce home court advantage by {(1-adjustments['home_advantage_multiplier'])*100:.0f}%")
        
        if adjustments['strength_variance_multiplier'] < 1.0:
            print(f"  - Make predictions more conservative by {(1-adjustments['strength_variance_multiplier'])*100:.0f}%")
        
        print("\nNext Steps:")
        print("  1. Calibration saved to model_calibration.json")
        print("  2. Update database_prediction.py to use these adjustments")
        print("  3. Run backtest again to verify improvements")
        print("=" * 80)
    
    def run_calibration(self):
        """Run complete calibration process"""
        print("Starting Automatic Model Calibration")
        print("=" * 80)
        
        # Load backtest results
        if not self.load_latest_backtest():
            print("ERROR: Could not load backtest results")
            return False
        
        # Analyze performance
        print("Analyzing backtest performance...")
        analysis = self.analyze_performance()
        
        if not analysis:
            print("ERROR: Could not analyze performance")
            return False
        
        # Calculate adjustments
        print("Calculating model adjustments...")
        adjustments = self.calculate_adjustments(analysis)
        
        # Save calibration
        print("Saving calibration parameters...")
        if not self.save_calibration(adjustments):
            print("ERROR: Could not save calibration")
            return False
        
        # Print report
        self.print_calibration_report(analysis, adjustments)
        
        return True

def main():
    """Main calibration function"""
    calibrator = ModelCalibrator()
    success = calibrator.run_calibration()
    
    if success:
        print("\nCalibration complete! Model adjustments saved.")
    else:
        print("\nCalibration failed. Check logs for details.")

if __name__ == "__main__":
    main()




