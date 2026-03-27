# 42-Learn2Slither 🐍

## Overview

A Q-Learning implementation of the classic Snake game for the 42 school project. The agent learns to play Snake using a Q-table that maps game states to optimal actions.

**Performance achieved: ~17.9 average snake length over 100 episodes**

## Architecture

```
src/
├── game.py           # Game logic, reward calculation, state management
├── snake.py          # Snake mechanics (movement, collision, vision)
├── agent.py          # Q-Learning agent (epsilon-greedy, learning)
├── interpreter.py    # Training loop and episode management
├── model_manager.py  # Save/load Q-tables
└── gui.py            # Visual rendering
```

## Game Configuration

**Board:** 10×10 with walls
**Apples:** 
- 2 GREEN (+100 reward when eaten, growth)
- 1 RED (-1 penalty when eaten, shrink)

**Agent:**
- **Learning Rate:** 0.1
- **Discount Factor (γ):** 0.95
- **Epsilon:** 0 (pure exploitation - no random exploration)
- **Movement Cost:** -1 per step
- **Inactivity Penalty:** 0.5 per step after 20 steps without eating
- **Starvation Limit:** 200 steps without eating = -10000 penalty + episode termination

## Reward System (Optimized)

```python
if snake.ate_apple:
    reward = +100
else:
    reward = -1 (movement cost)
    + inactivity_penalty (up to -0.5/step)
    + proximity_bonus (if apple visible in vision):
        - Distance 1: +3.0
        - Distance 2: +2.0
        - Distance 3: +1.5
        - Distance 4+: +0.5
```

**Key Insight:** Proximity bonus ONLY applies when the green apple is visible in the snake's direct line of sight (vision range 1-9). This encourages the agent to actively seek nearby food without shaping rewards for apples it can't see.

## Training Strategy

### Best-Model Tracking (Window-Based)
- Every 100 episodes, calculate average of the last 100
- If window_avg > best_window_avg: save Q-table snapshot
- Rationale: Single episode peaks are outliers; 100-episode windows show sustainable performance
- **Result:** Training performance (17.9) transfers perfectly to test (17.14)

### Epsilon Strategy
- Tested and rejected: Hybrid epsilon (0→0.1), Epsilon decay (0.6→0)
- Reason: Random actions destroy carefully-built Q-values
- **Final:** Epsilon=0 (pure exploitation) → fastest convergence

## Usage

### Train a New Model
```bash
python main.py
# Choose option 1: Train agent and save model
# Enter number of episodes (e.g., 20000)
# Choose fast mode (no GUI) for speed
```

### Test a Saved Model
```bash
python main.py
# Choose option 2: Load and test saved model
# Select model to test
```

### Quick Test Script (20k episodes)
```bash
python test_decay_then_test.py
```
Trains for 20k episodes with window-based best-model tracking, saves best model, tests it for 100 episodes.

### Play with GUI (Untrained Agent)
```bash
python main.py
# Choose option 3: Play with GUI
```

## Performance Metrics

### Baseline Configurations Tested

| Config | Training Avg | Test Avg | Gap | Notes |
|--------|-------------|----------|-----|-------|
| Apple visible only | 17.7 | 16.62 | -1.08 | Simple +5 bonus when apple visible |
| No apple visible | 17.1 | 17.04 | -0.06 | Removing bonus hurts learning |
| **Enhanced proximity** ✓ | **17.9** | **17.14** | **-0.76** | Best performance |
| Green reward 150 | 17.5 | 15.38 | -2.12 | Too high reward destabilizes learning |

## Key Findings

1. **Epsilon=0 is optimal:** Pure exploitation converges fastest; exploration destroys learned Q-values
2. **Single-episode peaks are misleading:** Best single episode ≠ sustainable best strategy
3. **Window-based tracking (100-ep) solves this:** Captures consistent performance, not lucky spikes
4. **Proximity bonus needs vision constraint:** Rewarding distance to unseen apples confuses the agent
5. **Train-test transfer matters:** Model saved from training peak should match test performance

## Files Structure

**Essential Files:**
- `main.py` - CLI for training, testing, playing
- `test_decay_then_test.py` - Automated test script (20k episodes)
- `src/` - All game and agent logic
- `models/` - Saved Q-table models

**Experimental Files (Non-Essential):**
- `train_*.py` - Various hyperparameter experiments
- `test_*.py` - One-off tests for epsilon strategies

## Model Files

Saved models in `models/`:
- `best_window_20k.json` - Baseline with proximity bonus
- `best_proximity_bonus_20k.json` - Enhanced proximity (final best)
- Others are experimental variants

## Implementation Notes

### Why Q-Learning?
- Simple and deterministic (no randomness issues with small state space)
- State space: ~40k unique states (more than enough coverage)
- Easy to debug and understand convergence

### State Representation (Vision-Based)
```
Vision dict:
{
  'UP':    (obstacle_dist, has_green, has_red),
  'DOWN':  (obstacle_dist, has_green, has_red),
  'LEFT':  (obstacle_dist, has_green, has_red),
  'RIGHT': (obstacle_dist, has_green, has_red),
  'HEAD_LENGTH': (snake_length,)
}

Obstacle range: 1-9 (1=immediate, 9=far, 10=none)
```

### Action Space
4 discrete actions: UP, DOWN, LEFT, RIGHT

## Troubleshooting

**Model not improving:** Increase episodes (20k→50k) or adjust inactivity penalty
**Model overfitting to one direction:** Reduce epsilon to absolute 0 if not already
**GUI too slow:** Use test_decay_then_test.py for batch training (no GUI)

## Author

Developed as part of 42 school curriculum for Q-Learning practice.