"""Grid layout with obstacles, zones, and static locations."""

from typing import Tuple, Dict, List, Set


class WarehouseGrid:
    """10x10 warehouse grid with shelves, dispatch zones, and charging station.
    
    Layout:
        - Shelves are fixed obstacles (robot cannot pass)
        - Dispatch zones A, B, C are drop-off points
        - Charging station is 1 cell where robot recharges
        - Home position is robot's starting point
    """
    
    def __init__(self, seed: int = None):
        """Initialize warehouse grid.
        
        Args:
            seed: Random seed for reproducibility (currently not used for static layout)
        """
        self.width = 10
        self.height = 10
        
        # Fixed home position
        self.home_pos = (0, 0)
        
        # Fixed charging station (top-right area)
        self.charging_station = (9, 9)
        
        # Fixed dispatch zones
        self.dispatch_zones = {
            "A": (9, 0),
            "B": (9, 5),
            "C": (0, 9),
        }
        
        # Fixed shelf positions (obstacles)
        self.shelves = self._create_shelves()
        
        # All obstacle positions for quick lookup
        self._obstacle_cache = set(self.shelves)
    
    def _create_shelves(self) -> Set[Tuple[int, int]]:
        """Create shelf layout - multiple obstacles throughout grid.
        
        Returns:
            Set of (x, y) positions that are shelves
        """
        shelves = set()
        
        # Vertical shelves
        for y in range(2, 8):
            shelves.add((2, y))
            shelves.add((5, y))
            shelves.add((8, y))
        
        # Horizontal shelves
        for x in range(1, 9):
            shelves.add((x, 3))
            shelves.add((x, 7))
        
        return shelves
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within bounds and not a shelf.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position is walkable
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if (x, y) in self._obstacle_cache:
            return False
        return True
    
    def is_shelf(self, x: int, y: int) -> bool:
        """Check if position is a shelf."""
        return (x, y) in self.shelves
    
    def get_valid_moves(self, x: int, y: int) -> List[str]:
        """Get list of valid move directions from current position.
        
        Args:
            x: Current X coordinate
            y: Current Y coordinate
            
        Returns:
            List of valid directions: ["up", "down", "left", "right"]
        """
        valid = []
        moves = {
            "up": (x, y - 1),
            "down": (x, y + 1),
            "left": (x - 1, y),
            "right": (x + 1, y),
        }
        
        for direction, (nx, ny) in moves.items():
            if self.is_valid_position(nx, ny):
                valid.append(direction)
        
        return valid
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions.
        
        Args:
            pos1: (x, y) tuple
            pos2: (x, y) tuple
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_state(self) -> dict:
        """Get grid configuration state."""
        return {
            "width": self.width,
            "height": self.height,
            "home_pos": self.home_pos,
            "charging_station": self.charging_station,
            "dispatch_zones": self.dispatch_zones.copy(),
            "shelves": sorted(list(self.shelves)),
        }
