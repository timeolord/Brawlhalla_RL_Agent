import time
import cv2
import mss
import numpy
import win32gui
import win32con


class GameCapture:
    def __init__(self, game_name, pos_x, pos_y, width, height, res_div):
        self.resolution = (pos_x + width, pos_y + height)
        self.output_resolution = (int(width / res_div), int(height / res_div))
        # Find game HWND
        self.game_hwnd = win32gui.FindWindow(None, game_name)

        if self.game_hwnd == 0:
            raise NameError("Error: game window not found")

        # Initializes mss
        self.sct = mss.mss()

        # Accounts for the shadows in SetWindowPos so the actual captured screen size is the correct resolution
        width += 16
        height += 40

        # Sets the game to the chosen resolution
        win32gui.SetWindowPos(self.game_hwnd, win32con.HWND_TOPMOST, pos_x, pos_y, width, height,
                              win32con.SWP_SHOWWINDOW)
        win32gui.SetActiveWindow(self.game_hwnd)
        win32gui.SetForegroundWindow(self.game_hwnd)

        # Gets the size of the game for display capture
        self.game_size = (pos_x + 8, pos_y + 32, width - 8, height - 8)
        # The offsets are to account for the shadows and upper bar.
        # These are done by eye, but they should be roughly accurate

    def testCapture(self):
        while "Screen capturing":
            last_time = time.time()

            # Get raw pixels from the screen, save it to a Numpy array
            # noinspection PyTypeChecker
            img = numpy.array(self.sct.grab(self.game_size))

            # Convert to grayscale
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            # Downscale
            img = cv2.resize(img, self.output_resolution)

            img = numpy.swapaxes(img, 0, 1)
            img = numpy.expand_dims(img, 2)

            # Display the picture
            cv2.imshow("OpenCV/Numpy normal", img)

            # FPS counter
            try:
                print("fps: {}".format(1 / (time.time() - last_time)))
            except ZeroDivisionError:
                print("")

            # Press "q" to quit
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

    def capture(self):
        # Get raw pixels from the screen, save it to a Numpy array
        # noinspection PyTypeChecker
        img = numpy.array(self.sct.grab(self.game_size))

        # Convert to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Downscale
        img = cv2.resize(img, self.output_resolution)

        img = numpy.swapaxes(img, 0, 1)
        img = numpy.expand_dims(img, 2)

        """
                while True:
            # Display the picture
            cv2.imshow("OpenCV/Numpy normal", img)
            
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
        """

        return img

    def captureBox(self, x1, y1, x2, y2):
        width = x2 - x1
        height = y2 - y1
        # noinspection PyTypeChecker
        img = numpy.array(self.sct.grab({"left": x1, "top": y1, "width": width, "height": height}))

        return img

