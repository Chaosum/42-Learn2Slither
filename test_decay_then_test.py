#!/usr/bin/env python3
"""
Train with epsilon decay + best-model tracking
Then test the saved best model 100 times to get average size
"""

from src.game import Game
from src.agent import Agent
from src.interpreter import Interpreter
from src.model_manager import ModelManager

if __name__ == "__main__":
    print("=" * 70)
    print("Training with Epsilon=0 (Pure Exploitation) + Best-Model Tracking")
    print("=" * 70)
    print("Strategy:")
    print("  Epsilon: 0 (pure exploitation - fastest convergence)")
    print("  Episodes: 20000")
    print("  Saving: Best episode found during training")
    print("=" * 70)
    
    # ========== PHASE 1: TRAINING ==========
    game = Game(mapsize=10)
    agent = Agent()
    interpreter = Interpreter(agent, game)
    
    print("\nTraining for 20000 episodes...\n")
    training_results = interpreter.train(
        episodes=20000,
        verbose=True,
        gui=False
    )
    
    # Display training results
    print("\n" + "=" * 70)
    print("TRAINING RESULTS")
    print("=" * 70)
    print(f"Total episodes: {len(training_results['episode_lengths'])}")
    print(f"Best 100-episode window average: {training_results['best_window_avg']:.2f}")
    print(f"Best window: episodes {training_results['best_window_start']+1}-{training_results['best_window_end']}")
    
    last_10 = training_results['episode_lengths'][-10:]
    print(f"\nLast 10 episodes: {last_10}")
    print(f"Last 10 avg: {sum(last_10) / 10:.1f}")
    
    # ========== PHASE 2: SAVING ==========
    model_manager = ModelManager()
    print("\n" + "=" * 70)
    model_name = input("Model name to save (default: best_window_20k): ").strip()
    if not model_name:
        model_name = "best_window_20k"
    
    # IMPORTANT: Save the BEST Q-table from the best 100-window, not the final one!
    best_agent_for_saving = Agent()
    best_agent_for_saving.q_table = training_results['best_q_table']
    best_agent_for_saving.epsilon = 0
    best_agent_for_saving.learning_rate = agent.learning_rate
    best_agent_for_saving.discount_factor = agent.discount_factor
    
    model_manager.save_model(best_agent_for_saving, model_name)
    print(f"[OK] Saved BEST window model (ep {training_results['best_window_start']+1}-{training_results['best_window_end']}): {model_name}")
    
    # ========== PHASE 3: TESTING ==========
    print("\n" + "=" * 70)
    print("Testing Best Model (100 episodes)")
    print("=" * 70)
    print(f"Q-table size: {len(training_results['best_q_table'])} states")
    
    # Load the model
    test_agent = Agent()
    model_manager.load_model(test_agent, model_name)
    test_agent.epsilon = 0  # Pure exploitation for testing
    
    print(f"Loaded Q-table size: {len(test_agent.q_table)} states")
    
    test_game = Game(mapsize=10)
    test_interpreter = Interpreter(test_agent, test_game)
    
    print(f"\nTesting {model_name} for 100 episodes (epsilon=0)...\n")
    test_results = test_interpreter.train(
        episodes=100,
        verbose=False,  # Don't spam output
        gui=False
    )
    
    # Calculate stats
    test_sizes = test_results['episode_lengths']
    avg_size = sum(test_sizes) / len(test_sizes)
    max_size = max(test_sizes)
    min_size = min(test_sizes)
    
    print("\n" + "=" * 70)
    print("TEST RESULTS (100 episodes)")
    print("=" * 70)
    print(f"Average size: {avg_size:.2f}")
    print(f"Max size: {max_size}")
    print(f"Min size: {min_size}")
    print(f"Test episode sizes: {test_sizes}")
    print("=" * 70)
