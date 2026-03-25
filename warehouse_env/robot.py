"""Robot state and movement logic."""

from typing import Optional, Tuple


class Robot:
    """Manages robot state: position, battery, and carrying package.
    
    Attributes:
        position: Current [x, y] location
        battery: Remaining battery level (0-100)
        carrying: ID of package being carried (None if empty)
        home_pos: Starting position for each episode
    """
    
    def __init__(self, home_pos: Tuple[int, int] = (0, 0)):
        """Initialize robot at home position.
        
        Args:
            home_pos: Initial position [x, y]
        """
        self.home_pos = home_pos
        self.position = list(home_pos)
        self.battery = 100
        self.carrying = None
    
    def reset(self) -> None:
        """Reset robot to initial state."""
        self.position = list(self.home_pos)
        self.battery = 100
        self.carrying = None
    
    def move(self, direction: str) -> bool:
        """Move robot in given direction (validation done in env).
        
        Args:
            direction: One of "up", "down", "left", "right"
            
        Returns:
            True if move was executed (battery check still needed)
        """
        if direction == "up":
            self.position[1] -= 1
        elif direction == "down":
            self.position[1] += 1
        elif direction == "left":
            self.position[0] -= 1
        elif direction == "right":
            self.position[0] += 1
        else:
            return False
        
        self._drain_battery(1)
        return True
    
    def charge(self) -> None:
        """Fully recharge battery."""
        self.battery = 100
        self._drain_battery(1)  # Charging still costs 1 step
    
    def pick_up(self, package_id: Optional[str]) -> bool:
        """Pick up a package.
        
        Args:
            package_id: ID of package to pick up
            
        Returns:
            True if successful (carrying empty and package valid)
        """
        if self.carrying is None:
            self.carrying = package_id
            self._drain_battery(1)
            return True
        return False
    
    def drop_off(self) -> Optional[str]:
        """Drop off current package.
        
        Returns:
            ID of dropped package, or None if not carrying
        """
        if self.carrying is not None:
            pkg_id = self.carrying
            self.carrying = None
            self._drain_battery(1)
            return pkg_id
        return None
    
    def _drain_battery(self, amount: int) -> None:
        """Reduce battery by amount (minimum 0)."""
        self.battery = max(0, self.battery - amount)
    
    def is_alive(self) -> bool:
        """Check if robot still has battery."""
        return self.battery > 0
    
    def get_state(self) -> dict:
        """Get robot state as dictionary."""
        return {
            "position": self.position.copy(),
            "battery": self.battery,
            "carrying": self.carrying,
        }
