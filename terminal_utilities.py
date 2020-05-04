
import os
import sys
import platform

from ansi_codes import *

class CursorOff(object):
    def __enter__(self):
        os.system('tput civis')
    def __exit__(self, *args):
        os.system('tput cnorm')

try:
    import tty, termios
except ImportError:
    message = 'Probably not Linux/Mac'

def linux_get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class GetChar():
    def __init__(self):
        platform_name = platform.system()
        if platform_name not in ['Linux','Darwin','Windows']:
            print('portable_get_char: Error: OS not detected or not supported.')
            exit()

        if platform_name in ['Linux', 'Darwin']:
            self.get_char = linux_get_char

        elif platform_name == 'Windows':
            self.get_char = msvcrt.getch
