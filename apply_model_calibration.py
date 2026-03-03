#!/usr/bin/env python3
"""
Apply Model Calibration to Predictions
Loads calibration parameters and adjusts predictions accordingly
"""

import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CalibrationApplier:
    """Apply calibration adjustments to predictions"""
    
    def __init__(self):
        self.calibration = None
        self.load_calibration()
    
    def load_calibration(self):
        """Load calibration parameters"""
        if not os.path.exists('model_calibration.json'):
            logging.warning("No calibration file found. Using default parameters.")
            self.calibration = self.get_default_calibration()
            return False
        
        try:
            with open('model_calibration.json', 'r') as f:
                self.calibration = json.load(f)
            
            logging.info("Calibration parameters loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Error loading calibration: {e}")
            self.calibration = self.get_default_calibration()
            return False
    
    def get_default_calibration(self):
        """Get default calibration (no adjustments)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'adjustments': {
                'confidence_multiplier': 1.0,
                'home_score_adjustment': 0.0,
                'away_score_adjustment': 0.0,
                'home_advantage_multiplier': 1.0,
                'strength_variance_multiplier': 1.0,
                'score_prediction_reliability': 1.0
            }
        }
    
    def apply_to_prediction(self, prediction: dict) -> dict:
        """Apply calibration adjustments to a prediction"""
        if not self.calibration:
            return prediction
        
        adjustments = self.calibration.get('adjustments', {})
        adjusted = prediction.copy()
        
        # Apply confidence adjustment
        conf_mult = adjustments.get('confidence_multiplier', 1.0)
        adjusted['confidence'] = min(1.0, max(0.0, prediction['confidence'] * conf_mult))
        
        # Apply score adjustments
        home_adj = adjustments.get('home_score_adjustment', 0.0)
        away_adj = adjustments.get('away_score_adjustment', 0.0)
        
        if 'predicted_home_score' in adjusted:
            adjusted['predicted_home_score'] = int(prediction['predicted_home_score'] + home_adj)
        if 'predicted_away_score' in adjusted:
            adjusted['predicted_away_score'] = int(prediction['predicted_away_score'] + away_adj)
        
        # Apply home advantage adjustment
        home_adv_mult = adjustments.get('home_advantage_multiplier', 1.0)
        if 'home_strength' in adjusted:
            # Adjust home strength by reducing/increasing home advantage component
            adjusted['home_advantage_factor'] = home_adv_mult
        
        # Apply strength variance adjustment
        strength_mult = adjustments.get('strength_variance_multiplier', 1.0)
        if 'prediction_score' in adjusted:
            # Make prediction less extreme
            adjusted['prediction_score'] = prediction['prediction_score'] * strength_mult
        
        # Add calibration metadata
        adjusted['calibrated'] = True
        adjusted['calibration_timestamp'] = self.calibration.get('timestamp')
        
        return adjusted
    
    def print_adjustment_info(self):
        """Print information about current adjustments"""
        if not self.calibration:
            print("No calibration loaded")
            return
        
        adjustments = self.calibration.get('adjustments', {})
        
        print("\nActive Calibration Adjustments:")
        print("=" * 60)
        print(f"Loaded from: {self.calibration.get('timestamp', 'Unknown')}")
        print(f"\nAdjustments:")
        print(f"  Confidence Multiplier: {adjustments.get('confidence_multiplier', 1.0):.3f}")
        print(f"  Home Score Adjustment: {adjustments.get('home_score_adjustment', 0.0):+.1f} points")
        print(f"  Away Score Adjustment: {adjustments.get('away_score_adjustment', 0.0):+.1f} points")
        print(f"  Home Advantage Multiplier: {adjustments.get('home_advantage_multiplier', 1.0):.2f}")
        print(f"  Strength Variance Multiplier: {adjustments.get('strength_variance_multiplier', 1.0):.2f}")
        print("=" * 60)

# Global calibration applier instance
_calibration_applier = None

def get_calibration_applier():
    """Get global calibration applier instance"""
    global _calibration_applier
    if _calibration_applier is None:
        _calibration_applier = CalibrationApplier()
    return _calibration_applier

def apply_calibration(prediction: dict) -> dict:
    """Apply calibration to a prediction (convenience function)"""
    applier = get_calibration_applier()
    return applier.apply_to_prediction(prediction)

def main():
    """Test calibration application"""
    applier = CalibrationApplier()
    applier.print_adjustment_info()
    
    # Test prediction
    test_prediction = {
        'predicted_winner': 'Boston Celtics',
        'confidence': 0.75,
        'predicted_home_score': 115,
        'predicted_away_score': 108,
        'home_strength': 0.65,
        'away_strength': 0.55,
        'prediction_score': 0.10
    }
    
    print("\nTest Prediction:")
    print(f"  Original Confidence: {test_prediction['confidence']:.1%}")
    print(f"  Original Scores: {test_prediction['predicted_away_score']}-{test_prediction['predicted_home_score']}")
    
    adjusted = applier.apply_to_prediction(test_prediction)
    
    print("\nAdjusted Prediction:")
    print(f"  Adjusted Confidence: {adjusted['confidence']:.1%}")
    print(f"  Adjusted Scores: {adjusted['predicted_away_score']}-{adjusted['predicted_home_score']}")
    print(f"  Confidence Change: {(adjusted['confidence'] - test_prediction['confidence'])*100:+.1f}%")

if __name__ == "__main__":
    main()




