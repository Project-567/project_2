import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import uniform
import random
import time
from IPython.display import display, clear_output
from Gridworld import Gridworld
import pickle

actions = [[-1, 0], [0, 1], [1, 0], [0, -1]] #up, right, down, left = (clockwise from up) 
action_count = len(actions) # total number of actions
gridSize = 5 # create a square grid of gridSize by gridSize
state_count = gridSize*gridSize # total number of states

def generate_episode(steps):

    # set initial state
    state_vector = grid.initial_state()

    # initialize state (with iniitial state), action list and reward list
    state_list = [state_vector]
    action_list = []
    reward_list = []

    # generate an episode
    for i in range(steps):

        # pick an action based on categorical distribution in policy
        action_index = int(np.random.choice(action_count, 1, p=policy[grid.states.index(state_vector)])) 
        action_vector = actions[action_index] # convert the integer index (ie. 0) to action (ie. [-1, 0])

        # get new state and reward after taking action from current state
        new_state_vector, reward = grid.transition_reward(state_vector, action_vector)
        state_vector = list(new_state_vector)

        # save state, action chosen and reward to list
        state_list.append(state_vector)
        action_list.append(action_vector)
        reward_list.append(reward)
        
    return state_list, action_list, reward_list

# define average function
def Average(lst): 
    return sum(lst) / len(lst) 

# create a grid object
grid = Gridworld(5)

# intialize parameters
gamma = 0.99
epsilon = 0.1
epsilon = [0.01, 0.1, 0.25]
runs = 20
episode_length = 500
window_length = int(episode_length/20)
max_steps = 200

# define variables for keeping track of time steps
Terminal = max_steps
t_list=[]
for i in range(1,max_steps+1):
    t = Terminal - i
    t_list.append(t)

for eps in epsilon:

    # initiate lists for plotting
    average_test_reward_list = []
    Q_values_list = []

    for run in range(1, runs+1):

        # Initiate a random policy
        random_policy = np.random.randint(100, size=(state_count, action_count))
        random_policy = random_policy/random_policy.sum(axis=1)[:,None]
        policy = random_policy

        # initialize q values for all state action pairs
        Q_values = np.zeros((state_count, action_count))

        # Define lists for plots
        average_reward_list = []
        cumulative_reward_list = []
        cumulative_reward = 0
        delta_list = []
        episode_test_reward_list = []

        for episode in range(episode_length):
        
            # generate an episode of specified step count
            state_list, action_list, reward_list = generate_episode(max_steps)
            
            # calculate average reward of each episode
            average_reward_list.append(Average(reward_list))
            
            # obtain cumulative reward for plotting
            cumulative_reward = cumulative_reward + sum(reward_list)
            cumulative_reward_list.append(cumulative_reward)

            # intialize variables
            G = 0
            delta = 0
            
            # initiate returns and visited list to none
            returns_list = []
            visited_list = []

            # loop for each step of episode: T-1, T-2, T-3 ... 0 = 199, 198, 197 ... 0
            for t in t_list:

                # calculate G: starting with the last reward at index t (naturally accounts for pseudocode's "t-1")
                G = gamma*G + reward_list[t]
                
                # combine state action pair, for example, state = [0,0], action = [0,1], state_action_pair = [0,0,0,1]
                state_action_pair = []
                state_action_pair.extend(state_list[t])
                state_action_pair.extend(action_list[t])

                # check if state action pair have been visited before (if not: continue, else: move to the next time step)
                if state_action_pair not in visited_list:

                    # add state action pair to visited list
                    visited_list.append(state_action_pair)

                    # append G to returns
                    returns_list.append(G)

                    # find state and action index, for example, converting action [-1, 0] to 0, and same for state #
                    state_index = grid.states.index(state_list[t])
                    action_index = actions.index(action_list[t])

                    # calculate max delta change for plotting max q value change
                    delta = max(delta, np.abs(Average(returns_list) - Q_values[state_index][action_index]))      
                    
                    # write Q_values to the state-action pair
                    Q_values[state_index][action_index] = Average(returns_list)

                    # choose best action at given state
                    choose_action = np.argmax(Q_values[state_index])
                    
                    # if Q_values is all zero, randomly pick an action
                    if np.count_nonzero(Q_values[state_index]) == 0:
                        choose_action = random.randint(0,3)

                    # overwrite policy
                    for a in range(action_count): # for action in actions [0, 1, 2, 3]
                        if choose_action == a: # if the choose_action is the same as the current action
                            # policy[state_index][a] = 1 - eps 
                            policy[state_index][a] = 1 - eps + eps/action_count 
                        else: # if choose_action is not the same as the current action
                            # policy[state_index][a] = eps/3 
                            policy[state_index][a] = eps/action_count
            
            # append delta to list
            delta_list.append(delta)
            
            # TEST POLICY after each episode
            # Generate test trajectory with the greedy policy
            state_list, action_list, test_reward_list = generate_episode(200)
            
            # sum up all the rewards obtained during test trajectory and append to list
            episode_test_reward_list.append(sum(test_reward_list))
            
            # print current episode
            clear_output(wait=True)
            display('Epsilon: ' + str(eps) + ' Run: ' + str(run) + ' Episode: ' + str(episode))

        # get average test reward
        average_test_reward_list.append(Average(episode_test_reward_list))

        Q_values_list.append(Q_values)

        # test reward of each episode
        plt.plot(episode_test_reward_list)
        plt.title('Testing: Monte Carlo Reward after Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        # plot moving average
        delta_frame = pd.DataFrame(episode_test_reward_list)
        rolling_mean = delta_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/MonteCarlo/test_reward/test_reward_run_' + str(int(run)) + '_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # max delta of each episode, where delta is the change in Q values
        plt.plot(delta_list)
        plt.title('Training: Monte Carlo Max Delta for Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Max Delta')
        # plot moving average
        delta_frame = pd.DataFrame(delta_list)
        rolling_mean = delta_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/MonteCarlo/delta/delta_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # average reward per episode
        plt.plot(average_reward_list)
        plt.title('Training: Monte Carlo Avg. Reward for Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Average Reward')
        # plot moving average
        reward_frame = pd.DataFrame(average_reward_list)
        rolling_mean = reward_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/MonteCarlo/average_reward/avg_reward_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # cumulative reward per episode
        plt.plot(cumulative_reward_list)
        plt.title('Training: Monte Carlo Cumulative Reward for Run: '+ str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Cumulative Reward')
        plt.savefig('Graphs/MonteCarlo/cumulative_reward/cumulative_reward_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

    # test reward of each episode, where delta is the change in Q values
    plt.plot(average_test_reward_list)
    plt.title('Testing: Monte Carlo Avg. Reward, Epsilon: ' + str(float(eps)))
    plt.xlabel('Run')
    plt.ylabel('Reward')
    plt.xticks(np.arange(0, runs, step=1))
    plt.savefig('Graphs/MonteCarlo/average_test_rewards/avg_test_reward_epsilon_' + str(float(eps)) + '.png')
    plt.clf()
    time.sleep(0.1)

    # save Q value tables to a pickle
    with open('Graphs/MonteCarlo/Qvalues/MC_Qvalues_' + str(eps) + '.pkl', 'wb') as f:
        pickle.dump(Q_values_list, f)
