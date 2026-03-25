#!/usr/bin/env python
"""Test demo visualization works."""

import sys
from warehouse_env.env import WarehouseEnv
from warehouse_env.renderer import WarehouseRenderer
from agent.greedy_agent import GreedyAgent

# Initialize
env = WarehouseEnv(seed=42)
renderer = WarehouseRenderer(width=10, height=10)
agent = GreedyAgent(env)

print("=" * 80)
print("DEMO TEST - Greedy Agent Navigation")
print("=" * 80)
print()

# Reset
state = env.reset()
agent.reset()

# Show initial grid
print("Initial Warehouse State:")
grid_str = renderer.render(
    tuple(state["robot_position"]),
    state["packages"],
    {z: tuple(p) for z, p in state["dispatch_zones"].items()},
    tuple(state["charging_station"]),
    state["shelves"],
    state["battery"],
    state["step_count"],
    state["carrying"]
)
print(grid_str)
print()
print(f"Packages to deliver: {len(state['packages'])}")
for pkg in state["packages"]:
    print(f"  - {pkg['id']}: priority {pkg['priority']}, zone {pkg['target_zone']}")
print()

# Run 10 steps
print("Running 10 steps with Greedy Agent:\n")
for step in range(10):
    action = agent.get_action(state)
    state, reward, done, info = env.step(action)
    
    delivery_marker = " 📦 DELIVERED!" if info.get("delivery") else ""
    collision_marker = " ⚠ COLLISION" if info.get("collision") else ""
    
    print(f"Step {step+1:2d}: {action:12s} | Reward: {reward:+6.1f} | Battery: {state['battery']:3d}% | Delivered: {state['packages_delivered']}/{len(env.packages)}{delivery_marker}{collision_marker}")
    
    if done:
        print(f"\nEpisode ended at step {state['step_count']}")
        break

print()
print(f"Final Grid State:")
grid_str = renderer.render(
    tuple(state["robot_position"]),
    state["packages"],
    {z: tuple(p) for z, p in state["dispatch_zones"].items()},
    tuple(state["charging_station"]),
    state["shelves"],
    state["battery"],
    state["step_count"],
    state["carrying"]
)
print(grid_str)

print()
print("✓ Demo visualization test passed!")
