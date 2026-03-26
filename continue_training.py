"""
Quick continuation script - loads model and trains more episodes
Usage: python continue_training.py model_name episodes
Example: python continue_training.py model_100sess 5000
"""

import sys
from src.game import Game
from src.agent import Agent
from src.interpreter import Interpreter
from src.model_manager import ModelManager


def continue_training(model_name, additional_episodes, use_gui=False):
    """Load model and continue training"""
    print(f"\n{'='*60}")
    print(f"RESUMING: {model_name}")
    print(f"Additional episodes: {additional_episodes}")
    if use_gui:
        print(f"Mode: GUI (slower but visual)")
    else:
        print(f"Mode: Fast (no GUI)")
    print(f"{'='*60}\n")
    
    # Load model
    model_manager = ModelManager()
    agent = Agent()
    
    if not model_manager.load_model(agent, model_name):
        print(f"❌ Failed to load {model_name}")
        return False
    
    print(f"✅ Loaded {model_name}")
    print(f"   Q-table: {len(agent.q_table)} states\n")
    
    # Reset for more exploration (but not aggressive - model already trained)
    # Use lower epsilon since model already has good Q-table
    agent.epsilon = 0.3  # Only 30% random, not 60%
    
    # Train
    game = Game(mapsize=10)
    interpreter = Interpreter(agent, game)
    
    episode_lengths = interpreter.train(
        episodes=additional_episodes,
        verbose=True,
        gui=use_gui
    )
    
    if episode_lengths:
        avg = sum(episode_lengths[-10:]) / 10
        mx = max(episode_lengths)
        
        print(f"\n{'='*60}")
        print(f"✅ Done!")
        print(f"   Episodes: {additional_episodes}")
        print(f"   Max: {mx}")
        print(f"   Avg(last 10): {avg:.1f}")
        print(f"{'='*60}\n")
        
        # Save
        model_manager.save_model(agent, model_name)
        print(f"✅ Saved: {model_name}\n")
        
        return True
    
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python continue_training.py <model_name> <episodes> [--gui]")
        print("Example: python continue_training.py model_100sess 5000")
        print("Example with GUI: python continue_training.py model_100sess 500 --gui")
        sys.exit(1)
    
    model_name = sys.argv[1]
    try:
        episodes = int(sys.argv[2])
    except ValueError:
        print("❌ Episodes must be a number")
        sys.exit(1)
    
    use_gui = "--gui" in sys.argv
    
    success = continue_training(model_name, episodes, use_gui)
    sys.exit(0 if success else 1)
