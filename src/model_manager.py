"""Model saving and loading for trained agents"""
import json
import os
from pathlib import Path


class ModelManager:
    """Manages saving and loading Q-learning agent models"""

    MODELS_DIR = Path("models")

    def __init__(self):
        """Initialize model directory"""
        self.MODELS_DIR.mkdir(exist_ok=True)

    def save_model(self, agent, name):
        """
        Save agent's Q-table to file
        
        Args:
            agent: Agent instance
            name: str - Model name (e.g., "model_1", "model_10", "model_100")
        """
        filepath = self.MODELS_DIR / f"{name}.json"
        
        # Convert Q-table to JSON-serializable format
        q_table_serializable = {}
        for state_key, actions in agent.q_table.items():
            # Convert tuple keys to strings
            state_str = str(state_key)
            q_table_serializable[state_str] = actions
        
        data = {
            "q_table": q_table_serializable,
            "epsilon": agent.epsilon,
            "learning_rate": agent.learning_rate,
            "discount_factor": agent.discount_factor,
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"[OK] Model saved: {filepath}")

    def load_model(self, agent, name):
        """
        Load agent's Q-table from file
        
        Args:
            agent: Agent instance to update
            name: str - Model name to load
        
        Returns:
            bool - Success status
        """
        filepath = self.MODELS_DIR / f"{name}.json"
        
        if not filepath.exists():
            print(f"[ERROR] Model not found: {filepath}")
            return False
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Restore Q-table
            agent.q_table = {}
            for state_str, actions in data["q_table"].items():
                # Convert string keys back to tuples
                state_tuple = eval(state_str)
                agent.q_table[state_tuple] = actions
            
            # Restore hyperparameters
            agent.epsilon = 0  # Set to 0 for deterministic testing (no exploration)
            agent.learning_rate = data.get("learning_rate", 0.1)
            agent.discount_factor = data.get("discount_factor", 0.95)
            
            print(f"[OK] Model loaded: {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading model: {e}")
            return False

    def list_models(self):
        """List all available saved models"""
        models = list(self.MODELS_DIR.glob("*.json"))
        if not models:
            print("No models saved yet")
            return []
        
        model_names = [m.stem for m in models]
        print("Available models:")
        for name in sorted(model_names):
            print(f"  - {name}")
        return model_names

    def delete_model(self, name):
        """Delete a saved model"""
        filepath = self.MODELS_DIR / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            print(f"✓ Model deleted: {name}")
        else:
            print(f"✗ Model not found: {name}")
