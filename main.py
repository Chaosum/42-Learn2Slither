from src.game import Game
from src.agent import Agent
from src.interpreter import Interpreter
from src.model_manager import ModelManager


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
		# Set speed to slowest (1) for debug mode
		gui.speed = 1
	
	vision = game.compute_vision()
	
	while True:
		action = agent.choose_action(vision)
		
		# Display vision cross and decision
		print(f"\n--- Step {steps + 1} ---")
		print(game.print_vision_debug(action))
		
		# Handle GUI events if enabled
		if gui:
			if not gui.handle_events():
				# User closed GUI - stop all tests
				if gui:
					gui.close()
				return {
					"total_reward": total_reward,
					"steps": steps,
					"status": "USER_STOPPED"  # Signal to stop all tests
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
		
		if reward > 0 and reward > 1:  # Growth reward
			print(f"Ate apple! Reward: +{reward}")
		elif reward > 0:  # Survival bonus
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
			print("Invalid choice (1-4). Please try again.")


def train_and_save_model(model_manager):
	"""Train agent and save model"""
	
	try:
		sessions = int(input("Number of sessions: "))
		if sessions <= 0:
			print("Number of sessions must be a positive integer.")
			return
	except ValueError:
		print("Invalid input. Please enter a valid integer.")
		return
	# Choose training mode
	print("\nTRAINING MODE")
	print("-" * 60)
	print("1. Fast training (no GUI)")
	print("2. Visual training (with GUI)")
	print("-" * 60)
	
	mode_choice = input("Choose (1-2): ").strip()
	if mode_choice not in ["1", "2"]:
		print("Invalid choice. Using fast training (no GUI)")
		mode_choice = "1"
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
		best_episode_length = training_results['best_episode_length']
		best_episode_num = training_results['best_episode_num']
		best_q_table = training_results['best_q_table']

		if episode_lengths:
			avg_length = sum(episode_lengths[-10:]) / len(
				episode_lengths[-10:]
			)
			max_length = max(episode_lengths[-10:])
			print(f"\nTraining complete!")
			print(f"Average size (last 10): {avg_length:.1f}")
			print(f"Max size (last 10): {max_length}")
			
			# Show best episode found
			print(f"\nBest episode: #{best_episode_num} with size {best_episode_length}")
			
			# If best model is not the final one, restore it
			if best_q_table is not None and best_episode_length > max_length:
				print(f"Final model ({max_length}) weaker than best episode ({best_episode_length})")
				print("Restoring best model found during training...")
				agent.q_table = best_q_table

			# Save model
			model_name = input(
				f"Model name (default: model_{sessions}): "
			).strip()
			if not model_name:
				model_name = f"model_{sessions}"

			model_manager.save_model(agent, model_name)

			while True:
				test_now = input("\nTest model now? (y/n): ").strip().lower()
				if test_now in ["y", "n"]:
					break
				print("Please enter 'y' or 'n'")
			if test_now == "y":
				test_game = Game(mapsize=10)
				test_interpreter = Interpreter(agent, test_game)
				play_with_model(agent, test_interpreter, mapsize=10, num_episodes=100, use_gui=False, debug_mode=False, verbose=False)
	except KeyboardInterrupt:
		print("\nTraining interrupted by user")


def test_saved_model(model_manager):
	"""Load and test a saved model"""
	models = model_manager.list_models()

	if not models:
		print("No models available to test")
		return

	model_choice = input("\nEnter model name to test: ").strip()
	if not model_choice:
		print("Model name cannot be empty")
		return

	# Ask for map size
	print("\nMAP SIZE")
	print("-" * 60)
	print("1. Default (10x10)")
	print("2. Custom size")
	print("-" * 60)
	
	size_choice = input("Choose (1-2): ").strip()
	if size_choice not in ["1", "2"]:
		print("Invalid choice. Using default (10x10)")
		size_choice = "1"
	
	if size_choice == "2":
		try:
			mapsize = int(input("Enter custom map size: "))
			if mapsize < 5 or mapsize > 50:
				print("Map size must be between 5 and 50")
				return
		except ValueError:
			print("Please enter a valid integer (5-50)")
			return
	else:
		mapsize = 10

	# Ask for number of test runs
	try:
		num_runs = int(input("Number of test runs: "))
		if num_runs <= 0:
			print("Number of runs must be positive")
			return
	except ValueError:
		print("Please enter a valid integer")
		return

	# Ask for test mode (GUI or no GUI)
	print("\nTEST MODE")
	print("-" * 60)
	print("1. Fast testing (no GUI)")
	print("2. Visual testing (with GUI)")
	print("3. Debug console + GUI")
	print("-" * 60)
	
	mode_choice = input("Choose (1-3): ").strip()
	if mode_choice not in ["1", "2", "3"]:
		print("Invalid choice. Using fast testing (no GUI)")
		mode_choice = "1"
	use_gui = mode_choice == "2"
	debug_mode = mode_choice == "3"
	
	# Create fresh agent and load model
	game = Game(mapsize=mapsize)
	agent = Agent()
	
	if not model_manager.load_model(agent, model_choice):
		print("Failed to load model")
		return

	agent.epsilon = 0
	interpreter = Interpreter(agent, game)

	print(f"\n▶️  Testing on {mapsize}x{mapsize} map ({num_runs} runs)...")

	play_with_model(agent, interpreter, mapsize, num_runs, use_gui, debug_mode)


def play_with_model(agent, interpreter, mapsize=10, num_episodes=10, use_gui=True, debug_mode=False, verbose=True):
	"""Test episodes with or without GUI"""
	debug_gui = debug_mode  # If debug mode, always include GUI
	
	print(f"\n🐍 Running {num_episodes} test episodes", end="")
	if use_gui:
		print(" (with GUI)...")
	elif debug_mode:
		print(" (debug console + GUI)...")
	else:
		print(" (no GUI)...")
	
	episode_lengths = []
	episode_rewards = []
	
	for episode in range(num_episodes):
		interpreter.game = Game(mapsize=mapsize)
		
		if use_gui:
			stats = interpreter.play_episode_gui()
		elif debug_mode:
			stats = play_episode_debug(interpreter, use_gui=debug_gui)
		else:
			stats = interpreter.play_episode(render=False)
		
		# Check if user stopped tests
		if stats['status'] == "USER_STOPPED":
			print("\n⛔ Tests stopped by user")
			break
		
		max_length = len(interpreter.game.snake.body)
		episode_lengths.append(max_length)
		episode_rewards.append(stats['total_reward'])
		
		if verbose:
			print(f"Run {episode + 1}/{num_episodes} - Size: {max_length} | Reward: {stats['total_reward']:.1f} | Status: {stats['status']}")
	
	# Show summary only if tests were run
	if not episode_lengths:
		print("\n⛔ No episodes completed")
		return
	
	# Show summary
	avg_length = sum(episode_lengths) / len(episode_lengths)
	max_length_overall = max(episode_lengths)
	min_length_overall = min(episode_lengths)
	avg_reward = sum(episode_rewards) / len(episode_rewards)
	
	print("\n" + "=" * 60)
	print(f"TEST SUMMARY ({len(episode_lengths)} episodes)")
	print("=" * 60)
	print(f"Average size: {avg_length:.1f}")
	print(f"Max size: {max_length_overall}")
	print(f"Min size: {min_length_overall}")
	print(f"Average reward: {avg_reward:.1f}")
	print("=" * 60)


if __name__ == "__main__":
	main()
