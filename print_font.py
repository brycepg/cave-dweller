import os

import pygame
import pygcurse

win = pygcurse.PygcurseWindow(60, 30, fullscreen=False)
win.font = pygame.font.Font(os.path.join('fonts', 'pdv.ttf'), 16)
while True:
    for i in range(1,256):
        win.putchar(chr(i), i%60, i//60, 'white', 'gray')
