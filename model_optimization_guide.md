# Model Optimization Guide

## Overview

This guide shows how to systematically optimize the 207 parameters in the advanced configuration to maximize prediction accuracy.

## Prerequisites

- Advanced configuration loaded (`model_config_advanced.py`)
- Historical game data for backtesting
- Backtest verification tool (`verify_backtest_data.py`)

## Optimization Process

### Phase 1: Baseline Establishment

```python
# Run backtest with default advanced config
from enhanced_prediction import predict_game_outcome_advanced
from model_optimization import run_full_backtest

# Test on last season's games
results = run_full_backtest(
    start_date='2024-10-01',
    end_date='2025-04-30',
    config='advanced'
)

print(f"Baseline Accuracy: {results['accuracy']:.2%}")
print(f"Average Confidence: {results['avg_confidence']:.2%}")
print(f"Score MAE: {results['score_mae']:.2f}")
```

### Phase 2: Grid Search on Key Parameters

```python
from model_config_advanced import load_config, update_parameter, save_config
import numpy as np

config = load_config()

# Test range for home advantage
home_adv_range = np.arange(0.08, 0.13, 0.01)

best_accuracy = 0
best_home_adv = 0.10

for home_adv in home_adv_range:
    # Update config
    update_parameter(config, home_adv, 'home_advantage', 'base_advantage')
    save_config(config)
    
    # Run backtest
    results = run_full_backtest(...)
    
    if results['accuracy'] > best_accuracy:
        best_accuracy = results['accuracy']
        best_home_adv = home_adv

print(f"Optimal home advantage: {best_home_adv}")
```

### Phase 3: Strength Weights Optimization

```python
from scipy.optimize import minimize

def objective_function(weights):
    """Objective to minimize (negative accuracy)"""
    # Ensure weights sum to 1.0
    weights = weights / weights.sum()
    
    # Update config
    config = load_config()
    param_names = ['win_percentage', 'point_differential', 'offensive_efficiency',
                   'defensive_efficiency', 'recent_form', 'news_sentiment']
    
    for i, name in enumerate(param_names):
        update_parameter(config, float(weights[i]), 'strength_weights', name)
    
    save_config(config)
    
    # Run backtest
    results = run_full_backtest(...)
    
    # Return negative accuracy (we want to maximize, scipy minimizes)
    return -results['accuracy']

# Initial weights
x0 = np.array([0.25, 0.20, 0.15, 0.15, 0.15, 0.10])

# Constraints: weights must sum to 1.0, all positive
constraints = [
    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
]
bounds = [(0.05, 0.40) for _ in range(6)]

# Optimize
result = minimize(
    objective_function,
    x0,
    method='SLSQP',
    bounds=bounds,
    constraints=constraints
)

optimal_weights = result.x / result.x.sum()
print("Optimal strength weights:", optimal_weights)
```

### Phase 4: Confidence Calibration

```python
def calibrate_confidence(results_df):
    """
    Calibrate confidence scores based on actual accuracy
    
    Args:
        results_df: DataFrame with columns: ['confidence', 'is_correct']
    
    Returns:
        dict: Calibration multipliers by confidence bin
    """
    bins = [0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.0]
    calibration = {}
    
    for i in range(len(bins)-1):
        bin_mask = (results_df['confidence'] >= bins[i]) & (results_df['confidence'] < bins[i+1])
        bin_data = results_df[bin_mask]
        
        if len(bin_data) > 0:
            actual_accuracy = bin_data['is_correct'].mean()
            predicted_conf = bin_data['confidence'].mean()
            
            # Calibration factor
            if predicted_conf > 0:
                calibration[f"{bins[i]:.2f}-{bins[i+1]:.2f}"] = actual_accuracy / predicted_conf
    
    return calibration

# Run backtest and collect results
results_df = run_detailed_backtest(...)

# Get calibration factors
calibration = calibrate_confidence(results_df)

print("Confidence calibration factors:")
for bin_range, factor in calibration.items():
    print(f"  {bin_range}: {factor:.3f}")
```

### Phase 5: Advanced Feature Engineering

```python
# Test different time decay rates
decay_rates = [0.90, 0.93, 0.95, 0.97, 0.99]

results = []
for decay in decay_rates:
    update_parameter(config, decay, 'recent_form', 'time_decay', 'decay_rate')
    save_config(config)
    
    accuracy = run_full_backtest(...)['accuracy']
    results.append((decay, accuracy))

best_decay = max(results, key=lambda x: x[1])
print(f"Optimal decay rate: {best_decay[0]} (accuracy: {best_decay[1]:.2%})")
```

## Optimization Strategies

### Strategy 1: Greedy Sequential

Optimize one parameter at a time while keeping others fixed.

**Pros**: Simple, interpretable
**Cons**: May miss global optimum

```python
def greedy_optimize(param_path, value_range):
    """
    Optimize single parameter greedily
    
    Args:
        param_path: tuple of keys (e.g., ('home_advantage', 'base_advantage'))
        value_range: array of values to test
    """
    config = load_config()
    best_accuracy = 0
    best_value = None
    
    for value in value_range:
        update_parameter(config, value, *param_path)
        save_config(config)
        
        results = run_full_backtest(...)
        if results['accuracy'] > best_accuracy:
            best_accuracy = results['accuracy']
            best_value = value
    
    return best_value, best_accuracy
```

### Strategy 2: Bayesian Optimization

Use Bayesian optimization for efficient parameter search.

```python
from skopt import gp_minimize
from skopt.space import Real

def objective(params):
    """Objective function for Bayesian optimization"""
    home_adv, win_weight, diff_weight = params
    
    config = load_config()
    update_parameter(config, home_adv, 'home_advantage', 'base_advantage')
    update_parameter(config, win_weight, 'strength_weights', 'win_percentage')
    update_parameter(config, diff_weight, 'strength_weights', 'point_differential')
    
    # Normalize weights
    # ... (normalize other weights to sum to 1.0)
    
    save_config(config)
    results = run_full_backtest(...)
    
    return -results['accuracy']  # Minimize negative accuracy

# Define search space
space = [
    Real(0.08, 0.13, name='home_advantage'),
    Real(0.15, 0.35, name='win_percentage'),
    Real(0.15, 0.30, name='point_differential')
]

# Run optimization
res = gp_minimize(objective, space, n_calls=50, random_state=42)

print(f"Best parameters: {res.x}")
print(f"Best accuracy: {-res.fun:.2%}")
```

### Strategy 3: Genetic Algorithm

Evolve parameters using genetic algorithm.

```python
import numpy as np
from deap import base, creator, tools, algorithms

def evaluate_config(individual):
    """Evaluate fitness of a configuration"""
    # individual is array of parameter values
    # Map to actual config and test
    
    config = load_config()
    # Update config with individual's values
    # ... (mapping logic)
    
    results = run_full_backtest(...)
    return (results['accuracy'],)  # Return as tuple

# Setup DEAP
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", np.random.uniform, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=10)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_config)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Run evolution
pop = toolbox.population(n=50)
hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)

pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=20, 
                                stats=stats, halloffame=hof, verbose=True)

best_individual = hof[0]
print(f"Best configuration: {best_individual}")
```

## Evaluation Metrics

### Primary Metrics

```python
def calculate_metrics(predictions, actuals):
    """Calculate comprehensive evaluation metrics"""
    metrics = {}
    
    # Accuracy
    metrics['accuracy'] = np.mean(predictions['winner'] == actuals['winner'])
    
    # Confidence-weighted accuracy
    metrics['weighted_accuracy'] = np.sum(
        (predictions['winner'] == actuals['winner']) * predictions['confidence']
    ) / np.sum(predictions['confidence'])
    
    # Score prediction MAE
    metrics['home_score_mae'] = np.mean(np.abs(
        predictions['home_score'] - actuals['home_score']
    ))
    metrics['away_score_mae'] = np.mean(np.abs(
        predictions['away_score'] - actuals['away_score']
    ))
    
    # Spread accuracy (within 5 points)
    spread_diff = np.abs(
        (predictions['home_score'] - predictions['away_score']) - 
        (actuals['home_score'] - actuals['away_score'])
    )
    metrics['spread_accuracy_5'] = np.mean(spread_diff <= 5)
    
    # Brier score (probabilistic accuracy)
    brier_score = np.mean((predictions['probability'] - actuals['outcome']) ** 2)
    metrics['brier_score'] = brier_score
    
    # Log loss
    epsilon = 1e-15
    probs = np.clip(predictions['probability'], epsilon, 1 - epsilon)
    log_loss = -np.mean(
        actuals['outcome'] * np.log(probs) + 
        (1 - actuals['outcome']) * np.log(1 - probs)
    )
    metrics['log_loss'] = log_loss
    
    return metrics
```

### Secondary Metrics

```python
def calculate_advanced_metrics(predictions, actuals):
    """Calculate advanced evaluation metrics"""
    metrics = {}
    
    # Accuracy by confidence bin
    bins = [0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.0]
    for i in range(len(bins)-1):
        mask = (predictions['confidence'] >= bins[i]) & (predictions['confidence'] < bins[i+1])
        if mask.any():
            metrics[f'accuracy_{bins[i]:.2f}_{bins[i+1]:.2f}'] = np.mean(
                predictions.loc[mask, 'winner'] == actuals.loc[mask, 'winner']
            )
    
    # Home/away accuracy
    metrics['home_accuracy'] = np.mean(
        predictions['home_team'] == actuals['winner']
    )
    metrics['away_accuracy'] = np.mean(
        predictions['away_team'] == actuals['winner']
    )
    
    # Accuracy by prediction strength
    pred_gap = np.abs(predictions['home_strength'] - predictions['away_strength'])
    metrics['strong_pred_accuracy'] = np.mean(
        (predictions.loc[pred_gap > 0.2, 'winner'] == actuals.loc[pred_gap > 0.2, 'winner'])
    )
    metrics['weak_pred_accuracy'] = np.mean(
        (predictions.loc[pred_gap < 0.1, 'winner'] == actuals.loc[pred_gap < 0.1, 'winner'])
    )
    
    return metrics
```

## Best Practices

### 1. Use Hold-Out Validation

```python
# Split data: 70% train, 30% test
train_games = historical_games[:int(len(historical_games) * 0.7)]
test_games = historical_games[int(len(historical_games) * 0.7):]

# Optimize on train set
optimize_params(train_games)

# Evaluate on test set
final_metrics = evaluate(test_games)
```

### 2. Cross-Validation

```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)

fold_results = []
for train_idx, val_idx in kf.split(historical_games):
    train_games = historical_games.iloc[train_idx]
    val_games = historical_games.iloc[val_idx]
    
    # Optimize on train
    optimize_params(train_games)
    
    # Evaluate on validation
    metrics = evaluate(val_games)
    fold_results.append(metrics)

# Average across folds
avg_accuracy = np.mean([r['accuracy'] for r in fold_results])
print(f"CV Accuracy: {avg_accuracy:.2%} ± {np.std([r['accuracy'] for r in fold_results]):.2%}")
```

### 3. Early Stopping

```python
def optimize_with_early_stopping(param_path, value_range, patience=5):
    """Optimize with early stopping if no improvement"""
    best_accuracy = 0
    best_value = None
    no_improve_count = 0
    
    for value in value_range:
        update_parameter(config, value, *param_path)
        save_config(config)
        
        results = run_full_backtest(...)
        
        if results['accuracy'] > best_accuracy:
            best_accuracy = results['accuracy']
            best_value = value
            no_improve_count = 0
        else:
            no_improve_count += 1
            
        if no_improve_count >= patience:
            print(f"Early stopping at {value}")
            break
    
    return best_value, best_accuracy
```

### 4. Parameter Importance Analysis

```python
def analyze_parameter_importance():
    """Analyze which parameters have most impact on accuracy"""
    base_config = load_config()
    base_accuracy = run_full_backtest(...)['accuracy']
    
    importance = {}
    
    # Test each parameter
    param_tests = [
        (('home_advantage', 'base_advantage'), [0.08, 0.10, 0.12]),
        (('strength_weights', 'win_percentage'), [0.20, 0.25, 0.30]),
        # ... more parameters
    ]
    
    for param_path, values in param_tests:
        accuracies = []
        for value in values:
            config = load_config()
            update_parameter(config, value, *param_path)
            save_config(config)
            
            accuracy = run_full_backtest(...)['accuracy']
            accuracies.append(accuracy)
        
        # Importance = variance in accuracy
        importance[param_path] = np.var(accuracies)
    
    # Sort by importance
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    
    print("Parameter importance ranking:")
    for param, var in sorted_importance:
        print(f"  {param}: {var:.6f}")
    
    return sorted_importance
```

## Monitoring and Iteration

### Track Optimization History

```python
from model_config import add_optimization_result

# After each optimization run
add_optimization_result(
    accuracy=results['accuracy'],
    confidence=results['avg_confidence'],
    avg_score_error=results['score_mae'],
    config_used=config
)

# View history
from model_config import get_best_config

best = get_best_config()
print(f"Best historical config had {best['accuracy']:.2%} accuracy")
```

### A/B Testing in Production

```python
# Deploy both configs, randomly assign
import random

def get_prediction(home_team, away_team, game_date):
    if random.random() < 0.5:
        # Config A (current)
        return predict_with_config_a(home_team, away_team, game_date)
    else:
        # Config B (new)
        return predict_with_config_b(home_team, away_team, game_date)

# Track results and compare after N predictions
```

## Conclusion

Systematic optimization of the 207 parameters requires:
1. **Baseline establishment**
2. **Methodical testing** of parameter ranges
3. **Proper validation** to avoid overfitting
4. **Continuous monitoring** of production performance
5. **Iterative improvement** based on results

Expected timeline:
- Initial optimization: 1-2 weeks
- Fine-tuning: 2-4 weeks
- Production validation: 4-8 weeks
- Ongoing maintenance: Monthly reviews
















