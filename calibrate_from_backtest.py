#!/usr/bin/env python3
"""
Calibrate Prediction Model from Backtest Results
Adjust confidence and accuracy based on backtest performance
"""

import json
import numpy as np
from datetime import datetime
import os

def analyze_backtest_results(results_file='backtest_results.json'):
    """Analyze backtest results and generate calibration factors"""
    
    if not os.path.exists(results_file):
        print(f"❌ Backtest results file not found: {results_file}")
        return None
    
    # Load results
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data.get('detailed_results', [])
    
    if not results:
        print("❌ No results found in backtest file")
        return None
    
    print(f"📊 Analyzing {len(results)} backtest results...")
    
    # Calculate metrics by confidence bucket
    confidence_buckets = {
        'very_low': {'range': (0, 0.4), 'predictions': [], 'correct': 0},
        'low': {'range': (0.4, 0.5), 'predictions': [], 'correct': 0},
        'medium': {'range': (0.5, 0.6), 'predictions': [], 'correct': 0},
        'high': {'range': (0.6, 0.7), 'predictions': [], 'correct': 0},
        'very_high': {'range': (0.7, 1.0), 'predictions': [], 'correct': 0}
    }
    
    # Categorize predictions
    for result in results:
        confidence = result['confidence']
        is_correct = result['is_correct']
        
        for bucket_name, bucket in confidence_buckets.items():
            min_conf, max_conf = bucket['range']
            if min_conf <= confidence < max_conf:
                bucket['predictions'].append(result)
                if is_correct:
                    bucket['correct'] += 1
                break
    
    # Calculate calibration factors
    calibration_factors = {}
    
    print("\n📈 Confidence Calibration Analysis:")
    print("=" * 60)
    
    for bucket_name, bucket in confidence_buckets.items():
        predictions = bucket['predictions']
        if not predictions:
            continue
        
        count = len(predictions)
        correct = bucket['correct']
        actual_accuracy = correct / count
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        
        # Calculate calibration factor
        # If confidence is higher than actual accuracy, reduce it
        # If confidence is lower than actual accuracy, increase it
        calibration_factor = actual_accuracy / avg_confidence if avg_confidence > 0 else 1.0
        
        calibration_factors[bucket_name] = {
            'count': count,
            'actual_accuracy': actual_accuracy,
            'avg_confidence': avg_confidence,
            'calibration_factor': calibration_factor,
            'range': bucket['range']
        }
        
        print(f"\n{bucket_name.upper()} ({bucket['range'][0]:.0%}-{bucket['range'][1]:.0%}):")
        print(f"  Games: {count}")
        print(f"  Avg Confidence: {avg_confidence:.1%}")
        print(f"  Actual Accuracy: {actual_accuracy:.1%}")
        print(f"  Calibration Factor: {calibration_factor:.3f}")
        
        if calibration_factor < 0.9:
            print(f"  ⚠️  Model is OVERCONFIDENT - reduce confidence by {(1-calibration_factor)*100:.0f}%")
        elif calibration_factor > 1.1:
            print(f"  ⚠️  Model is UNDERCONFIDENT - increase confidence by {(calibration_factor-1)*100:.0f}%")
        else:
            print(f"  ✅ Well calibrated")
    
    # Overall statistics
    total_predictions = len(results)
    total_correct = sum(r['is_correct'] for r in results)
    overall_accuracy = total_correct / total_predictions
    avg_confidence = np.mean([r['confidence'] for r in results])
    
    print(f"\n📊 OVERALL STATISTICS:")
    print("=" * 60)
    print(f"Total Predictions: {total_predictions}")
    print(f"Correct: {total_correct}")
    print(f"Accuracy: {overall_accuracy:.1%}")
    print(f"Average Confidence: {avg_confidence:.1%}")
    print(f"Overall Calibration: {overall_accuracy / avg_confidence:.3f}")
    
    return {
        'calibration_factors': calibration_factors,
        'overall_accuracy': overall_accuracy,
        'avg_confidence': avg_confidence,
        'timestamp': datetime.now().isoformat()
    }

def generate_calibrated_confidence_function(calibration_data):
    """Generate Python code for calibrated confidence calculation"""
    
    if not calibration_data:
        return None
    
    print(f"\n🔧 Generating Calibrated Confidence Function:")
    print("=" * 60)
    
    code = '''
def apply_confidence_calibration(raw_confidence, calibration_data):
    """Apply calibration to raw confidence based on backtest results"""
    
    # Define confidence buckets and their calibration factors
    calibration_factors = {
'''
    
    for bucket_name, data in calibration_data['calibration_factors'].items():
        code += f"        '{bucket_name}': {{'range': {data['range']}, 'factor': {data['calibration_factor']:.3f}}},\n"
    
    code += '''    }
    
    # Find appropriate calibration factor
    calibration_factor = 1.0
    for bucket_name, bucket in calibration_factors.items():
        min_conf, max_conf = bucket['range']
        if min_conf <= raw_confidence < max_conf:
            calibration_factor = bucket['factor']
            break
    
    # Apply calibration
    calibrated_confidence = raw_confidence * calibration_factor
    
    # Ensure bounds
    calibrated_confidence = max(0.15, min(0.80, calibrated_confidence))
    
    return calibrated_confidence
'''
    
    print(code)
    
    # Save to file
    with open('confidence_calibration.py', 'w') as f:
        f.write(code)
    
    print("\n✅ Calibration function saved to confidence_calibration.py")
    
    return code

def update_prediction_with_calibration(calibration_data):
    """Update database_prediction.py with calibration"""
    
    print(f"\n🔄 Updating Prediction System with Calibration:")
    print("=" * 60)
    
    # Generate calibration adjustments
    adjustments = []
    
    for bucket_name, data in calibration_data['calibration_factors'].items():
        factor = data['calibration_factor']
        if factor < 0.9:
            adjustment = f"Reduce {bucket_name} confidence by {(1-factor)*100:.0f}%"
        elif factor > 1.1:
            adjustment = f"Increase {bucket_name} confidence by {(factor-1)*100:.0f}%"
        else:
            adjustment = f"{bucket_name} confidence well-calibrated"
        adjustments.append(adjustment)
    
    print("📋 Recommended Adjustments:")
    for adj in adjustments:
        print(f"  • {adj}")
    
    # Calculate global adjustment
    overall_factor = calibration_data['overall_accuracy'] / calibration_data['avg_confidence']
    
    print(f"\n🎯 Global Calibration Factor: {overall_factor:.3f}")
    
    if overall_factor < 0.9:
        print(f"  ⚠️  Model is {((1-overall_factor)*100):.0f}% overconfident overall")
        print(f"  💡 Recommendation: Multiply all confidence scores by {overall_factor:.3f}")
    elif overall_factor > 1.1:
        print(f"  ⚠️  Model is {((overall_factor-1)*100):.0f}% underconfident overall")
        print(f"  💡 Recommendation: Multiply all confidence scores by {overall_factor:.3f}")
    else:
        print(f"  ✅ Model is well-calibrated overall")
    
    return overall_factor

def main():
    """Main calibration process"""
    print("🔧 Prediction Model Calibration from Backtest")
    print("=" * 60)
    
    # Analyze backtest results
    calibration_data = analyze_backtest_results()
    
    if not calibration_data:
        print("\n❌ Calibration failed - no backtest data available")
        print("\n💡 Run a backtest first to generate calibration data:")
        print("   1. Go to Streamlit app")
        print("   2. Navigate to Quick Backtest page")
        print("   3. Run backtest and download results")
        print("   4. Save as 'backtest_results.json'")
        return
    
    # Generate calibrated function
    generate_calibrated_confidence_function(calibration_data)
    
    # Update prediction system
    global_factor = update_prediction_with_calibration(calibration_data)
    
    # Save calibration data
    with open('calibration_data.json', 'w') as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"\n💾 Calibration data saved to calibration_data.json")
    print(f"\n✅ Calibration complete!")
    print(f"\n📝 Next steps:")
    print(f"   1. Review the calibration factors above")
    print(f"   2. Apply global factor of {global_factor:.3f} to all predictions")
    print(f"   3. Run another backtest to verify improvements")

if __name__ == "__main__":
    main()

