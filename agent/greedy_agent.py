"""Greedy heuristic agent - prioritizes high-value packages."""

from typing import List, Dict, Tuple, Optional
import math


class GreedyAgent:
    """Heuristic-based agent using greedy policy.
    
    Strategy:
        1. If carrying a package, move toward its target dispatch zone
        2. If not carrying, move toward highest-priority undelivered package
        3. If battery low, go to charging station
    
    This is a strong baseline and can beat random agent significantly.
    """
    
    def __init__(self, env):
        """Initialize greedy agent.
        
        Args:
            env: WarehouseEnv instance
        """
        self.env = env
        self.action_history = []
    
    def get_action(self, state: dict) -> str:
        """Select greedy action based on heuristics.
        
        Args:
            state: Current environment state dict
            
        Returns:
            Action string
        """
        robot_pos = tuple(state["robot_position"])
        carrying = state["carrying"]
        battery = state["battery"]
        packages = state["packages"]
        
        # Priority 1: Emergency charge if battery critically low
        if battery < 10:
            action = self._move_toward_position(
                robot_pos, tuple(state["charging_station"])
            )
            if action == "at_target":
                action = "charge"
            self.action_history.append(action)
            return action
        
        # Priority 2: If carrying package, deliver it
        if carrying:
            pkg_dict = None
            for pkg in packages:
                if pkg["id"] == carrying:
                    pkg_dict = pkg
                    break
            
            if pkg_dict:
                target_zone = pkg_dict["target_zone"]
                target_pos = tuple(state["dispatch_zones"][target_zone])
                
                if robot_pos == target_pos:
                    action = "drop_off"
                else:
                    action = self._move_toward_position(robot_pos, target_pos)
                
                self.action_history.append(action)
                return action
        
        # Priority 3: Find best undelivered package to go pick up
        best_pkg = self._find_best_package(robot_pos, packages)
        
        if best_pkg is None:
            # No packages left, idle
            action = "move_up"  # Arbitrary valid action
        else:
            pkg_location = tuple(best_pkg["location"])
            
            if robot_pos == pkg_location:
                action = "pick_up"
            else:
                action = self._move_toward_position(robot_pos, pkg_location)
        
        self.action_history.append(action)
        return action
    
    def _find_best_package(self, robot_pos: Tuple[int, int], packages: List[Dict]) -> Optional[Dict]:
        """Find highest-priority undelivered package by priority and distance.
        
        Args:
            robot_pos: Current robot position
            packages: List of package dicts
            
        Returns:
            Best package dict, or None if none available
        """
        candidates = [pkg for pkg in packages if not pkg["delivered"] and pkg["location"]]
        
        if not candidates:
            return None
        
        # Sort by: priority (descending), then distance (ascending)
        def score(pkg):
            distance = self._manhattan_distance(robot_pos, tuple(pkg["location"]))
            # Higher priority = better, shorter distance = better
            # Use negative priority so higher priority sorts first
            return (-pkg["priority"], distance)
        
        candidates.sort(key=score)
        return candidates[0]
    
    def _move_toward_position(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """Greedily move one step closer to target position.
        
        Uses Manhattan distance heuristic: move in direction that reduces distance.
        
        Args:
            from_pos: Current position
            to_pos: Target position
            
        Returns:
            Action that moves closer (or "at_target" if already there)
        """
        if from_pos == to_pos:
            return "at_target"
        
        fx, fy = from_pos
        tx, ty = to_pos
        
        # Calculate which direction reduces Manhattan distance
        moves_with_distance = {
            "up": (fx, fy - 1),
            "down": (fx, fy + 1),
            "left": (fx - 1, fy),
            "right": (fx + 1, fy),
        }
        
        valid_moves = self.env.grid.get_valid_moves(fx, fy)
        
        best_move = None
        best_distance = float('inf')
        
        for move in valid_moves:
            next_pos = moves_with_distance[move]
            distance = self._manhattan_distance(next_pos, to_pos)
            
            if distance < best_distance:
                best_distance = distance
                best_move = move
        
        # Fallback (shouldn't happen in valid scenarios)
        if best_move is None:
            best_move = "up"
        
        # Convert direction to action
        return f"move_{best_move}"
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def reset(self) -> None:
        """Reset agent history."""
        self.action_history = []
