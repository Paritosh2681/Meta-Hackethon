"""Random agent baseline - selects uniformly random valid actions."""

import random
from typing import List


class RandomAgent:
    """Agent that takes uniformly random valid actions.
    
    Baseline for comparison. Serves as null hypothesis for RL agents.
    """
    
    def __init__(self, env):
        """Initialize random agent.
        
        Args:
            env: WarehouseEnv instance
        """
        self.env = env
        self.action_history = []
    
    def get_action(self, state: dict) -> str:
        """Select uniformly random valid action.
        
        Args:
            state: Current environment state dict
            
        Returns:
            Random action string
        """
        valid_actions = self.env.get_valid_actions()
        action = random.choice(valid_actions)
        self.action_history.append(action)
        return action
    
    def reset(self) -> None:
        """Reset agent state (history)."""
        self.action_history = []
