"""Core warehouse environment with standard RL API."""

import random
from typing import Tuple, Dict, List, Optional, Any
from .grid import WarehouseGrid
from .robot import Robot
from .package import Package
from .reward import RewardCalculator


class WarehouseEnv:
    """Smart warehouse logistics environment for AI agent training.
    
    Implements standard RL API:
        - reset() → initial state dict
        - step(action) → (state, reward, done, info)
        - state() → current state dict (non-mutating)
    
    Grid: 10x10 warehouse with shelves, dispatch zones, charging station.
    Robot: Battery-constrained with pick/drop actions.
    Packages: Dynamic spawn, variable priority with deadlines.
    """
    
    # Valid actions
    MOVE_ACTIONS = {"move_up", "move_down", "move_left", "move_right"}
    ROBOT_ACTIONS = {"pick_up", "drop_off", "charge"}
    VALID_ACTIONS = MOVE_ACTIONS | ROBOT_ACTIONS
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize warehouse environment.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed_value = seed
        if seed is not None:
            random.seed(seed)
        
        # Core components
        self.grid = WarehouseGrid(seed=seed)
        self.robot = Robot(home_pos=self.grid.home_pos)
        self.reward_calc = RewardCalculator()
        
        # Episode state
        self.packages: List[Package] = []
        self.step_count = 0
        self.episode_done = False
        self.episode_reward = 0.0
        self.packages_delivered = 0
        
        # Episode limits
        self.max_steps = 500
        self.episode = 0
    
    def reset(self) -> Dict[str, Any]:
        """Reset environment to initial state for new episode.
        
        Randomizes:
            - Package locations and count (3-6 packages)
            - Package target zones
            - Package priorities
        
        Returns:
            Initial state dict with full environment snapshot
        """
        self.step_count = 0
        self.episode_done = False
        self.episode_reward = 0.0
        self.packages_delivered = 0
        self.episode += 1
        
        # Reset robot
        self.robot.reset()
        
        # Create random packages (3-6 per episode)
        num_packages = random.randint(3, 6)
        self.packages = []
        
        zones = list(self.grid.dispatch_zones.keys())
        used_positions = {self.grid.home_pos, self.grid.charging_station}
        used_positions.update(self.grid.shelves)
        
        for i in range(num_packages):
            # Random location (not home, charger, or shelf)
            while True:
                x = random.randint(0, self.grid.width - 1)
                y = random.randint(0, self.grid.height - 1)
                if (x, y) not in used_positions and self.grid.is_valid_position(x, y):
                    used_positions.add((x, y))
                    break
            
            # Random target zone
            target_zone = random.choice(zones)
            
            # Random priority (weighted: more low priority)
            priority = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            
            pkg = Package(
                id=f"pkg_{i}",
                location=(x, y),
                target_zone=target_zone,
                priority=priority,
            )
            self.packages.append(pkg)
        
        return self.state()
    
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute one step of environment.
        
        Args:
            action: One of {
                "move_up", "move_down", "move_left", "move_right",
                "pick_up", "drop_off", "charge"
            }
        
        Returns:
            Tuple of (state, reward, done, info) where:
                state: Current environment state dict
                reward: Float reward for this step
                done: Boolean whether episode ended
                info: Debug dictionary with step details
        """
        reward = 0.0
        info = {
            "action": action,
            "valid_action": True,
            "collision": False,
            "delivery": None,
            "package_expired": False,
            "battery_dead": False,
        }
        
        # Validate action
        if action not in self.VALID_ACTIONS:
            reward = self.reward_calc.calculate_step_penalty()
            info["valid_action"] = False
            self.step_count += 1
            self.episode_reward += reward
            return self.state(), reward, self.episode_done, info
        
        # Decrement deadlines for priority 3 packages
        for pkg in self.packages:
            if not pkg.delivered:
                expired = pkg.decrement_deadline()
                if expired:
                    reward += self.reward_calc.calculate_deadline_expiry_penalty()
                    info["package_expired"] = True
        
        # Execute movement actions
        if action in self.MOVE_ACTIONS:
            direction = action.replace("move_", "")
            rx, ry = self.robot.position
            
            # Check if move is valid
            if direction not in self.grid.get_valid_moves(rx, ry):
                reward += self.reward_calc.calculate_collision_penalty()
                info["collision"] = True
            else:
                self.robot.move(direction)
        
        # Pick up action
        elif action == "pick_up":
            if self.robot.carrying is None:
                # Find package at robot position
                pkg_at_pos = None
                for pkg in self.packages:
                    if (not pkg.delivered and pkg.location and
                        pkg.location[0] == self.robot.position[0] and
                        pkg.location[1] == self.robot.position[1]):
                        pkg_at_pos = pkg
                        break
                
                if pkg_at_pos:
                    self.robot.pick_up(pkg_at_pos.id)
                    pkg_at_pos.location = None  # Remove from location
                else:
                    reward += self.reward_calc.calculate_step_penalty()
            else:
                reward += self.reward_calc.calculate_step_penalty()
        
        # Drop off action
        elif action == "drop_off":
            if self.robot.carrying:
                dropped_id = self.robot.drop_off()
                
                # Find package and check if at correct zone
                target_pkg = None
                for pkg in self.packages:
                    if pkg.id == dropped_id:
                        target_pkg = pkg
                        break
                
                if target_pkg:
                    zone_pos = self.grid.dispatch_zones.get(target_pkg.target_zone)
                    correct_zone = (zone_pos == tuple(self.robot.position))
                    
                    if correct_zone:
                        target_pkg.delivered = True
                        self.packages_delivered += 1
                        deadline_met = (target_pkg.priority == 3 and
                                       target_pkg.steps_remaining > 0)
                        reward += self.reward_calc.calculate_delivery_reward(
                            target_pkg.priority,
                            correct_zone=True,
                            deadline_met=deadline_met
                        )
                        info["delivery"] = {
                            "package_id": dropped_id,
                            "priority": target_pkg.priority,
                            "correct_zone": True,
                        }
                    else:
                        reward += self.reward_calc.calculate_delivery_reward(
                            target_pkg.priority,
                            correct_zone=False
                        )
                        info["delivery"] = {
                            "package_id": dropped_id,
                            "priority": target_pkg.priority,
                            "correct_zone": False,
                        }
            else:
                reward += self.reward_calc.calculate_step_penalty()
        
        # Charge action
        elif action == "charge":
            if (self.robot.position[0] == self.grid.charging_station[0] and
                self.robot.position[1] == self.grid.charging_station[1]):
                self.robot.charge()
            else:
                reward += self.reward_calc.calculate_step_penalty()
        
        # Check if robot battery dead
        if not self.robot.is_alive():
            reward += self.reward_calc.calculate_battery_death_penalty()
            self.episode_done = True
            info["battery_dead"] = True
        
        # Check if all packages delivered
        all_delivered = all(pkg.delivered for pkg in self.packages)
        if all_delivered and not self.episode_done:
            reward += self.reward_calc.calculate_completion_bonus()
            self.episode_done = True
        
        # Check step limit
        self.step_count += 1
        if self.step_count >= self.max_steps:
            self.episode_done = True
        
        # Add step penalty (for all actions)
        reward += self.reward_calc.calculate_step_penalty()
        
        self.episode_reward += reward
        
        return self.state(), reward, self.episode_done, info
    
    def state(self) -> Dict[str, Any]:
        """Get current environment state (non-mutating).
        
        Returns:
            Dictionary with complete environment state:
                - robot_position: [x, y]
                - battery: int (0-100)
                - carrying: package_id or null
                - packages: list of package dicts
                - dispatch_zones: dict mapping A/B/C to [x, y]
                - charging_station: [x, y]
                - step_count: int
                - episode_done: bool
                - episode_reward: float
                - packages_delivered: int
        """
        return {
            "robot_position": self.robot.position.copy(),
            "battery": self.robot.battery,
            "carrying": self.robot.carrying,
            "packages": [pkg.to_dict() for pkg in self.packages],
            "dispatch_zones": {
                zone: list(pos) for zone, pos in self.grid.dispatch_zones.items()
            },
            "charging_station": list(self.grid.charging_station),
            "shelves": sorted(list(self.grid.shelves)),
            "step_count": self.step_count,
            "episode_done": self.episode_done,
            "episode_reward": self.episode_reward,
            "packages_delivered": self.packages_delivered,
        }
    
    def get_valid_actions(self) -> List[str]:
        """Get list of all valid actions.
        
        Returns:
            List of action strings
        """
        return list(self.VALID_ACTIONS)
    
    def get_reward_schema(self) -> Dict[str, float]:
        """Get reward structure reference.
        
        Returns:
            Dictionary of all reward values
        """
        return self.reward_calc.get_reward_schema()
