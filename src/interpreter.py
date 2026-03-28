class Interpreter:
    """Interpreter orchestrates the agent, game, and learning loop"""

    def __init__(self, agent, game):
        self.agent = agent
        self.game = game
    
    def run_episode(self, learning=True):
        total_reward = 0
        steps = 0
        game_status = None
        
        vision = self.game.compute_vision()
        
        while True:
            action = self.agent.choose_action(vision)
            new_vision, reward, status = self.game.step(action)
            
            if learning:
                self.agent.learn(new_vision, reward)
            
            total_reward += reward
            steps += 1
            game_status = status
            
            if status != "OK":
                break
            
            vision = new_vision
        
        return {
            "total_reward": total_reward,
            "steps": steps,
            "status": game_status
        }
    
    def train(self, episodes=1000, verbose=True, gui=False):
        self.episodes_total = episodes
        episode_lengths = []
        episode_rewards = []
        gui_instance = None
        best_episode_length = 0
        best_episode_num = 0
        best_q_table = None
        
        if gui:
            from src.gui import GUI
        
        for episode in range(episodes):
            # Epsilon decay: 1.0 → 0.05 gradually over all episodes (maintain exploration)
            self.agent.epsilon = max(0.05, 1.0 - (episode / episodes) * 0.95)
            
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
            vision = self.game.compute_vision()
            
            if gui:
                gui_instance.render(step=0, reward=0, status="START")
            
            while True:
                if gui and not gui_instance.handle_events():
                    gui_instance.close()
                    break
                
                action = self.agent.choose_action(vision)
                new_vision, reward, status = self.game.step(action)
                self.agent.learn(new_vision, reward)
                
                total_reward += reward
                steps += 1
                game_status = status
                current_length = len(self.game.snake.body)
                max_length = max(max_length, current_length)
                
                if gui:
                    gui_instance.render(step=steps, reward=reward, status=status)
                
                if status != "OK":
                    break
                
                vision = new_vision
            
            episode_lengths.append(max_length)
            episode_rewards.append(total_reward)
            
            if max_length > best_episode_length:
                best_episode_length = max_length
                best_episode_num = episode + 1
                best_q_table = {k: v.copy() for k, v in self.agent.q_table.items()}
            
            if verbose and (episode + 1) % 100 == 0:
                window_avg = sum(episode_lengths[-100:]) / 100
                window_reward = sum(episode_rewards[-100:]) / 100
                max_obs = max(episode_lengths[-100:])
                print(f"Episode {episode + 1}/{episodes} - "
                      f"Avg Size: {window_avg:.1f} | "
                      f"Avg Reward: {window_reward:.1f} | "
                      f"Max Size: {max_obs} | "
                      f"Best: #{best_episode_num} (Size: {best_episode_length})")
        
        if gui and gui_instance:
            gui_instance.close()
        
        return {
            'episode_lengths': episode_lengths,
            'episode_rewards': episode_rewards,
            'best_episode_length': best_episode_length,
            'best_episode_num': best_episode_num,
            'best_q_table': best_q_table
        }
    
    def play_episode(self, render=True):
        self.agent.epsilon = 0
        stats = self.run_episode(learning=False)
        
        if render:
            print(f"Episode finished: {stats['status']}")
            print(f"Steps: {stats['steps']}, Reward: {stats['total_reward']}")
        
        return stats

    
    def play_episode_gui(self):
        from src.gui import GUI
        
        gui = GUI(self.game, cell_size=30)
        self.agent.epsilon = 0
        
        total_reward = 0
        steps = 0
        vision = self.game.compute_vision()
        gui.render(step=steps, reward=0, status="INIT")
        game_status = "OK"
        
        while True:
            if not gui.handle_events():
                break
            
            action = self.agent.choose_action(vision)
            new_vision, reward, status = self.game.step(action)
            total_reward += reward
            steps += 1
            game_status = status
            
            gui.render(step=steps, reward=reward, status=status)
            
            if status != "OK":
                import time
                time.sleep(2)
                break
            
            vision = new_vision
        
        gui.close()
        
        return {
            "total_reward": total_reward,
            "steps": steps,
            "status": game_status
        }
