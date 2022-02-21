import pydirectinput
import win32api
import GameCapture
import time
import pytesseract
import cv2
import BrawlhallaGymEnv
import stable_baselines3

env = BrawlhallaGymEnv.BrawlhallaEnv()

model = stable_baselines3.DQN("MlpPolicy", env, verbose=1, buffer_size=50_000)

model.learn(total_timesteps=int(2e5))

model.save("Brawlhalla")





