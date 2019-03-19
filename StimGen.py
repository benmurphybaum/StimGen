#StimGen python

#Must use python 2.7, not 3
#pygame, pyglet, and psychopy

#import widgets
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLineEdit,QGroupBox,QComboBox,QFrame
from PyQt5.QtWidgets import QLabel,QListWidget,QListWidgetItem,QSpacerItem,QVBoxLayout,QGridLayout,QCheckBox,QInputDialog,QListView
from PyQt5 import QtCore,QtGui

#timing libraries
from time import sleep

#for saving and loading stimuli from disk
import json
import os
import h5py

#for copying dictionaries
import copy

#PsychoPy
from psychopy import visual, clock, core

import math

#Motion Clouds
import MotionClouds as mc
import numpy as np

#Build the GUI
class App(QMainWindow):

    #startup code
    def __init__(self):
        global objectList, seqList, stim, seqAssign, seqDict

        super(App,self).__init__()

        self.title = "StimGen 5.0"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 780

        #fonts
        bold = QtGui.QFont("Helvetica", 12,weight=QtGui.QFont.Normal)
        boldLarge = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        #Initialize/Close Session Controls
        self.initSession = QPushButton('Initialize Session',self)
        self.closeSession = QPushButton('Close Session',self)
        self.initSession.move(100,110)
        self.initSession.setFont(bold)
        self.closeSession.move(250,110)
        self.closeSession.setFont(bold)
        self.initSession.clicked.connect(lambda: self.buttonProc("initSession"))
        self.closeSession.clicked.connect(lambda: self.buttonProc("closeSession"))

        #Design, Masks, Sequences Buttons
        self.designButton = QPushButton('Design',self)
        self.designButton.move(215,280)
        self.designButton.setFont(bold)
        self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');
        self.designButton.clicked.connect(lambda: self.buttonProc("designButton"))

        self.masksButton = QPushButton('Masks',self)
        self.masksButton.move(360,280)
        self.masksButton.setFont(bold)
        self.masksButton.clicked.connect(lambda: self.buttonProc("masksButton"))

        self.sequencesButton = QPushButton('Sequences',self)
        self.sequencesButton.move(505,280)
        self.sequencesButton.setFont(bold)
        self.sequencesButton.clicked.connect(lambda: self.buttonProc("sequencesButton"))

        self.runStimulus = QPushButton('Run',self)
        self.runStimulus.move(10,720)
        self.runStimulus.resize(75,30)
        self.runStimulus.setFont(boldLarge)
        self.runStimulus.setStyleSheet('QPushButton {background-color: rgba(150, 245, 150, 150)}')
        self.runStimulus.clicked.connect(lambda: self.buttonProc("runStimulus"))

        self.abortStimulus = QPushButton('Abort',self)
        self.abortStimulus.move(90,720)
        self.abortStimulus.resize(75,30)
        self.abortStimulus.setFont(boldLarge)
        self.abortStimulus.setStyleSheet('QPushButton {background-color: rgba(245, 150, 150, 150)}')
        self.abortStimulus.clicked.connect(lambda: self.buttonProc("abortStimulus"))

        self.sequenceMessage = QLabel('',self)
        self.sequenceMessage.move(175,720)
        self.sequenceMessage.resize(300,60)

        #Object List
        objectList = ['Circle']

        #Sequence list
        seqList = ['None']

        #Build Control Panels
        self.buildStimusBank()
        self.buildDesignPanel()
        self.buildMasksPanel()
        self.buildSequencePanel()
        self.buildPathPanel()
        self.buildGlobalsPanel()


        #Menus and Control settings
        self.setControlDict()
        self.setContextualMenus()
        self.flipControls('objectType','Circle')
        self.flipControls('motionType','Static')
        self.flipControls('modulationType','Static')
        self.setDefaults()

        #Make first stimulus and sequence assignment dictionaries
        stim = {}
        seqAssign = {} #holds sequence assignments for each control
        seqDict = {} #holds the actual sequence entries

        self.addStimDict()

        #get the stimulus files
        self.getStimulusBank()

        if self.stimBank.count() > 0:
            self.stimBank.setCurrentRow(0)
            self.loadStimulus()

        self.show()

        #globals
        global isOpen #stimulus window is closed
        isOpen = 0

    #Handles all variable entries
    def variableProc(self,controlName,entry):
        global stim, seqDict

        #Need to check each variable for validity
        if controlName == 'background':
            bgnd = self.getBackground()
            try:
                win.color= [bgnd,bgnd,bgnd]

                #Double flip, one to send new bgnd to buffer, then another to flip buffer to screen
                win.flip()
                win.flip()
            except:
                return
        elif controlName == 'seqEntry':
            item = self.seqListBox.currentItem()
            name = item.text()
            entry = self.seqEntry.text()
            seqDict[name] = entry.split(",") #list
        else:
            #all other variable controls
            #Assign variable entry to the stim dictionary for the selected object
            index = self.objectListBox.currentRow()
            if self.isFloat(entry):
                stim[index][controlName] = float(entry)   #some need to be float though
            else:
                stim[index][controlName] = int(entry)

    #Handles all button clicks
    def buttonProc(self,controlName):
        global isOpen,abortStatus

        if  controlName == 'designButton':
            self.designPanel.show()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');

            self.maskPanel.hide()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            self.sequencePanel.hide()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');
        elif controlName == 'masksButton':
            self.designPanel.hide()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            self.maskPanel.show()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');

            self.sequencePanel.hide()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');
        elif controlName == 'sequencesButton':
            self.designPanel.hide()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            self.maskPanel.hide()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            self.sequencePanel.show()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');
        elif controlName == 'initSession':
            #Open a stimulus window
            self.initializeSession()
        elif controlName == 'closeSession':
            #Close the stimulus window
            try:
                win.close()
                isOpen = 0 #window is open
            except NameError:
                return

        elif controlName == 'runStimulus':
            #Reset abort abortStatus
            abortStatus = 0

            #Run the stimulus
            self.runStim()

        elif controlName == 'abortStimulus':
            self.abortStim()

        elif controlName == 'addObject':
            self.addStimObject()

        elif controlName == 'removeObject':
            self.removeStimObject()

        elif controlName == 'addSeq':
            self.addSequence()

        elif controlName == 'removeSeq':
            self.removeSequence()

        elif controlName == 'saveStim':
            self.saveStimulus()
        elif controlName == 'deleteStim':
            self.deleteStimulus()
        else:
            #default
            print('other')

    #Handles all drop down menu selections
    def menuProc(self,controlName,selection):
        global objectList, stim, seqAssign

        #Set contextual menus
        self.flipControls(controlName,selection)

        #currently selected object
        index = self.objectListBox.currentRow()

        #Adjust list boxes items
        if controlName == 'objectType':
            objectList[index] = selection

            #edit the listbox item for objects and masks
            self.objectListBox.item(index).setText(selection)
            self.maskObjectListBox.item(index).setText(selection)

            #Assign objectType box entry to the stim dictionary for the selected object
            index = self.objectListBox.currentRow()
            stim[index][controlName] = selection

        elif controlName.find('Seq') != -1:
        #if it's a sequence menu
        #assign sequence name to the seq dictionary for that control

            #which object?
            object = self.objectListBox.currentRow()

            seqAssign[object][controlName]['sequence'] = selection
            if selection != 'None':
                seqAssign[object][controlName]['control'].setStyleSheet("background-color: rgba(150, 245, 150, 150)")
            else:
                seqAssign[object][controlName]['control'].setStyleSheet("background-color: white")
                seqAssign[object][controlName]['control'].setStyleSheet("color: black")

            #display assigned sequences to the GUI
            self.displaySeqAssignments(object)
        else:
            #add parameter to stim dictionary for all other drop down menus (motionType,coordinateType, etc...)
            stim[index][controlName] = selection

    #Handles all of the list box selections
    def listProc(self,controlName,index):
        if controlName == 'objectListBox':
            self.setObjectParameters(index)

            #display assigned sequences to the GUI
            self.displaySeqAssignments(index)

        elif controlName == 'seqListBox':
            name = seqList[index + 1]
            entry = (seqDict[name])
            entry = ','.join(entry)
            self.seqEntry.setText(entry)

        elif controlName == 'stimBank':
            self.loadStimulus()

    #adds a new sequence
    def addSequence(self):
        global seqList, seqDict
        #show input dialog for naming the sequence
        name, ok = QInputDialog.getText(self, 'Add Sequence',
            'Sequence Name:')

        #add to the sequence list
        seqList.append(name)
        size = len(seqList)

        #add empty sequence to the seqDict
        seqDict[name] = ''

        #reset the sequence entry variable
        self.seqEntry.setText('')

        #update the sequence list box
        self.seqListBox.addItem(name)
        self.seqListBox.setCurrentRow(size-2)#-2 bc seqList has extra 'None' item
        self.seqListBox.setSelectionMode(1)

        #update all of the sequence menus
        for key,_ in seqAssign[0].iteritems():
            control[key].addItem(name)

    #adds new object to the stimulus design
    def addStimObject(self):
        global objectList

        objectList.append('Circle')
        self.objectListBox.addItem('Circle')
        self.maskObjectListBox.addItem('Circle')
        self.addStimDict()

        numObjects = len(objectList)
        self.objectListBox.setCurrentRow(numObjects-1)
        self.setObjectParameters(numObjects-1)

    #removes the selected stimulus object
    def removeStimObject(self):
        global objectList

        if len(objectList) == 1: #doesn't delete last object
            return

        item = self.objectListBox.currentItem()
        index = self.objectListBox.currentRow()
        self.objectListBox.takeItem(self.objectListBox.row(item))

        item = self.maskObjectListBox.currentItem()
        self.maskObjectListBox.takeItem(self.maskObjectListBox.row(item))
        del objectList[index]

        #remove dictionary references to the object
        stim.pop(index,None)
        seqAssign.pop(index,None)

    #Deletes the selected sequence
    def removeSequence(self):
        global seqList, seqDict

        #prevent deleting 'None'
        if len(seqList) == 1:
            return

        #selected item and its index
        item = self.seqListBox.currentItem()
        index = self.seqListBox.currentRow()

        #delete sequence from the list box
        self.seqListBox.takeItem(self.seqListBox.row(item))

        #remove from seqList and seqDict
        del seqList[index]
        seqDict.pop(item.text())

        #update sequence assignment menus
        for object,_ in seqAssign.iteritems():
            for key,_ in seqAssign[object].iteritems():
                seqMenu = seqAssign[object][key]['control']
                seqMenu.removeItem(index + 1) #add one to avoid deleting 'None'

    #Uses stimulus dictionary to fill out the parameters in the GUI for the selected object
    def setObjectParameters(self,index):

        if index == -1:
            return

        for key,val in stim[index].iteritems():
            #handle by control type
            type = control[key].__class__.__name__
            if type == 'QLineEdit':
                control[key].setText(str(val))

            elif type == 'QComboBox':
                 #which index has the text
                items = [control[key].itemText(i) for i in range(control[key].count())]
                whichItem = items.index(val)
                control[key].setCurrentIndex(whichItem)

                #flip the controls depending on the drop down menu selection
                self.flipControls(key,val)

        #check sequence assignments
        for key,_ in seqAssign[index].iteritems():
            sequence = seqAssign[index][key]['sequence']
            if sequence == 'None':
                #set menu to none if there is no sequence assignment
                control[key].setCurrentIndex(0)
                control[key].setStyleSheet("background-color: white")
                control[key].setStyleSheet("color: black")
            else:
                #which item in sequence menu is it?
                whichItem = seqList.index(sequence)
                control[key].setCurrentIndex(whichItem+1)
                control[key].setStyleSheet("background-color: rgba(150, 245, 150, 150)")

    #Finds sequence assignments, and displays what they are at the bottom of the GUI
    def displaySeqAssignments(self,objectNum):
        seqDisplay = []

        for key,_ in seqAssign[objectNum].iteritems():
            sequence = seqAssign[objectNum][key]['sequence']
            if sequence != 'None':
                seqDisplay.append('[' + str(objectNum) + '] ' + seqAssign[objectNum][key]['parent'] + ': ')
                seqDisplay.append(','.join(seqDict[sequence]) + '\n')

        #convert list to string
        seqDisplay = ''.join(seqDisplay)
        #display on GUI
        self.sequenceMessage.setText(seqDisplay)

    #Changes controls based on object Type
    def flipControls(self,controlName,selection):

        if selection == 'Circle':
            for key,value in circleSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Rectangle':
            self.designPanelLayout.addWidget(self.orientationLabel,9,0)
            self.designPanelLayout.addWidget(self.orientation,9,1)
            self.designPanelLayout.addWidget(self.orientationSeq,9,2)

            for key,value in rectangleSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Grating':
            self.designPanelLayout.addWidget(self.orientationLabel,10,0)
            self.designPanelLayout.addWidget(self.orientation,10,1)
            self.designPanelLayout.addWidget(self.orientationSeq,10,2)
            for key,value in gratingSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Static' and controlName == 'motionType':
            #self.designPanelLayout.addWidget(self.blank5,7,8,4,1)
            for key,value in staticMotionSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Drift' and controlName == 'motionType':
            #self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
            for key,value in driftMotionSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Static' and controlName == 'modulationType':
            for key,value in staticModSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection != 'Static' and controlName == 'modulationType':
            for key,value in dynamicModSettings.iteritems():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

    #Converts 0-255 range to -1 to 1 range
    def getBackground(self):
        if len(self.background.text()) > 0:
            val = float(self.background.text())
            bgnd = (2 * val/255) - 1 #normalize from -1 to 1
            return bgnd
        else:
            return

    #Open a stimulus window
    def initializeSession(self):
        global win,isOpen,ifi

        bgnd = self.getBackground()

        win = visual.Window(
            #size=[500, 500],
            units="pix",
            fullscr=True,
            color=[bgnd, bgnd, bgnd],
            screen = 0,
            monitor = None
        )

        #Frame rate
        ifi = 1/win.getActualFrameRate(10,100)

        isOpen = 1 #window is open

    #Fills out the stimulus parameters into a structure
    def runStim(self):

        #stim dictionary holds the parameters for all the objects
        numObjects = len(stim)

        #global parameters
        ppm = float(self.ppm.text())
        xOffset = int(self.xOffset.text())
        yOffset = int(self.yOffset.text())
        trialTime = float(self.trialTime.text())
        repeats = int(self.repeats.text())
        bgnd = self.getBackground()

        #runTime dictionary is created here, and will hold parameters
        #calculated at run time for each object
        runTime = {}
        #Timer dictionaries
        timer = {}

        for i in range(numObjects):
            runTime[i] = {
            'delayFrames':0,
            'frames':0,
            'startX':0,
            'startY':0,
            'halfCycle':0,
            'cycleCount':0,
            'firstIntensity':0,
            'secondIntensity':0,
            'stimulus':0,
            'stimFrame':0
            }

            timer[i] = 0

        #start at 0 sweeps
        numSweeps = 0

        #check for sequence assignments to get the total number of sweeps
        for i in range(numObjects):
            for key,_ in seqAssign[i].iteritems():
                sequence = seqAssign[i][key]['sequence']
                if sequence != 'None':
                    #extract sequence entry
                    entry = seqDict[sequence]

                    #size of entry
                    size = len(entry)
                    if size > numSweeps:
                        numSweeps = size
            #frame delay for each objectType
            runTime[i]['delayFrames'] = int(round(stim[i]['delay']/ifi)) #round to nearest integer

            #frame duration for each object
            runTime[i]['frames'] = int(round(stim[i]['duration']/ifi)) #round to nearest integer

        #What is the total duration of the stimulus, including delays?
        durList = []
        durList = [runTime[i]['delayFrames'] + runTime[i]['frames'] for i in range(numObjects)]
        totalDuration = max(durList)

        #if no sequences are assigned or they are all empty, set sweeps to 1
        if numSweeps == 0:
            numSweeps = 1

####### STIMULUS LOOP
        #try:
        #Loop through repeats
        for repeat in range(repeats): #use repeat setting for first object

            #loop through sweeps from sequence assignments
            for sweep in range(numSweeps):
                #check for abort click
                if abortStatus:
                    return

                #reset frame counts
                frameCount = 0

                #check for sequence assignments
                for i,_ in seqAssign.iteritems():
                    for key,_ in seqAssign[i].iteritems():
                        sequence = seqAssign[i][key]['sequence']
                        if sequence != 'None':
                            #extract sequence entry
                            entry = seqDict[sequence]
                            #parent control name
                            parent = seqAssign[i][key]['parent']
                            #insert sequence variable into the stim dictionary for each sweep
                            stim[i][parent] = float(entry[sweep])

                    #Set runTime dictionary for each sweeps
                    #piggy backs off the seqAssign loop, which also iterates through the objects

                    #frame delay for each objectType
                    runTime[i]['delayFrames'] = int(round(stim[i]['delay']/ifi)) #round to nearest integer

                    #frame duration for each object
                    runTime[i]['frames'] = int(round(stim[i]['duration']/ifi)) #round to nearest integer

                    #starting positions of each object
                    runTime[i]['startX'] = ppm * (xOffset + stim[i]['xPos']) + ppm * stim[i]['startRad'] * math.cos(stim[i]['angle'] * math.pi/180)
                    runTime[i]['startY'] = ppm * (yOffset + stim[i]['yPos']) + ppm * stim[i]['startRad'] * math.sin(stim[i]['angle'] * math.pi/180)

                    #Modulation parameters
                    if stim[i]['modulationType'] != 'Static':
                        runTime[i]['halfCycle'] = int(round((0.5/stim[i]['modulationFreq'])/ifi)) #in number of frames
                        runTime[i]['cycleCount'] = 1

                    #intensities
                    firstIntensity,secondIntensity = self.getIntensity(i)
                    runTime[i]['firstIntensity'] = firstIntensity
                    runTime[i]['secondIntensity'] = secondIntensity

                    #Define stimulus
                    runTime[i]['stimulus'] = self.defineStimulus(runTime,ppm,xOffset,yOffset,i)

                    #reset stimulus frame counts
                    runTime[i]['stimFrame'] = 0
                    #reset cycle counts
                    runTime[i]['cycleCount'] = 0

                #overall timer that is started before delay
                totalTimer = 0
                totalTimer = core.Clock()

                #loop through total stimulus duration
                for frame in range(totalDuration):

                    #Loop through each object
                    for i in range(numObjects):

                        #extract stimulus intensity so you only do it once per object
                        firstIntensity = runTime[i]['firstIntensity']
                        secondIntensity = runTime[i]['secondIntensity']

                        #delay
                        if frameCount < runTime[i]['delayFrames']:
                            continue

                        #start timer only on first frame of the stimulus
                        if runTime[i]['stimFrame'] == 0:
                            timer[i] = 0
                            timer[i] = core.Clock()

                        #check for abort click
                        if abortStatus:
                            win.flip()
                            return

                        #Draw each stimulus object to the buffer window

                        #MOTION CLOUD STIMULI
                        if stim[i]['objectType'] == 'Cloud':
                            #get the motion cloud frame
                            stimulus = visual.ImageStim(
                                win=win,
                                units = 'pix',
                                image = motionCloud[:,:,frame],
                                size = (500,500),
                                ori = stim[i]['orientation'],
                                pos = ((xOffset + stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
                                )

                            runTime[i]['stimulus'] = stimulus
                        else:
                            #NON-MOTION CLOUD STIMULI

                            #Update position for moving stimuli
                            if stim[i]['motionType'] == 'Drift':
                                if stim[i]['objectType'] == 'Grating':
                                    disp('Need grating drift frequency control')
                                else:
                                    x = runTime[i]['startX'] + ppm * stim[i]['speed'] * timer[i].getTime() * math.cos(stim[i]['angle'] * math.pi/180)
                                    y = runTime[i]['startY'] + ppm * stim[i]['speed'] * timer[i].getTime() * math.sin(stim[i]['angle'] * math.pi/180)
                                    runTime[i]['stimulus'].pos = (x,y)

                            #Update intensity for modulated stimuli
                            if stim[i]['modulationType'] == 'Square':
                                #Flip the intensities between light/dark at each cycle
                                if runTime[i]['stimFrame'] == runTime[i]['halfCycle'] * runTime[i]['cycleCount']:
                                    if (runTime[i]['cycleCount'] % 2) == 0:
                                        if stim[i]['objectType'] == 'Grating':
                                            runTime[i]['stimulus'].contrast = firstIntensity
                                        else:
                                            #non-grating stimuli
                                            runTime[i]['stimulus'].fillColor = [firstIntensity,firstIntensity,firstIntensity]
                                            runTime[i]['stimulus'].lineColor = [firstIntensity,firstIntensity,firstIntensity]
                                    else:
                                        if stim[i]['objectType'] == 'Grating':
                                            runTime[i]['stimulus'].contrast = secondIntensity
                                        else:
                                            #non-grating stimuli
                                            runTime[i]['stimulus'].fillColor = [secondIntensity,secondIntensity,secondIntensity]
                                            runTime[i]['stimulus'].lineColor = [secondIntensity,secondIntensity,secondIntensity]

                                    runTime[i]['cycleCount'] = runTime[i]['cycleCount'] + 1 #counts which modulation cycle it's on

                            elif stim[i]['modulationType'] == 'Sine':
                                #out of bounds intensities
                                if firstIntensity - bgnd > 1:
                                    firstIntensity = bgnd + 1
                                elif firstIntensity - bgnd < -1:
                                    firstIntensity = bgnd - 1

                                if stim[i]['objectType'] != 'Grating':
                                    intensity = (firstIntensity - bgnd) * math.sin(2 * math.pi * stim[i]['modulationFreq'] * timer[i].getTime())
                                    runTime[i]['stimulus'].fillColor = [intensity,intensity,intensity]
                                    runTime[i]['stimulus'].lineColor = [intensity,intensity,intensity]
                                else:
                                    runTime[i]['stimulus'].contrast = (stim[i]['contrast']/100.0) * math.sin(2 * math.pi * stim[i]['modulationFreq'] * timer[i].getTime())

                        runTime[i]['stimulus'].draw() #draws every frame

                        #increase stimFrame count if the code has reached here
                        runTime[i]['stimFrame'] = runTime[i]['stimFrame'] + 1

                    #Flip the window every loop no matter what
                    win.flip()

                    frameCount = frameCount + 1

                #Wait for trial time to expire before starting next sweep
                while totalTimer.getTime() < trialTime:
                    win.flip()

###############

            #Flip the window to background again
            win.flip()
            win.flip()

        #except:
        #    print('exception')
        #    return
        #for object in objectList:
        #    if stim[object]['objectType'] == 'Cloud':
        #        self.saveCloud(motionCloud)

    #Defines the stimulus textures
    def defineStimulus(self,runTime,ppm,xOffset,yOffset,i):
        global motionCloud

        firstIntensity = runTime[i]['firstIntensity']
        secondIntensity = runTime[i]['secondIntensity']

        if stim[i]['objectType'] == 'Circle':
            stimulus = visual.Circle(
            win = win,
            units = 'pix',
            radius = stim[i]['diameter']*ppm/2,
            fillColor = [firstIntensity,firstIntensity,firstIntensity],
            lineColor = [firstIntensity,firstIntensity,firstIntensity],
            edges = 100,
            pos = ((xOffset + stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
            )

        elif stim[i]['objectType'] == 'Rectangle':
            stimulus = visual.Rect(
            win = win,
            units = 'pix',
            width = stim[i]['width'] * ppm,
            height = stim[i]['length'] * ppm,
            ori = stim[i]['orientation'],
            fillColor = [firstIntensity,firstIntensity,firstIntensity],
            lineColor = [firstIntensity,firstIntensity,firstIntensity],
            pos = ((xOffset+ stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
            )
        elif stim[i]['objectType'] == 'Grating':
            stimulus = visual.GratingStim(
            win = win,
            units = 'pix',
            size = (2048,2048),
            tex = 'sin',
            texRes = 1024,
            sf = stim[i]['spatialFreq'] / (ppm * 1000),
            ori = stim[i]['orientation'],
            #need to calculate the phase such that grating is centered around middle point of monitor
            phase = stim[i]['spatialPhase'] * np.pi/180,
            color = [1,1,1],
            contrast = stim[i]['contrast']/100.0,
            pos = ((xOffset + stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
            )
            print(stim[i]['spatialPhase'])
        elif stim[i]['objectType'] == 'Cloud':

            # define Fourier domain
            fx, fy, ft = mc.get_grids(mc.N_X, mc.N_Y, mc.N_frame)
            # define an envelope
            envelope = mc.envelope_gabor(fx, fy, ft,
            V_X=1., V_Y=1., B_V=.1,
            sf_0=.05, B_sf=.05,
            theta=np.pi/3, B_theta=np.pi/8, alpha=1.)

            motionCloud = mc.random_cloud(envelope)
            motionCloud = self.rectif_stimGen(motionCloud,contrast=1,method='Michelson',verbose=False)
            #doesn't return the stimulus, but sets the array as a global
            return
        else:
            print('other')

        return stimulus

    #alternative rectifier that goes -1 to 1 instead of MotionCloud's 0 to 1
    def rectif_stimGen(self,z_in, contrast, method, verbose):
        """
        Transforms an image (can be 1, 2 or 3D) with normal histogram into
        a 0.5 centered image of determined contrast
        method is either 'Michelson' or 'Energy'

        Phase randomization takes any image and turns it into Gaussian-distributed
        noise of the same power (or, equivalently, variance).
        # See: Peter J. Bex J. Opt. Soc. Am. A/Vol. 19, No. 6/June 2002 Spatial
        frequency, phase, and the contrast of natural images
        """
        z = z_in.copy()
        # Final rectification
        if verbose:
            print('Before Rectification of the frames')
            print( 'Mean=', np.mean(z[:]), ', std=', np.std(z[:]), ', Min=', np.min(z[:]), ', Max=', np.max(z[:]), ' Abs(Max)=', np.max(np.abs(z[:])))

        z -= np.mean(z[:]) # this should be true *on average* in MotionClouds

        if (method == 'Michelson'):
            z = (1.* z/np.max(np.abs(z[:]))* contrast)
        else:
            z = (1.* z/np.std(z[:])  * contrast)

        if verbose:
            print('After Rectification of the frames')
            print('Mean=', np.mean(z[:]), ', std=', np.std(z[:]), ', Min=', np.min(z[:]), ', Max=', np.max(z[:]))
            print('percentage pixels clipped=', np.sum(np.abs(z[:])>1.)*100/z.size)
        return z

    #Returns positive and negative contrast values around the background
    def getIntensity(self,i):
        bgnd = float(self.background.text())

        #print(i)
        if stim[i]['contrastType'] == 'Michelson':
            firstIntensity = bgnd + bgnd * (stim[i]['contrast']/100.0)
            secondIntensity = bgnd - bgnd * (stim[i]['contrast']/100.0)

            #all situations of out of bounds intensities
            if firstIntensity > 255.0: #out of range, set to maximum
                firstIntensity = 255.0
                secondIntensity = bgnd - (255.0 - bgnd) #same amount below background as light is above background
            elif secondIntensity < 0:
                secondIntensity = 0 #out of range, set to minimum
                firstIntensity = 2 * bgnd #set to 100% contrast

                #reverse case, where firstIntensity is dark
            elif secondIntensity > 255.0:
                secondIntensity = 255.0
                firstIntensity = bgnd - (255.0 - bgnd)
            elif firstIntensity < 0:
                secondIntensity = 0
                secondIntensity = 2 * bgnd

        elif stim[i]['contrastType'] == 'Weber':
            firstIntensity = bgnd * (stim[i]['contrast']/100.0) + bgnd

            secondIntensity = bgnd

            #out of bounds intensities
            if firstIntensity > 255.0:
                firstIntensity = 255.0
            elif firstIntensity < 0:
                firstIntensity = 0

        elif stim[i]['contrastType'] == 'Intensity':
            firstIntensity = stim[i]['contrast']
            secondIntensity = bgnd

            #out of bounds intensities
            if firstIntensity > 255.0:
                firstIntensity = 255.0
            elif firstIntensity < 0:
                firstIntensity = 0

        #Convert from 0-255 to -1 to 1 range
        firstIntensity = (2 * firstIntensity/255.0) - 1
        secondIntensity = (2 * secondIntensity/255.0) - 1

        return (firstIntensity,secondIntensity)

    #Aborts stimulus
    def abortStim(self):
        global abortStatus
        abortStatus = 1

    #Adds another stimulus dictionary for the new object
    def addStimDict(self):
        global stim

        numObjects = len(objectList)

        #index is zero offset
        #stimulus parameter dictionary
        stim[numObjects-1] = {
        'objectType':'Circle',
        'gratingType':'Square',
        'coordinateType':'Cartesian',
        'xPos':0,
        'yPos':0,
        'diameter':0,
        'length':0,
        'width':0,
        'spatialFreq':0,
        'spatialPhase':0,
        'orientation':0,
        'contrastType':'Weber',
        'contrast':0,
        'modulationType':'Static',
        'modulationFreq':0,
        'motionType':'Static',
        'speed':0,
        'startRad':0,
        'angle':0,
        'trajectory':'None',
        'delay':float(self.delay.text()),
        'duration':float(self.duration.text()),
        }

        seqAssign[numObjects - 1] = {
        'diameterSeq':{
            'control':self.diameterSeq,
            'parent':'diameter',
            'sequence':'None'
            },
        'lengthSeq':{
            'control':self.lengthSeq,
            'parent':'length',
            'sequence':'None'
            },
        'widthSeq':{
            'control':self.widthSeq,
            'parent':'width',
            'sequence':'None'
            },
        'orientationSeq':{
            'control':self.orientationSeq,
            'parent':'orientation',
            'sequence':'None'
            },
        'spatialFreqSeq':{
            'control':self.spatialFreqSeq,
            'parent':'spatialFreq',
            'sequence':'None'
            },
        'spatialPhaseSeq':{
            'control':self.spatialPhaseSeq,
            'parent':'spatialPhase',
            'sequence':'None'
            },
        'contrastSeq':{
            'control':self.contrastSeq,
            'parent':'contrast',
            'sequence':'None'
            },
        'modulationFreqSeq':{
            'control':self.modulationFreqSeq,
            'parent':'modulationFreq',
            'sequence':'None'
            },
        'xPosSeq':{
            'control':self.xPosSeq,
            'parent':'xPos',
            'sequence':'None'
            },
        'yPosSeq':{
            'control':self.yPosSeq,
            'parent':'yPos',
            'sequence':'None'
            },
        'speedSeq':{
            'control':self.speedSeq,
            'parent':'speed',
            'sequence':'None'
            },
        'startRadSeq':{
            'control':self.startRadSeq,
            'parent':'startRad',
            'sequence':'None'
            },
        'angleSeq':{
            'control':self.angleSeq,
            'parent':'angle',
            'sequence':'None'
            },
        'delaySeq':{
            'control':self.delaySeq,
            'parent':'delay',
            'sequence':'None'
            },
        'durationSeq':{
            'control':self.durationSeq,
            'parent':'duration',
            'sequence':'None'
            },
        'maskXPosSeq':{
            'control':self.maskXPosSeq,
            'parent':'maskXPos',
            'sequence':'None'
            },
        'maskYPosSeq':{
            'control':self.maskYPosSeq,
            'parent':'maskYPos',
            'sequence':'None'
            }
        }

    #Makes a dictionary containing string references to all the GUI objects
    def setControlDict(self):
        global control

        control = {
        'ppm':self.ppm,
        'objectListBox':self.objectListBox,
        'objectType':self.objectType,
        'gratingType':self.gratingType,
        'coordianateType':self.coordinateType,
        'xPos':self.xPos,
        'xPosLabel':self.xPosLabel,
        'xPosSeq':self.xPosSeq,
        'yPos':self.yPos,
        'yPosLabel':self.yPosLabel,
        'yPosSeq':self.yPosSeq,
        'diameter':self.diameter,
        'diameterLabel':self.diameterLabel,
        'diameterSeq':self.diameterSeq,
        'length':self.length,
        'lengthLabel':self.lengthLabel,
        'lengthSeq':self.lengthSeq,
        'width':self.width,
        'widthLabel':self.widthLabel,
        'widthSeq':self.widthSeq,
        'spatialFreq':self.spatialFreq,
        'spatialFreqLabel':self.spatialFreqLabel,
        'spatialFreqSeq':self.spatialFreqSeq,
        'spatialPhase':self.spatialPhase,
        'spatialPhaseLabel':self.spatialPhaseLabel,
        'spatialPhaseSeq':self.spatialPhaseSeq,
        'orientation':self.orientation,
        'orientationLabel':self.orientationLabel,
        'orientationSeq':self.orientationSeq,
        'contrastType':self.contrastType,
        'contrast':self.contrast,
        'contrastLabel':self.contrastLabel,
        'contrastSeq':self.contrastSeq,
        'modulationType':self.modulationType,
        'modulationFreq':self.modulationFreq,
        'modulationFreqLabel':self.modulationFreqLabel,
        'modulationFreqSeq':self.modulationFreqSeq,
        'motionType':self.motionType,
        'speed':self.speed,
        'speedLabel':self.speedLabel,
        'speedSeq':self.speedSeq,
        'startRad':self.startRad,
        'startRadLabel':self.startRadLabel,
        'startRadSeq':self.startRadSeq,
        'angle':self.angle,
        'angleLabel':self.angleLabel,
        'angleSeq':self.angleSeq,
        'coordinateType':self.coordinateType,
        'xOffset':self.xOffset,
        'yOffset':self.yOffset,
        'maskType':self.maskType,
        'maskObjectType':self.maskObjectType,
        'maskCoordinateType':self.maskCoordinateType,
        'maskXPos':self.maskXPos,
        'maskXPosLabel':self.maskXPosLabel,
        'maskXPosSeq':self.maskXPosSeq,
        'maskYPos':self.maskYPos,
        'maskYPosLabel':self.maskYPosLabel,
        'maskYPosSeq':self.maskYPosSeq,
        'seqEntry':self.seqEntry,
        'maskObjectListBox':self.maskObjectListBox,
        'trajectory':self.trajectory,
        'trajListBox':self.trajListBox,
        'angleListBox':self.angleListBox,
        'durationListBox':self.durationListBox,
        'trajAngle':self.trajAngle,
        'trajDuration':self.trajDuration,
        'trialTime':self.trialTime,
        'repeats':self.repeats,
        'duration':self.duration,
        'durationSeq':self.durationSeq,
        'delay':self.delay,
        'delaySeq':self.delaySeq,
        'background':self.background
        }

    #Set contextual menu dictionaries
    def setContextualMenus(self):
        global circleSettings,rectangleSettings,gratingSettings,driftMotionSettings
        global staticMotionSettings,dynamicModSettings,staticModSettings

        circleSettings = {
        'gratingType':0,
        'diameter':1,
        'diameterLabel':1,
        'diameterSeq':1,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0
        }

        rectangleSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'length':1,
        'lengthLabel':1,
        'lengthSeq':1,
        'width':1,
        'widthLabel':1,
        'widthSeq':1,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0
        }

        gratingSettings = {
        'gratingType':1,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'spatialPhase':1,
        'spatialPhaseLabel':1,
        'spatialPhaseSeq':1,
        'spatialFreq':1,
        'spatialFreqLabel':1,
        'spatialFreqSeq':1
        }

        driftMotionSettings = {
        'angle':1,
        'angleLabel':1,
        'angleSeq':1,
        'startRad':1,
        'startRadLabel':1,
        'startRadSeq':1,
        'speed':1,
        'speedLabel':1,
        'speedSeq':1,
        }

        staticMotionSettings = {
        'angle':0,
        'angleLabel':0,
        'angleSeq':0,
        'startRad':0,
        'startRadLabel':0,
        'startRadSeq':0,
        'speed':0,
        'speedLabel':0,
        'speedSeq':0,
        }

        staticModSettings = {
        'modulationFreq':0,
        'modulationFreqLabel':0,
        'modulationFreqSeq':0
        }

        dynamicModSettings ={
        'modulationFreq':1,
        'modulationFreqLabel':1,
        'modulationFreqSeq':1
        }

    #Design Panel
    def buildDesignPanel(self):
        left = 165
        top = 300
        width = 475
        height = 400

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
        large = QtGui.QFont("Helvetica", 13)

        #Group box and designPanelLayout layout
        self.designPanel = QGroupBox(self)
        self.designPanelLayout = QGridLayout()

        self.designPanel.setLayout(self.designPanelLayout)
        self.designPanel.move(left,top)
        self.designPanel.resize(width,height)
        self.designPanelLayout.setVerticalSpacing(5)

        #Blanks
        self.blank1 = QLabel('',self)
        self.blank2 = QLabel('',self)
        self.blank2.setFixedWidth(15)
        self.blank3 = QLabel('',self)
        self.blank3.setFixedWidth(15)
        self.blank4 = QLabel('',self)
        self.blank5 = QLabel('',self)
        self.blank6 = QLabel('',self)

        #Add/Remove Objects
        self.addObject = QPushButton('Add\nObject',self)
        self.designPanelLayout.addWidget(self.addObject,0,0,2,2)
        self.removeObject = QPushButton('Remove\nObject',self)
        self.designPanelLayout.addWidget(self.removeObject,2,0,2,2)
        self.addObject.clicked.connect(lambda: self.buttonProc("addObject"))
        self.removeObject.clicked.connect(lambda: self.buttonProc("removeObject"))

        #Object List Box
        self.objectListBox = QListWidget(self)
        self.designPanelLayout.addWidget(self.objectListBox,0,3,4,3)
        self.objectListBox.addItems(objectList)
        self.objectListBox.setFont(large)
        self.objectListBox.setCurrentRow(0)
        self.objectListBox.setSelectionMode(1)
        self.objectListBox.itemClicked.connect(lambda: self.listProc('objectListBox',self.objectListBox.currentRow()))

        #insert blank after the object list box row
        self.blank1.setFixedHeight(20)
        self.designPanelLayout.addWidget(self.blank1,4,0,1,11)
        self.designPanelLayout.setRowStretch(14,1)
        self.blank1.setAlignment(QtCore.Qt.AlignVCenter)

        #Object Type
        self.objectTypeLabel = QLabel('Type',self)
        self.objectTypeLabel.setFont(bold)
        self.objectTypeLabel.setFixedHeight(20)

        self.objectType = QComboBox(self)
        self.objectType.addItems(['Circle','Rectangle','Grating','Cloud'])
        self.objectType.activated.connect(lambda: self.menuProc('objectType',self.objectType.currentText()))

        self.designPanelLayout.addWidget(self.objectTypeLabel,5,0)
        self.designPanelLayout.addWidget(self.objectType,6,0,1,2)

        #Add blank slot to the right of the object type menu
        self.designPanelLayout.addWidget(self.blank2,7,3)
        #self.blank2.setStyleSheet("QLabel {background-color: blue;}")
        self.blank2.setFixedHeight(20)
        self.blank2.setAlignment(QtCore.Qt.AlignVCenter)

        #Coordinates
        self.coordinateLabel = QLabel('Coordinates')
        self.coordinateLabel.setFont(bold)
        self.coordinateType = QComboBox()
        self.coordinateType.setFixedHeight(20)
        self.coordinateType.addItems(['Cartesian','Polar'])
        self.coordinateType.activated.connect(lambda: self.menuProc('coordinateType',self.coordinateType.currentText()))

        self.designPanelLayout.addWidget(self.coordinateLabel,0,8,1,2)
        self.designPanelLayout.addWidget(self.coordinateType,1,8,1,2)

        #X offset
        self.xPosLabel = QLabel('X Offset')
        self.xPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.xPos = QLineEdit()
        self.xPos.setAlignment(QtCore.Qt.AlignRight)
        self.xPos.setFixedWidth(40)
        self.xPosSeq = QComboBox()
        self.xPosSeq.addItem('None')
        self.xPosSeq.setFixedWidth(20)
        self.xPos.editingFinished.connect(lambda: self.variableProc('xPos',self.xPos.text()))
        self.xPosSeq.activated.connect(lambda: self.menuProc('xPosSeq',self.xPosSeq.currentText()))

        self.designPanelLayout.addWidget(self.xPosLabel,2,8)
        self.designPanelLayout.addWidget(self.xPos,2,9)
        self.designPanelLayout.addWidget(self.xPosSeq,2,10)

        #Y offset
        self.yPosLabel = QLabel('Y Offset')
        self.yPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.yPos = QLineEdit()
        self.yPos.setAlignment(QtCore.Qt.AlignRight)
        self.yPos.setFixedWidth(40)
        self.yPosSeq = QComboBox()
        self.yPosSeq.addItem('None')
        self.yPosSeq.setFixedWidth(20)
        self.yPos.editingFinished.connect(lambda: self.variableProc('yPos',self.yPos.text()))
        self.yPosSeq.activated.connect(lambda: self.menuProc('yPosSeq',self.yPosSeq.currentText()))

        self.designPanelLayout.addWidget(self.yPosLabel,3,8)
        self.designPanelLayout.addWidget(self.yPos,3,9)
        self.designPanelLayout.addWidget(self.yPosSeq,3,10)

        #Diameter
        self.diameterLabel = QLabel('Diameter',self)
        self.diameterLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.diameter = QLineEdit(self)
        self.diameter.setFixedWidth(40)
        self.diameter.setAlignment(QtCore.Qt.AlignRight)
        self.diameterSeq = QComboBox(self)
        self.diameterSeq.addItem('None')
        self.diameterSeq.setFixedWidth(20)
        self.diameter.editingFinished.connect(lambda: self.variableProc('diameter',self.diameter.text()))
        self.diameterSeq.activated.connect(lambda: self.menuProc('diameterSeq',self.diameterSeq.currentText()))

        self.designPanelLayout.addWidget(self.diameterLabel,7,0)
        self.designPanelLayout.addWidget(self.diameter,7,1)
        self.designPanelLayout.addWidget(self.diameterSeq,7,2)

        #Grating type
        self.gratingType = QComboBox(self)
        self.gratingType.addItems(['Square','Sine'])
        self.designPanelLayout.addWidget(self.gratingType,7,0,1,2)
        self.gratingType.activated.connect(lambda: self.menuProc('gratingType',self.gratingType.currentText()))

        #Length
        self.lengthLabel = QLabel('Length',self)
        self.lengthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.length = QLineEdit(self)
        self.length.setFixedWidth(40)
        self.length.setAlignment(QtCore.Qt.AlignRight)
        self.lengthSeq = QComboBox(self)
        self.lengthSeq.addItem('None')
        self.lengthSeq.setFixedWidth(20)
        self.length.editingFinished.connect(lambda: self.variableProc('length',self.length.text()))
        self.lengthSeq.activated.connect(lambda: self.menuProc('lengthSeq',self.lengthSeq.currentText()))

        self.designPanelLayout.addWidget(self.lengthLabel,7,0)
        self.designPanelLayout.addWidget(self.length,7,1)
        self.designPanelLayout.addWidget(self.lengthSeq,7,2)

        #Width
        self.widthLabel = QLabel('Width',self)
        self.widthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.width = QLineEdit(self)
        self.width.setFixedWidth(40)
        self.width.setAlignment(QtCore.Qt.AlignRight)
        self.widthSeq = QComboBox(self)
        self.widthSeq.addItem('None')
        self.widthSeq.setFixedWidth(20)
        self.width.editingFinished.connect(lambda: self.variableProc('width',self.width.text()))
        self.widthSeq.activated.connect(lambda: self.menuProc('widthSeq',self.widthSeq.currentText()))

        self.designPanelLayout.addWidget(self.widthLabel,8,0)
        self.designPanelLayout.addWidget(self.width,8,1)
        self.designPanelLayout.addWidget(self.widthSeq,8,2)

        #Spatial Frequency
        self.spatialFreqLabel = QLabel('Sp. Freq.',self)
        self.spatialFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.spatialFreq = QLineEdit(self)
        self.spatialFreq.setFixedWidth(40)
        self.spatialFreq.setAlignment(QtCore.Qt.AlignRight)
        self.spatialFreqSeq = QComboBox(self)
        self.spatialFreqSeq.addItem('None')
        self.spatialFreqSeq.setFixedWidth(20)
        self.spatialFreq.editingFinished.connect(lambda: self.variableProc('spatialFreq',self.spatialFreq.text()))
        self.spatialFreqSeq.activated.connect(lambda: self.menuProc('spatialFreqSeq',self.spatialFreqSeq.currentText()))

        self.designPanelLayout.addWidget(self.spatialFreqLabel,8,0)
        self.designPanelLayout.addWidget(self.spatialFreq,8,1)
        self.designPanelLayout.addWidget(self.spatialFreqSeq,8,2)

        #Orientation
        self.orientationLabel = QLabel('Orient.',self)
        self.orientationLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.orientation = QLineEdit(self)
        self.orientation.setAlignment(QtCore.Qt.AlignRight)
        self.orientationSeq = QComboBox(self)
        self.orientationSeq.addItem('None')
        self.orientationSeq.setFixedWidth(20)
        self.orientation.editingFinished.connect(lambda: self.variableProc('orientation',self.orientation.text()))
        self.orientationSeq.activated.connect(lambda: self.menuProc('orientationSeq',self.orientationSeq.currentText()))

        self.designPanelLayout.addWidget(self.orientationLabel,9,0)
        self.designPanelLayout.addWidget(self.orientation,9,1)
        self.designPanelLayout.addWidget(self.orientationSeq,9,2)

        #Spatial phase
        self.spatialPhaseLabel = QLabel('Phase',self)
        self.spatialPhaseLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.spatialPhase = QLineEdit(self)
        self.spatialPhase.setAlignment(QtCore.Qt.AlignRight)
        self.spatialPhaseSeq = QComboBox(self)
        self.spatialPhaseSeq.addItem('None')
        self.spatialPhaseSeq.setFixedWidth(20)
        self.spatialPhase.editingFinished.connect(lambda: self.variableProc('spatialPhase',self.spatialPhase.text()))
        self.spatialPhaseSeq.activated.connect(lambda: self.menuProc('spatialPhaseSeq',self.spatialPhaseSeq.currentText()))

        self.designPanelLayout.addWidget(self.spatialPhaseLabel,9,0)
        self.designPanelLayout.addWidget(self.spatialPhase,9,1)
        self.designPanelLayout.addWidget(self.spatialPhaseSeq,9,2)

        #Contrast
        self.contrastTypeLabel = QLabel('Contrast',self)
        self.contrastTypeLabel.setFont(bold)
        self.contrastType = QComboBox(self)
        self.contrastType.addItems(['Weber','Michelson','Intensity'])
        self.contrastType.activated.connect(lambda: self.menuProc('contrastType',self.contrastType.currentText()))

        self.contrastLabel = QLabel('% Contrast',self)
        self.contrastLabel.setFixedHeight(20)
        self.contrast = QLineEdit(self)
        self.contrast.setAlignment(QtCore.Qt.AlignRight)
        self.contrast.setFixedWidth(40)
        self.contrastSeq = QComboBox(self)
        self.contrastSeq.addItem('None')
        self.contrastSeq.setFixedWidth(20)
        self.contrast.editingFinished.connect(lambda: self.variableProc('contrast',self.contrast.text()))
        self.contrastSeq.activated.connect(lambda: self.menuProc('contrastSeq',self.contrastSeq.currentText()))

        self.designPanelLayout.addWidget(self.contrastTypeLabel,5,4,1,2)
        self.designPanelLayout.addWidget(self.contrastType,6,4,1,2)
        self.designPanelLayout.addWidget(self.contrastLabel,7,4)
        self.designPanelLayout.addWidget(self.contrast,7,5)
        self.designPanelLayout.addWidget(self.contrastSeq,7,6)

        #Add blank slot to the right of the contrast edit box
        self.designPanelLayout.addWidget(self.blank3,7,7)
        #self.blank3.setStyleSheet("QLabel {background-color: blue;}")
        self.blank3.setFixedHeight(20)
        self.blank3.setAlignment(QtCore.Qt.AlignVCenter)

        #Modulation
        self.modulationTypeLabel = QLabel('Modulation',self)
        self.modulationTypeLabel.setFont(bold)
        self.modulationTypeLabel.setFixedHeight(20)
        self.modulationType = QComboBox(self)
        self.modulationType.activated.connect(lambda: self.menuProc('modulationType',self.modulationType.currentText()))

        self.modulationType.addItems(['Static','Square','Sine'])

        self.modulationFreqLabel = QLabel('Frequency',self)
        self.modulationFreq =  QLineEdit(self)
        self.modulationFreq.setFixedWidth(40)
        self.modulationFreq.setAlignment(QtCore.Qt.AlignRight)
        self.modulationFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.modulationFreqSeq = QComboBox(self)
        self.modulationFreqSeq.addItem('None')
        self.modulationFreqSeq.setFixedWidth(20)
        self.modulationFreq.editingFinished.connect(lambda: self.variableProc('modulationFreq',self.modulationFreq.text()))
        self.modulationFreqSeq.activated.connect(lambda: self.menuProc('modulationFreqSeq',self.modulationFreqSeq.currentText()))

        self.designPanelLayout.addWidget(self.modulationTypeLabel,8,4,1,2)
        self.designPanelLayout.addWidget(self.modulationType,9,4,1,2)
        self.designPanelLayout.addWidget(self.modulationFreqLabel,10,4)
        self.designPanelLayout.addWidget(self.modulationFreq,10,5)
        self.designPanelLayout.addWidget(self.modulationFreqSeq,10,6)

        #Motion Type
        self.motionTypeLabel = QLabel('Motion',self)
        self.motionTypeLabel.setFont(bold)
        self.motionTypeLabel.setFixedHeight(20)
        self.motionType = QComboBox(self)
        self.motionType.activated.connect(lambda: self.menuProc('motionType',self.motionType.currentText()))
        self.motionType.addItems(['Static','Drift'])

        self.designPanelLayout.addWidget(self.motionTypeLabel,5,8)
        self.designPanelLayout.addWidget(self.motionType,6,8,1,2)

        #Speed
        self.speedLabel = QLabel('Speed',self)
        self.speedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.speed = QLineEdit(self)
        self.speed.setFixedWidth(40)
        self.speed.setAlignment(QtCore.Qt.AlignRight)
        self.speedSeq = QComboBox(self)
        self.speedSeq.addItem('None')
        self.speedSeq.setFixedWidth(20)
        self.speed.editingFinished.connect(lambda: self.variableProc('speed',self.speed.text()))
        self.speedSeq.activated.connect(lambda: self.menuProc('speedSeq',self.speedSeq.currentText()))

        self.designPanelLayout.addWidget(self.speedLabel,7,8)
        self.designPanelLayout.addWidget(self.speed,7,9)
        self.designPanelLayout.addWidget(self.speedSeq,7,10)

        #Start Radius
        self.startRadLabel = QLabel('Start Rad.',self)
        self.startRadLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.startRad = QLineEdit(self)
        self.startRad.setFixedWidth(40)
        self.startRad.setAlignment(QtCore.Qt.AlignRight)
        self.startRadSeq = QComboBox(self)
        self.startRadSeq.addItem('None')
        self.startRadSeq.setFixedWidth(20)
        self.startRad.editingFinished.connect(lambda: self.variableProc('startRad',self.startRad.text()))
        self.startRadSeq.activated.connect(lambda: self.menuProc('startRadSeq',self.startRadSeq.currentText()))

        self.designPanelLayout.addWidget(self.startRadLabel,8,8)
        self.designPanelLayout.addWidget(self.startRad,8,9)
        self.designPanelLayout.addWidget(self.startRadSeq,8,10)

        #Angle
        self.angleLabel = QLabel('Angle',self)
        self.angleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.angle = QLineEdit(self)
        self.angle.setFixedWidth(40)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.angleSeq = QComboBox(self)
        self.angleSeq.addItem('None')
        self.angleSeq.setFixedWidth(20)
        self.angle.editingFinished.connect(lambda: self.variableProc('angle',self.angle.text()))
        self.angleSeq.activated.connect(lambda: self.menuProc('angleSeq',self.angleSeq.currentText()))

        self.designPanelLayout.addWidget(self.angleLabel,9,8)
        self.designPanelLayout.addWidget(self.angle,9,9)
        self.designPanelLayout.addWidget(self.angleSeq,9,10)

        #blank after angle row so hiding modFrequency doesn't change grid
        self.blank5.setFixedHeight(20)
        self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
        #self.blank5.setStyleSheet("QLabel {background-color: green;}")
        self.blank5.setAlignment(QtCore.Qt.AlignVCenter)

        #insert blank after the spatial frequency row
        self.blank4.setFixedHeight(20)
        self.designPanelLayout.addWidget(self.blank4,11,0,1,10)
        #self.blank4.setStyleSheet("QLabel {background-color: black;}")
        self.blank4.setAlignment(QtCore.Qt.AlignVCenter)

        #Delay
        self.timingLabel = QLabel('Timing',self)
        self.timingLabel.setFont(bold)
        self.delayLabel = QLabel('Delay',self)
        self.delay = QLineEdit(self)
        self.delay.setFixedWidth(40)
        self.delay.setAlignment(QtCore.Qt.AlignRight)
        self.delayLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.delaySeq = QComboBox(self)
        self.delaySeq.addItem('None')
        self.delaySeq.setFixedWidth(20)
        self.delay.editingFinished.connect(lambda: self.variableProc('delay',self.delay.text()))
        self.delaySeq.activated.connect(lambda: self.menuProc('delaySeq',self.delaySeq.currentText()))

        self.designPanelLayout.addWidget(self.timingLabel,12,0)
        self.designPanelLayout.addWidget(self.delayLabel,13,0)
        self.designPanelLayout.addWidget(self.delay,13,1)
        self.designPanelLayout.addWidget(self.delaySeq,13,2)

        #Duration
        self.durationLabel = QLabel('Duration',self)
        self.duration = QLineEdit(self)
        self.duration.setFixedWidth(40)
        self.duration.setAlignment(QtCore.Qt.AlignRight)
        self.durationLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.durationSeq = QComboBox(self)
        self.durationSeq.addItem('None')
        self.durationSeq.setFixedWidth(20)
        self.duration.editingFinished.connect(lambda: self.variableProc('duration',self.duration.text()))
        self.durationSeq.activated.connect(lambda: self.menuProc('durationSeq',self.durationSeq.currentText()))

        self.designPanelLayout.addWidget(self.durationLabel,14,0)
        self.designPanelLayout.addWidget(self.duration,14,1)
        self.designPanelLayout.addWidget(self.durationSeq,14,2)

        #Trial Time
        self.trialTimeLabel = QLabel('Trial Time',self)
        self.trialTime = QLineEdit(self)
        self.trialTime.setFixedWidth(40)
        self.trialTime.setAlignment(QtCore.Qt.AlignRight)
        self.trialTimeLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.designPanelLayout.addWidget(self.trialTimeLabel,15,0)
        self.designPanelLayout.addWidget(self.trialTime,15,1)

        #Repititions
        self.repititionLabel = QLabel('Repititions',self)
        self.repititionLabel.setFont(bold)
        self.repeatsLabel = QLabel('Repeats',self)
        self.repeatsLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.repeats = QLineEdit(self)
        self.repeats.setFixedWidth(40)
        self.repeats.setAlignment(QtCore.Qt.AlignRight)

        self.loopCheckLabel = QLabel('Loop',self)
        self.loopCheckLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.loopCheck = QCheckBox(self)
        self.loopCheck.setChecked(False)

        self.designPanelLayout.addWidget(self.repititionLabel,12,4,1,2)
        self.designPanelLayout.addWidget(self.repeatsLabel,13,4)
        self.designPanelLayout.addWidget(self.repeats,13,5)
        self.designPanelLayout.addWidget(self.loopCheckLabel,14,4)
        self.designPanelLayout.addWidget(self.loopCheck,14,5)

        #Trajectories
        self.trajectoryLabel = QLabel('Trajectories')
        self.trajectoryLabel.setFont(bold)
        self.trajectory = QComboBox()
        self.trajectory.addItem('None')
        self.trajectory.activated.connect(lambda: self.menuProc('trajectory',self.trajectory.currentText()))

        self.designPanelLayout.addWidget(self.trajectoryLabel,12,8,1,2)
        self.designPanelLayout.addWidget(self.trajectory,13,8,1,2)

        #Triggers
        self.triggerLabel = QLabel('Triggers')
        self.triggerLabel.setFont(bold)
        self.trigger = QComboBox()
        self.trigger.addItems(['None','Wait For Trigger','Send Trigger'])

        self.designPanelLayout.addWidget(self.triggerLabel,14,8,1,2)
        self.designPanelLayout.addWidget(self.trigger,15,8,1,2)

    #Masks Panel
    def buildMasksPanel(self):
        left = 165
        top = 300
        width = 475
        height = 164

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
        large = QtGui.QFont("Helvetica", 13)

        #Group box and  maskPanelLayout layout
        self.maskPanel = QGroupBox(self)
        maskPanelLayout = QGridLayout()

        #Start with the mask panel hidden
        self.maskPanel.hide()
        self.maskPanel.setLayout(maskPanelLayout)
        self.maskPanel.move(left,top)
        self.maskPanel.resize(width,height)

        #Mask Types
        self.maskTypeLabel = QLabel('Type')
        self.maskTypeLabel.setFont(bold)

        self.maskType = QComboBox()
        self.maskType.addItems(['None','Mask','Window'])

        maskPanelLayout.addWidget(self.maskTypeLabel,0,0)
        maskPanelLayout.addWidget(self.maskType,1,0)

        #Mask Object Types
        self.maskObjectTypeLabel = QLabel('Object')
        self.maskObjectTypeLabel.setFont(bold)

        self.maskObjectType = QComboBox()
        self.maskObjectType.addItems(['Circle','Rectangle'])
        self.maskObjectType.setFixedWidth(106)
        self.maskObjectType.activated.connect(lambda: self.menuProc('maskObjectType',self.maskObjectType.currentText()))

        maskPanelLayout.addWidget(self.maskObjectTypeLabel,2,0)
        maskPanelLayout.addWidget(self.maskObjectType,3,0)

        #Mask Object List Box
        self.maskObjectListBox = QListWidget(self)
        self.maskObjectListBox.setFixedWidth(127)
        self.maskObjectListBox.addItems(objectList)
        self.maskObjectListBox.setFont(large)
        self.maskObjectListBox.setCurrentRow(0)
        self.maskObjectListBox.setSelectionMode(1)

        maskPanelLayout.addWidget(self.maskObjectListBox,0,2,4,1)

        #Mask Coordinates
        self.maskCoordinateLabel = QLabel('Coordinates')
        self.maskCoordinateLabel.setFont(bold)

        self.maskCoordinateType = QComboBox()
        self.maskCoordinateType.setFixedWidth(106)
        self.maskCoordinateType.addItems(['Cartesian','Polar'])
        self.maskCoordinateType.activated.connect(lambda: self.menuProc('maskCoordinateType',self.maskCoordinateType.currentText()))

        maskPanelLayout.addWidget(self.maskCoordinateLabel,0,4,1,2)
        maskPanelLayout.addWidget(self.maskCoordinateType,1,4,1,2)

        #Mask X offset
        self.maskXPosLabel = QLabel('X Offset')
        self.maskXPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskXPos = QLineEdit()
        self.maskXPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskXPos.setFixedWidth(40)
        self.maskXPos.editingFinished.connect(lambda: self.variableProc('maskXPos',self.maskXPos.text()))

        self.maskXPosSeq = QComboBox()
        self.maskXPosSeq.addItem('None')
        self.maskXPosSeq.setFixedWidth(20)
        self.maskXPosSeq.activated.connect(lambda: self.menuProc('maskXPosSeq',self.maskXPosSeq.currentText()))

        maskPanelLayout.addWidget(self.maskXPosLabel,2,4)
        maskPanelLayout.addWidget(self.maskXPos,2,5)
        maskPanelLayout.addWidget(self.maskXPosSeq,2,6)

        #Mask Y offset
        self.maskYPosLabel = QLabel('Y Offset')
        self.maskYPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskYPos = QLineEdit()
        self.maskYPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskYPos.setFixedWidth(40)
        self.maskYPos.editingFinished.connect(lambda: self.variableProc('maskYPos',self.maskYPos.text()))

        self.maskYPosSeq = QComboBox()
        self.maskYPosSeq.addItem('None')
        self.maskYPosSeq.setFixedWidth(20)
        self.maskYPosSeq.activated.connect(lambda: self.menuProc('maskYPosSeq',self.maskYPosSeq.currentText()))

        maskPanelLayout.addWidget(self.maskYPosLabel,3,4)
        maskPanelLayout.addWidget(self.maskYPos,3,5)
        maskPanelLayout.addWidget(self.maskYPosSeq,3,6)

        #Spacer
        self.blank1 = QLabel('')
        maskPanelLayout.addWidget(self.blank1,4,0)

        self.blank2 = QLabel('')
        maskPanelLayout.addWidget(self.blank2,5,0)

        self.blank3 = QLabel('            ')
        maskPanelLayout.addWidget(self.blank3,0,3)
        #self.blank3.setStyleSheet("QLabel {background-color: black;}")

        self.blank4 = QLabel('')
        maskPanelLayout.addWidget(self.blank4,0,1)

    #Sequences  Panel
    def buildSequencePanel(self):
        left = 165
        top = 300
        width = 475
        height = 400

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

        #Group box and sequencePanelLayout layout
        self.sequencePanel = QGroupBox(self)
        seqPanelLayout = QGridLayout()
        seqPanelLayout.setSpacing(5)

        #Start with the mask panel hidden
        self.sequencePanel.hide()
        self.sequencePanel.setLayout(seqPanelLayout)
        self.sequencePanel.move(left,top)
        self.sequencePanel.resize(width,height)

        #Add sequence button
        self.addSeq = QPushButton('Add\nSequence')
        seqPanelLayout.addWidget(self.addSeq,0,0,2,2)
        self.addSeq.clicked.connect(lambda: self.buttonProc("addSeq"))

        #Remove sequence button
        self.removeSeq = QPushButton('Remove\nSequence')
        seqPanelLayout.addWidget(self.removeSeq,2,0,2,2)
        self.removeSeq.clicked.connect(lambda: self.buttonProc("removeSeq"))

        #Sequence list box
        self.seqListBox = QListWidget()
        seqPanelLayout.addWidget(self.seqListBox,0,2,4,2)
        self.seqListBox.itemClicked.connect(lambda: self.listProc('seqListBox',self.seqListBox.currentRow()))

        #Sequence entry
        self.seqEntry = QLineEdit()
        seqPanelLayout.addWidget(self.seqEntry,4,0,1,4)
        self.seqEntry.editingFinished.connect(lambda: self.variableProc('seqEntry',self.seqEntry.text()))

        #Spacer
        self.blank1 = QLabel('')
        seqPanelLayout.addWidget(self.blank1,5,0)

        #Trajectory list box label
        self.trajListBoxLabel = QLabel('Trajectories')
        self.trajListBoxLabel.setFont(bold)
        self.trajListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajListBoxLabel,6,2,1,2)

        #Add trajectory button
        self.addTraj = QPushButton('Add\nTrajectory')
        seqPanelLayout.addWidget(self.addTraj,7,0,2,2)
        self.addTraj.clicked.connect(lambda: self.buttonProc("addTraj"))

        #Remove trajectory button
        self.removeTraj = QPushButton('Remove\nTrajectory')
        seqPanelLayout.addWidget(self.removeTraj,9,0,2,2)
        self.removeTraj.clicked.connect(lambda: self.buttonProc("removeTraj"))

        #Trajectory list box
        self.trajListBox = QListWidget()
        seqPanelLayout.addWidget(self.trajListBox,7,2,4,2)

        #Angle list box label
        self.angleListBoxLabel = QLabel('Angle')
        self.angleListBoxLabel.setFont(bold)
        self.angleListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.angleListBoxLabel,11,0,1,2)

        #Angle list box
        self.angleListBox = QListWidget()
        seqPanelLayout.addWidget(self.angleListBox,12,0,4,2)

        #Duration list box label
        self.durationListBoxLabel = QLabel('Duration')
        self.durationListBoxLabel.setFont(bold)
        self.durationListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.durationListBoxLabel,11,2,1,2)

        #Duration list box
        self.durationListBox = QListWidget()
        seqPanelLayout.addWidget(self.durationListBox,12,2,4,2)

        #Spacer
        self.blank2 = QLabel('            ')
        seqPanelLayout.addWidget(self.blank2,11,4)

        #Trajectory Angle Label
        self.trajAngleLabel = QLabel('Angle')
        self.trajAngleLabel.setFont(bold)
        self.trajAngleLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajAngleLabel,11,5)

        #Trajectory Duration Label
        self.trajDurationLabel = QLabel('Duration')
        self.trajDurationLabel.setFont(bold)
        self.trajDurationLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajDurationLabel,11,6)

        #Trajectory Angle Entry
        self.trajAngle = QLineEdit()
        seqPanelLayout.addWidget(self.trajAngle,12,5)

        #Trajectory Duration Entry
        self.trajDuration = QLineEdit()
        seqPanelLayout.addWidget(self.trajDuration,12,6)

        #Append Segment Button
        self.appendSegment = QPushButton('Append Segment')
        seqPanelLayout.addWidget(self.appendSegment,13,5,1,2)
        self.appendSegment.clicked.connect(lambda: self.buttonProc("appendSegment"))

        #Edit Segment Button
        self.editSegment = QPushButton('Edit Segment')
        seqPanelLayout.addWidget(self.editSegment,14,5,1,2)
        self.editSegment.clicked.connect(lambda: self.buttonProc("editSegment"))

        #Remove Segment Button
        self.removeSegment = QPushButton('Remove Segment')
        seqPanelLayout.addWidget(self.removeSegment,15,5,1,2)
        self.removeSegment.clicked.connect(lambda: self.buttonProc("removeSegment"))

    #Path Panel
    def buildPathPanel(self):
        left = 10
        top = 135
        width = 475
        height = 125

        self.pathGroup = QGroupBox(self)
        pathLayout = QGridLayout()

        self.pathGroup.setLayout(pathLayout)
        self.pathGroup.move(left,top)
        self.pathGroup.resize(width,height)

        #Stimulus path
        self.stimPathLabel = QLabel('Path:',self)
        self.stimPathLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.stimPath = QLineEdit(self)
        self.stimPath.setText('/Users/bmb/Documents/MATLAB/stimGen/stimuli/')
        self.stimPathBrowse = QPushButton('...',self)
        self.stimPathBrowse.clicked.connect(lambda: self.buttonProc("stimPathBrowse"))
        self.stimPathBrowse.setFixedWidth(40)
        pathLayout.addWidget(self.stimPathLabel,0,0)
        pathLayout.addWidget(self.stimPath,0,1,1,2)
        pathLayout.addWidget(self.stimPathBrowse,0,3)


        #Save To path
        self.saveToPathLabel = QLabel('Save To:',self)
        self.saveToPathLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.saveToPath = QLineEdit(self)
        self.saveToPathBrowse = QPushButton('...',self)
        self.saveToPathBrowse.clicked.connect(lambda: self.buttonProc("saveToPathBrowse"))
        self.saveToPathBrowse.setFixedWidth(40)
        pathLayout.addWidget(self.saveToPathLabel,1,0)
        pathLayout.addWidget(self.saveToPath,1,1,1,2)
        pathLayout.addWidget(self.saveToPathBrowse,1,3)

        #File name
        self.fileNameLabel = QLabel('File Name:',self)
        self.fileNameLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.fileName = QLineEdit(self)
        pathLayout.addWidget(self.fileNameLabel,2,0)
        pathLayout.addWidget(self.fileName,2,1)

        #Stim ID
        self.stimIDLabel = QLabel('Stim ID:',self)
        self.stimIDLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.stimID = QLineEdit(self)
        self.stimID.setFixedWidth(40)
        self.stimID.setAlignment(QtCore.Qt.AlignCenter)
        pathLayout.addWidget(self.stimIDLabel,2,2)
        pathLayout.addWidget(self.stimID,2,3)

    #Globals Panel
    def buildGlobalsPanel(self):
        left = 495
        top = 10
        width = 145
        height = 250

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

        self.globalsGroup = QGroupBox(self)
        self.globalsGroup.move(left,top)
        self.globalsGroup.resize(width,height)

        self.globalsLayout =QGridLayout()
        self.globalsGroup.setLayout(self.globalsLayout)

        #Globals label
        self.globalsLabel = QLabel('Globals')
        self.globalsLayout.addWidget(self.globalsLabel,0,0)
        self.globalsLabel.setFont(bold)

        #Monitor
        self.monitor = QComboBox(self)
        self.monitor.setFixedWidth(45)
        self.monitorLabel= QLabel('Monitor')

        #Find number of monitors
        self.monitor.addItem('1')
        self.globalsLayout.addWidget(self.monitorLabel,1,0,1,2)
        self.monitorLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.monitor,1,2)

        #PPM
        self.ppmLabel = QLabel('PPM')
        self.ppm = QLineEdit()
        self.ppm.setFixedWidth(45)
        self.ppm.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.ppmLabel,2,0,1,2)
        self.ppmLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.ppm,2,2)

        #Background
        self.backgroundLabel = QLabel('Background')
        self.background = QLineEdit()
        self.background.setFixedWidth(45)
        self.background.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.backgroundLabel,3,0,1,2)
        self.backgroundLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.background,3,2)
        self.background.editingFinished.connect(lambda: self.variableProc('background',self.background.text()))


        #X Offset
        self.xOffsetLabel = QLabel('X Offset')
        self.xOffset = QLineEdit()
        self.xOffset.setFixedWidth(45)
        self.xOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.xOffsetLabel,4,0,1,2)
        self.xOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.xOffset,4,2)
        self.xOffset.editingFinished.connect(lambda: self.variableProc('xOffset',self.xOffset.text()))

        #Y Offset
        self.yOffsetLabel = QLabel('Y Offset')
        self.yOffset = QLineEdit()
        self.yOffset.setFixedWidth(45)
        self.yOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffsetLabel,5,0,1,2)
        self.yOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffset,5,2)
        self.yOffset.editingFinished.connect(lambda: self.variableProc('yOffset',self.yOffset.text()))

        #Sync Frames
        self.syncFramesLabel = QLabel('Sync Frames')
        self.syncFrames = QLineEdit()
        self.syncFrames.setFixedWidth(45)
        self.syncFrames.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFramesLabel,6,0,1,2)
        self.syncFramesLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFrames,6,2)
        self.syncFrames.editingFinished.connect(lambda: self.variableProc('syncFrames',self.syncFrames.text()))

        #Sync Spot
        self.syncSpotLabel = QLabel('Sync Spot',self)
        self.syncSpotLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.syncSpot = QCheckBox(self)
        self.syncSpot.setChecked(True)
        self.globalsLayout.addWidget(self.syncSpotLabel,7,0,1,2)
        self.globalsLayout.addWidget(self.syncSpot,7,2)

        #Gamma Table
        self.gammaTableLabel = QLabel('Gamma')
        self.gammaTable = QComboBox()
        self.gammaTable.addItems(['1.0','2.2'])
        self.gammaTable.setFixedWidth(45)

        self.globalsLayout.addWidget(self.gammaTableLabel,8,0,1,2)
        self.gammaTableLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.gammaTable,8,2)

    #Stimulus Bank
    def buildStimusBank(self):
        left = 10
        top = 318
        width = 145
        height = 350

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
        large = QtGui.QFont("Helvetica", 13)

        #Stimulus Bank Label
        self.stimBankLabel  = QLabel('Stimulus Bank',self)
        self.stimBankLabel.move(left+30,top-55)

        #Stimulus subfolder
        self.subFolder = QComboBox(self)
        self.subFolder.move(left,top-30)
        self.subFolder.resize(width,25)
        self.subFolder.addItem('Ben')

        #Stimulus Bank
        self.stimBank = QListWidget(self)
        self.stimBank.setFont(large)
        self.stimBank.move(left,top)
        self.stimBank.resize(width,height)
        self.stimBank.itemClicked.connect(lambda: self.listProc('stimBank',self.stimBank.currentRow()))

        #save stimulus
        self.saveStim = QPushButton('Save',self)
        self.saveStim.move(left+5,top + 360)
        self.saveStim.resize(60,20)
        self.saveStim.clicked.connect(lambda: self.buttonProc("saveStim"))

        #delete stimulus
        self.deleteStim = QPushButton('Delete',self)
        self.deleteStim.move(left+80,top + 360)
        self.deleteStim.resize(60,20)
        self.deleteStim.clicked.connect(lambda: self.buttonProc("deleteStim"))

    #save the stimulus to a text file
    def saveStimulus(self):
        global seqAssign

        #convert stimulus/sequence dictionaries into json string
        seqAssignTemp = copy.deepcopy(seqAssign)

        #can't save control references using json, so eliminating those in the saved file
        for object,_ in seqAssignTemp.iteritems():
            for item,_ in seqAssignTemp[object].iteritems():
                seqAssignTemp[object][item]['control'] = 0

        stimulus = json.dumps(stim)
        sequence = json.dumps(seqAssignTemp)
        seqDefs = json.dumps(seqDict)

        #show input dialog for naming the sequence
        name, ok = QInputDialog.getText(self, 'Save Stimulus',
            'Stimulus Name:')

        fileName = name + '.stim'

        subfolder = self.subFolder.currentText()

        path = '/Users/bmb/Documents/GitHub/StimGen/stimuli/' + subfolder + '/' + fileName

        print('Saved Stimulus: ' + path)

        #open and write dictionaries to the file
        with open(path,'w+') as file:
            file.write('Stimulus:')
            file.write(stimulus)
            file.write('Sequences:')
            file.write(seqDefs)
            file.write('Assignments:')
            file.write(sequence)

        file.close()

        #refresh stimulus bank
        self.getStimulusBank()

        #set the list box to select the newly saved stimulus
        newItem = self.stimBank.findItems(name,QtCore.Qt.MatchExactly)
        self.stimBank.setCurrentItem(newItem[0])

    #saves MotionCloud array as an HDF5
    def saveCloud(self,cloud):

        #put the file in the stimulus subfolder
        fileName = 'cloudFile.hdf5'
        subfolder = self.subFolder.currentText()
        path = '/Users/bmb/Documents/GitHub/StimGen/stimuli/' + subfolder + '/' + fileName

        file = h5py.File(path,'w')
        file.create_dataset('MC',data=cloud,compression='gzip',compression_opts=9)
        file.close()

    #deletes stimulus file from disk
    def deleteStimulus(self):

        #prevent deletion of last stimulus
        if(self.stimBank.count() == 1):
            return

        #which stimulus is selected
        stimulus = self.stimBank.currentItem()
        index = self.stimBank.currentRow()

        stimName = stimulus.text()

        fileName = stimName + '.stim'
        subfolder = self.subFolder.currentText()
        path = '/Users/bmb/Documents/GitHub/StimGen/stimuli/' + subfolder + '/' + fileName

        #delete the file, remove it from the stimulus bank
        os.remove(path)
        self.stimBank.takeItem(self.stimBank.row(stimulus))

        #refresh stimulus bank
        self.getStimulusBank()

        if index > 0:
            self.stimBank.setCurrentRow(index - 1)
        else:
            self.stimBank.setCurrentRow(0)

    #loads stimulus data into variables
    def loadStimulus(self):

        global seqAssign,seqDict,stim
        global objectList,seqList

        #which stimulus is selected
        stimulus = self.stimBank.currentItem()
        index = self.stimBank.currentRow()

        stimName = stimulus.text()
        fileName = stimName + '.stim'
        subfolder = self.subFolder.currentText()
        path = '/Users/bmb/Documents/GitHub/StimGen/stimuli/' + subfolder + '/' + fileName

        #open and read stimulus file to dictionaries
        with open(path,'r') as file:
            fileStr = file.read()
            #gets first section of data before 'Sequences:'
            stimStr,theRest = fileStr.split('Sequences:',1)
            seqStr,theRest = theRest.split('Assignments',1)
            assignmentStr = theRest

            #some character removals to make it pure json compatible string
            assignmentStr = assignmentStr[1:]
            stimStr = stimStr.replace('Stimulus:','')

            stim = json.loads(stimStr)
            seqDict = json.loads(seqStr)
            seqAssign = json.loads(assignmentStr)

            #convert the string keys to integers
            stim = {int(k):v for k,v in stim.items()}
            seqAssign = {int(k):v for k,v in seqAssign.items()}

            #convert string controls to object controls
            for object,_ in seqAssign.iteritems():
                for controlName,_ in seqAssign[object].iteritems():
                    seqAssign[object][controlName]['control'] = control[controlName]

            #repopulate seqList and add sequences to the sequence list box
            seqList = ['None']
            self.seqListBox.clear()
            for seq in seqDict:
                seqList.append(seq)
                self.seqListBox.addItem(seq)

            if len(seqList) > 1:
                self.seqListBox.setCurrentRow(0)

                #sets the sequence entry for the first sequence in list
                self.listProc('seqListBox',0)
            else:
                self.seqEntry.setText('')

            #update all of the sequence menus
            for key,_ in seqAssign[0].iteritems():
                control[key].clear() #first reset sequence menus
                control[key].addItems(seqList)

            #clear object list and repopulate with loaded objects
            objectList = []
            numObjects = len(stim)
            for i in range(numObjects):
                objectList.append(stim[i]['objectType'])

            #populate the controls for the first object
            self.objectListBox.clear()
            self.objectListBox.addItems(objectList)
            self.objectListBox.setCurrentRow(0)
            self.setObjectParameters(0)

            self.maskObjectListBox.clear()
            self.maskObjectListBox.addItems(objectList)
            self.maskObjectListBox.setCurrentRow(0)

            #display sequence assignment message
            self.displaySeqAssignments(0)

    #find all the stimulus files in the selected subfolder
    def getStimulusBank(self):
        subfolder = self.subFolder.currentText()
        path = '/Users/bmb/Documents/GitHub/StimGen/stimuli/' + subfolder

        fileList = os.listdir(path)
        stimList = []

        i = 0
        for _ in fileList:
            fileList[i],ext = os.path.splitext(fileList[i])

            #only accept .stim files (these are just text files with .stim extension)
            if ext == '.stim':
                stimList.append(fileList[i])

            i += 1

        #add stimulus files to the stimulus bank
        self.stimBank.clear()
        self.stimBank.addItems(stimList)

        #alphabetical order
        self.stimBank.sortItems(QtCore.Qt.AscendingOrder)

    #is the string a decimal number?
    def isFloat(self,s):
        if '.' in s:
            return True
        else:
            return False

    #Default settings
    def setDefaults(self):
        self.ppm.setText('1')
        self.background.setText('127')
        self.xOffset.setText('0')
        self.yOffset.setText('0')
        self.syncFrames.setText('0')
        self.xPos.setText('0')
        self.yPos.setText('0')
        self.maskXPos.setText('0')
        self.maskYPos.setText('0')
        self.diameter.setText('0')
        self.length.setText('0')
        self.width.setText('0')
        self.spatialFreq.setText('0')
        self.spatialPhase.setText('0')
        self.orientation.setText('0')
        self.contrast.setText('0')
        self.modulationFreq.setText('0')
        self.repeats.setText('1')
        self.speed.setText('0')
        self.startRad.setText('0')
        self.angle.setText('0')
        self.delay.setText('0')
        self.duration.setText('1')
        self.trialTime.setText('0')

#Start the application
if __name__ == '__main__':

    #create instance of application
    StimGen = QApplication([])

    #scaling will transfer to lower res monitors
    StimGen.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    #styles
    StimGen.setStyle('Fusion')
    myFont = QtGui.QFont('Helvetica', 12,weight=QtGui.QFont.Light)
    StimGen.setFont(myFont)
   # StimGen.setStyleSheet("QPushButton {border-radius: 20px;}")
    #StimGen.setStyleSheet("QPushButton {background-color: blue;}")
    ex = App()
    StimGen.exec_()
