import torch
import torch.optim as optim
import numpy as np
from Models.networks import PolicyNetwork

class REINFORCE:
    def __init__(self, env, learning_rate = 0.0005, gamma = 0.99):
        self.env = env
        self.state_dim = env.observation_space.shape[0]
        self.action_dim = env.action_space.n
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Policy Network
        self.policy_net = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr = learning_rate)
        
        # Discount Factor
        self.gamma = gamma
        
    def select_action(self, state):
        # State to tensor and action probs
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        probs = self.policy_net(state)
        # Action Sample
        action_dist = torch.distributions.Categorical(probs)
        action = action_dist.sample()
        log_prob = action_dist.log_prob(action)
        return action.item(), log_prob
    
    #Monte Carlo estimation of Q-Values
    def calculate_returns(self, rewards):
        returns = []
        R = 0
        
        #Calculate returns from the end of episode to the beginning
        for r in rewards [::-1]:
            R = r + self.gamma * R
            returns.insert(0, R)
        returns = torch.tensor(returns).to(self.device)
        returns = (returns - returns.mean()) / (returns.std() + 1e-9)
        return returns
    
    def train(self, max_steps = 200000):
        all_episode_rewards = []
        total_steps = 0 
        
        while total_steps < max_steps:
            state , _ = self.env.reset()
            log_probs = []
            rewards = []
            episode_reward, done = 0, False
            
            
            while not done:
                if total_steps >= max_steps:
                    break
                
                #Collect trajectory (Monte Carlo Method of collecting the entireepisode before doing updates)
                action, log_prob = self.select_action(state)
                next_state, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                
                log_probs.append(log_prob)
                rewards.append(reward)
                episode_reward += reward
                state = next_state
                total_steps += 1
                
            if total_steps > max_steps:
                    break    
                
            #Calculate return
            returns = self.calculate_returns(rewards)
            # policy_loss = [-lp * R for lp, R in zip(log_probs, returns)]
            
            #Calculate loss and update policy (Monte Carlo returns [R] in the policy Update)
            policy_loss = []
            for log_prob, R in zip(log_probs, returns):
                policy_loss.append(-log_prob * R)   #Negative for gradient ascent
                
            self.optimizer.zero_grad()
            loss = torch.stack(policy_loss).sum()
            loss.backward()
            # policy_loss = torch.stack(policy_loss).sum()
            # policy_loss.backward()
            self.optimizer.step()
            
            all_episode_rewards.append(episode_reward)
            
            #Log Progress
            if len(all_episode_rewards) % 10 == 0:
                avg_reward = np.mean(all_episode_rewards[-10:])
                print(f"Steps: {total_steps}, Episode: {len(all_episode_rewards)}, Avg Reward: {avg_reward:.1f}")                
        return all_episode_rewards