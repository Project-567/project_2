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

# define a function that chooses action based on epsilon-greedy
def choose_action(state, epsilon):
    
    # choose an action type: explore or exploit
    action_type = int(np.random.choice(2, 1, p=[epsilon,1-epsilon]))

    # find best action based on Q values
    best_action_index = np.argmax(Q_values[state])

    # pick a random action
    random_action_index = random.choice(range(4))

    # choose an action based on exploit or explore
    if action_type == 0:
        # explore
        # while random action is the same as the best action, pick a new action
        while random_action_index == best_action_index:
            random_action_index = random.choice(range(4))
        action_index = random_action_index
    else:
        # exploit
        # print("exploit")
        action_index = best_action_index
    
    # if Q_values is all zero, randomly pick an action
    if np.count_nonzero(Q_values[state]) == 0:
        action_index = random.randint(0,3)
        
    return action_index

# define average function
def Average(lst): 
    return sum(lst) / len(lst) 

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

# create a grid object
grid = Gridworld(5)

# initialize other parameters
gamma = 0.99
lr = 0.1
epsilon = [0.01, 0.1, 0.25]
runs = 20
episode_length = 500
window_length = int(episode_length/20)


for eps in epsilon:
    average_test_reward_list = []
    Q_values_list = []

    for run in range(1, runs+1):

        # initialize q values for all state action pairs
        Q_values = np.zeros((state_count, action_count))

        # define lists for plots
        average_reward_list = []
        cumulative_reward_list = []
        cumulative_reward = 0
        delta_list = []
        episode_test_reward_list =[]

        # iterate over episodes
        for episode in range(episode_length):
            
            reward_list = []
            delta = 0
            
            # initialize state (output: [4, 4])
            state_vector = grid.initial_state()
            state_index = grid.states.index(state_vector)

            # choose an action based on epsilon-greedy (output: action index ie. 0)
            action_index = choose_action(state_index, eps)
            action_vector = actions[action_index]

            # iterate over 200 steps within each episode
            for step in range(200):

                # get the next state and reward after taking the chosen action in the current state
                next_state_vector, reward = grid.transition_reward(state_vector, action_vector)
                next_state_index = grid.states.index(list(next_state_vector))
                
                # add reward to list
                reward_list.append(reward)
                
                # choose an action based on epsilon-greedy (output: action index ie. 0)
                next_action_index = choose_action(next_state_index, eps)
                next_action_vector = actions[next_action_index]

                # calculate max delta change for plotting max q value change
                Q_value = Q_values[state_index][action_index] + lr*(reward + gamma*Q_values[next_state_index][next_action_index] - Q_values[state_index][action_index])
                delta = max(delta, np.abs(Q_value - Q_values[state_index][action_index]))   
                
                # update Q value
                Q_values[state_index][action_index] = Q_values[state_index][action_index] + lr*(reward + gamma*Q_values[next_state_index][next_action_index] - Q_values[state_index][action_index])
                
                # update state and action vector
                state_vector = list(next_state_vector)
                state_index = grid.states.index(state_vector)
                action_vector = list(next_action_vector)
                action_index = next_action_index
            
            delta_list.append(delta)
            
            average_reward_list.append(Average(reward_list))
            
            # cumulative rewards
            cumulative_reward = cumulative_reward + sum(reward_list)
            cumulative_reward_list.append(cumulative_reward)
            
            # initialize q values for all state action pairs
            policy = np.zeros((state_count, action_count))
            
            # Generate Greedy policy based on Q_values after each episode
            for state in range(len(Q_values)):
                # find the best action at each state
                best_action = np.argmax(Q_values[state])
                # write deterministic policy based on Q_values
                policy[state][best_action] = 1
            
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

        # test reward of each episode, where delta is the change in Q values
        plt.plot(episode_test_reward_list)
        plt.title('Testing: Sarsa Reward after Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        # plot moving average
        delta_frame = pd.DataFrame(episode_test_reward_list)
        rolling_mean = delta_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/Sarsa/test_reward/test_reward_run_' + str(int(run)) + '_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # max delta of each episode, where delta is the change in Q values
        plt.plot(delta_list)
        plt.title('Training: Sarsa Max Delta for Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Max Delta')
        # plot moving average
        delta_frame = pd.DataFrame(delta_list)
        rolling_mean = delta_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/Sarsa/delta/delta_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # average reward per episode
        plt.plot(average_reward_list)
        plt.title('Training: Sarsa Avg. Reward for Run: ' + str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Average Reward')
        # plot moving average
        reward_frame = pd.DataFrame(average_reward_list)
        rolling_mean = reward_frame.rolling(window=window_length).mean()
        plt.plot(rolling_mean, label='Moving Average', color='orange')
        plt.savefig('Graphs/Sarsa/average_reward/avg_reward_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

        # cumulative reward per episode
        plt.plot(cumulative_reward_list)
        plt.title('Training: Sarsa Cumulative Reward for Run: '+ str(int(run)) + ', Epsilon: ' + str(float(eps)))
        plt.xlabel('Episode')
        plt.ylabel('Cumulative Reward')
        plt.savefig('Graphs/Sarsa/cumulative_reward/cumulative_reward_run_'+str(int(run))+'_epsilon_' + str(float(eps)) + '.png')
        plt.clf()
        time.sleep(0.1)

    # test reward of each episode, where delta is the change in Q values
    plt.plot(average_test_reward_list)
    plt.title('Testing: Sarsa Avg. Reward, Epsilon: ' + str(float(eps)))
    plt.xlabel('Run')
    plt.ylabel('Reward')
    plt.xticks(np.arange(0, runs, step=1))
    plt.savefig('Graphs/Sarsa/average_test_rewards/avg_test_reward_epsilon_' + str(float(eps)) + '.png')
    plt.clf()
    time.sleep(0.1)

    # save Q value tables to a pickle
    with open('Graphs/Sarsa/Qvalues/Sarsa_Qvalues_' + str(eps) + '.pkl', 'wb') as f:
        pickle.dump(Q_values_list, f)