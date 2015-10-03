import os
import time

import pygame
import pygcurse

win = pygcurse.PygcurseWindow(60, 30, fullscreen=False)
win.font = pygame.font.Font(os.path.join('fonts', 'dog_vga_437.ttf'), 16)
#win.font = pygame.font.Font(os.path.join('fonts', 'pdv.ttf'), 16)
while True:
    for i in range(1,3000):
        txt = chr(i).strip()
        if txt:
            print(txt, end=" ")
            win.putchars(str(i) + " " + txt + "\n", ((i//30)*5)%(30//5) , i%30)
        time.sleep(.1)
