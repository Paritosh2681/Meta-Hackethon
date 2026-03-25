"""Interactive demo showing agent navigating warehouse in real-time."""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from warehouse_env.env import WarehouseEnv
from warehouse_env.renderer import WarehouseRenderer
from agent.greedy_agent import GreedyAgent
from agent.rl_agent import QLearningAgent


def demo(agent_type: str = "greedy", episode: int = 1, delay: float = 0.3):
    """Run interactive warehouse demo with ASCII rendering.
    
    Args:
        agent_type: "random", "greedy", or "rl"
        episode: Which episode to run
        delay: Delay between steps in seconds (for visualization)
    """
    print("=" * 80)
    print("WAREHOUSE ENVIRONMENT - INTERACTIVE DEMO")
    print("=" * 80)
    print()
    
    # Initialize environment and agent
    env = WarehouseEnv(seed=42)
    renderer = WarehouseRenderer(width=10, height=10)
    
    if agent_type == "greedy":
        agent = GreedyAgent(env)
        agent_name = "Greedy Agent"
    elif agent_type == "rl":
        agent = QLearningAgent(env)
        q_table_path = os.path.join(os.path.dirname(__file__), "q_table.pkl")
        if os.path.exists(q_table_path):
            agent.load_q_table(q_table_path)
            print(f"Loaded trained Q-table")
        else:
            print(f"Warning: No Q-table found. Using untrained agent.")
        agent.set_training(False)
        agent_name = "RL Agent (Q-Learning)"
    else:
        from agent.random_agent import RandomAgent
        agent = RandomAgent(env)
        agent_name = "Random Agent"
    
    print(f"Agent: {agent_name}")
    print(f"Delay between steps: {delay}s")
    print()
    print("Controls:")
    print("  SPACE = Next step")
    print("  'q' = Quit")
    print()
    
    # Reset and run episode
    state = env.reset()
    agent.reset()
    step = 0
    
    # Print initial state
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
    print(f"Initial packages: {len(state['packages'])}")
    for pkg in state["packages"]:
        print(f"  {pkg['id']}: zone {pkg['target_zone']}, priority {pkg['priority']}")
    print()
    
    # Run episode
    while not state["episode_done"]:
        step += 1
        
        # Get action
        action = agent.get_action(state)
        next_state, reward, done, info = env.step(action)
        
        # Render
        print(f"\n--- Step {step} ---")
        print(f"Action: {action}")
        print(f"Reward: {reward:+.1f}")
        
        if info.get("collision"):
            print("⚠ COLLISION! Hit wall or shelf")
        if info.get("delivery"):
            d = info["delivery"]
            symbol = "✓" if d["correct_zone"] else "✗"
            print(f"{symbol} Delivered {d['package_id']} to zone {d['target_zone']} "
                  f"(priority {d['priority']})")
        if info.get("battery_dead"):
            print("🔋 BATTERY DEAD! Episode ended.")
        if info.get("package_expired"):
            print("⏰ Priority 3 package deadline expired!")
        
        # Render grid
        grid_str = renderer.render(
            tuple(next_state["robot_position"]),
            next_state["packages"],
            {z: tuple(p) for z, p in next_state["dispatch_zones"].items()},
            tuple(next_state["charging_station"]),
            next_state["shelves"],
            next_state["battery"],
            next_state["step_count"],
            next_state["carrying"]
        )
        
        print()
        print(grid_str)
        
        # Status
        print()
        print(f"Packages delivered: {next_state['packages_delivered']}/{len(state['packages'])}")
        print(f"Battery: {next_state['battery']}%")
        if next_state["carrying"]:
            for pkg in next_state["packages"]:
                if pkg["id"] == next_state["carrying"]:
                    print(f"Carrying: {pkg['id']} → zone {pkg['target_zone']}")
        
        state = next_state
        
        # Wait for user input or auto-advance
        if delay > 0:
            time.sleep(delay)
        else:
            try:
                user_input = input("\nPress SPACE for next step, 'q' to quit: ").strip().lower()
                if user_input == 'q':
                    break
            except EOFError:
                pass  # In case running non-interactively
    
    # Summary
    summary = renderer.render_summary(
        next_state["packages_delivered"],
        len(state["packages"]),
        next_state["episode_reward"],
        next_state["episode_done"]
    )
    
    print()
    print(summary)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run interactive warehouse demo")
    parser.add_argument(
        "--agent",
        choices=["random", "greedy", "rl"],
        default="greedy",
        help="Agent type"
    )
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between steps (seconds)")
    parser.add_argument("--episode", type=int, default=1, help="Episode number")
    
    args = parser.parse_args()
    demo(agent_type=args.agent, delay=args.delay)
