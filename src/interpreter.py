class Interpreter:
    """Interpreter orchestrates the agent, game, and learning loop"""

    def __init__(self, agent, game):
        """
        Initialize the interpreter
        
        Args:
            agent: Agent instance
            game: Game instance
        """
        self.agent = agent
        self.game = game
    
    def run_episode(self):
        """
        Run one complete episode
        
        Returns:
            dict: Episode statistics (total_reward, steps, status)
        """
        total_reward = 0
        steps = 0
        game_status = None
        
        # Get initial vision
        vision = self.game.snake.get_vision(self.game.map, self.game.apples, self.game.mapsize)
        
        while True:
            # Agent chooses action based on vision
            action = self.agent.choose_action(vision)
            
            # Execute action in game
            new_vision, reward, status = self.game.step(action)
            
            # Agent learns from reward and new state
            self.agent.learn(new_vision, reward)
            
            total_reward += reward
            steps += 1
            game_status = status
            
            # Episode ends if not OK
            if status != "OK":
                break
            
            vision = new_vision
        
        return {
            "total_reward": total_reward,
            "steps": steps,
            "status": game_status
        }
    
    def train(self, episodes=1000, verbose=True, gui=False):
        """
        Train the agent for multiple episodes
        
        Args:
            episodes: int - Number of episodes to train
            verbose: bool - Print progress every 100 episodes
            gui: bool - Show GUI visualization during training
        
        Returns:
            dict: {
                'episode_lengths': list of max lengths per episode,
                'best_avg': best average score found,
                'best_episode': episode where best avg was found,
                'best_q_table': Q-table snapshot at best performance
            }
        """
        self.episodes_total = episodes  # Store total episodes for epsilon decay calculation
        episode_lengths = []
        gui_instance = None
        best_window_avg = 0
        best_window_start = 0
        best_window_end = 0
        best_q_table = None
        
        if gui:
            from src.gui import GUI
        
        for episode in range(episodes):
            # EPSILON = 0 (Pure Exploitation)
            # Explored vs tried epsilon decay 0.6->0, but it doesn't transfer well to testing
            # epsilon=0 is faster to good performance and more stable at test time
            self.agent.epsilon = 0
            
            # Reset game for new episode
            self.game = type(self.game)(self.game.mapsize)
            
            # Initialize or update GUI
            if gui:
                if gui_instance is None:
                    gui_instance = GUI(self.game, cell_size=20)
                else:
                    # Update GUI game reference for new episode
                    gui_instance.game = self.game
            
            total_reward = 0
            steps = 0
            max_length = 1  # Snake starts at length 1
            game_status = None
            
            # Get initial vision
            vision = self.game.snake.get_vision(self.game.map, self.game.apples, self.game.mapsize)
            
            if gui:
                gui_instance.render(step=0, reward=0, status="START")
            
            while True:
                # Check for quit in GUI
                if gui and not gui_instance.handle_events():
                    gui_instance.close()
                    return {
                        'episode_lengths': episode_lengths,
                        'best_avg': best_avg,
                        'best_episode': best_episode,
                        'best_q_table': best_q_table
                    }
                
                # Agent chooses action
                action = self.agent.choose_action(vision)
                
                # Execute action
                new_vision, reward, status = self.game.step(action)
                self.agent.learn(new_vision, reward)
                
                total_reward += reward
                steps += 1
                game_status = status
                
                # Track max length
                current_length = len(self.game.snake.body)
                max_length = max(max_length, current_length)
                
                # Render GUI
                if gui:
                    gui_instance.render(step=steps, reward=reward, status=status)
                
                if status != "OK":
                    break
                
                vision = new_vision
            
            episode_lengths.append(max_length)
            
            # Track best 100-episode window average
            if verbose and (episode + 1) % 100 == 0:
                window_avg = sum(episode_lengths[-100:]) / 100
                max_observed = max(episode_lengths[-100:])
                
                # If this window is better than previous best, save it
                if window_avg > best_window_avg:
                    best_window_avg = window_avg
                    best_window_start = episode + 1 - 100
                    best_window_end = episode + 1
                    best_q_table = {k: v.copy() for k, v in self.agent.q_table.items()}
                
                print(f"Episode {episode + 1}/{episodes} - "
                      f"Avg Size: {window_avg:.1f} | "
                      f"Max Size: {max_observed} | "
                      f"Best Window Avg: {best_window_avg:.1f} (ep {best_window_start}-{best_window_end})")
        
        if gui and gui_instance:
            gui_instance.close()
        
        return {
            'episode_lengths': episode_lengths,
            'best_window_avg': best_window_avg,
            'best_window_start': best_window_start,
            'best_window_end': best_window_end,
            'best_q_table': best_q_table
        }
    
    def play_episode(self, render=True):
        """
        Play one episode without learning (exploit only)
        
        Args:
            render: bool - Print game state
        
        Returns:
            dict: Episode statistics
        """
        # Temporarily disable exploration (epsilon=0)
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0
        
        stats = self.run_episode()
        
        # Restore original epsilon
        self.agent.epsilon = original_epsilon
        
        if render:
            print(f"Episode finished: {stats['status']}")
            print(f"Steps: {stats['steps']}, Reward: {stats['total_reward']}")
        
        return stats
    
    def step_by_step_episode(self, auto=False):
        """
        Play one episode with step-by-step visualization
        Press Enter after each action to continue
        
        Args:
            auto: bool - Auto-play without waiting for input (for demo)
        """
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0  # No exploration, just exploit
        
        total_reward = 0
        steps = 0
        
        print("\n" + "=" * 50)
        print("STEP-BY-STEP EPISODE")
        print("=" * 50)
        
        # Get initial vision and render
        vision = self.game.snake.get_vision(self.game.map, self.game.apples, self.game.mapsize)
        self.game.render()
        
        while True:
            # Get action from agent
            action = self.agent.choose_action(vision)
            print(f"\n➡️  ACTION: {action}")
            
            if not auto:
                input("Press Enter to execute action...")
            else:
                import time
                time.sleep(1)  # Auto delay for demo
            
            # Execute action
            new_vision, reward, status = self.game.step(action)
            total_reward += reward
            steps += 1
            
            print(f"✨ Reward: {reward:+.1f} | Status: {status}")
            
            # Render new state
            self.game.render()
            
            if status != "OK":
                print(f"\n❌ GAME OVER: {status}")
                print(f"Total Reward: {total_reward:.2f}")
                print(f"Total Steps: {steps}")
                break
            
            vision = new_vision
        
        self.agent.epsilon = original_epsilon
        
        return {
            "total_reward": total_reward,
            "steps": steps,
            "status": status
        }
    
    def play_episode_gui(self):
        """
        Play one episode with graphical interface (pygame)
        
        Returns:
            dict: Episode statistics
        """
        from src.gui import GUI
        
        gui = GUI(self.game, cell_size=30)
        
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0  # No exploration, just exploit
        
        total_reward = 0
        steps = 0
        max_steps = 500  # Prevent infinite loops from circular behavior
        
        # Get initial vision
        vision = self.game.snake.get_vision(self.game.map, self.game.apples, self.game.mapsize)
        gui.render(step=steps, reward=0, status="INIT")
        
        game_status = "OK"
        
        while True:
            # Check for quit
            if not gui.handle_events():
                break
            
            # Safety timeout to prevent infinite loops
            if steps >= max_steps:
                game_status = "TIMEOUT"
                break
            
            # Get action from agent
            action = self.agent.choose_action(vision)
            
            # Execute action
            new_vision, reward, status = self.game.step(action)
            total_reward += reward
            steps += 1
            game_status = status
            
            # Render
            gui.render(step=steps, reward=reward, status=status)
            
            if status != "OK":
                # Show game over for 2 seconds
                import time
                time.sleep(2)
                break
            
            vision = new_vision
        
        gui.close()
        self.agent.epsilon = original_epsilon
        
        return {
            "total_reward": total_reward,
            "steps": steps,
            "status": game_status
        }
