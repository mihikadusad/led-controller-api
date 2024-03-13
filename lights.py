# Vishal Nandakumar, Mihika Dusad, Sritan Motati, Samarth Bhargav, Daniel Qiu 6
""" LIGHT CONTROLLER API """

import socket
import time
from timeit import default_timer
import commands


class LightController:
    def __init__(self, lights_per_segment=300, num_segments=2048):
        """Initialize the connnection with the SP108E."""

        self.host_ip = "192.168.4.1"  # might need to change the last digit
        self.port = 8189
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host_ip, self.port))
        self.n = min(300, lights_per_segment)
        self.num_segments = min(2048 // self.n, num_segments)

        MIN_SLEEP = 0.1

        self.s.send(commands.sec_count(self.num_segments))
        time.sleep(MIN_SLEEP)

        self.s.send(commands.dot_count(self.n))
        time.sleep(MIN_SLEEP)

        self.s.send(commands.rgb_ordering(0))
        time.sleep(MIN_SLEEP)

        self.s.send(b'\x38\x00\x00\x00\x24\x83')
        self.s.recv(10)

        self.bytes = bytearray(self.n*3)
        for i in range(self.n*3):
            self.bytes[i] = 0

        self.send_colors()

    def set(self, i, r, g, b):
        """Set the ith light to a desired r g b value. You need to call send_colors to have the change reflect onto the lights."""

        self.bytes[3*i] = r
        self.bytes[3*i + 1] = g
        self.bytes[3*i + 2] = b

    def set_frame(self, colors):
        """Set the first len(colors) lights to desired colors. You need to call send_colors to have the change reflect onto the lights."""

        if (len(colors) > self.n):
            colors = colors[:self.n]

        for i, c in enumerate(colors):
            self.bytes[3*i] = c[0]
            self.bytes[3*i + 1] = c[1]
            self.bytes[3*i + 2] = c[2]

    def send_colors(self, colors=None, delay=0.0):
        """Send the lights information to the controllers."""

        start_time = default_timer()

        if colors is not None:
            self.set_frame(colors)

        self.s.send(self.bytes)
        res = self.s.recv(10)

        end_time = default_timer()
        tot_time = end_time - start_time

        time.sleep(max(0, delay - tot_time))

        return res

### EXAMPLE USAGE ###


if __name__ == "__main__":
    lc = LightController(250, 3)

    frame1 = [[255, 0, 0], [0, 255, 0]]*10
    frame2 = [[0, 255, 0], [0, 0, 255]]*10
    frame3 = [[0, 0, 255], [255, 0, 0]]*10

    while True:
        lc.set_frame(frame1)
        res = lc.send_colors()

        lc.set_frame(frame2)
        res = lc.send_colors()

        lc.set_frame(frame3)
        res = lc.send_colors()
