#PsychoPy
from psychopy import visual
import PyQt5
import numpy as np

global win


win = visual.Window(
    size=[500,500],
    units="pix",
    fullscr=False,
    color=[0, 0, 0],
    allowStencil=True,
    winType = 'pyglet',
    screen = 0
)
