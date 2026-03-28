import random


class Agent:
    """Q-learning agent for Learn2Slither"""

    def __init__(self, epsilon=0.1, learning_rate=0.1, discount_factor=0.95):
        self.q_table = {}
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.last_state = None
        self.last_action = None
        self.last_direction = None
    
    def _vision_to_key(self, vision):
        return (
            vision['UP'][0], vision['UP'][1], vision['UP'][2],
            vision['DOWN'][0], vision['DOWN'][1], vision['DOWN'][2],
            vision['LEFT'][0], vision['LEFT'][1], vision['LEFT'][2],
            vision['RIGHT'][0], vision['RIGHT'][1], vision['RIGHT'][2]
        )
    
    def _init_state(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in self.actions}
    
    def _get_valid_actions(self):
        if self.last_direction is None:
            return self.actions
        opposites = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        
        opposite = opposites.get(self.last_direction)
        return [a for a in self.actions if a != opposite]
    
    def choose_action(self, vision):
        state_key = self._vision_to_key(vision)
        self._init_state(state_key)
        self.last_state = state_key
        valid_actions = self._get_valid_actions()
        
        if random.random() < self.epsilon:
            action = random.choice(valid_actions)
        else:
            action = max(valid_actions, key=lambda a: self.q_table[state_key][a])
        
        self.last_direction = action
        self.last_action = action
        return action
    
    def learn(self, new_state, reward):
        """
        Update Q-value based on reward (basic Q-learning)
        
        Args:
            new_state: Dict with keys 'UP', 'DOWN', 'LEFT', 'RIGHT' or None if game over
            reward: float - Reward received
        """
        if self.last_state is None or self.last_action is None:
            return
        
        # If game ended, new_state is None (no next state)
        if new_state is None:
            new_state_key = None
            max_next_q = 0
        else:
            new_state_key = self._vision_to_key(new_state)
            self._init_state(new_state_key)
            max_next_q = max(self.q_table[new_state_key].values())
        
        # Q-learning formula:
        # Q(s,a) = Q(s,a) + alpha * (r + gamma * max(Q(s',a')) - Q(s,a))
        current_q = self.q_table[self.last_state][self.last_action]
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[self.last_state][self.last_action] = new_q
