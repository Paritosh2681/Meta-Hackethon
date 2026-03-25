"""Q-Learning agent that learns from warehouse environment."""

import random
import pickle
import numpy as np
from typing import Dict, Tuple, Optional
from collections import defaultdict


class QLearningAgent:
    """Tabular Q-Learning agent for warehouse environment.
    
    Uses state discretization:
        - Robot position: 100 cells (10x10 grid)
        - Robot battery: 5 levels (0-20, 20-40, 40-60, 60-80, 80-100)
        - Carrying package: yes/no
        - Nearest undelivered package direction: N/S/E/W/none
    
    Action space: 7 actions from environment
    
    This creates discrete, learnable state space for Q-table optimization.
    """
    
    def __init__(self, env, alpha: float = 0.1, gamma: float = 0.99, epsilon: float = 1.0):
        """Initialize Q-Learning agent.
        
        Args:
            env: WarehouseEnv instance
            alpha: Learning rate (0-1)
            gamma: Discount factor (0-1)
            epsilon: Exploration rate (0-1)
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Q-table: states → actions → Q-value
        self.q_table: Dict[Tuple, Dict[str, float]] = defaultdict(
            lambda: {action: 0.0 for action in self.env.get_valid_actions()}
        )
        
        self.action_history = []
        self.training = True
    
    def get_action(self, state: dict) -> str:
        """Select action using epsilon-greedy policy.
        
        Args:
            state: Current environment state dict
            
        Returns:
            Action string
        """
        # Discretize state into Q-table key
        state_key = self._discretize_state(state)
        
        # Epsilon-greedy selection
        if self.training and random.random() < self.epsilon:
            # Explore: random action
            action = random.choice(self.env.get_valid_actions())
        else:
            # Exploit: best known action
            action = max(
                self.q_table[state_key].items(),
                key=lambda x: x[1]
            )[0]
        
        self.action_history.append((state_key, action))
        return action
    
    def update_q_value(
        self,
        state: dict,
        action: str,
        reward: float,
        next_state: dict,
        done: bool
    ) -> None:
        """Update Q-table using Q-Learning update rule.
        
        Args:
            state: Previous environment state
            action: Action taken
            reward: Reward received
            next_state: Resulting environment state
            done: Whether episode ended
        """
        state_key = self._discretize_state(state)
        next_state_key = self._discretize_state(next_state)
        
        # Q-Learning update rule
        if done:
            target = reward
        else:
            max_next_q = max(self.q_table[next_state_key].values())
            target = reward + self.gamma * max_next_q
        
        current_q = self.q_table[state_key][action]
        new_q = current_q + self.alpha * (target - current_q)
        self.q_table[state_key][action] = new_q
    
    def decay_exploration(self) -> None:
        """Decay exploration rate after each episode."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def set_training(self, training: bool) -> None:
        """Set agent to training or evaluation mode.
        
        Args:
            training: If False, uses pure exploitation (no epsilon exploration)
        """
        self.training = training
    
    def save_q_table(self, filepath: str) -> None:
        """Save Q-table to disk.
        
        Args:
            filepath: Path to save Q-table pickle file
        """
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
    
    def load_q_table(self, filepath: str) -> None:
        """Load Q-table from disk.
        
        Args:
            filepath: Path to load Q-table pickle file
        """
        with open(filepath, 'rb') as f:
            loaded = pickle.load(f)
            self.q_table = defaultdict(
                lambda: {action: 0.0 for action in self.env.get_valid_actions()},
                loaded
            )
    
    def reset(self) -> None:
        """Reset agent history."""
        self.action_history = []
    
    def _discretize_state(self, state: dict) -> Tuple:
        """Convert continuous state to discrete state key for Q-table.
        
        State dimensions:
            - Robot position: (0-9, 0-9) → 0-99 cell index
            - Battery level: 0-100 → 5 buckets
            - Carrying: bool → 0 or 1
            - Nearest package direction: string → 0-4
            - Has priority 3 urgent package: bool → 0 or 1
        
        Args:
            state: Full state dictionary
            
        Returns:
            Tuple suitable as dict key for Q-table
        """
        rx, ry = state["robot_position"]
        pos_idx = ry * 10 + rx  # Flatten 2D position
        
        battery = state["battery"]
        battery_level = min(4, battery // 20)  # 0-4 based on 20% buckets
        
        carrying = 1 if state["carrying"] else 0
        
        # Find nearest undelivered package direction
        nearest_dir = self._get_nearest_package_direction(state)
        
        # Check if any priority 3 packages
        has_urgent = 0
        for pkg in state["packages"]:
            if pkg["priority"] == 3 and not pkg["delivered"]:
                has_urgent = 1
                break
        
        return (pos_idx, battery_level, carrying, nearest_dir, has_urgent)
    
    def _get_nearest_package_direction(self, state: dict) -> int:
        """Determine nearest undelivered package direction.
        
        Args:
            state: Environment state
            
        Returns:
            Direction code: 0=up, 1=down, 2=left, 3=right, 4=none/delivered
        """
        robot_pos = tuple(state["robot_position"])
        
        # Find nearest undelivered package
        nearest_pkg = None
        nearest_dist = float('inf')
        
        for pkg in state["packages"]:
            if not pkg["delivered"] and pkg["location"]:
                loc = tuple(pkg["location"])
                dist = abs(loc[0] - robot_pos[0]) + abs(loc[1] - robot_pos[1])
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_pkg = (loc[0] - robot_pos[0], loc[1] - robot_pos[1])
        
        if nearest_pkg is None:
            return 4  # No packages
        
        dx, dy = nearest_pkg
        
        # Return direction of nearest package
        if dy < 0:
            return 0  # Up
        elif dy > 0:
            return 1  # Down
        elif dx < 0:
            return 2  # Left
        elif dx > 0:
            return 3  # Right
        else:
            return 4  # At package location
    
    def get_q_table_size(self) -> int:
        """Get number of states in Q-table.
        
        Returns:
            Number of unique states encountered
        """
        return len(self.q_table)
