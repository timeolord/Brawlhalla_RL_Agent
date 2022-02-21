import time
import cv2
import numpy
import numpy as np
import pytesseract
from gym import spaces
import GameCapture
import gym
import pydirectinput


class BrawlhallaEnv(gym.Env):
    def __init__(self):
        self.resolution = (848, 480)
        
        self.gc = GameCapture.GameCapture("Brawlhalla", 0, 0, *self.resolution)
        self.number_actions = 8
        self.action_space = spaces.Discrete(self.number_actions)
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.resolution[1], self.resolution[0]),
                                            dtype=np.uint8)

        # From main menu to custom lobby
        pydirectinput.click(*(176, 362))
        pydirectinput.click(*(172, 362))
        # Remove third bot
        time.sleep(0.1)
        pydirectinput.click(*(65, 171))
        pydirectinput.click(*(54, 183))
        time.sleep(0.05)
        # Remove fourth bot
        pydirectinput.click(*(65, 171))
        pydirectinput.click(*(54, 183))

    def reset(self):
        print("Resetting")
        # Select Char
        pydirectinput.click(*(160, 106), clicks=2, interval=0.1)
        time.sleep(1)
        pydirectinput.click(*(160, 106), clicks=2, interval=0.1)
        # Start Game
        time.sleep(1)
        pydirectinput.press('c', presses=5, interval=0.1)
        # Wait for loading screen
        time.sleep(10)

        return self.gc.capture()

    def step(self, action):

        info = {}

        # Checks if done by checking the background
        if numpy.array_equal(self.gc.captureBox(100, 80, 101, 81), [[[34, 4, 0, 255]]]):
            done = True

            # Calculates the reward from the end screen

            # Reads higher player number
            higher_player_num = (self.readArea(320, 327, 347, 338, 100, 5)).lstrip()
            # Reads lower player number
            lower_player_num = (self.readArea(488, 364, 516, 374, 100, 5)).lstrip()
            if "Player 1" in lower_player_num:
                # Reads Damage Done by the lower player
                damage_done = self.readArea(545, 428, 570, 437, 190, 4)
                try:
                    damage_done = float(damage_done.replace("O", '0'))
                except ValueError:
                    damage_done = 0
                # Reads Damage Taken on the lower player
                damage_taken = self.readArea(545, 438, 570, 446, 190, 4)
                try:
                    damage_taken = float(damage_taken.replace("O", '0'))
                except ValueError:
                    damage_done = 0
            elif "Player 1" in higher_player_num:
                # Reverses the numbers if player 1 wins, since damage taken by the enemy is the same as damage done
                # by the player
                # Reads Damage Done by the lower playercv
                damage_taken = self.readArea(545, 428, 570, 437, 190, 4)
                try:
                    damage_taken = float(damage_taken.replace("O", '0'))
                except ValueError:
                    damage_taken = 0
                # Reads Damage Taken on the lower player
                damage_done = self.readArea(545, 438, 570, 446, 190, 4)
                try:
                    damage_done = float(damage_done.replace("O", '0'))
                except ValueError:
                    damage_done = 0
            else:
                damage_done = 0
                damage_taken = 0
                print("OCR error on the end screen")

            # Discounts the damage taken by half, to avoid extremely negative values and divides by 100 to keep
            # values around 1 and -1
            reward = (damage_done/100) + 0.01
            print(reward)

            time.sleep(1)
            # Leaves the end screen
            pydirectinput.click(*(160, 106))
            pydirectinput.press('c', presses=5, interval=0.1)
            # Lets the game go back to character select
            time.sleep(1)
        else:
            done = False
            reward = 0
            if action == 0:
                pydirectinput.press('up')
            elif action == 1:
                pydirectinput.press('down')
            elif action == 2:
                pydirectinput.press('left')
            elif action == 3:
                pydirectinput.press('right')
            elif action == 4:
                pydirectinput.press('z')
            elif action == 5:
                pydirectinput.press('x')
            elif action == 6:
                pydirectinput.press('c')
            elif action == 7:
                pydirectinput.press('v')

        time.sleep(0.1)

        return self.gc.capture(), reward, done, info

    def render(self, mode='console'):
        pass

    def close(self):
        pass

    def readArea(self, x1, y1, x2, y2, threshold, scale):
        # Captures the area
        words = self.gc.captureBox(x1, y1, x2, y2)
        # Scales the image
        width = int(words.shape[1] * scale)
        height = int(words.shape[0] * scale)
        words = cv2.resize(words, (width, height), interpolation=cv2.INTER_LINEAR)
        # Converts to gray scale
        words = cv2.cvtColor(words, cv2.COLOR_RGB2GRAY)
        # Applies thresholding
        _, words = cv2.threshold(words, threshold, 255, cv2.THRESH_BINARY)
        # Inverts the color
        words = cv2.bitwise_not(words)
        # Erodes the image
        words = cv2.erode(words, None, iterations=1)
        # Blurs the image
        words = cv2.GaussianBlur(words, (3, 3), 0)
        # Returns the tesseract output
        return pytesseract.image_to_string(words, config='--psm 7 -l eng')
