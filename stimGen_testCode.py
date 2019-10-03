#PsychoPy
from psychopy import visual

import numpy as np

global win

def get_stimulus_array(firstIntensity):

    #original stimulus definition
    stimulus = visual.Circle(
    units = 'pix',
    win = win,
    radius = 2,
    fillColor = [1,1,1],
    lineColor = [1,1,1],
    contrast = firstIntensity,
    edges = 100,
    )

    frames = int(round(0.0501/0.0167))

    stimulus.draw()

    theStimFrame = visual.BufferImageStim(win,buffer='back',stim=[stimulus])
    w = int(theStimFrame.size[0])
    h = int(theStimFrame.size[1])


    stimArray = np.zeros((w,h))

    for frame in range(frames):
        #draw the frame to the back buffer
        stimulus.draw()
        #save to the next frame in the array
        theStimFrame = visual.BufferImageStim(win,buffer='back',stim=[stimulus])
        theStimFrameArray = np.array(theStimFrame.image)
        stimArray = np.vstack((stimArray,theStimFrameArray))

        x = 1
        y = 1
        stimulus.pos = (x,y)

    return stimArray

bgnd = 0

win = visual.Window(
    size=[5,5],
    units="pix",
    fullscr=False,
    color=[bgnd, bgnd, bgnd],
    allowStencil=True,
    winType = 'pyglet',
    screen = 0
)

win.flip()

stimArray = get_stimulus_array(100)
