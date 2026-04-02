import sys
from src.game import Game
from src.agent import Agent
from src.interpreter import Interpreter
from src.model_manager import ModelManager
from src.gui_lobby import Lobby
from src.gui_testing import TestingGUI
from src.gui_dialogs_simple import InputDialogs
from src.gui_summary import SummaryWindow


def play_episode_debug(interpreter, use_gui=False):
    """Play one episode with debug visualization and optional GUI"""
    from src.gui import GUI

    agent = interpreter.agent
    game = interpreter.game

    total_reward = 0
    steps = 0
    game_status = None
    gui = None

    if use_gui:
        gui = GUI(game, cell_size=20)
        gui.speed = 1

    vision = game.compute_vision()

    while True:
        action = agent.choose_action(vision)

        print(f"\n--- Step {steps + 1} ---")
        print(game.print_vision_debug(action))

        if gui:
            if not gui.handle_events():
                if gui:
                    gui.close()
                return {
                    "total_reward": total_reward,
                    "steps": steps,
                    "status": "USER_STOPPED"
                }
            gui.render(step=steps, reward=0, status="DEBUG")

        new_vision, reward, status = game.step(action)
        total_reward += reward
        steps += 1
        game_status = status

        if status != "OK":
            if status == "WALL":
                print(f"\nHit wall! Reward: {reward:.1f}")
            elif status == "SELF":
                print(f"\nHit self! Reward: {reward:.1f}")
            elif status == "STARVED":
                print(f"\nStarved! Reward: {reward:.1f}")
            else:
                print(f"\nStatus: {status}! Reward: {reward:.1f}")
            break

        if reward > 0 and reward > 1:
            print(f"Ate apple! Reward: +{reward}")
        elif reward > 0:
            print(f"✓ Survived step. Reward: +{reward:.1f}")
        else:
            print(f"Move penalty. Reward: {reward:.1f}")

        vision = new_vision

    if gui:
        gui.close()

    return {
        "total_reward": total_reward,
        "steps": steps,
        "status": game_status
    }


def main():
    """Main entry point for training and testing"""
    model_manager = ModelManager()

    while True:
        # Show graphical lobby
        lobby = Lobby()
        choice = lobby.show()

        if choice == "1":
            train_and_save_model(model_manager)
        elif choice == "2":
            test_saved_model(model_manager)
        elif choice == "3":
            print("\nThanks for playing! Closing application...")
            sys.exit(0)
        else:
            print("Invalid choice (1-3). Please try again.")


def train_and_save_model(model_manager):
    """Train agent and save model"""

    sessions = InputDialogs.ask_integer(
        "Training Sessions",
        "How many training episodes?",
        default=100,
        min_val=1,
        max_val=10000
    )

    if sessions is None or sessions <= 0:
        InputDialogs.show_error(
            "Invalid Input",
            "Number of sessions must be positive"
        )
        return

    mode = InputDialogs.ask_choice(
        "Training Mode",
        [
            ("Fast training (no GUI)", "1"),
            ("Visual training (with GUI)", "2"),
            ("Debug mode (GUI + vision)", "3"),
        ]
    )

    if not mode:
        return

    use_gui = mode in ("2", "3")
    debug_mode = mode == "3"

    game = Game(mapsize=10)
    agent = Agent(learning_rate=0.15)
    interpreter = Interpreter(agent, game)

    InputDialogs.show_info(
        "Training Started",
        f"Training for {sessions} episodes..."
    )

    try:
        training_results = interpreter.train(
            episodes=sessions,
            verbose=True,
            gui=use_gui,
            debug_mode=debug_mode
        )

        episode_lengths = training_results['episode_lengths']
        best_episode_length = training_results['best_episode_length']
        best_episode_num = training_results['best_episode_num']
        best_q_table = training_results['best_q_table']

        if episode_lengths:
            avg_length = sum(episode_lengths[-10:]) / len(
                episode_lengths[-10:]
            )
            max_length = max(episode_lengths[-10:])
            print("\nTraining complete!")
            print(f"Average size (last 10): {avg_length:.1f}")
            print(f"Max size (last 10): {max_length}")

            print(
                f"\nBest episode: #{best_episode_num} with size "
                f"{best_episode_length}")

            if best_q_table is not None and best_episode_length > max_length:
                print(
                    f"Final model ({max_length}) weaker than "
                    f"best episode ({best_episode_length})")
                print("Restoring best model found during training...")
                agent.q_table = best_q_table

            # Show summary window
            summary_data = {
                "Episodes": sessions,
                "Avg Length (last 10)": f"{avg_length:.1f}",
                "Max Length (last 10)": max_length,
                "Best Episode": f"#{best_episode_num}",
                "Best Size": best_episode_length
            }
            SummaryWindow("Training Results", summary_data).show()

            model_name = InputDialogs.ask_string(
                "Save Model",
                f"Model name (default: model_{sessions}):"
            )
            if not model_name:
                model_name = f"model_{sessions}"
            try:
                import numpy as np
                import matplotlib.pyplot as plt
                plot_path = model_manager.MODELS_DIR / \
                    f"{model_name}_training.png"
                y = np.array(list(map(float, episode_lengths)))
                x = np.arange(1, len(y) + 1)
                plt.figure(figsize=(10, 4))
                window = 100
                cumsum = np.concatenate(([0.0], np.cumsum(y)))
                idx = np.arange(1, len(y) + 1)
                starts = np.maximum(0, idx - window)
                sums = cumsum[idx] - cumsum[starts]
                counts = idx - starts
                y_roll = sums / counts
                plt.figure(figsize=(10, 4))
                plt.plot(
                    idx,
                    y_roll,
                    lw=2,
                    color='tab:blue',
                    label='Rolling mean (100)')
                plt.fill_between(idx, y_roll, alpha=0.12, color='tab:blue')
                plt.xlabel('Episode')
                plt.ylabel('Snake length')
                plt.title(f'Training progress ({len(y)} episodes)')
                if len(x) == 1:
                    plt.xlim(0.5, 1.5)
                else:
                    plt.xlim(1, x[-1])
                plt.ylim(0, max(y) + 1)
                step = max(1, len(x) // 9)
                plt.xticks(x[::step])
                plt.grid(alpha=0.3)
                plt.legend(loc='upper left')
                plt.tight_layout()
                plt.savefig(plot_path)
                plt.close()
                print(f"Saved training plot: {plot_path}")
            except Exception:
                pass

            model_manager.save_model(agent, model_name)

            test_now = InputDialogs.ask_yes_no(
                "Test Model",
                "Test model now?"
            )
            if test_now:
                test_game = Game(mapsize=10)
                test_interpreter = Interpreter(agent, test_game)
                play_with_model(
                    agent,
                    test_interpreter,
                    mapsize=10,
                    num_episodes=100,
                    use_gui=False,
                    debug_mode=False,
                    verbose=False)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")


def test_saved_model(model_manager):
    """Load and test a saved model"""
    models = model_manager.list_models()

    if not models:
        print("No models available to test")
        return

    # Create choice list from available models
    model_choices = [(m, m) for m in models]

    model_choice = InputDialogs.ask_choice(
        "Select Model",
        model_choices
    )
    if not model_choice:
        return

    size_choice = InputDialogs.ask_choice(
        "Map Size",
        [
            ("Default (10x10)", "1"),
            ("Custom size", "2"),
        ]
    )

    if not size_choice:
        return

    if size_choice == "2":
        mapsize = InputDialogs.ask_integer(
            "Custom Map Size",
            "Enter map size (5-50):",
            default=10,
            min_val=5,
            max_val=50
        )

        if mapsize is None or mapsize < 5 or mapsize > 50:
            InputDialogs.show_error(
                "Invalid Input",
                "Map size must be between 5 and 50"
            )
            return
    else:
        mapsize = 10

    num_runs = InputDialogs.ask_integer(
        "Test Runs",
        "Number of test runs:",
        default=10,
        min_val=1,
        max_val=1000
    )

    if num_runs is None or num_runs <= 0:
        InputDialogs.show_error(
            "Invalid Input",
            "Number of runs must be positive"
        )
        return

    mode_choice = InputDialogs.ask_choice(
        "Test Mode",
        [
            ("Fast testing (no GUI)", "1"),
            ("Visual testing (with GUI)", "2"),
            ("Debug mode (GUI + vision)", "3"),
        ]
    )

    if not mode_choice:
        return

    use_gui = mode_choice in ("2", "3")
    debug_mode = mode_choice == "3"
    game = Game(mapsize=mapsize)
    agent = Agent()

    if not model_manager.load_model(agent, model_choice):
        print("Failed to load model")
        return

    agent.epsilon = 0
    interpreter = Interpreter(agent, game)

    print(f"\nTesting on {mapsize}x{mapsize} map ({num_runs} runs)...")

    play_with_model(agent, interpreter, mapsize, num_runs, use_gui, debug_mode)


def play_with_model(
        agent,
        interpreter,
        mapsize=10,
        num_episodes=10,
        use_gui=True,
        debug_mode=False,
        verbose=True):
    """Test episodes with persistent GUI if enabled"""

    print(f"\nRunning {num_episodes} test episodes", end="")
    if use_gui:
        print(" (with GUI)...")
    else:
        print(" (no GUI)...")

    episode_lengths = []
    episode_rewards = []
    episodes_data = []

    # Use persistent GUI if enabled
    gui = None
    if use_gui:
        gui = TestingGUI(mapsize=mapsize, cell_size=20)

    for episode in range(num_episodes):
        interpreter.game = Game(mapsize=mapsize)

        if gui:
            # Use persistent testing GUI for all episodes
            stats = _play_episode_with_gui(
                interpreter, gui, episode + 1, num_episodes, debug_mode
            )
        else:
            stats = interpreter.play_episode(render=False)

        if stats['status'] == "USER_STOPPED":
            print("\nTests stopped by user")
            break

        max_length = len(interpreter.game.snake.body)
        episode_lengths.append(max_length)
        episode_rewards.append(stats['total_reward'])
        episodes_data.append({
            'length': max_length,
            'reward': stats['total_reward'],
            'status': stats['status']
        })

        if verbose and not gui:
            avg_ep_reward = stats['total_reward'] / max(1, stats['steps'])
            print(
                f"Run {episode + 1}/{num_episodes} - "
                f"Size: {max_length} | "
                f"Avg Reward/Step: {avg_ep_reward:.3f} | "
                f"Status: {stats['status']}")

    # Show results
    if gui:
        gui.show_results(episodes_data)
        gui.close()

    if not episode_lengths:
        print("\nNo episodes completed")
        return
    avg_length = sum(episode_lengths) / len(episode_lengths)
    max_length_overall = max(episode_lengths)
    min_length_overall = min(episode_lengths)

    print("\n" + "=" * 60)
    print(f"TEST SUMMARY ({len(episode_lengths)} episodes)")
    print("=" * 60)
    print(f"Average size: {avg_length:.1f}")
    print(f"Max size: {max_length_overall}")
    print(f"Min size: {min_length_overall}")
    print("=" * 60)

    # Show summary window
    summary_data = {
        "Episodes": len(episode_lengths),
        "Average Length": f"{avg_length:.1f}",
        "Max Length": max_length_overall,
        "Min Length": min_length_overall
    }
    SummaryWindow("Test Results", summary_data).show()


def _play_episode_with_gui(interpreter, gui, episode, total_episodes,
                           debug_mode=False):
    """Play one episode with persistent GUI"""
    agent = interpreter.agent
    game = interpreter.game

    total_reward = 0
    steps = 0
    game_status = "OK"

    vision = game.compute_vision()

    while True:
        action = agent.choose_action(vision)
        new_vision, reward, status = game.step(action)

        total_reward += reward
        steps += 1
        game_status = status

        if debug_mode:
            vision_display = game.print_vision_debug(direction_chosen=action)
            print(vision_display)

        gui.render(
            game,
            episode=episode,
            step=steps,
            reward=reward,
            status=status
        )

        if not gui.running:
            return {
                "total_reward": total_reward,
                "steps": steps,
                "status": "USER_STOPPED"
            }

        if status != "OK":
            break

        vision = new_vision

    return {
        "total_reward": total_reward,
        "steps": steps,
        "status": game_status
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("   🐍 Welcome to Learn2Slither 🐍")
    print("   Q-Learning Snake Game")
    print("="*60 + "\n")

    main()
