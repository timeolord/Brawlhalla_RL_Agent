import time
import cv2
import numpy
import numpy as np
import pytesseract
from gym import spaces
import GameCapture
import gym
import pydirectinput
import threading

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def pressAndHold(key):
    pydirectinput.keyDown(key)
    pydirectinput.keyUp(key)


class BrawlhallaEnv(gym.Env):
    def __init__(self):
        # Starts a dummy thread for input control
        self.clicker = threading.Thread(target=pydirectinput.press, args=('',))
        self.clicker.start()

        self.resolution = (848, 480)
        self.res_div = 4
        self.model_resolution = (int(self.resolution[0] / self.res_div), int(self.resolution[1] / self.res_div))
        
        self.gc = GameCapture.GameCapture("Brawlhalla", 0, 0, *self.resolution, self.res_div)
        self.number_actions = 8
        self.action_space = spaces.Discrete(self.number_actions)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.model_resolution[0], self.model_resolution[1], 1),
                                            dtype=np.uint8)

        # Main Menu -> Offline Play
        pydirectinput.press('down')
        pydirectinput.press('down')
        pydirectinput.press('down')
        pydirectinput.press('down')
        pydirectinput.press('down')
        # Custom Game
        pydirectinput.press('enter')
        pydirectinput.press('enter')
        # Remove third bot
        pydirectinput.press('v')
        pydirectinput.press('enter')
        pydirectinput.press('enter')
        # Remove fourth bot
        pydirectinput.press('enter')
        pydirectinput.press('enter')
        pydirectinput.press('v')
        self.done_pixel = self.gc.captureBox(100, 80, 101, 81)

    def reset(self):
        # Start Game
        pydirectinput.press('enter', presses=10)
        # Wait for loading screen
        time.sleep(5)

        return self.gc.capture()

    def step(self, action):

        info = {}

        # Checks if done by checking the background
        if numpy.array_equal(self.gc.captureBox(100, 80, 101, 81), self.done_pixel):
            done = True

            # Calculates the reward from the end screen
            win = 0
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
                    damage_taken = 0
            elif "Player 1" in higher_player_num:
                # Reverses the numbers if player 1 wins, since damage taken by the enemy is the same as damage done
                # by the player
                # Reads Damage Done by the lower player
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
                win = 1
            else:
                damage_done = 0
                damage_taken = 0
                print("OCR error on the end screen")

            # Discounts the damage taken by half, to avoid extremely negative values and divides by 100 to keep
            # values around 1 and -1
            reward = (damage_done/100)
            reward += win
            # print(reward)

            # Leaves the end screen
            pydirectinput.press('c', presses=3, _pause=False)
        else:

            done = False
            # Encourages just being alive
            reward = 0.00001
            button = ''
            if action == 0:
                button = 'up'
            elif action == 1:
                button = 'down'
            elif action == 2:
                button = 'left'
            elif action == 3:
                button = 'right'
            elif action == 4:
                button = 'z'
            elif action == 5:
                button = 'x'
            elif action == 6:
                button = 'c'
            elif action == 7:
                button = 'v'

            if button != '':
                if button != 'left' and button != 'right':
                    self.clicker = threading.Thread(target=pydirectinput.press, args=(button,), name="t")
                else:
                    if self.clicker.name == "h":
                        self.clicker.join()
                    self.clicker = threading.Thread(target=pressAndHold, args=(button,), name="h")

            self.clicker.start()

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
