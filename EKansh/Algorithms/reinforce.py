# import torch
# import torch.optim as optim
# import numpy as np
# from Models.networks import PolicyNetwork
import torch
import torch.optim as optim
import numpy as np
from collections import deque  # Added for SMA
from Models.networks import PolicyNetwork

# class REINFORCE:
#     def __init__(self, env, learning_rate = 0.001, gamma = 0.99):
#         self.env = env
#         self.state_dim = env.observation_space.shape[0]
#         self.action_dim = env.action_space.n
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
#         # Policy Network
#         self.policy_net = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)
#         self.optimizer = optim.Adam(self.policy_net.parameters(), lr = learning_rate)
        
#         # Add this line to store gamma
#         self.gamma = gamma
        
#     def select_action(self, state):
#         state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
#         probs = self.policy_net(state)
#         action_dist = torch.distributions.Categorical(probs)
#         action = action_dist.sample()
#         log_prob = action_dist.log_prob(action)
#         return action.item(), log_prob
    
#     #Monte Carlo estimation of Q-Values
#     def calculate_returns(self, rewards):
#         returns = []
#         R = 0
        
#         #Calculate returns from the end of episode to the beginning
#         for r in rewards [::-1]:
#             R = r + self.gamma * R
#             returns.insert(0, R)
#         returns = torch.tensor(returns).to(self.device)
#         returns = (returns - returns.mean()) / (returns.std() + 1e-9)
#         return returns
    
#     def train(self, num_episodes = 500):
#         all_episode_rewards = []
        
#         for episode in range(num_episodes):
#             state , _ = self.env.reset()
#             log_probs = []
#             rewards = []
#             episode_reward = 0
#             done = False
            
#             #Collect trajectory (Monte Carlo Method of collecting the entireepisode before doing updates)
#             while not done:
#                 action, log_prob = self.select_action(state)
#                 next_state, reward, terminated, truncated, _ = self.env.step(action)
#                 done = terminated or truncated
                
#                 log_probs.append(log_prob)
#                 rewards.append(reward)
#                 episode_reward += reward
#                 state = next_state
                
#             #Calculate return
#             returns = self.calculate_returns(rewards)
            
#             #Calculate loss and update policy (Monte Carlo returns [R] in the policy Update)
#             policy_loss = []
#             for log_prob, R in zip(log_probs, returns):
#                 policy_loss.append(-log_prob * R)   #Negative for gradient ascent
                
#             self.optimizer.zero_grad()
#             policy_loss = torch.stack(policy_loss).sum()
#             policy_loss.backward()
#             self.optimizer.step()
            
#             all_episode_rewards.append(episode_reward)
            
#             if episode % 10 == 0:
#                 avg_reward = np.mean(all_episode_rewards[-10:])
#                 print(f"Episode {episode}, Avg.2 Reward (last 10): {avg_reward:.1f}")
                
#         return all_episode_rewards





# import torch
# import torch.optim as optim
# import numpy as np
# from Models.networks import PolicyNetwork # gamma =0.99,0.9,0.98 in first try ,

# class REINFORCE:
#     def __init__(self, env, learning_rate= 0.00099 , gamma=0.99, entropy_coef=0.01, clip_norm=1.0): #00001 was useless ,.01 is good but can do far better, 0.02 useless ,#0.001 is also working side by side
#         self.env = env
#         self.state_dim = env.observation_space.shape[0]
#         self.action_dim = env.action_space.n
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
#         # Policy Network (unchanged)
#         self.policy_net = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)
#         self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
#         # Discount factor remains unchanged
#         self.gamma = gamma
        
#         # Additional hyperparameters for improvement
#         self.entropy_coef = entropy_coef  # Encourages exploration
#         self.clip_norm = clip_norm        # Maximum allowed gradient norm
#         print("as")

#     def select_action(self, state):
#         # Convert state to tensor and compute action probabilities
#         state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
#         probs = self.policy_net(state_tensor)
#         action_dist = torch.distributions.Categorical(probs)
#         action = action_dist.sample()
#         log_prob = action_dist.log_prob(action)
#         entropy = action_dist.entropy()  # Capture entropy for regularization
#         return action.item(), log_prob, entropy

#     def calculate_returns(self, rewards):
#         returns = []
#         R = 0
#         # Compute discounted returns by iterating backward over rewards
#         for r in reversed(rewards):
#             R = r + self.gamma * R
#             returns.insert(0, R)
#         returns = torch.tensor(returns, dtype=torch.float32, device=self.device)
#         # Normalize returns to stabilize training
#         returns = (returns - returns.mean()) / (returns.std() + 1e-9)
#         return returns
    

    
#     def train(self, num_episodes=500, smoothing_factor=0.1):
#         all_episode_rewards = []
#         ema_reward = None  # For logging only

#         for episode in range(num_episodes):
#             # Support for both Gymnasium and older Gym APIs
#             reset_result = self.env.reset()
#             state = reset_result[0] if isinstance(reset_result, tuple) else reset_result
            
#             log_probs = []
#             entropies = []
#             rewards = []
#             episode_reward = 0
#             done = False
            
#             # Collect a full episode trajectory
#             while not done:
#                 action, log_prob, entropy = self.select_action(state)
#                 step_result = self.env.step(action)
#                 if len(step_result) == 5:
#                     next_state, reward, terminated, truncated, _ = step_result
#                     done = terminated or truncated
#                 else:
#                     next_state, reward, done, _ = step_result

#                 log_probs.append(log_prob)
#                 entropies.append(entropy)
#                 rewards.append(reward)
#                 episode_reward += reward
#                 state = next_state
            
#             # Compute normalized discounted returns
#             returns = self.calculate_returns(rewards)
#             baseline = returns.mean()  # Baseline to reduce variance
            
#             # Compute policy loss with baseline subtraction and entropy bonus
#             policy_loss = []
#             for log_prob, entropy, R in zip(log_probs, entropies, returns):
#                 advantage = R - baseline
#                 loss = -log_prob * advantage - self.entropy_coef * entropy
#                 policy_loss.append(loss)
            
#             self.optimizer.zero_grad()
#             total_loss = torch.stack(policy_loss).sum()
#             total_loss.backward()
            
#             # Apply gradient clipping to stabilize updates
#             torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.clip_norm)
#             self.optimizer.step()
            
#             all_episode_rewards.append(episode_reward)
            
#             # Update the EMA for logging
#             if ema_reward is None:
#                 ema_reward = episode_reward
#             else:
#                 ema_reward = smoothing_factor * episode_reward + (1 - smoothing_factor) * ema_reward
            
#             # Every 10 episodes, print both the raw average (last 10 episodes) and the EMA
#             if episode % 10 == 0:
#                 raw_avg = np.mean(all_episode_rewards[-10:])
#                 print(f"Episode {episode}, Raw Avg (last 10): {raw_avg:.1f}, EMA: {ema_reward:.1f}")
                
#         return all_episode_rewards



class REINFORCE:
    def __init__(self, env, learning_rate=0.001, gamma=0.99, entropy_coef=0.01, clip_norm=1.0):
        self.env = env
        self.state_dim = env.observation_space.shape[0]
        self.action_dim = env.action_space.n
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.policy_net = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.clip_norm = clip_norm

    def select_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        probs = self.policy_net(state_tensor)
        action_dist = torch.distributions.Categorical(probs)
        action = action_dist.sample()
        log_prob = action_dist.log_prob(action)
        entropy = action_dist.entropy()
        return action.item(), log_prob, entropy

    def calculate_returns(self, rewards):
        returns = []
        R = 0
        for r in reversed(rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        returns = torch.tensor(returns, dtype=torch.float32, device=self.device)
        returns = (returns - returns.mean()) / (returns.std() + 1e-9)
        return returns

    # def train(self, num_episodes=500):
    #     all_episode_rewards = []
    #     reward_window = deque(maxlen=10)  # For tracking last 10 rewards

    #     for episode in range(num_episodes):
    #         reset_result = self.env.reset()
    #         state = reset_result[0] if isinstance(reset_result, tuple) else reset_result

    #         log_probs = []
    #         entropies = []
    #         rewards = []
    #         episode_reward = 0
    #         done = False

    #         while not done:
    #             action, log_prob, entropy = self.select_action(state)
    #             step_result = self.env.step(action)
    #             if len(step_result) == 5:
    #                 next_state, reward, terminated, truncated, _ = step_result
    #                 done = terminated or truncated
    #             else:
    #                 next_state, reward, done, _ = step_result

    #             log_probs.append(log_prob)
    #             entropies.append(entropy)
    #             rewards.append(reward)
    #             episode_reward += reward
    #             state = next_state

    #         returns = self.calculate_returns(rewards)
    #         baseline = returns.mean()

    #         policy_loss = []
    #         for log_prob, entropy, R in zip(log_probs, entropies, returns):
    #             advantage = R - baseline
    #             loss = -log_prob * advantage - self.entropy_coef * entropy
    #             policy_loss.append(loss)

    #         self.optimizer.zero_grad()
    #         total_loss = torch.stack(policy_loss).sum()
    #         total_loss.backward()
    #         torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.clip_norm)
    #         self.optimizer.step()

    #         all_episode_rewards.append(episode_reward)
    #         reward_window.append(episode_reward)
    #         sma_reward = np.mean(reward_window)

    #         # ✅ Only print every 10 episodes
    #         if episode % 10 == 0:
    #             print(f"Episode {episode}, Reward: {episode_reward:.1f}, SMA (last 10): {sma_reward:.1f}")

    #     return all_episode_rewards
    def train(self, num_episodes=500, sma_window=3):
        all_episode_rewards = []
        step_avg_rewards = []

        for episode in range(num_episodes):
            reset_result = self.env.reset()
            state = reset_result[0] if isinstance(reset_result, tuple) else reset_result

            log_probs = []
            entropies = []
            rewards = []
            episode_reward = 0
            done = False

            while not done:
                action, log_prob, entropy = self.select_action(state)
                step_result = self.env.step(action)
                if len(step_result) == 5:
                    next_state, reward, terminated, truncated, _ = step_result
                    done = terminated or truncated
                else:
                    next_state, reward, done, _ = step_result

                log_probs.append(log_prob)
                entropies.append(entropy)
                rewards.append(reward)
                episode_reward += reward
                state = next_state

            returns = self.calculate_returns(rewards)
            baseline = returns.mean()

            policy_loss = []
            for log_prob, entropy, R in zip(log_probs, entropies, returns):
                advantage = R - baseline
                loss = -log_prob * advantage - self.entropy_coef * entropy
                policy_loss.append(loss)

            self.optimizer.zero_grad()
            total_loss = torch.stack(policy_loss).sum()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.clip_norm)
            self.optimizer.step()

            all_episode_rewards.append(episode_reward)

            # ✅ Every 10 episodes: compute avg and inline smoothed value
            if (episode + 1) % 10 == 0:
                step_avg = np.mean(all_episode_rewards[-10:])
                step_avg_rewards.append(step_avg)

                if len(step_avg_rewards) >= sma_window:
                    weights = np.ones(sma_window) / sma_window
                    smoothed_value = np.convolve(step_avg_rewards, weights, mode='valid')[-1]
                else:
                    smoothed_value = step_avg  # Not enough for smoothing yet

                print(f"Episode {episode + 1}, Avg over last 10: {step_avg:.1f}, Smoothed: {smoothed_value:.1f}")

        # ✅ Final smoothing over full list (optional)
        if len(step_avg_rewards) >= sma_window:
            weights = np.ones(sma_window) / sma_window
            smoothed_all = np.convolve(step_avg_rewards, weights, mode='valid')
        else:
            smoothed_all = step_avg_rewards

        return smoothed_all