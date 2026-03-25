"""Evaluate and compare agents side-by-side."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from warehouse_env.env import WarehouseEnv
from agent.random_agent import RandomAgent
from agent.greedy_agent import GreedyAgent
from agent.rl_agent import QLearningAgent


def evaluate_agent(agent, agent_name: str, env: WarehouseEnv, episodes: int = 100, seed: int = 42):
    """Evaluate single agent over multiple episodes.
    
    Args:
        agent: Agent instance
        agent_name: Name for logging
        env: WarehouseEnv instance
        episodes: Number of episodes to evaluate
        seed: Random seed
        
    Returns:
        Dictionary with metrics
    """
    total_reward = 0.0
    total_steps = 0
    total_delivered = 0
    battery_deaths = 0
    total_packages = 0
    
    for episode in range(episodes):
        state = env.reset()
        agent.reset()
        
        total_packages += len(state["packages"])
        
        while not state["episode_done"]:
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            state = next_state
        
        total_reward += env.episode_reward
        total_steps += env.step_count
        total_delivered += env.packages_delivered
        
        if not env.robot.is_alive():
            battery_deaths += 1
    
    metrics = {
        "agent": agent_name,
        "episodes": episodes,
        "avg_reward": total_reward / episodes,
        "avg_steps": total_steps / episodes,
        "avg_delivered": total_delivered / episodes,
        "delivery_rate": (total_delivered / total_packages * 100) if total_packages > 0 else 0,
        "battery_deaths": battery_deaths,
        "death_rate": (battery_deaths / episodes * 100),
    }
    
    return metrics


def evaluate(episodes: int = 100, seed: int = 42):
    """Run evaluation for all agents.
    
    Args:
        episodes: Episodes per agent
        seed: Random seed
    """
    print("=" * 100)
    print("WAREHOUSE ENVIRONMENT - AGENT EVALUATION")
    print("=" * 100)
    print()
    
    # Initialize environment
    env = WarehouseEnv(seed=seed)
    
    # Random agent
    print(f"Evaluating Random Agent ({episodes} episodes)...")
    random_agent = RandomAgent(env)
    random_metrics = evaluate_agent(random_agent, "Random", env, episodes=episodes, seed=seed)
    print(f"  ✓ Complete")
    
    # Greedy agent
    print(f"Evaluating Greedy Agent ({episodes} episodes)...")
    env = WarehouseEnv(seed=seed)
    greedy_agent = GreedyAgent(env)
    greedy_metrics = evaluate_agent(greedy_agent, "Greedy", env, episodes=episodes, seed=seed)
    print(f"  ✓ Complete")
    
    # RL agent
    print(f"Evaluating RL Agent ({episodes} episodes)...")
    env = WarehouseEnv(seed=seed)
    rl_agent = QLearningAgent(env, alpha=0.1, gamma=0.99, epsilon=0.01)
    
    # Try to load trained Q-table
    q_table_path = os.path.join(os.path.dirname(__file__), "q_table.pkl")
    if os.path.exists(q_table_path):
        rl_agent.load_q_table(q_table_path)
        print(f"  ✓ Loaded Q-table from {q_table_path}")
    else:
        print(f"  ⚠ No Q-table found at {q_table_path}")
        print(f"    Using untrained agent. Run train.py first for best results.")
    
    rl_agent.set_training(False)  # Disable exploration
    rl_metrics = evaluate_agent(rl_agent, "RL (Q-Learning)", env, episodes=episodes, seed=seed)
    print(f"  ✓ Complete")
    
    # Print comparison table
    print()
    print("=" * 100)
    print("EVALUATION RESULTS")
    print("=" * 100)
    print()
    
    metrics_list = [random_metrics, greedy_metrics, rl_metrics]
    
    # Header
    print(f"{'Agent':<20} | {'Avg Reward':>12} | {'Avg Steps':>10} | {'Delivered':>10} | {'Delivery%':>9} | {'Deaths':>6} | {'Death%':>7}")
    print("-" * 100)
    
    # Rows
    for m in metrics_list:
        print(
            f"{m['agent']:<20} | "
            f"{m['avg_reward']:>12.1f} | "
            f"{m['avg_steps']:>10.1f} | "
            f"{m['avg_delivered']:>10.1f} | "
            f"{m['delivery_rate']:>8.1f}% | "
            f"{m['battery_deaths']:>6} | "
            f"{m['death_rate']:>6.1f}%"
        )
    
    # Analysis
    print()
    print("=" * 100)
    print("ANALYSIS")
    print("=" * 100)
    
    # Compare vs random baseline
    random_reward = random_metrics["avg_reward"]
    
    print()
    print(f"Random Agent Baseline: {random_reward:.1f} reward/episode")
    print()
    
    for m in metrics_list[1:]:
        improvement = ((m["avg_reward"] - random_reward) / abs(random_reward) * 100) if random_reward != 0 else 0
        print(f"{m['agent']}:")
        print(f"  Reward improvement: {improvement:+.1f}%")
        print(f"  Delivery rate: {m['delivery_rate']:.1f}%")
        print(f"  Battery survival: {100 - m['death_rate']:.1f}%")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate warehouse agents")
    parser.add_argument("--episodes", type=int, default=100, help="Episodes per agent")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    evaluate(episodes=args.episodes, seed=args.seed)
