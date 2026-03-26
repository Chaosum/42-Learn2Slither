from src.game import Game
from src.agent import Agent
from src.interpreter import Interpreter
from src.model_manager import ModelManager


def main():
    """Main entry point for training and testing"""
    model_manager = ModelManager()

    while True:
        print("\n" + "=" * 60)
        print("Learn2Slither - Q-Learning Snake Game")
        print("=" * 60)
        print("\n🎮 MAIN MENU")
        print("-" * 60)
        print("1. Train agent and save model")
        print("2. Load and test saved model")
        print("3. Play with GUI (untrained)")
        print("4. Step-by-step demo (untrained)")
        print("5. List saved models")
        print("6. Exit")
        print("-" * 60)

        choice = input("\nChoose (1-6): ").strip()

        if choice == "1":
            train_and_save_model(model_manager)

        elif choice == "2":
            test_saved_model(model_manager)

        elif choice == "3":
            game = Game(mapsize=10)
            agent = Agent()
            interpreter = Interpreter(agent, game)
            print("\n🎥 Loading graphical interface...")
            interpreter.play_episode_gui()

        elif choice == "4":
            game = Game(mapsize=10)
            agent = Agent()
            interpreter = Interpreter(agent, game)
            print("\n🎮 Step-by-step demo (auto)...")
            interpreter.step_by_step_episode(auto=True)

        elif choice == "5":
            model_manager.list_models()

        elif choice == "6":
            print("\nThanks for playing!")
            return

        else:
            print("Invalid choice. Please try again.")


def train_and_save_model(model_manager):
    """Train agent and save model"""
    print("\n📚 TRAINING OPTIONS")
    print("-" * 60)
    print("1. Train 1 session")
    print("2. Train 10 sessions")
    print("3. Train 100 sessions")
    print("4. Custom training sessions")
    print("-" * 60)

    train_choice = input("Choose (1-4): ").strip()

    sessions_map = {"1": 1, "2": 10, "3": 100}

    if train_choice in sessions_map:
        sessions = sessions_map[train_choice]
    elif train_choice == "4":
        try:
            sessions = int(input("Number of sessions: "))
        except ValueError:
            print("Invalid input")
            return
    else:
        print("Invalid choice")
        return

    # Choose training mode
    print("\n🎨 TRAINING MODE")
    print("-" * 60)
    print("1. Fast training (no GUI) - ⚡ Best results")
    print("2. Visual training (with GUI) - 👀 See learning in action")
    print("-" * 60)
    
    mode_choice = input("Choose (1-2): ").strip()
    use_gui = mode_choice == "2"

    # Create fresh game and agent
    game = Game(mapsize=10)
    agent = Agent(learning_rate=0.15)  # Learning rate 0.15 for better convergence
    interpreter = Interpreter(agent, game)

    print(f"\n🎓 Training for {sessions} sessions...")
    if use_gui:
        print("👀 Visual mode (slower but shows learning)")
    else:
        print("⚡ Fast mode (best results)")

    try:
        training_results = interpreter.train(
            episodes=sessions,
            verbose=True,
            gui=use_gui
        )

        episode_lengths = training_results['episode_lengths']
        best_window_avg = training_results['best_window_avg']
        best_window_start = training_results['best_window_start']
        best_window_end = training_results['best_window_end']
        best_q_table = training_results['best_q_table']

        if episode_lengths:
            avg_length = sum(episode_lengths[-10:]) / len(
                episode_lengths[-10:]
            )
            max_length = max(episode_lengths[-10:])
            print(f"\n✅ Training complete!")
            print(f"Average size (last 10): {avg_length:.1f}")
            print(f"Max size (last 10): {max_length}")
            
            # Show best performance found
            print(f"\n📊 Best window performance: avg {best_window_avg:.1f} at episodes {best_window_start}-{best_window_end}")
            
            # If best model is not the final one, restore it
            if best_q_table is not None and best_window_avg > avg_length:
                print(f"⚠️  Final model ({avg_length:.1f}) degraded from best window ({best_window_avg:.1f})")
                print("💾 Restoring best model found during training...")
                agent.q_table = best_q_table

            # Save model
            model_name = input(
                f"Model name (default: model_{sessions}): "
            ).strip()
            if not model_name:
                model_name = f"model_{sessions}"

            model_manager.save_model(agent, model_name)

            # Offer to test immediately
            test_now = input("\nTest model now? (y/n): ").strip().lower()
            if test_now == "y":
                # Create FRESH game for testing (don't reuse trained game)
                test_game = Game(mapsize=10)
                test_interpreter = Interpreter(agent, test_game)
                play_with_model(agent, test_interpreter)
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")


def test_saved_model(model_manager):
    """Load and test a saved model"""
    models = model_manager.list_models()

    if not models:
        print("No models available to test")
        return

    model_choice = input("\nEnter model name to test: ").strip()

    # Create fresh agent and load model
    game = Game(mapsize=10)
    agent = Agent()

    if not model_manager.load_model(agent, model_choice):
        print("Failed to load model")
        return

    # Set epsilon to 0 for testing (no exploration)
    agent.epsilon = 0

    interpreter = Interpreter(agent, game)

    print("\n▶️  Playing with loaded model (no learning)...")
    print("Window will close after episode ends")

    play_with_model(agent, interpreter)


def play_with_model(agent, interpreter):
    """Play single episode with GUI"""
    # Set epsilon to 0 (exploit only, no exploration)
    original_epsilon = agent.epsilon
    agent.epsilon = 0

    print("\n🐍 Starting game session...")
    interpreter.play_episode_gui()

    # Restore epsilon
    agent.epsilon = original_epsilon


if __name__ == "__main__":
    main()
