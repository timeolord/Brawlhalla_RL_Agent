import pydirectinput
import win32api
import GameCapture
import time
import pytesseract
import cv2
import BrawlhallaGymEnv
import stable_baselines3
import datetime
import pickle
import GameCapture



#vresolution = (848, 480)
#res_div = 4
#gc = GameCapture.GameCapture("Brawlhalla", 0, 0, *resolution, res_div)
#gc.testCapture()
env = BrawlhallaGymEnv.BrawlhallaEnv()

# (1, "episode")
#policy_kwargs={"net_arch": [64, 64]}
#model = stable_baselines3.DQN("CnnPolicy", env, verbose=1, buffer_size=2 ** 15,
#                              learning_starts=2 ** 10, target_update_interval=2 ** 10, learning_rate=0.001,
#                              train_freq=20, exploration_initial_eps=1, exploration_final_eps=0.1,
#                              batch_size=2 ** 9, gradient_steps=1, exploration_fraction=0.5,
#                              policy_kwargs={"net_arch": [64, 64]})
#print(model.policy)c
model = stable_baselines3.DQN.load("Brawlhalla25-12-31.zip")
model.set_env(env)
model.load_replay_buffer("ReplayBuffer")
#model.exploration_fraction = 0.3

while True:
    model.learn(total_timesteps=int(2 ** 15), log_interval=1)
    name = "Brawlhalla" + datetime.datetime.now().strftime("%d-%H-%M")
    model.save_replay_buffer("ReplayBuffer")
    model.save(name)







