"""Reward calculation for warehouse environment."""

from typing import Dict, List, Tuple


class RewardCalculator:
    """Calculates rewards based on actions and outcomes."""
    
    # Reward values
    DELIVERY_REWARD = {1: 10, 2: 20, 3: 30}  # By priority
    PRIORITY_3_BONUS = 15  # Bonus for meeting deadline
    WRONG_ZONE_PENALTY = -5
    COLLISION_PENALTY = -2
    STEP_PENALTY = -1
    BATTERY_DEATH_PENALTY = -20
    PRIORITY_3_EXPIRE_PENALTY = -10
    COMPLETION_BONUS = 50
    
    def __init__(self):
        """Initialize reward calculator."""
        pass
    
    def calculate_delivery_reward(
        self,
        priority: int,
        correct_zone: bool,
        deadline_met: bool = False
    ) -> float:
        """Calculate reward for package delivery.
        
        Args:
            priority: Package priority (1, 2, or 3)
            correct_zone: Whether delivered to correct zone
            deadline_met: Whether priority 3 deadline was met
            
        Returns:
            Total reward for delivery
        """
        if not correct_zone:
            return self.WRONG_ZONE_PENALTY
        
        reward = self.DELIVERY_REWARD.get(priority, 0)
        
        if priority == 3 and deadline_met:
            reward += self.PRIORITY_3_BONUS
        
        return reward
    
    def calculate_step_penalty(self) -> float:
        """Get penalty per step taken."""
        return self.STEP_PENALTY
    
    def calculate_collision_penalty(self) -> float:
        """Get penalty for hitting wall/shelf."""
        return self.COLLISION_PENALTY
    
    def calculate_battery_death_penalty(self) -> float:
        """Get penalty for battery death."""
        return self.BATTERY_DEATH_PENALTY
    
    def calculate_deadline_expiry_penalty(self) -> float:
        """Get penalty for priority 3 deadline expiry."""
        return self.PRIORITY_3_EXPIRE_PENALTY
    
    def calculate_completion_bonus(self) -> float:
        """Get bonus for delivering all packages."""
        return self.COMPLETION_BONUS
    
    def get_reward_schema(self) -> Dict[str, float]:
        """Return all reward values as schema reference."""
        return {
            "delivery_priority_1": self.DELIVERY_REWARD[1],
            "delivery_priority_2": self.DELIVERY_REWARD[2],
            "delivery_priority_3": self.DELIVERY_REWARD[3],
            "priority_3_deadline_bonus": self.PRIORITY_3_BONUS,
            "wrong_zone_penalty": self.WRONG_ZONE_PENALTY,
            "collision_penalty": self.COLLISION_PENALTY,
            "step_penalty": self.STEP_PENALTY,
            "battery_death_penalty": self.BATTERY_DEATH_PENALTY,
            "deadline_expiry_penalty": self.PRIORITY_3_EXPIRE_PENALTY,
            "completion_bonus": self.COMPLETION_BONUS,
        }
