"""Training loop for Q-Learning agent with live logging."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warehouse_env.env import WarehouseEnv
from agent.rl_agent import QLearningAgent


def train(episodes: int = 1000, seed: int = 42):
    """Train Q-Learning agent.
    
    Args:
        episodes: Number of episodes to train
        seed: Random seed for reproducibility
    """
    print("=" * 70)
    print("WAREHOUSE ENVIRONMENT - Q-LEARNING TRAINING")
    print("=" * 70)
    
    env = WarehouseEnv(seed=seed)
    agent = QLearningAgent(env, alpha=0.1, gamma=0.99, epsilon=1.0)
    
    episode_rewards = []
    episode_steps = []
    episode_delivered = []
    
    print(f"Training for {episodes} episodes...")
    print(f"Initial epsilon: {agent.epsilon:.4f}")
    print()
    
    for episode in range(1, episodes + 1):
        state = env.reset()
        agent.reset()
        episode_reward = 0.0
        
        while not state["episode_done"]:
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            
            # Update Q-values
            agent.update_q_value(state, action, reward, next_state, done)
            
            episode_reward += reward
            state = next_state
        
        # Decay exploration
        agent.decay_exploration()
        
        episode_rewards.append(episode_reward)
        episode_steps.append(env.step_count)
        episode_delivered.append(env.packages_delivered)
        
        # Print progress every 50 episodes
        if episode % 50 == 0:
            avg_reward_50 = sum(episode_rewards[-50:]) / 50
            avg_steps_50 = sum(episode_steps[-50:]) / 50
            avg_delivered_50 = sum(episode_delivered[-50:]) / 50
            
            print(
                f"Episode {episode:4d}/{episodes} | "
                f"Reward: {episode_reward:7.1f} | "
                f"Avg(last 50): {avg_reward_50:6.1f} | "
                f"Avg Steps: {avg_steps_50:5.1f} | "
                f"Delivered: {avg_delivered_50:4.1f}/5 | "
                f"ε: {agent.epsilon:.4f} | "
                f"Q-States: {agent.get_q_table_size()}"
            )
    
    # Save Q-table
    q_table_path = os.path.join(
        os.path.dirname(__file__), "q_table.pkl"
    )
    agent.save_q_table(q_table_path)
    print()
    print(f"Q-table saved to: {q_table_path}")
    
    # Training summary
    print()
    print("=" * 70)
    print("TRAINING SUMMARY")
    print("=" * 70)
    print(f"Final epsilon: {agent.epsilon:.4f}")
    print(f"Total Q-table states: {agent.get_q_table_size()}")
    print(f"Final episode reward: {episode_rewards[-1]:.1f}")
    print(f"Average reward (last 100): {sum(episode_rewards[-100:]) / 100:.1f}")
    print(f"Average steps (last 100): {sum(episode_steps[-100:]) / 100:.1f}")
    print(f"Average packages delivered (last 100): {sum(episode_delivered[-100:]) / 100:.1f}")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Q-Learning warehouse agent")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    train(episodes=args.episodes, seed=args.seed)
