"""ASCII renderer for warehouse visualization."""

from typing import Dict, List, Tuple, Optional, Set


class WarehouseRenderer:
    """Renders warehouse state as ASCII grid to terminal."""
    
    # Symbols
    WALL = "#"
    SHELF = "█"
    ZONE_A = "A"
    ZONE_B = "B"
    ZONE_C = "C"
    ROBOT = "R"
    PACKAGE = "P"
    CHARGING = "⚡"
    EMPTY = "."
    
    def __init__(self, width: int = 10, height: int = 10):
        """Initialize renderer.
        
        Args:
            width: Grid width
            height: Grid height
        """
        self.width = width
        self.height = height
    
    def render(
        self,
        robot_pos: Tuple[int, int],
        packages: List[Dict],
        dispatch_zones: Dict[str, Tuple[int, int]],
        charging_station: Tuple[int, int],
        shelves: Set[Tuple[int, int]],
        battery: int,
        step_count: int,
        carrying: Optional[str] = None
    ) -> str:
        """Render warehouse state as ASCII grid.
        
        Args:
            robot_pos: Current robot [x, y]
            packages: List of package dicts
            dispatch_zones: Dict of zone positions
            charging_station: Charging station position
            shelves: Set of shelf positions
            battery: Current battery level
            step_count: Current step count
            carrying: Package ID being carried
            
        Returns:
            String representation of warehouse
        """
        # Create empty grid
        grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        # Mark shelves
        for sx, sy in shelves:
            if 0 <= sx < self.width and 0 <= sy < self.height:
                grid[sy][sx] = self.SHELF
        
        # Mark dispatch zones
        for zone, (zx, zy) in dispatch_zones.items():
            if 0 <= zx < self.width and 0 <= zy < self.height:
                grid[zy][zx] = zone
        
        # Mark charging station
        if 0 <= charging_station[0] < self.width and 0 <= charging_station[1] < self.height:
            grid[charging_station[1]][charging_station[0]] = self.CHARGING
        
        # Mark packages (only if not delivered)
        for pkg in packages:
            if not pkg["delivered"] and pkg["location"]:
                px, py = pkg["location"]
                if 0 <= px < self.width and 0 <= py < self.height:
                    priority = pkg["priority"]
                    grid[py][px] = str(priority)  # Show priority number
        
        # Mark robot (overwrites other symbols)
        rx, ry = robot_pos
        if 0 <= rx < self.width and 0 <= ry < self.height:
            grid[ry][rx] = self.ROBOT
        
        # Build output string
        lines = []
        lines.append("╔" + "═" * (self.width * 2 - 1) + "╗")
        
        for row in grid:
            lines.append("║" + " ".join(row) + "║")
        
        lines.append("╚" + "═" * (self.width * 2 - 1) + "╝")
        
        # Add status bar
        carrying_str = f"carrying: {carrying}" if carrying else "carrying: empty"
        status = f"Step: {step_count:3d} | Battery: {battery:3d}% | {carrying_str}"
        lines.append(status)
        
        # Add legend
        legend = f"Legend: R=Robot {self.CHARGING}=Charger {self.SHELF}=Shelf A/B/C=Zones 1/2/3=Package priority"
        lines.append(legend)
        
        return "\n".join(lines)
    
    def render_summary(
        self,
        delivered: int,
        total_packages: int,
        total_reward: float,
        episode_done: bool
    ) -> str:
        """Render episode summary.
        
        Args:
            delivered: Number of packages delivered
            total_packages: Total packages in episode
            total_reward: Cumulative episode reward
            episode_done: Whether episode ended
            
        Returns:
            String with summary
        """
        status = "COMPLETE" if episode_done else "IN PROGRESS"
        return (
            f"\n--- Episode Summary ---\n"
            f"Status: {status}\n"
            f"Delivered: {delivered}/{total_packages}\n"
            f"Episode Reward: {total_reward:.1f}\n"
        )
