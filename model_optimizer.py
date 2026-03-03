"""
Model Optimizer: Automatic hyperparameter tuning for NBA prediction model
Runs multiple backtests with different parameter configurations
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import itertools
import json
from datetime import datetime
from model_config import load_config, save_config, add_optimization_result
import copy

class ModelOptimizer:
    def __init__(self):
        self.base_config = load_config()
        self.results = []
    
    def generate_configurations(self, param_grid):
        """Generate all combinations of parameters to test
        
        Args:
            param_grid: Dict of parameter names to lists of values to try
            
        Example:
            {
                'home_advantage': [0.08, 0.10, 0.12],
                'strength_weights.win_percentage': [0.25, 0.30, 0.35]
            }
        """
        configs = []
        
        # Get all parameter names and their value lists
        param_names = list(param_grid.keys())
        param_values = [param_grid[name] for name in param_names]
        
        # Generate all combinations
        for combination in itertools.product(*param_values):
            config = copy.deepcopy(self.base_config)
            
            # Apply each parameter value
            for param_name, value in zip(param_names, combination):
                # Handle nested parameters like 'strength_weights.win_percentage'
                keys = param_name.split('.')
                current = config
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[keys[-1]] = value
            
            # Normalize strength_weights to sum to 1.0
            self._normalize_strength_weights(config)
            
            configs.append(config)
        
        return configs
    
    def _normalize_strength_weights(self, config):
        """Ensure strength_weights sum to 1.0"""
        if 'strength_weights' in config:
            weights = config['strength_weights']
            total = sum(weights.values())
            if total > 0:
                for key in weights:
                    weights[key] = weights[key] / total
    
    def run_optimization(self, backtest_func, param_grid, games, num_games=20):
        """Run optimization across multiple configurations
        
        Args:
            backtest_func: Function that runs backtest and returns results
            param_grid: Dict of parameters to optimize
            games: List of games to backtest
            num_games: Number of games per backtest
        
        Returns:
            Best configuration and results
        """
        configurations = self.generate_configurations(param_grid)
        total_configs = len(configurations)
        
        print(f"\n{'='*80}")
        print(f"STARTING MODEL OPTIMIZATION")
        print(f"{'='*80}")
        print(f"Total configurations to test: {total_configs}")
        print(f"Games per configuration: {num_games}")
        print(f"Total predictions: {total_configs * num_games}")
        print(f"{'='*80}\n")
        
        best_config = None
        best_accuracy = 0
        
        for idx, config in enumerate(configurations, 1):
            print(f"\n[{idx}/{total_configs}] Testing configuration...")
            print(f"  Home advantage: {config.get('home_advantage', 0.1):.3f}")
            
            # Show key strength weights
            sw = config.get('strength_weights', {})
            print(f"  Strength weights:")
            print(f"    - Win %: {sw.get('win_percentage', 0.30):.2f}")
            print(f"    - Point Diff: {sw.get('point_differential', 0.25):.2f}")
            print(f"    - Recent Form: {sw.get('recent_form', 0.10):.2f}")
            
            # Run backtest with this configuration
            try:
                results = backtest_func(config, games, num_games)
                
                accuracy = results.get('accuracy', 0)
                avg_confidence = results.get('avg_confidence', 0)
                avg_score_error = results.get('avg_score_error', 999)
                
                print(f"  Results:")
                print(f"    ✓ Accuracy: {accuracy:.1%}")
                print(f"    ✓ Avg Confidence: {avg_confidence:.1%}")
                print(f"    ✓ Avg Score Error: {avg_score_error:.1f} pts")
                
                # Store result
                self.results.append({
                    'config': config,
                    'accuracy': accuracy,
                    'avg_confidence': avg_confidence,
                    'avg_score_error': avg_score_error
                })
                
                # Add to optimization history
                add_optimization_result(accuracy, avg_confidence, avg_score_error, config)
                
                # Track best
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_config = config
                    print(f"    🎯 NEW BEST CONFIGURATION!")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION COMPLETE")
        print(f"{'='*80}")
        
        if best_config:
            print(f"\nBest Configuration:")
            print(f"  Accuracy: {best_accuracy:.1%}")
            print(f"  Home advantage: {best_config.get('home_advantage', 0.1):.3f}")
            
            sw = best_config.get('strength_weights', {})
            print(f"  Strength weights:")
            for key, value in sw.items():
                print(f"    - {key}: {value:.2f}")
            
            # Save best config
            save_config(best_config)
            print(f"\n✓ Best configuration saved to model_config.json")
        
        return {
            'best_config': best_config,
            'best_accuracy': best_accuracy,
            'all_results': self.results
        }
    
    def quick_optimization(self, backtest_func, games, num_games=20):
        """Run a quick optimization with pre-defined parameter ranges"""
        param_grid = {
            'home_advantage': [0.08, 0.10, 0.12, 0.15],
            'strength_weights.win_percentage': [0.25, 0.30, 0.35],
            'strength_weights.recent_form': [0.05, 0.10, 0.15],
            'confidence_weights.high_data_quality.data_quality': [0.25, 0.30, 0.35]
        }
        
        return self.run_optimization(backtest_func, param_grid, games, num_games)
    
    def comprehensive_optimization(self, backtest_func, games, num_games=20):
        """Run a comprehensive optimization with many parameters"""
        param_grid = {
            'home_advantage': [0.05, 0.08, 0.10, 0.12, 0.15],
            'strength_weights.win_percentage': [0.20, 0.25, 0.30, 0.35, 0.40],
            'strength_weights.point_differential': [0.15, 0.20, 0.25, 0.30],
            'strength_weights.recent_form': [0.05, 0.10, 0.15, 0.20],
            'strength_weights.news_sentiment': [0.05, 0.10, 0.15],
            'calibration.smoothing_factor': [0.5, 0.6, 0.7, 0.8]
        }
        
        return self.run_optimization(backtest_func, param_grid, games, num_games)

if __name__ == '__main__':
    # Test configuration generation
    optimizer = ModelOptimizer()
    
    test_grid = {
        'home_advantage': [0.08, 0.10, 0.12],
        'strength_weights.win_percentage': [0.25, 0.30]
    }
    
    configs = optimizer.generate_configurations(test_grid)
    print(f"Generated {len(configs)} configurations")
    
    for i, config in enumerate(configs, 1):
        print(f"\nConfig {i}:")
        print(f"  home_advantage: {config['home_advantage']}")
        print(f"  win_percentage: {config['strength_weights']['win_percentage']}")


