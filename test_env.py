#!/usr/bin/env python
"""Quick test of warehouse environment."""

from warehouse_env.env import WarehouseEnv

# Test initialization
env = WarehouseEnv(seed=42)
print("✓ Environment initialized")

# Test reset
state = env.reset()
print(f"✓ Initial state keys: {list(state.keys())}")
print(f"✓ Robot position: {state['robot_position']}")
print(f"✓ Packages spawned: {len(state['packages'])}")
print()

# Test step API
print("Testing step() API:")
for i in range(5):
    action = "move_right"
    state, reward, done, info = env.step(action)
    print(f"  Step {state['step_count']}: {action} → Reward: {reward:+.1f}, Battery: {state['battery']}%")

print()
print("✓ All basic environment tests passed!")
print()
print("Next steps:")
print("  1. Run demo: python demo.py --agent greedy")
print("  2. Train agent: python train.py --episodes 100")
print("  3. Evaluate: python evaluate.py --episodes 50")
