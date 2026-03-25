"""Package dataclass with priority and delivery logic."""

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class Package:
    """Represents a package in the warehouse.
    
    Attributes:
        id: Unique package identifier (e.g., "pkg_0")
        location: Current [x, y] position or None if delivered
        target_zone: Dispatch zone ('A', 'B', or 'C')
        priority: Urgency level (1=low, 2=medium, 3=high)
        delivered: Whether package has been delivered
        steps_remaining: Steps until priority 3 deadline (None for priority 1-2)
    """
    
    id: str
    location: Optional[Tuple[int, int]]
    target_zone: str
    priority: int
    delivered: bool = False
    steps_remaining: Optional[int] = field(default=None)
    
    def __post_init__(self):
        """Initialize steps_remaining for priority 3 packages."""
        if self.priority == 3 and self.steps_remaining is None:
            self.steps_remaining = 30
    
    def decrement_deadline(self) -> bool:
        """Decrement deadline timer. Returns True if deadline passed."""
        if self.priority == 3 and self.steps_remaining is not None:
            self.steps_remaining -= 1
            return self.steps_remaining <= 0
        return False
    
    def to_dict(self) -> dict:
        """Convert package to dictionary representation."""
        return {
            "id": self.id,
            "location": list(self.location) if self.location else None,
            "target_zone": self.target_zone,
            "priority": self.priority,
            "delivered": self.delivered,
            "steps_remaining": self.steps_remaining,
        }
