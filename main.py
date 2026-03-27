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
		print("\nMAIN MENU")
		print("-" * 60)
		print("1. Train agent and save model")
		print("2. Load and test a saved model")
		print("3. List saved models")
		print("4. Exit")
		print("-" * 60)

		choice = input("\nChoose (1-4): ").strip()

		if choice == "1":
			train_and_save_model(model_manager)

		elif choice == "2":
			test_saved_model(model_manager)

		elif choice == "3":
			model_manager.list_models()

		elif choice == "4":
			print("\nThanks for playing!")
			return

		else:
			print("Invalid choice. Please try again.")


def train_and_save_model(model_manager):
	"""Train agent and save model"""
	
	sessions = int(input("Number of sessions: "))
	if sessions <= 0:
		print("Number of sessions must be a positive integer.")
		return
	# Choose training mode
	print("\nTRAINING MODE")
	print("-" * 60)
	print("1. Fast training (no GUI)")
	print("2. Visual training (with GUI)")
	print("-" * 60)
	
	mode_choice = input("Choose (1-2): ").strip()
	use_gui = mode_choice == "2"

	# Create fresh game and agent
	game = Game(mapsize=10)
	agent = Agent(learning_rate=0.15)
	interpreter = Interpreter(agent, game)

	print(f"\nTraining for {sessions} sessions...")

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
	"""Play 10 episodes with GUI and show statistics"""
	# Set epsilon to 0 (exploit only, no exploration)
	original_epsilon = agent.epsilon
	agent.epsilon = 0

	print("\n🐍 Running 10 test episodes (GUI)...")
	
	episode_lengths = []
	episode_rewards = []
	
	for episode in range(10):
		# Fresh game for each test episode
		interpreter.game = Game(mapsize=10)
		
		stats = interpreter.play_episode_gui()
		max_length = len(interpreter.game.snake.body)
		
		episode_lengths.append(max_length)
		episode_rewards.append(stats['total_reward'])
		
		print(f"Episode {episode + 1}/10 - Size: {max_length} | Reward: {stats['total_reward']:.1f} | Status: {stats['status']}")
	
	# Show summary
	avg_length = sum(episode_lengths) / len(episode_lengths)
	max_length_overall = max(episode_lengths)
	avg_reward = sum(episode_rewards) / len(episode_rewards)
	
	print("\n" + "=" * 60)
	print("TEST SUMMARY (10 episodes)")
	print("=" * 60)
	print(f"Average size: {avg_length:.1f}")
	print(f"Max size: {max_length_overall}")
	print(f"Average reward: {avg_reward:.1f}")
	print("=" * 60)

	# Restore epsilon
	agent.epsilon = original_epsilon


if __name__ == "__main__":
	main()
