#StimGen python

# StimGen is a Qt-based python application for designing and presenting visual stimuli through a projector
# or other external monitor. The interface is an arrangement of Qt widgets that set stimulus parameters such
# as the type of object, and its size, orientation, motion, timing, etc. These parameters are all imported into a master
# stimulus dictionary called 'stim', which is then recalled at runtime. Stimuli are generally produced frame-by-frame as 
# they are presented, except for some cases where the entire stimulus is held in memory before-hand. Stimuli are
# saved into a stimulus bank on disk, and is able to be recalled in future sessions.  


#Qt widgets
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QMenuBar,QMenu,QAction,QPushButton,QLineEdit,QGroupBox,QComboBox,QFrame,QAbstractItemView,QDesktopWidget
from PyQt5.QtWidgets import QLabel,QListWidget,QListWidgetItem,QSpacerItem,QVBoxLayout,QGridLayout,QCheckBox,QInputDialog,QListView,QFontDialog,QErrorMessage
from PyQt5 import QtCore,QtGui

#PsychoPy - visual stimulus library
from psychopy import visual, core, parallel, event, monitors

#Motion Clouds - specialized visual stimulus library for generated natural scenes
import MotionClouds as mc

#timing libraries
from time import sleep
from time import time

#for browsing file explorer
import tkinter.filedialog
from tkinter import Tk

#for loading bitmap images
from PIL import Image

#for saving and loading stimuli from disk
import json
import os

import h5py
import csv

import platform

#math operations
import numpy as np

#random number generators
from random import random, randint, seed

#for copying dictionaries
import copy

#triggers - set to 1 to import the nidaqmx library.
global NI_FLAG 
NI_FLAG = 0

if NI_FLAG:
    import nidaqmx as ni


#Build the GUI
class App(QMainWindow):

    #startup code
    def __init__(self):
        global objectList, seqList, trajList, maskList, stim, globalSettings, trajectoryStim, seqAssign, seqDict, trajDict, maskDict, basePath, stimPath, imagePath, gammaPath, saveToPath, system
        global scale_w,scale_h,device,isOpen,centeringActive,subfolder,gammaTable

        super(App,self).__init__()

        isOpen = 0 #stimulus window is closed
        centeringActive = 0

        self.screen = QDesktopWidget().availableGeometry(1)
        w = self.screen.width()
        h = self.screen.height()


        #coded on 2880x1800 retina display
        scale_h = 1
        scale_w = 1

        #GUI dimensions
        self.title = "StimGen 6.0"
        self.left = 10 * scale_w
        self.top = 10 * scale_h
        self.width = 650 * scale_w
        self.height = 780 * scale_h

        #path to the StimGen.py file
        basePath = os.getcwd() + "/"
        saveToPath = basePath + 'StimulusLog/'
        stimPath = basePath + 'stimuli/'
        imagePath = basePath + 'images/'
        gammaPath = basePath + 'gamma/'

        #operating system
        system = platform.system()

        #set default fonts/sizes depending on operating system
        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto", 10,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Roboto", 12,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Roboto Light",28,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Roboto Light",10,weight=QtGui.QFont.Light)
            counterFont = QtGui.QFont('Roboto Light',18,weight=QtGui.QFont.Normal)

        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 12,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Helvetica",32,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Helvetica",12,weight=QtGui.QFont.ExtraLight)
            counterFont = QtGui.QFont('Helvetica',18,weight=QtGui.QFont.Normal)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        #StimGen icon

        self.iconLabel = QLabel('S T I M G E N',self)
        # iconPath = imagePath + 'logo3.png'
        # icon = QPixmap(iconPath)
        # self.iconLabel.setPixmap(icon)
        self.iconLabel.move(90 * scale_w,35 * scale_h)
        self.iconLabel.setFixedSize(300 * scale_w,30 * scale_h)
        self.iconLabel.setFont(titleFont)
        self.iconLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)


        # iconPath = imagePath + 'logo3.png'
        # icon = QPixmap(iconPath)
        # self.iconLabel.setPixmap(icon)
        self.iconSubLabel = QLabel('A python environment for designing and presenting custom visual stimuli',self)
        self.iconSubLabel.move(20 * scale_w,70 * scale_h)
        self.iconSubLabel.setFixedSize(450 * scale_w,30 * scale_h)
        self.iconSubLabel.setFont(subTitleFont)
        self.iconSubLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

        #Initialize/Close Session Controls
        self.initSession = QPushButton('Initialize',self)
        self.closeSession = QPushButton('Close',self)
        self.initSession.move(115 * scale_w,110 * scale_h)
        self.initSession.setFixedSize(100 * scale_w,30 * scale_h)
        self.initSession.setFont(bold)
        self.closeSession.move(265 * scale_w,110 * scale_h)
        self.closeSession.setFixedSize(100 * scale_w,30 * scale_h)
        self.closeSession.setFont(bold)
        self.initSession.clicked.connect(lambda: self.buttonProc("initSession"))
        self.closeSession.clicked.connect(lambda: self.buttonProc("closeSession"))

        #Design, Masks, Sequences Buttons
        self.designButton = QPushButton('Design',self)
        self.designButton.move(215 * scale_w,280 * scale_h)
        self.designButton.setFixedSize(100 * scale_w,30 * scale_h)
        self.designButton.setFont(bold)
        self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}')
        self.designButton.clicked.connect(lambda: self.buttonProc("designButton"))

        self.masksButton = QPushButton('Masks',self)
        self.masksButton.move(360 * scale_w,280 * scale_h)
        self.masksButton.setFixedSize(100 * scale_w,30 * scale_h)
        self.masksButton.setFont(bold)
        self.masksButton.clicked.connect(lambda: self.buttonProc("masksButton"))

        self.sequencesButton = QPushButton('Sequences',self)
        self.sequencesButton.move(505 * scale_w,280 * scale_h)
        self.sequencesButton.setFixedSize(100 * scale_w,30 * scale_h)
        self.sequencesButton.setFont(bold)
        self.sequencesButton.clicked.connect(lambda: self.buttonProc("sequencesButton"))

        self.runStimulus = QPushButton('Run',self)
        self.runStimulus.move(10 * scale_w + 5,720 * scale_h)
        self.runStimulus.resize(60 * scale_w,30 * scale_h)
        self.runStimulus.setFont(boldLarge)
        self.runStimulus.setStyleSheet('QPushButton {background-color: rgba(150, 245, 150, 150)}')
        self.runStimulus.clicked.connect(lambda: self.buttonProc("runStimulus"))

        self.abortStimulus = QPushButton('Abort',self)
        self.abortStimulus.move(90 * scale_w,720 * scale_h)
        self.abortStimulus.resize(60 * scale_w,30 * scale_h)
        self.abortStimulus.setFont(boldLarge)
        self.abortStimulus.setStyleSheet('QPushButton {background-color: rgba(245, 150, 150, 150)}')
        self.abortStimulus.clicked.connect(lambda: self.buttonProc("abortStimulus"))

        

        self.sequenceMessage = QLabel('',self)
        self.sequenceMessage.move(175 * scale_w,720 * scale_h)
        self.sequenceMessage.resize(775 * scale_w,60 * scale_h)

        self.stimCountDown = QLabel('',self)
        self.stimCountDown.setFont(counterFont)
        self.stimCountDown.move(25 * scale_w,750 * scale_h)

        self.sweepMonitor = QLabel('',self)
        self.sweepMonitor.setFont(counterFont)
        self.sweepMonitor.move(105 * scale_w,750 * scale_h)

        #Object List
        objectList = ['Circle']

        #Sequence list
        seqList = ['None']

        #Trajectory list
        trajList = ['None']

        #Mask list
        maskList = []

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
        self.flipControls('coordinateType','Cartesian')
        self.setDefaults()

        #Make first stimulus and sequence assignment dictionaries
        stim = {}
        trajectoryStim = {}
        globalSettings = {}

        seqAssign = {} #holds sequence assignments for each control
        seqDict = {} #holds the actual sequence entries
        trajDict = {} #holds the trajectory entries
        maskDict = {} #holds the mask entries

        self.addStimDict()

        #initialize the global settings
        self.setGlobalSettingsDict()

        #load global settings file
        self.loadGlobalSettings()

        #get the stimulus files
        self.getStimulusBank()

        #get the stimulus images
        self.getImageBank()

        #get the saved frames bank
        self.getFrameBank()

        if self.stimBank.count() > 0:
            self.stimBank.setCurrentRow(0)
            self.loadStimulus()

        subfolder = self.subFolder.currentText()

        self.setupMenu()

        #show the GUI
        self.show()

        #load the gamma table according to the menu selection
        gammafile = gammaPath + 'gammaTableRig4_12bit.txt'
        gammaTable = np.loadtxt(gammafile,dtype=int)

        #set the default to custom gamma table
        self.gammaTable.setCurrentText('Custom')
        
    #Sets up the menu items in the status bar
    def setupMenu(self):

        myMenu = QMenuBar(self)
        myMenu.setGeometry(0,0,200,20)

        #Session Menu
        initSessionAction = QAction('&Initialize', self)
        initSessionAction.triggered.connect(self.initializeSession)
        closeSessionAction = QAction('&Close Session', self)
        closeSessionAction.triggered.connect(self.closeStimGenSession)

        sessionMenu = myMenu.addMenu('Session')
        sessionMenu.addAction(initSessionAction)
        sessionMenu.addAction(closeSessionAction)

        #Stimuli Menu
        saveStimulusAction = QAction('&Save Stimulus',self)
        deleteStimulusAction = QAction('&Delete Stimulus',self)
        newUserAction = QAction('&Add New User',self)
        exportFramesAction = QAction('&Export Frames',self)

        saveStimulusAction.triggered.connect(self.saveStimulus)
        deleteStimulusAction.triggered.connect(self.deleteStimulus)
        newUserAction.triggered.connect(self.createNewUser)
        exportFramesAction.triggered.connect(self.saveFramesToDisk)

        stimuliMenu = myMenu.addMenu('Stimuli')
        stimuliMenu.addAction(saveStimulusAction)
        stimuliMenu.addAction(deleteStimulusAction)
        stimuliMenu.addAction(newUserAction)
        stimuliMenu.addAction(exportFramesAction)

        #Calibration Menu
        centerStimulusAction = QAction('&Center Stimulus',self)
        centerStimulusAction.triggered.connect(self.centerStimulus)

        measureFrameRateAction = QAction('&Measure Frame Rate',self)
        measureFrameRateAction.triggered.connect(self.measureFrameRate)

        saveGlobalSettingsAction = QAction('&Save Global Settings',self)
        saveGlobalSettingsAction.triggered.connect(self.saveGlobalSettings_Verbose)

        setupTriggerAction = QAction('&Setup Triggers',self)
        setupTriggerAction.triggered.connect(self.setupTriggers)

        calibrationMenu = myMenu.addMenu('Calibration')
        calibrationMenu.addAction(centerStimulusAction)
        calibrationMenu.addAction(measureFrameRateAction)
        calibrationMenu.addAction(saveGlobalSettingsAction)
        calibrationMenu.addAction(setupTriggerAction)

    #Opens up a wizard for dynamically centering the projector with the IR image from the microscope
    def centerStimulus(self):
        global centeringActive, isOpen, win

        ppm = float(self.ppm.text())

        background = self.getBackground()

        #get the starting position of the crosshairs from the current offset position
        startX = int(float(self.xOffset.text()) * ppm)
        startY = int(float(self.yOffset.text()) * ppm)

        if isOpen == 0:
            self.initializeSession()
        else:
            self.closeStimGenSession()
            self.initializeSession()

        isOpen = 1

        #Make a crosshairs stimulus
        self.horizCross = visual.Rect(
            win = win,
            units = 'pix',
            width = 1,
            height = 500,
            ori = 0,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = 1,
            pos = (startX,startY)
            )

        self.vertCross = visual.Rect(
            win = win,
            units = 'pix',
            width = 1,
            height = 500,
            ori = 90,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = 1,
            pos = (startX,startY)
            )

        self.innerRingDark = visual.Circle(
            win = win,
            units = 'pix',
            radius = 100*ppm/2,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = background,
            edges = 100,
            pos = (startX,startY)
            )

        self.innerRingBright = visual.Circle(
             win = win,
            units = 'pix',
            radius = 110*ppm/2,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = 1,
            edges = 100,
            pos = (startX,startY)
        )

        self.outerRingDark = visual.Circle(
            win = win,
            units = 'pix',
            radius = 200*ppm/2,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = background,
            edges = 100,
            pos = (startX,startY)
            )

        self.outerRingBright = visual.Circle(
             win = win,
            units = 'pix',
            radius = 210*ppm/2,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = 1,
            edges = 100,
            pos = (startX,startY)
        )

        self.outerRingBright.draw()
        self.outerRingDark.draw()
        
        self.innerRingBright.draw()
        self.innerRingDark.draw()

        self.horizCross.draw()
        self.vertCross.draw()
        win.flip()

        centeringActive = 1
        
        while centeringActive == 1:
            key = event.waitKeys(maxWait=0.1,keyList=['left','right','up','down','return'],clearEvents=True)

            if key is None:
                continue
            elif key[0] == 'return':
                centeringActive == 0
                break
            else:
                self.moveCenterPos(key[0])
       

        #assign the new center position to the globals
        (x,y) = self.horizCross.pos

        self.xOffset.setText(str(int(float(x/ppm))))
        self.yOffset.setText(str(int(float(y/ppm))))
        self.setGlobalSettingsDict()
        self.saveGlobalSettings()

        #flip to a blank screen again
        win.flip()

    #For stimulus centering, moves the crosshairs with arrow keystrokes
    def moveCenterPos(self,direction):

        if direction == 'left':
            x,y = self.horizCross.pos
            self.horizCross.setPos((x-1,y))
            self.vertCross.setPos((x-1,y))
            
            self.outerRingBright.setPos((x-1,y))
            self.outerRingDark.setPos((x-1,y))
            
            self.innerRingBright.setPos((x-1,y))
            self.innerRingDark.setPos((x-1,y))

        elif direction == 'right':
            x,y = self.horizCross.pos
            self.horizCross.setPos((x+1,y))
            self.vertCross.setPos((x+1,y))

            self.outerRingBright.setPos((x+1,y))
            self.outerRingDark.setPos((x+1,y))
            
            self.innerRingBright.setPos((x+1,y))
            self.innerRingDark.setPos((x+1,y))

        elif direction == 'up':
            x,y = self.horizCross.pos
            self.horizCross.setPos((x,y+1))
            self.vertCross.setPos((x,y+1))

            self.outerRingBright.setPos((x,y+1))
            self.outerRingDark.setPos((x,y+1))
            
            self.innerRingBright.setPos((x,y+1))
            self.innerRingDark.setPos((x,y+1))

        elif direction == 'down':
            x,y = self.horizCross.pos
            self.horizCross.setPos((x,y-1))
            self.vertCross.setPos((x,y-1))

            self.outerRingBright.setPos((x,y-1))
            self.outerRingDark.setPos((x,y-1))
            
            self.innerRingBright.setPos((x,y-1))
            self.innerRingDark.setPos((x,y-1))

        self.outerRingBright.draw()
        self.outerRingDark.draw()
        
        self.innerRingBright.draw()
        self.innerRingDark.draw()

        self.horizCross.draw()
        self.vertCross.draw()
        
        win.flip()

    #Opens a window for defining input/output trigger addresses
    def setupTriggers(self):
        self.triggerMenu = triggerMenu()
        self.triggerMenu.show()

    #Handles all variable entries
    def variableProc(self,controlName,entry):
        global stim, seqDict, maskDict

        ppm = float(self.ppm.text())

        #Need to check each variable for validity
        if controlName == 'background':
            #update the globals dict
            self.setGlobalSettingsDict()

            bgnd = self.getBackground()
            try:
                win.color= [bgnd,bgnd,bgnd]

                #Double flip, one to send new bgnd to buffer, then another to flip buffer to screen
                #Flip the sync spot
                win.flip()

                #build the sync spot stimulus object
                syncSpot = visual.Rect(
                win = win,
                units = 'pix',
                width = 80 * ppm,
                height = 80 * ppm,
                fillColor = [1,1,1],
                lineColor = [1,1,1],
                contrast = -1,
                pos = (532-40,-404+40)
                )

                self.drawSyncSpot(syncSpot,-1) #draw sync spot to dark if it's checked
                win.flip()
            except:
                return
        elif controlName == 'seqEntry':
            item = self.seqListBox.currentItem()
            name = item.text()
            entry = self.seqEntry.text()
            seqDict[name] = entry.split(",") #list

        elif controlName.find('mask') != -1:
            #it's a mask variable, add to mask dictionary instead of stimulus dictionary
            index = self.maskObjectListBox.currentRow()

            if index == -1:
                return

            if self.isFloat(entry):
                maskDict[index][controlName] = float(entry)   #some need to be float though
            else:
                if entry.isnumeric():
                    maskDict[index][controlName] = int(entry)
                else:
                    control[controlName].setText('0')
                    maskDict[index][controlName] = 0

        elif controlName == 'apertureDiam':
            if entry.isnumeric():
                stim[0][controlName] = float(entry)
            else:
                control[controlName].setText('0')
                stim[0][controlName] = 0.0
        elif controlName == 'TargetResolution':
            #Must ensure that the target resolution for checkerboard noise is a multiple of the noise pixel size.
            pixelSize = float(self.noiseSize.text())
            target = float(entry)

            div = np.round(pixelSize / target)
            pixelSize = div * target
            index = self.objectListBox.currentRow()
            stim[index][controlName] = int(target)
            stim[index]['noiseSize'] = int(pixelSize)
            self.noiseSize.setText(str(pixelSize))

        elif controlName == 'noiseSize':
            if self.PositionalShiftType.currentText() == 'Random':
                target = float(self.TargetResolution.text())
                pixelSize = float(entry)

                div = np.round(pixelSize / target)
                pixelSize = div * target
                index = self.objectListBox.currentRow()
                stim[index]['TargetResolution'] = int(target)
                stim[index][controlName] = int(pixelSize)
                self.noiseSize.setText(str(pixelSize))
            else:  
                index = self.objectListBox.currentRow()
                stim[index][controlName] = int(entry)
        else:
            #all other variable controls
            #Assign variable entry to the stim dictionary for the selected object
            keys = list(globalSettings.keys())
            if controlName in keys:
                #Update the global settings dict in case a global has been changed
                self.setGlobalSettingsDict()
            else:
                index = self.objectListBox.currentRow()
                if self.isFloat(entry):
                    stim[index][controlName] = float(entry)   #some need to be float though
                else:
                    try:
                        stim[index][controlName] = int(entry)
                    except:
                        control[controlName].setText('0')
                        stim[index][controlName] = 0

    #Handles all button clicks
    def buttonProc(self,controlName):
        global isOpen, abortStatus, saveToPath, stimPath, stimID, stim

        if  controlName == 'designButton':
            self.designPanel.show()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}')

            self.maskPanel.hide()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

            self.sequencePanel.hide()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

            #Bug when masks are changed sometimes grating settings go back to circle settings
            self.setContextualMenus() #ensures that the parameters have the correct settings.


        elif controlName == 'masksButton':
            self.designPanel.hide()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

            self.maskPanel.show()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}')

            self.sequencePanel.hide()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

        elif controlName == 'sequencesButton':
            self.designPanel.hide()
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

            self.maskPanel.hide()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}')

            self.sequencePanel.show()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}')

        elif controlName == 'initSession':
            #Open a stimulus window
            self.initializeSession()

        elif controlName == 'closeSession':
            #Close the stimulus window
            self.closeStimGenSession()

        elif controlName == 'runStimulus':
            #Reset abort abortStatus
            abortStatus = 0

            if isOpen == 0:
                return 0

            #Run the stimulus
            self.runStim(0)

            #save data to stimulus log
            if abortStatus == 0:
                self.writeStimLog()
                stimID = stimID + 1
                self.stimID.setText(str(stimID))

        elif controlName == 'abortStimulus':
            self.abortStim()

        elif controlName == 'startEphys':
            self.triggerEphys()

        elif controlName == 'addObject':
            self.addStimObject()

        elif controlName == 'removeObject':
            self.removeStimObject()

        elif controlName == 'addSeq':
            self.addSequence()

        elif controlName == 'removeSeq':
            self.removeSequence()

        elif controlName == 'addTraj':
            self.addTrajectory()

        elif controlName == 'removeTraj':
            self.removeTrajectory()

        elif controlName == 'appendSegment':
            item = self.trajListBox.currentItem() #which trajectory
            name = item.text()

            trajDict[name]['angle'].append(self.trajAngle.text())
            trajDict[name]['duration'].append(self.trajDuration.text())
            trajDict[name]['speed'].append(self.trajSpeed.text())
            trajDict[name]['link'].append(self.trajLink.text())

            self.updateTrajectory(name)
        elif controlName == 'appendHold':
            item = self.trajListBox.currentItem() #which trajectory
            name = item.text()
            trajDict[name]['angle'].append('0')
            trajDict[name]['duration'].append(self.trajDuration.text())
            trajDict[name]['speed'].append('*Hold*')
            trajDict[name]['link'].append('0')

            self.updateTrajectory(name)

        elif controlName == 'editSegment':
            item = self.trajListBox.currentItem() #which trajectory
            name = item.text()

            #selected segment is the same for the duration list box
            index = self.angleListBox.currentRow()

            
            #edit the entry in place
            trajDict[name]['angle'][index] = self.trajAngle.text()
            trajDict[name]['duration'][index] = self.trajDuration.text()
            trajDict[name]['speed'][index] = self.trajSpeed.text()
            trajDict[name]['link'][index] = self.trajLink.text()

            self.updateTrajectory(name)
        elif controlName == 'removeSegment':
            # item = self.trajListBox.currentItem() #which trajectory
            # name = item.text()

            # #selected segment is the same for the duration list box
            # index = self.angleListBox.currentRow()

            #  #edit the entry in place
            # trajDict[name]['angle'][index] = self.trajAngle.text()
            # trajDict[name]['duration'][index] = self.trajDuration.text()
            print('Need to code')
        elif controlName == 'saveStim':
            self.saveStimulus()

        elif controlName == 'deleteStim':
            self.deleteStimulus()

        elif controlName == 'addMask':
            self.addMaskObject()

        elif controlName == 'removeMask':
            self.removeMaskObject()

        elif controlName == 'stimPathBrowse':
            Tk().withdraw()
            stimPath = filedialog.askdirectory(initialdir = stimPath)
            self.stimPath.setText(stimPath)

        elif controlName == 'saveToPathBrowse':
            if len(saveToPath) == 0:
                startPath = basePath
            else:
                startPath = saveToPath
            Tk().withdraw()
            saveToPath = filedialog.askdirectory(initialdir = startPath)
            self.saveToPath.setText(saveToPath)

        elif controlName == 'batchStimAdd':
            stimName = self.batchStimMenu.currentText()
            self.batchStimList.addItem(stimName)

            currentObject = self.objectListBox.currentItem()
            objectNum = self.objectListBox.row(currentObject)
            stim[objectNum]['batchStimList'].append(stimName)

        elif controlName == 'batchStimRemove':
            #selected item and its index
            item = self.batchStimList.currentItem()
            index = self.batchStimList.row(item)

            if index == -1:
                return

            #delete stimulus from the list box
            self.batchStimList.takeItem(index)

            #remove stimulus item from the stim dict
            currentObject = self.objectListBox.currentItem()
            objectNum = self.objectListBox.row(currentObject)
            stim[objectNum]['batchStimList'].pop(index)
        elif controlName == 'sendTTL':
            (interface,digitalOut,digitalIn,portAddress) = self.getTriggerSettings()
            self.sendTTLPulse(interface,digitalOut,digitalIn,portAddress)
        else:
            #default
            print('other')

    #writes the stimulus that was just run to the stimulus log on disk
    def writeStimLog(self):

        saveToPath = self.saveToPath.text()

        if len(saveToPath) == 0:
            return

        #ensure valid path
        if saveToPath.endswith('/') == False:
            saveToPath = saveToPath + '/'

        if os.path.isdir(saveToPath) == 0:
            os.mkdir(saveToPath[:-1])

        fileName = self.fileName.text()
        if len(fileName) == 0:
            path = saveToPath + 'StimulusLog.txt'
            # return #only save if a file name has been provided
        else:
            if fileName.endswith('.txt') == False:
                fileName = fileName + '.txt'
            path = saveToPath + fileName

        #which stimulus is selected
        stimulus = self.stimBank.currentItem()
        stimName = stimulus.text()

        #open and write dictionaries to the file
        with open(path,'a+') as file:
            writer = csv.writer(file)
            writer.writerow(['***' + stimName + ':' + self.stimID.text()]) #Stimulus Name ***Stimulus:stimID

            for object,_ in stim.items():
                writer.writerow(['ObjectNum:' + str(object)]) #write object number

                for key,value in stim[object].items():
                    writer.writerow([key + ':' + str(value)])    #write stimulus parameters

                writer.writerow([]) #blank spacer row

            writer.writerow(['Sequences:']) #Sequences
            for key,value in seqDict.items():
                writer.writerow([key + ':' + str(value)]) #write sequence definitions

            writer.writerow(['Trajectories:']) #Trajectories
            for traj,_ in trajDict.items():
                writer.writerow([traj + '|']) #write trajectory name
                for key,value in trajDict[traj].items():
                    writer.writerow([key + ':' + str(value)]) #write trajectory definitions

            writer.writerow([]) #blank spacer row at end
            file.close()

    def convertBitDepth(self,val,valDepth,bitDepth):
        #valDepth: original bit depth
        #BitDepth: new bit depth

        converted = (2**bitDepth - 1) * (val / (2**valDepth - 1))
        return converted

    #Handles all drop down menu selections
    def menuProc(self,controlName,selection):
        global objectList, stim, seqAssign, win, subfolder, globalSettings, gammaTable, BitDepth

        #Set contextual menus
        self.flipControls(controlName,selection)

        #currently selected object
        index = self.objectListBox.currentRow()

        #Adjust list boxes items
        if controlName == 'objectType':
            objectList[index] = selection

            #edit the listbox item for objects and masks
            self.objectListBox.item(index).setText(selection)

            #Assign objectType box entry to the stim dictionary for the selected object
            index = self.objectListBox.currentRow()
            stim[index][controlName] = selection

        elif controlName.find('Seq') != -1:
            #if it's a sequence menu
            #assign sequence name to the seq dictionary for that control

            #which object?
            object = self.objectListBox.currentRow()
            
            seqAssign[object][controlName]['sequence'] = selection

            try:
                if selection != 'None':
                    seqAssign[object][controlName]['control'].setStyleSheet("background-color: rgba(150, 245, 150, 150)")
                else:
                    seqAssign[object][controlName]['control'].setStyleSheet("background-color: white")
                    seqAssign[object][controlName]['control'].setStyleSheet("color: black")
                pass
            except:
                print('except')
                pass
            

            #display assigned sequences to the GUI
            self.displaySeqAssignments(object)

        elif controlName.find('mask') != -1: #is it a mask menu?
            #which mask?
            index = self.maskObjectListBox.currentRow()
            if index == -1:
                return
            if controlName.find('Seq') != -1: #is it a mask sequence menu?
                if selection != 'None':
                    maskDict[index][controlName]['control'].setStyleSheet("background-color: rgba(150, 245, 150, 150)")
                else:
                    maskDict[index][controlName]['control'].setStyleSheet("background-color: white")
                    maskDict[index][controlName]['control'].setStyleSheet("color: black")
            else:
                maskDict[index][controlName] = selection
                #set currently selected mask object to the mask type
                self.maskObjectListBox.item(index).setText(selection)

        elif controlName == 'apertureStatus':
            stim[0][controlName] = selection
        elif controlName == 'PositionalShiftType':
            #Must ensure that the target resolution for checkerboard noise is a multiple of the noise pixel size.
            if selection == 'Random':
                pixelSize = float(self.noiseSize.text())
                target = float(self.TargetResolution.text())

                if target == 0:
                    target = pixelSize

                div = np.round(pixelSize / target)
                pixelSize = div * target
                index = self.objectListBox.currentRow()
                stim[index]['TargetResolution'] = int(target)
                stim[index]['noiseSize'] = int(pixelSize)
                self.noiseSize.setText(str(pixelSize))

            stim[index][controlName] = selection
        
        elif controlName == 'gammaTable':
            if selection == 'Native':
                gammafile = gammaPath + 'gammaTableLinear_' + str(BitDepth) + 'bit.txt'
            elif selection == 'Custom':
                gammafile = gammaPath + 'gammaTableRig4_' + str(BitDepth) + 'bit.txt'
            
            #load the gamma table according to the menu selection
            gammaTable = np.loadtxt(gammafile,dtype=int)
            
            #update the globals dict
            self.setGlobalSettingsDict()

            #apply background with the new gamma table
            bgnd = self.getBackground()
            try:
                win.color= [bgnd,bgnd,bgnd]
                win.flip()
                win.flip()

                #Double flip, one to send new bgnd to buffer, then another to flip buffer to screen
                #Flip the sync spot
                win.flip()

                #build the sync spot stimulus object
                syncSpot = visual.Rect(
                win = win,
                units = 'pix',
                width = 80 * ppm,
                height = 80 * ppm,
                fillColor = [1,1,1],
                lineColor = [1,1,1],
                contrast = -1,
                pos = (532-40,-404+40)
                )

                self.drawSyncSpot(syncSpot,-1) #draw sync spot to dark if it's checked
                win.flip()
            except:
                return
        elif controlName == 'encoding':
            bgnd = int(self.background.text())
         
            bgnd = self.convertBitDepth(bgnd,BitDepth,int(selection))
            self.background.setText(str(round(bgnd)))

            BitDepth = int(selection)
        
            gammatableStr = self.gammaTable.currentText()
            if gammatableStr == 'Native':
                gammafile = gammaPath + 'gammaTableLinear_' + selection + 'bit.txt'
            else:
                gammafile = gammaPath + 'gammaTableRig4_' + selection + 'bit.txt'
            
            #load the gamma table according to the menu selection
            gammaTable = np.loadtxt(gammafile,dtype=int)
            
            #update the globals dict
            self.setGlobalSettingsDict()

            #apply background with the new gamma table
            bgnd = self.getBackground()
            try:
                win.color= [bgnd,bgnd,bgnd]
                win.flip()
                win.flip()

                #Double flip, one to send new bgnd to buffer, then another to flip buffer to screen
                #Flip the sync spot
                win.flip()

                #build the sync spot stimulus object
                syncSpot = visual.Rect(
                win = win,
                units = 'pix',
                width = 80 * ppm,
                height = 80 * ppm,
                fillColor = [1,1,1],
                lineColor = [1,1,1],
                contrast = -1,
                pos = (532-40,-404+40)
                )

                self.drawSyncSpot(syncSpot,-1) #draw sync spot to dark if it's checked
                win.flip()
            except:
                return

        elif controlName == 'subFolder':

            if subfolder == selection:
                return

            subfolder = selection
            self.loadUserProfile(subfolder)
        elif controlName == 'subsubFolder':
            subfolder = selection
            self.changeUserSubFolder(subfolder)

        elif controlName == 'monitor':
            globalSettings['monitor'] = selection

        else:
            #add parameter to stim dictionary for all other drop down menus (motionType,coordinateType, etc...)
            stim[index][controlName] = selection

    #Handles all of the list box selections
    def listProc(self,controlName,index):
        global subfolder

        if controlName == 'objectListBox':
            self.setObjectParameters(index)

            #display assigned sequences to the GUI
            self.displaySeqAssignments(index)


        elif controlName == 'seqListBox':
            name = seqList[index + 1]
            entry = (seqDict[name])
            entry = ','.join(entry)
            self.seqEntry.setText(entry)

        elif controlName == 'trajListBox':
            name = trajList[index + 1]
            self.updateTrajectory(name)

        elif controlName == 'angleListBox':
            self.durationListBox.setCurrentRow(index)
            self.speedListBox.setCurrentRow(index)
            self.linkApertureListBox.setCurrentRow(index)

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]

            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])
            self.trajSpeed.setText(trajDict[name]['speed'][index])
            self.trajLink.setText(trajDict[name]['link'][index])

        elif controlName == 'durationListBox':
            self.angleListBox.setCurrentRow(index)
            self.speedListBox.setCurrentRow(index)
            self.linkApertureListBox.setCurrentRow(index)

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]
            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])
            self.trajSpeed.setText(trajDict[name]['speed'][index])
            self.trajLink.setText(trajDict[name]['link'][index])
            
        elif controlName == 'speedListBox':
            self.angleListBox.setCurrentRow(index)
            self.durationListBox.setCurrentRow(index)
            self.linkApertureListBox.setCurrentRow(index)

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]
            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])
            self.trajSpeed.setText(trajDict[name]['speed'][index])
            self.trajLink.setText(trajDict[name]['link'][index])

        elif controlName == 'linkApertureListBox':
            self.angleListBox.setCurrentRow(index)
            self.durationListBox.setCurrentRow(index)
            self.speedListBox.setCurrentRow(index)

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]
            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])
            self.trajSpeed.setText(trajDict[name]['speed'][index])
            self.trajLink.setText(trajDict[name]['link'][index])

        elif controlName == 'stimBank':
            
            self.loadStimulus()

        elif controlName == 'maskObjectListBox':
            self.maskObjectType.setCurrentText(maskDict[index]['maskType'])
            self.maskDiameter.setText(str(maskDict[index]['maskDiameter']))
            self.maskCoordinateType.setCurrentText(maskDict[index]['maskCoordinateType'])
            self.maskYPos.setText(str(maskDict[index]['maskYPos']))
            self.maskXPos.setText(str(maskDict[index]['maskXPos']))

    #handles all checkboxes
    def checkProc(self,controlName,isChecked):
        global globalSettings

        ppm = float(self.ppm.text())

        if controlName == 'syncSpot':
            #sync spot
            if isChecked:
                if isOpen == 1:
                    syncSpot = visual.Rect(
                    win = win,
                    units = 'pix',
                    width = 80 * ppm,
                    height = 80 * ppm,
                    fillColor = [1,1,1],
                    lineColor = [1,1,1],
                    contrast = -1,
                    pos = (532-40,-404+40)
                    )

                    syncSpot.draw()
                    win.flip()
                globalSettings['syncSpot'] = True
            else:
                globalSettings['syncSpot'] = False
                if isOpen == 1:
                    win.flip()

    def changeUserSubFolder(self,subsubfolder):
        global subfolder

        #clear the stimulus bank
        self.stimBank.clear()
        stimList = []

        #check the subfolder
        subfolder = self.subFolder.currentText()

        #add subfolder if it is there
        if len(subsubfolder) > 0:
            path = stimPath + subfolder + "/" + subsubfolder

        #get the files within the selected subsubfolder
        fileList = os.listdir(path)

        i = 0
        for _ in fileList:
            fileList[i],ext = os.path.splitext(fileList[i])

            #only accept .stim files (these are just text files with .stim extension)
            if ext == '.stim':
                stimList.append(fileList[i])
            i += 1

        #append items to the stimulus bank
        if len(stimList) > 0:
            self.stimBank.addItems(stimList)

            #alphabetical order
            self.stimBank.sortItems(QtCore.Qt.AscendingOrder)

        if self.stimBank.count() > 0:
            self.stimBank.setCurrentRow(0)
            self.loadStimulus()

    #loads the indicated user profile stimulus bank and global settings
    def loadUserProfile(self,profile):
        global subfolder

        #set the subfolder global to the profile of interest
        subfolder = profile

        #get the stimulus files
        self.getStimulusBank()
        if self.stimBank.count() > 0:
            self.stimBank.setCurrentRow(0)
            self.loadStimulus()

        #update the global settings for the new user
        self.loadGlobalSettings()

    #removes a mask from the stimulus
    def removeMaskObject(self):
        global maskList,maskDict

        #can't delete past 0
        numMasks = len(maskList)
        if numMasks == 0:
            return

        #selected mask
        index = self.maskObjectListBox.currentRow()

        #delete mask from the list box
        self.maskObjectListBox.takeItem(index)

        #remove object from the stimulus object list
        del maskList[index]

        #remove the mask from the mask dictionary
        if index == numMasks - 1: #if its the last object, no dictionary shifting is necessary
            maskDict.pop(index,None)
        else:
            numMasks = len(maskList) #new number of masks after deleting one of them

            #shift dictionary indices (for object indices 0,1,2 , deleting object 1 results in 0,1 dictionary indices)
            for object in range(index,numMasks):
                maskDict[object] = maskDict[object+1]

            #now delete final dictionary entries
            maskDict.pop(numMasks,None)

    #adds a new mask to the stimulus
    def addMaskObject(self):
        global maskList, maskDict

        #get mask type, add to the mask list box
        type = self.maskObjectType.currentText()
        maskList.append(type)

        size = len(maskList)

        self.maskObjectListBox.addItem('Circle') #always start with a circle
        self.maskObjectListBox.setCurrentRow(size-1)
        self.maskObjectListBox.setSelectionMode(1)

        self.maskDiameter.setText('0')
        self.maskYPos.setText('0')
        self.maskXPos.setText('0')
        self.maskDiameterSeq.setCurrentIndex(0)
        self.maskXPosSeq.setCurrentIndex(0)
        self.maskYPosSeq.setCurrentIndex(0)
        self.maskPolarRadius.setText('0')
        self.maskPolarAngle.setText('0')

        #add the mask to the stimulus dictionary
        maskDict[size-1] = {
        'maskType': type,
        'maskDiameter': 0,
        'maskCoordinateType':self.maskCoordinateType.currentText(),
        'maskXPos': 0,
        'maskYPos': 0,
        'maskPolarRadius':0,
        'maskPolarAngle':0,
        'maskDiameterSeq':{
            'control':self.maskDiameterSeq,
            'parent':'maskDiameter',
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
            },
        'maskPolarRadiusSeq':{
            'control':self.maskPolarRadiusSeq,
            'parent':'maskPolarRadius',
            'sequence':'None'
            },
        'maskPolarAngleSeq':{
            'control':self.maskPolarAngleSeq,
            'parent':'maskPolarAngle',
            'sequence':'None'
            }
        }

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
        for key,_ in seqAssign[0].items():
            control[key].addItem(name)

    #Deletes the selected sequence
    def removeSequence(self):
        global seqList, seqDict

        #prevent deleting 'None'
        numSequences = len(seqList)
        if numSequences == 1:
            return

        #selected item and its index
        item = self.seqListBox.currentItem()
        index = self.seqListBox.currentRow()

        theSequence = item.text()
        seqDict.pop(theSequence)

        #delete sequence from the list box
        self.seqListBox.takeItem(self.seqListBox.row(item))

        #remove from seqList and seqDict
        del seqList[index+1]

        #update sequence assignment menus
        for object,_ in seqAssign.items():
            for key,_ in seqAssign[object].items():
                seqMenu = seqAssign[object][key]['control']
                seqMenu.removeItem(index + 1) #add one to avoid deleting 'None'

                #if that sequence was a part of an assignment, change assignment to 'None'
                if seqAssign[object][key]['sequence'] == theSequence:
                    seqAssign[object][key]['sequence'] = 'None'

        #update GUI controls and menus
        self.setObjectParameters(self.objectListBox.currentRow())

        #refresh the sequence entry box to the newly selected sequence
        index = self.seqListBox.currentRow()
        name = seqList[index + 1]

        if name == 'None':
            self.seqEntry.setText('')
        else:
            entry = (seqDict[name])
            entry = ','.join(entry)
            self.seqEntry.setText(entry)


    def CheckSequenceType(self,entry):
        #check if the sequence is an expression or a list of values

        if isinstance(entry,list):
            entry = str(entry)

        if 'x' in entry:
            return 'Expression'
        elif '[' in entry:
            return 'Expression'
        else:
            return 'List'
            
                
    def SeqExpressionLen(self,entry):
        
        if isinstance(entry,list):
            entry = str(entry)
        
        start = entry.find('[') + 1
        end = entry.find(']',start)
        
        sweeps = entry[start:end]
        
        if(len(sweeps) == 0):
            nSweeps = 1
        else:
            nSweeps = int(sweeps)

        return nSweeps

    def resolveSeqExpression(self,entry,sweep):
        #sweepLenList holds the number of sweeps in each list item of a sequence

        whichSweep = 0
        whichEntry = 0

        for subEntry in entry:
           
            entryType = self.CheckSequenceType(subEntry)

            if entryType == 'Expression':
                expLen = self.SeqExpressionLen(subEntry)
                whichSweep += expLen
            else:
                expLen = 1
                whichSweep += 1

            if sweep < whichSweep:
                offset = sweep - (whichSweep - expLen)
                break
            whichEntry += 1

        #Get the correct entry position in the sequence
        entry = entry[whichEntry]

        entryType = self.CheckSequenceType(entry)

        if entryType == 'List':
            return float(entry)

        isRand = entry.find('rand(')
        
        if isRand == -1:
            #eliminates the sweep length indicator
            end = entry.find('[')
            entry = entry[0:end]
        else:
            #eliminates the randomize indicator and sweep length indicator
            end = entry.find('[')
            entry = entry[isRand+5:end]    

        #replace all 'x' values with the sweep number
        entry = entry.replace('x',str(offset))

        result = eval(entry)

        return result

    #adds a new trajectory
    def addTrajectory(self):
        global trajList,trajDict

        #show input dialog for naming the trajectory
        name, ok = QInputDialog.getText(self, 'Add Trajectory',
            'Trajectory Name:')

        #add to the trajectory list
        trajList.append(name)
        size = len(trajList)

        #select the newly made trajectory
        self.trajListBox.addItem(name)
        self.trajListBox.setCurrentRow(size-2)
        self.trajListBox.setSelectionMode(1)

        #reset the trajectory angle/duration variables
        self.trajAngle.setText('0')
        self.trajDuration.setText('0')
        self.trajSpeed.setText('0')
        self.trajLink.setText('0')

        #clear the angle/duration list boxes
        self.angleListBox.clear()
        self.durationListBox.clear()
        self.speedListBox.clear()
        self.linkApertureListBox.clear()

        #add trajectory to the trajectory menu
        self.trajectory.addItem(name)

        #add empty trajectory to the seqDict
        trajDict[name] = {
        'angle':[],
        'duration':[],
        'speed':[],
        'link':[]
        }

    #deletes the selected trajectory
    def removeTrajectory(self):
        global trajList, trajDict

        #prevent deleting 'None'
        size = len(trajList)
        if size == 1:
            return

        #selected item and its index
        item = self.trajListBox.currentItem()
        index = self.trajListBox.currentRow()

        #delete trajectory from the list box
        self.trajListBox.takeItem(self.trajListBox.row(item))

        #remove from trajList and trajDict
        del trajList[index+1]

        theTrajectory = item.text()
        trajDict.pop(theTrajectory)

        self.trajectory.removeItem(index + 1)

        size = len(trajList)#new number of trajectories
        if size == 1:
            #clear old values
            self.angleListBox.clear()
            self.durationListBox.clear()
            self.speedListBox.clear()
            self.linkApertureListBox.clear()
            return
        else:
            item = self.trajListBox.currentItem() #new selection
            name = item.text() #trajectory name
            self.updateTrajectory(name)

    #updates the angle/duration list boxes for the selected trajectory
    def updateTrajectory(self,name):
        global trajDict

        #what row is selected?
        row = self.angleListBox.currentRow()

        #clear old values
        self.angleListBox.clear()
        self.durationListBox.clear()
        self.speedListBox.clear()
        self.linkApertureListBox.clear()
        
        #update with new values
        angleList = trajDict[name]['angle']
        durList = trajDict[name]['duration']

        self.angleListBox.addItems(angleList)
        self.durationListBox.addItems(durList)

        #check for 'speed' key, due to update compatability
        if 'speed' in trajDict[name].keys():
            speedList = trajDict[name]['speed']
        else:
            for trajectory in trajDict:
                angleList = trajDict[trajectory]['angle']
                speedList = ['0' for _ in range(len(angleList))]
                trajDict[trajectory]['speed'] = speedList

        self.speedListBox.addItems(speedList)

        #check for 'link' key, due to update compatability
        if 'link' in trajDict[name].keys():
            linkList = trajDict[name]['link']
        else:
            for trajectory in trajDict:
                angleList = trajDict[trajectory]['angle']
                linkList = ['0' for _ in range(len(angleList))]
                trajDict[trajectory]['link'] = linkList

        self.linkApertureListBox.addItems(linkList)

        #set the selected row to what it originally was
        self.angleListBox.setCurrentRow(row)
        self.durationListBox.setCurrentRow(row)
        self.speedListBox.setCurrentRow(row)
        self.linkApertureListBox.setCurrentRow(row)

    #adds new object to the stimulus design
    def addStimObject(self):
        global objectList

        objectList.append('Circle')
        self.objectListBox.addItem('Circle')
        self.addStimDict()

        numObjects = len(objectList)

        self.objectListBox.setCurrentRow(numObjects-1)
        self.setObjectParameters(numObjects-1)
        self.displaySeqAssignments(numObjects-1)

    #removes the selected stimulus object
    def removeStimObject(self):
        global objectList

        numObjects = len(objectList)
        if numObjects == 1: #doesn't delete last object
            return

        #which object is selected
        index = self.objectListBox.currentRow()

        #remove object from the stimulus and mask list boxes
        self.objectListBox.takeItem(index)

        #remove object from the stimulus object list
        del objectList[index]

        if index == numObjects - 1: #if its the last object, no dictionary shifting is necessary
            stim.pop(index,None)
            seqAssign.pop(index,None)
        else:
            numObjects = len(objectList)
            #shift dictionary indices (for object indices 0,1,2 , deleting object 1 results in 0,1 dictionary indices)
            for object in range(index,numObjects):
                stim[object] = stim[object+1]
                seqAssign[object] = seqAssign[object+1]

            #now delete final dictionary entries
            stim.pop(numObjects,None)
            seqAssign.pop(numObjects,None)

        #refresh the GUI with the newly selected object
        index = self.objectListBox.currentRow()
        if index == -1:
            return

        self.setObjectParameters(index)
        self.displaySeqAssignments(index)

    #Uses stimulus dictionary to fill out the parameters in the GUI for the selected object
    def setObjectParameters(self,index):

        if index == -1:
            return

        for key,val in stim[index].items():
            
            if key in control:    
                #handle by control type
                type = control[key].__class__.__name__
                if type == 'QLineEdit':
                    control[key].setText(str(val))

                elif type == 'QComboBox':
                    #which index has the text
                    items = [control[key].itemText(i) for i in range(control[key].count())]

                    if val == '':
                        whichItem = 0
                    else:
                        whichItem = items.index(val)

                    control[key].setCurrentIndex(whichItem)
                    
                    #flip the controls depending on the drop down menu selection
                    self.flipControls(key,val)
                               

        #populate the batch list box
        self.batchStimList.clear()
        self.batchStimList.addItems(stim[index]['batchStimList'])
        self.batchStimList.setCurrentRow(0)

        #check sequence assignments
        for key,_ in seqAssign[index].items():
            sequence = seqAssign[index][key]['sequence']
            if sequence == 'None':
                #set menu to none if there is no sequence assignment
                try:
                    control[key].setCurrentIndex(0)
                    control[key].setStyleSheet("background-color: white")
                    control[key].setStyleSheet("color: black")
                except:
                    print('Style sheet error in setObjectParameters function...nonfatal.')
            else:
                #which item in sequence menu is it?
                whichItem = seqList.index(sequence)
                if whichItem == -1:
                    return

                try:
                    control[key].setCurrentIndex(whichItem+1)
                    control[key].setStyleSheet("background-color: rgba(150, 245, 150, 150)")
                except:
                    print('Style sheet error in setObjectParameters function...nonfatal.')

    #Finds sequence assignments, and displays what they are at the bottom of the GUI
    def displaySeqAssignments(self,objectNum):
        seqDisplay = []

        for key,_ in seqAssign[objectNum].items():
            sequence = seqAssign[objectNum][key]['sequence']
            if sequence != 'None':
                seqDisplay.append('[' + str(objectNum) + '] ' + seqAssign[objectNum][key]['parent'] + ' (' + seqAssign[objectNum][key]['sequence'] + ') : ')
                seqDisplay.append(','.join(seqDict[sequence]) + '\n')

        #convert list to string
        seqDisplay = ''.join(seqDisplay)
        #display on GUI
        self.sequenceMessage.setText(seqDisplay)

    #Changes controls based on object Type
    def flipControls(self,controlName,selection):
        
        if selection == 'Circle' and controlName == 'objectType':
            
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            
            for theControl in allSettings:
                if theControl in circleSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Rectangle' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.orientationLabel,9,0)
            self.designPanelLayout.addWidget(self.orientation,9,1)
            self.designPanelLayout.addWidget(self.orientationSeq,9,2)
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            self.designPanelLayout.addWidget(self.lengthLabel,8,0)
            self.designPanelLayout.addWidget(self.length,8,1)
            self.designPanelLayout.addWidget(self.lengthSeq,8,2)

            self.designPanelLayout.addWidget(self.widthLabel,7,0)
            self.designPanelLayout.addWidget(self.width,7,1)
            self.designPanelLayout.addWidget(self.widthSeq,7,2)

            for theControl in allSettings:
                if theControl in rectangleSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())
       
        elif selection == 'Grating' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.orientationLabel,10,0)
            self.designPanelLayout.addWidget(self.orientation,10,1)
            self.designPanelLayout.addWidget(self.orientationSeq,10,2)
            self.designPanelLayout.addWidget(self.angleLabel,8,8)
            self.designPanelLayout.addWidget(self.angle,8,9)
            self.designPanelLayout.addWidget(self.angleSeq,8,10)
            self.designPanelLayout.addWidget(self.driftFreqLabel,7,8)
            self.designPanelLayout.addWidget(self.driftFreq,7,9)
            self.designPanelLayout.addWidget(self.driftFreqSeq,7,10)
            
            for theControl in allSettings:
                if theControl in gratingSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Checkerboard' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)

            for theControl in allSettings:
                if theControl in checkerboardSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            #recursive call to set the positional shift type controls for checkerboard noise
            self.flipControls('PositionalShiftType',self.PositionalShiftType.currentText())

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Checkerboard 1D' and controlName == 'objectType':
        
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)

            self.designPanelLayout.addWidget(self.lengthLabel,8,0)
            self.designPanelLayout.addWidget(self.length,8,1)
            self.designPanelLayout.addWidget(self.lengthSeq,8,2)

            self.designPanelLayout.addWidget(self.widthLabel,9,0)
            self.designPanelLayout.addWidget(self.width,9,1)
            self.designPanelLayout.addWidget(self.widthSeq,9,2)

            self.designPanelLayout.addWidget(self.orientationLabel,11,0)
            self.designPanelLayout.addWidget(self.orientation,11,1)
            self.designPanelLayout.addWidget(self.orientationSeq,11,2)

            for theControl in allSettings:
                if theControl in checkerboard1DSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Cloud' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)

            for theControl in allSettings:
                if theControl in cloudSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Windmill' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.orientationLabel,9,0)
            self.designPanelLayout.addWidget(self.orientation,9,1)
            self.designPanelLayout.addWidget(self.orientationSeq,9,2)
            self.designPanelLayout.addWidget(self.driftFreqLabel,8,8)
            self.designPanelLayout.addWidget(self.driftFreq,8,9)
            self.designPanelLayout.addWidget(self.driftFreqSeq,8,10)

            for theControl in allSettings:
                if theControl in windmillSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Annulus' and controlName == 'objectType':

            for theControl in allSettings:
                if theControl in annulusSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Image' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
 
            for theControl in allSettings:
                if theControl in imageSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Frames' and controlName == 'objectType':
 
            for theControl in allSettings:
                if theControl in frameSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Batch' and controlName == 'objectType':
            index = self.stimBank.currentRow()

            self.batchStimMenu.clear()
            stimList = self.getStimulusBank()
            self.batchStimMenu.addItems(stimList)

            self.stimBank.setCurrentRow(index)

            for theControl in allSettings:
                if theControl in batchSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif selection == 'Snake' and controlName == 'objectType':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)

            for theControl in allSettings:
                if theControl in snakeSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Random Dot' and controlName == 'objectType':
            for theControl in allSettings:
                if theControl in randomDotSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()
            
            self.flipControls('motionType',self.motionType.currentText())
     
        elif selection == 'Static' and controlName == 'motionType':
            if self.objectType.currentText() == 'Random Dot':
                for theControl in allMotionSettings:
                    if theControl in randomDotMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            else:
                for theControl in allMotionSettings:
                    if theControl in staticMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()

        elif selection == 'Drift' and controlName == 'motionType':
            #self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
            #Grating and windmill have different options for motion than other stimuli
            if self.objectType.currentText() == 'Grating':
                for theControl in allMotionSettings:
                    if theControl in driftGratingMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
                        
            elif self.objectType.currentText() == 'Windmill':
                for theControl in allMotionSettings:
                    if theControl in windmillMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            elif self.objectType.currentText() == 'Random Dot':
                for theControl in allMotionSettings:
                    if theControl in randomDotMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            else:
                for theControl in allMotionSettings:
                    if theControl in driftMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()

        elif selection == 'Random Walk' and controlName == 'motionType':
            if self.objectType.currentText() == 'Random Dot':
                for theControl in allMotionSettings:
                    if theControl in randomDotMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            elif self.objectType.currentText() == 'Grating':
                for theControl in allMotionSettings:
                    if theControl in randomWalkGratingMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            else:
                for theControl in allMotionSettings:
                    if theControl in randomWalkMotionSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()

        elif selection == 'Static' and controlName == 'modulationType':

            for theControl in allModulationSettings:
                if theControl in staticModSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif selection == 'Noise' and controlName == 'modulationType':

            for theControl in allModulationSettings:
                if theControl in noiseModSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif selection != 'Static' and controlName == 'modulationType':
           
            for theControl in allModulationSettings:
                if theControl in dynamicModSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif selection == 'Cartesian' and controlName == 'coordinateType':

            for theControl in allCoordinateSettings:
                if theControl in cartesianSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()
                    
        elif selection == 'Polar' and controlName == 'coordinateType':

            for theControl in allCoordinateSettings:
                if theControl in polarSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif selection == 'Cartesian' and controlName == 'maskCoordinateType':
        
            for theControl in allCoordinateMaskSettings:
                if theControl in cartesianMaskSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()


        elif selection == 'Polar' and controlName == 'maskCoordinateType':
          
            for theControl in allCoordinateMaskSettings:
                if theControl in polarMaskSettings:
                    control[theControl].show()
                else:
                    control[theControl].hide()

        elif controlName == 'PositionalShiftType':
             #Set the positional shift controls
            if self.PositionalShiftType.currentText() == 'Static':
                for theControl in allPositionalShiftSettings:
                    if theControl in staticPositionalShiftSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()
            elif self.PositionalShiftType.currentText() == 'Random':
                for theControl in allPositionalShiftSettings:
                    if theControl in randomPositionalShiftSettings:
                        control[theControl].show()
                    else:
                        control[theControl].hide()

        
    #Converts 0-255 range to -1 to 1 range
    #Does this using gamma correction for whatever gamma table is loaded
    def getBackground(self):
        bgndStr = self.background.text()

        MaxValue = 2**BitDepth - 1

        if len(bgndStr) > 0:
            if bgndStr.isnumeric():
                val = int(self.background.text())

                # if val > 255:
                #     val = 255

                #12 bit intensity (0-4095) encoding instead of original 8 bit (0-255)
                if val > MaxValue:
                    val = MaxValue
                    self.background.setText(str(MaxValue))

                if val < 0:
                    val = 0

                gammaCorrectedVal = float(gammaTable[val])

                # bgnd = (2 * gammaCorrectedVal/255.) - 1 #normalize from -1 to 1

                bgnd = (2 * gammaCorrectedVal/float(MaxValue)) - 1 #normalize from -1 to 1
            else:
                control['background'].setText('0')
                val = float(gammaTable[0])

                bgnd = (2 * val/float(Maxvalue)) - 1 #normalize from -1 to 1

                # bgnd = (2 * val/255.) - 1 #normalize from -1 to 1

            return bgnd
        else:
            return

    #flips the sync spot on or off
    def drawSyncSpot(self,syncSpot,contrastVal):
        if self.syncSpot.isChecked():
            syncSpot.setContrast(contrastVal)
            if isOpen == 1:
                syncSpot.draw()

    #Opens a stimulus window
    def initializeSession(self):
        global win,isOpen,ifi

        bgnd = self.getBackground()

        #get the resolution of the selected monitor
        monitor = int(self.monitor.currentText())
        resolution = QDesktopWidget().screenGeometry(monitor)

        win = visual.Window(
            size=[resolution.width(),resolution.height()],
            units="pix",
            fullscr=False,
            color=[bgnd, bgnd, bgnd],
            allowStencil=True,
            winType = 'pyglet',
            screen = monitor,
            allowGUI = False,
        )

        isOpen = 1 #window is open

        #Frame rate
        rate = self.measureFrameRate()

        ifi = 1./rate

        ppm = float(self.ppm.text())

        #build the sync spot stimulus object
        syncSpot = visual.Rect(
        win = win,
        units = 'pix',
        width = 80 * ppm,
        height = 80 * ppm,
        fillColor = [1,1,1],
        lineColor = [1,1,1],
        contrast = -1,
        pos = (532-40,-404+40)
        )
        self.drawSyncSpot(syncSpot,-1) #dark sync spot
        win.flip()

    #Closes any open StimGen session
    def closeStimGenSession(self):
        global isOpen, win
        try:
            win.close()
            isOpen = 0 #window is open
        except NameError:
            return

    #Prints the measured frame rate of the open window to the terminal
    def measureFrameRate(self):
        if isOpen:
            rate = win.getActualFrameRate()
            print('Frame Rate: ' + str(rate) + ' Hz')
            return rate

    #Fills out the stimulus parameters into a structure
    def runStim(self,exportStimulus):
        global runTime,stimID, NI_FLAG,cloudArray,trajSegments

        #sets random number generator seed
        seed(1)

        #Blocks stimulus runs if the centering calibration is active
        # if centeringActive == 1:
            # return

        #If exportStimulus is set, the stimulus will run but not be presented,
        #and the frames will be exported as a bitmap file.

        originalStimulus = self.stimBank.currentItem()
        # index = self.stimBank.currentRow()
        originalStimName = originalStimulus.text()

        #BATCH STIMULUS LOOP
        if stim[0]['objectType'] == 'Batch':
            isBatch = 1
            numBatchStimuli = len(stim[0]['batchStimList'])
            stimList = stim[0]['batchStimList'] #save copy of the batch list
        else:
            isBatch = 0
            numBatchStimuli = 1
            stimList = [originalStimName]

        if stim[0]['objectType'] == 'Frames':
            isFrameStimulus = 1
        else:
            isFrameStimulus = 0

        if numBatchStimuli == 0:
            return #abort stimulus if none were defined

        for batchStim in range(numBatchStimuli):
            #fetch the stimulus dictionary for each subsequent batch stimulus
            if isBatch:
                theStimulus = stimList[batchStim]
                self.fetchStimDict(theStimulus)

            #stimID
            stimID = self.stimID.text()
            if len(stimID) == 0:
                stimID = 0
            else:
                stimID = int(stimID)

            #stim dictionary holds the parameters for all the objects
            numObjects = len(stim)

            #trajectory segment timing dictionary
            trajSegments = {}
            for object in range(numObjects):
                trajSegments[object] = {
                'numSegments':0,
                'segments':{},
                'startFrame':{}
                }
            
            #global parameters
            ppm = float(self.ppm.text())
            xOffset = int(self.xOffset.text())
            yOffset = int(self.yOffset.text())
            trialTime = float(self.trialTime.text())
            repeats = int(self.repeats.text())

            #build the sync spot stimulus object
            syncSpot = visual.Rect(
            win = win,
            units = 'pix',
            width = 80 * ppm,
            height = 80 * ppm,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = -1,
            pos = (532-40,-404+40)
            )

            self.drawSyncSpot(syncSpot,-1) #dark sync spot
            win.flip()

            if self.loopCheck.isChecked() == True:
                repeats = 1000
            bgnd = self.getBackground()

            #runTime dictionary is created here, and will hold parameters
            #calculated at run time for each object
            runTime = {}

            #holds any motion cloud image arrays that are defined
            cloudArray = {}
            
            randomAngles = {}

            #Timer dictionaries
            timer = {}

            #define the masks/aperture
            if stim[0]['apertureStatus'] == 'On':
                aperture = visual.Aperture(
                win = win,
                units = 'pix',
                shape = 'circle',
                size = stim[0]['apertureDiam'] * ppm,
                inverted = False,
                pos = (xOffset * ppm,yOffset * ppm)
                )
                aperture.enabled = True

            
                
            #parallel port address
            # port = parallel.ParallelPort(address=0x0378)
            # print(port)

            #make empty runtime dictionary
            #holds parameters that change with time during the stimulus
            for i in range(numObjects):
                runTime[i] = {
                'delayFrames':0,
                'frames':0,
                'startX':0,
                'startY':0,
                'halfCycle':0,
                'cycleCount':1,
                'noiseCycle':0,
                'phase':0,
                'driftIncrement':0,
                'firstIntensity':0,
                'secondIntensity':0,
                'stimulus':0,
                'stimFrame':0,
                'trajectory':{
                    'angle':[],
                    'startFrame':[],
                    'finalX':[],
                    'finalY':[]
                },
                'randomWalkAngle':0,
                'randomWalkInterval':0,
                'randomWalkFrameCount':0
                }

                #set up array of potential motion clouds for each object
                cloudArray[i] = {
                'MotionCloud':[]
                }

                
                timer[i] = 0

            #start at 0 sweeps
            numSweeps = 0

            #check for sequence assignments to get the total number of sweeps
            for i in range(numObjects):

                for key,_ in seqAssign[i].items():
                    sequence = seqAssign[i][key]['sequence']
                    
                    numSweepsTemp = 0
                    
                    if sequence != 'None':
                        #extract sequence entry
                        entry = seqDict[sequence]
                        
                        #determine if the sequence entry is an expression or a list of values
                        for subEntry in entry:
                            SeqType = self.CheckSequenceType(subEntry)
                        
                            if SeqType == 'Expression':
                                numSweepsTemp += self.SeqExpressionLen(subEntry)
                            else:
                                numSweepsTemp += 1
                                # #size of entry
                                # size = len(entry)
                                # if size > numSweeps:
                                #     numSweeps = size
                            
                        if(numSweepsTemp > numSweeps):
                            numSweeps = numSweepsTemp

                #if trajectory, check if it contains sequences and add them to the sweep count
                if stim[i]['trajectory'] != 'None':
                    name = stim[i]['trajectory']
                    numSegments = len(trajDict[name]['angle'])

                    for segment in range(numSegments):
                        if trajDict[name]['angle'][segment].isnumeric():
                            #numeric entry
                            continue
                        elif str(trajDict[name]['angle'][segment]) in seqList:
                            #is the entry a sequence?
                            #If so, replace the trajectory segment with the sequence entry for the current sweep
                            sequence = str(trajDict[name]['angle'][segment])
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

            # #What is the total duration of the stimulus, including delays?
            # durList = []
            # durList = [runTime[i]['delayFrames'] + runTime[i]['frames'] for i in range(numObjects)]
            # totalDuration = max(durList)

            #if no sequences are assigned or they are all empty, set sweeps to 1
            if numSweeps == 0:
                numSweeps = 1

            #new list for trigger timestamps
            triggerTimeStamps = []
            objectTimeStamps = []

            #Set up frame time stamp recorder
            frameTimeStamps = np.zeros((1,numSweeps*repeats))
            
            #STIMULUS LOOP #Loop through repeats
            for repeat in range(repeats): #use repeat setting for first object

                #loop through sweeps from sequence assignments
                for sweep in range(numSweeps):

                    #ensures consistent seeds for each sweep
                    seed(1)

                    #Instantiate a new random number generator and a second one for parallel use
                    #I'm using the second number generator in the noise stimulus, so that the same sequence of noise occurs
                    #whether I'm implementing random positional shifts or not. The positional shifts also use randomization,
                    #so I need to use a different number generator instance to avoid disrupting the pixel noise sequence.

                    rng = np.random.default_rng(1)

                    #check for abort click
                    if abortStatus:
                        self.stimCountDown.setText('')
                        self.sweepMonitor.setText('')
                        return

                    #writes the stimulus to an HDF5 file for retrieval by ScanImage and WaveSurfer/Turntable through the ethernet port
                    writeHDF5(stim,seqAssign,seqDict,trajDict,maskDict,originalStimName)

                    #reset frame counts
                    frameCount = 0

                    #keeps track of motion clouds, for random walk coordination
                    firstCloud = -1
                    randomAngleCount = np.zeros(numObjects,dtype=np.int8)

                    #check for sequence assignments and fill runtime dictionary
                    for i in range(numObjects):
                        
                        for key,_ in seqAssign[i].items():
                            sequence = seqAssign[i][key]['sequence']
                            if sequence != 'None':
                                #extract sequence entry
                                entry = seqDict[sequence]
                                #parent control name
                                parent = seqAssign[i][key]['parent']

                                #is this sequence an expression or a list of values?
                               #determine if the sequence entry is an expression or a list of values
                                # SeqType = self.CheckSequenceType(entry)
                                
                                # if SeqType == 'Expression':
                                #print(self.resolveSeqExpression(entry,sweep))
                                stim[i][parent] = self.resolveSeqExpression(entry,sweep)
                                # else:
                                #     #insert sequence variable into the stim dictionary for each sweep
                                #     stim[i][parent] = float(entry[sweep])

                        #Set runTime dictionary for each sweeps
                        #piggy backs off the seqAssign loop, which also iterates through the objects

                        #frame delay for each objectType
                        runTime[i]['delayFrames'] = int(round(stim[i]['delay']/ifi)) #round to nearest integer

                        #frame duration for each object
                        runTime[i]['frames'] = int(round(stim[i]['duration']/ifi)) #round to nearest integer

                        #What is the total duration of the stimulus, including delays?
                        durList = []
                        durList = [runTime[i]['delayFrames'] + runTime[i]['frames'] for i in range(numObjects)]
                        totalDuration = max(durList)

                       
                        #array of random angles that may be used for random walk stimuli
                        randomAngles[i] = {
                            'angles': np.zeros(totalDuration+1)
                        }


                        #starting positions of each object
                        if stim[i]['coordinateType'] == 'Cartesian':
                            xPos = stim[i]['xPos']
                            yPos = stim[i]['yPos']
                        elif stim[i]['coordinateType'] == 'Polar':
                            xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
                            yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)
                            
                        runTime[i]['startX'] = ppm * (xOffset + xPos) + ppm * stim[i]['startRad'] * np.cos(stim[i]['angle'] * np.pi/180.)
                        runTime[i]['startY'] = ppm * (yOffset + yPos) + ppm * stim[i]['startRad'] * np.sin(stim[i]['angle'] * np.pi/180.)

                        #Motion parameters
                        if stim[i]['motionType'] == 'Drift':
                            #if stim[i]['objectType'] == 'Grating':
                            runTime[i]['driftIncrement'] =  stim[i]['driftFreq'] * ifi
                                    # elif stim[i]['objectType'] == 'Windmill':
                                    #   runTime[i]['driftIncrement'] = stim[i]['driftFreq'] * ifi
                        elif stim[i]['motionType'] == 'Random Walk':
                            runTime[i]['randomWalkInterval'] =  round((1. / stim[i]['walkFreq']) / ifi)
                            runTime[i]['randomWalkFrameCount'] = 0
                            runTime[i]['driftIncrement'] =  stim[i]['driftFreq'] * ifi
                            

                        #Modulation parameters
                        if (stim[i]['modulationType'] == 'Square') or (stim[i]['modulationType'] == 'Sine'):
                            runTime[i]['halfCycle'] = int(round((0.5/stim[i]['modulationFreq'])/ifi)) # number of frames per half cycle
                            runTime[i]['cycleCount'] = 1

                        elif stim[i]['modulationType'] == 'Chirp':
                            if stim[i]['objectType'] == 'Grating':
                                chirpWave = self.buildChirp(i,ifi,0) #not gamma corrected, this will occur when the grating is calculated
                            else:
                                chirpWave = self.buildChirp(i,ifi,1) #gamma corrected for all other objects

                            #make sure total duration matches frame number if the stimulus is a chirp
                            stim[i]['contrast'] = 100
                            totalDuration = chirpWave.shape[0]
                            runTime[i]['frames'] = totalDuration

                        #noise frames per cycle
                        if stim[i]['objectType'] == 'Checkerboard' or stim[i]['objectType'] == 'Checkerboard 1D':
                            # runTime[i]['halfCycle'] = int(round((0.5/stim[i]['modulationFreq'])/ifi)) # number of frames per half cycle
                            runTime[i]['noiseCycle'] = int(round((1/stim[i]['modulationFreq']) / ifi)) # number of frames per half cycle

                            runTime[i]['cycleCount'] = 1

                        runTime[i]['phase'] = stim[i]['spatialPhase'] / 360.

                        #intensities
                        firstIntensity,secondIntensity = self.getIntensity(i)
                        runTime[i]['firstIntensity'] = firstIntensity
                        runTime[i]['secondIntensity'] = secondIntensity

                        
                        #Define stimulus
                        runTime[i]['stimulus'] = self.defineStimulus(runTime,ppm,xOffset,yOffset,i,ifi,sweep)

                        #setup the initial frame of the motion cloud stimulus
                        # motionCloud = cloudArray[i]['MotionCloud']

                        if stim[i]['objectType'] == 'Cloud':
                            #polar coordinates or cartesian coordinates?
                            if stim[i]['coordinateType'] == 'Cartesian':
                                xPos = stim[i]['xPos']
                                yPos = stim[i]['yPos']
                            elif stim[i]['coordinateType'] == 'Polar':
                                xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
                                yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)

                            #initialize a cloud aperture at the origin
                            cloudAperture = visual.Aperture(
                                win = win,
                                units = 'pix',
                                shape = 'circle',
                                size = stim[i]['objectAperture'] * ppm,
                                inverted = False,
                                pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                                )


                            stimulus = visual.ImageStim(
                                win=win,
                                units = 'pix',
                                image = cloudArray[i]['MotionCloud'][:,:,0],
                                size = (1280,800),
                                # ori = stim[i]['cloudOrient'],
                                pos = ((xOffset) * ppm,(yOffset) * ppm)
                                )
                            runTime[i]['stimulus'] = stimulus

                            

                        #reset stimulus frame counts
                        runTime[i]['stimFrame'] = 0
                        #reset cycle counts
                        runTime[i]['cycleCount'] = 1

                        #calculate trajectory frames
                        if stim[i]['trajectory'] != 'None':
                            #sets random number generator seed. Ensures that random walk trajectories are identical to
                            #those defined by standard motion random walk earlier in the code.
                            seed(1) 

                            self.calculateTrajectory(stim[i]['trajectory'],i,sweep,ifi,ppm,xOffset,yOffset)
                            runTime[i]['frames'] = len(trajectoryStim[i]['yPos'])

                        #Create an array that holds random walk angles for each object.
                        #This is for potential random walk stimuli, and just ensures consistent seeding across objects
                        seed(1)
                        randomAngles[i]['angles'] = [randint(0,360) for _ in range(totalDuration + 1)]

                        #If the object in question is a grating, fix the random angles to be +/- along the axis of motion
                        if stim[i]['objectType'] == 'Grating':
                            randomAngles[i]['angles'] = [1 if v < 180 else -1 for v in randomAngles[i]['angles']]

                    #define the masks/aperture
                    if stim[0]['apertureStatus'] == 'On':

                        if stim[i]['coordinateType'] == 'Cartesian':
                            xPos = stim[i]['xPos']
                            yPos = stim[i]['yPos']
                        elif stim[i]['coordinateType'] == 'Polar':
                            xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
                            yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)
                            
                        aperture = visual.Aperture(
                        win = win,
                        units = 'pix',
                        shape = 'circle',
                        size = stim[0]['apertureDiam'] * ppm,
                        inverted = False,

                        #offset of the aperture follows the local offset of the stimulus object
                        pos = ((xOffset + xPos)* ppm,(yOffset + yPos) * ppm)

                        #offset of the aperture only obeys global offset, not local offset
                        # pos = ((xOffset)* ppm,(yOffset) * ppm)
                        )
                        aperture.enabled = True

                    frameTimeStamps = np.resize(frameTimeStamps,(totalDuration,numSweeps*repeats))

                    #Which trigger interface is it?
                    if globalSettings['triggerInterface'] == 'Parallel Port':
                        
                        portAddress = globalSettings['parallelPortAddress']
                        port = parallel.ParallelPort(address = portAddress)
                        inputPin = globalSettings['digitalIn']
                        outputPin = globalSettings['digitalOut']

                        if port:

                            #Wait for parallel port input trigger
                            if self.trigger.currentText() == 'Wait For Trigger':
                                self.stimCountDown.setText('Waiting...')
                                self.stimCountDown.repaint()

                                port.setPin(inputPin,0) #set the pin low
                                # port.setPin(2,0) #set the pin low
                                triggerStatus = False
                                while triggerStatus == False:
                                    #keep reading the pin to check for trigger
                                    triggerStatus = port.readPin(inputPin)

                                #trigger recieved
                                triggerTime = time()
                                if repeat == 0 and sweep == 0:
                                    startTime = triggerTime

                            elif self.trigger.currentText() == 'Send Trigger':
                                #Send parallel port output trigger
                                (interface,digitalOut,digitalIn,portAddress) = self.getTriggerSettings()
                                triggerTime = self.sendTTLPulse(interface,digitalOut,digitalIn,portAddress)

                                if repeat == 0 and sweep == 0:
                                    startTime = triggerTime

                            else:
                                #No trigger selected
                                triggerTime = time()
                                
                                if repeat == 0 and sweep == 0:
                                    startTime = triggerTime

                            #Trigger sent, received, or no trigger (restarting stimulus loop)
                            triggerTimeStamps.append(triggerTime - startTime)
                        else:
                            print('Parallel port cannot be found, trigger cannot be sent.')
                            self.stimCountDown.setText('')
                            self.sweepMonitor.setText('')

                            triggerTime = time()
                            if repeat == 0 and sweep == 0:
                                    startTime = triggerTime
                            
                            #Trigger sent, received, or no trigger (restarting stimulus loop)
                            triggerTimeStamps.append(triggerTime - startTime)

                    elif globalSettings['triggerInterface'] == 'Nidaq Board':
                        if NI_FLAG:
                            digitalIn = globalSettings['digitalIn']
                            digitalOut = globalSettings['digitalOut']

                            if self.trigger.currentText() == 'Wait For Trigger':

                                if digitalIn:
                                    self.stimCountDown.setText('Waiting...')
                                    self.stimCountDown.repaint()
                                    #Wait for input trigger from a Nidaq digital input
                                    with ni.Task() as task:
                                        task.di_channels.add_di_chan(digitalIn)
                                        triggerStatus = False
                                        while triggerStatus == False:
                                            #read digital input P0.0 from the ephys board
                                            triggerStatus = task.read()
                                        # self.stimCountDown.setText('')
                                else:
                                    print("No digital input defined, couldn't wait for trigger")
                                    return
                        
                            elif self.trigger.currentText() == 'Send Trigger':
                                if digitalOut:
                                    #Send output trigger from a Nidaq digital out
                                    with ni.Task() as task:
                                        task.do_channels.add_do_chan(digitalOut)
                                        task.write(False)
                                        task.write(True)
                                        task.write(False)
                        else:
                            if repeat == 0 and sweep == 0:
                                startTime = time()
                            continue
                    
                    writeTimestamps('Triggers',triggerTimeStamps)

                    #overall timer that is started before delay
                    totalTimer = 0
                    totalTimer = core.Clock()

                    objectON = 0
                    onTime = 0

                    #loop through total stimulus duration
                    for frame in range(totalDuration):
                        #display the timer
                        self.stimCountDown.setText("%.2f" % (totalTimer.getTime()))
                        self.sweepMonitor.setText(str(sweep + 1) + '/' + str(numSweeps))

                        #flip sync spot to dark as default
                        self.drawSyncSpot(syncSpot,-1)

                        #Loop through each object
                        for i in range(numObjects):
                            
                            #extract stimulus intensity so you only do it once per object
                            firstIntensity = runTime[i]['firstIntensity']
                            secondIntensity = runTime[i]['secondIntensity']
                            
                            #Only check delay status if this isn't a .bmp frame stimulus,
                            #which already has the delays and duration built into it.
                            if isFrameStimulus == 0:
                                #delay
                                if frame < runTime[i]['delayFrames']:
                                    continue

                                #duration
                                if frame >= runTime[i]['delayFrames'] + runTime[i]['frames']:
                                    continue

                            
                            #sync spot bright
                            self.drawSyncSpot(syncSpot,1)

                            #timestamp the object turning on
                            if objectON == 0:
                                objectON = 1
                                

                            #start timer only on first frame of the stimulus
                            # if runTime[i]['stimFrame'] == 0:
                            #     timer[i] = 0
                            #     timer[i] = core.Clock()

                            #check for abort click
                            if abortStatus:
                                #Flip the window to background again
                                self.drawSyncSpot(syncSpot,-1)
                                win.flip()
                                self.stimCountDown.setText('')
                                self.sweepMonitor.setText('')
                                return

                            #Update stimulus parameters and Draw each stimulus object to the buffer window

                            #MOTION CLOUD STIMULI
                            if stim[i]['objectType'] == 'Cloud':
                                #get the motion cloud frame, depends on if it's a random walk motion or not. Random walk uses the same frame over and over
                                #at different x,y positions.
                                
                                if stim[i]['trajectory'] != 'None':
                                    runTime[i]['stimulus'].pos = self.getTrajectoryPosition(i,ifi,ppm)
                                    
                                elif stim[i]['motionType'] == "Random Walk":
                                    if firstCloud == -1:
                                        firstCloud = i

                                    if runTime[i]['randomWalkFrameCount'] > runTime[i]['randomWalkInterval']:
                                        runTime[i]['randomWalkFrameCount'] = 0

                                        #random angle between 0 and 360 degrees
                                        runTime[i]['randomWalkAngle'] = randomAngles[i]['angles'][randomAngleCount[i]]
                                        randomAngleCount[i] = randomAngleCount[i] + 1

                                        # runTime[i]['randomWalkAngle'] = randint(0,360)
                                        # print(runTime[i]['randomWalkAngle'])

                                    #coordinates the jitter for all motion clouds:
                                    #sets the walk angle to be the same as that of the first cloud definition
                                    #if only 1 cloud is defined, this will do nothing
                                    runTime[i]['randomWalkAngle'] = runTime[firstCloud]['randomWalkAngle']

                                    #increments the position of the stimulus according to the new angle
                                    x = ppm * stim[i]['speed'] * ifi * np.cos(runTime[i]['randomWalkAngle'] * np.pi/180)
                                    y = ppm * stim[i]['speed'] * ifi * np.sin(runTime[i]['randomWalkAngle'] * np.pi/180)

                                    #boundary conditions, reverse direction if stimulus begins to overrun the boundary (150 um from center)
                                    if runTime[i]['stimulus'].pos[0] + x > 150 or runTime[i]['stimulus'].pos[0] + x < -150:
                                        x = -x
                                        
                                    
                                    if runTime[i]['stimulus'].pos[1] + y > 150 or runTime[i]['stimulus'].pos[1] + y < -150:
                                        y = -y

                                    runTime[i]['stimulus'].pos += (x,y)
                                    
                                    runTime[i]['randomWalkFrameCount'] += 1
                                else:    
                                    runTime[i]['stimulus'].image = cloudArray[i]['MotionCloud'][:,:,runTime[i]['stimFrame']]
                                    # motionCloud = cloudArray[i]['MotionCloud']
                                    # stimulus = visual.ImageStim(
                                    #     win=win,
                                    #     units = 'pix',
                                    #     # image = motionCloud[:,:,runTime[i]['stimFrame']],
                                    #     image = cloudArray[i]['MotionCloud'][:,:,runTime[i]['stimFrame']],
                                    #     size = (1280,800),
                                    #     # ori = stim[i]['cloudOrient'],
                                    #     pos = ((xOffset + stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
                                    #     )

                                # runTime[i]['stimulus'] = stimulus

                            #BMP FRAME STIMULUS
                            elif stim[i]['objectType'] == 'Frames':
                                stimulus = visual.ImageStim(
                                    win=win,
                                    units = 'pix',
                                    image = stimFrames[frame],
                                    size = (1280,800),
                                    ori = 0,
                                    pos = (0,0)
                                    )

                                runTime[i]['stimulus'] = stimulus


                            #NOISE STIMULI
                            elif stim[i]['objectType'] == 'Checkerboard' or stim[i]['objectType'] == 'Checkerboard 1D':
                                #Flip the intensities between light/dark at each cycle

                                if runTime[i]['stimFrame'] == runTime[i]['noiseCycle'] * runTime[i]['cycleCount']:
                                    #Add random positional shifts

                                    #Target resolution is the multiple of the noise pixel size for the final STA.
                                    #For 100 micron noise pixels, targetresolution = 2 will yield 50 micron shifts in X and Y
                                    #and targetresolution = 4 will yield 25 micron shifts (up to 75 microns)
                                    if stim[i]['objectType'] == 'Checkerboard' and stim[i]['PositionalShiftType'] == 'Random':

                                        targetResolution = stim[i]['noiseSize'] / stim[i]['TargetResolution'] #integer multiple of the noise pixel size

                                        baselineShift = stim[i]['TargetResolution'] * ppm

                                        #Uses instantiated random number generator, which is independent of the one used
                                        #by the buildNoise and updateNoise methods in psychopy. This allows the same noise pixel
                                        #sequence to be driven both with or without random positional shifts.

                                        multiplier = rng.integers(-targetResolution+1,targetResolution) #low inclusive, high excluded
                                        xShift = multiplier * baselineShift
                                        
                                        multiplier = rng.integers(-targetResolution+1,targetResolution) #low inclusive, high excluded
                                        yShift = multiplier * baselineShift

                                        #the positional shifts operate around the origin position, 
                                        #so there won't be any random walk away from the origin over time
                                        xPosition = (xOffset + xPos) * ppm + xShift
                                        yPosition = (yOffset + yPos) * ppm + yShift

                                        runTime[i]['stimulus'].pos = (xPosition,yPosition)

                                    runTime[i]['stimulus'].updateNoise()
                                    runTime[i]['cycleCount'] = runTime[i]['cycleCount'] + 1 #counts which modulation cycle it's on

                            elif stim[i]['objectType'] == 'Snake':
                                if stim[i]['trajectory'] == 'None':
                                    xdist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.cos(stim[i]['angle'] * np.pi/180)
                                    ydist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.sin(stim[i]['angle'] * np.pi/180)

                                    x = runTime[i]['startX'] + xdist/2.
                                    y = runTime[i]['startY'] + ydist/2.

                                    runTime[i]['stimulus'].pos = (x,y)
                                    runTime[i]['stimulus'].width = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi)

                                else:
                                    #which segment are we on?
                                    for x in range(snakeStim[i]['numSegments'],0,-1): #count down
                                        if runTime[i]['stimFrame'] >= snakeStim[i]['startFrame'][x-1]:
                                            currentSegment = x-1
                                            break
                                        else:
                                            currentSegment = 0

                                    
                                    snakeStim[i]['segments'][currentSegment].pos = self.getTrajectoryPosition(i,ifi,ppm)
                                    snakeStim[i]['segments'][currentSegment].width = (stim[i]['width'] + stim[i]['speed'] * ((runTime[i]['stimFrame'] - snakeStim[i]['startFrame'][currentSegment]) * ifi)) * ppm
                                    # runTime[i]['stimulus'].pos = (x,y)


                                    #runTime[i]['stimulus'].pos = self.getTrajectoryPosition(i,ifi,ppm)


                            #ALL OTHER STIMULI
                            else:
                                #Update position for moving stimuli
                                if stim[i]['motionType'] == 'Drift':
                                    if stim[i]['objectType'] == 'Grating':
                                        runTime[i]['stimulus'].phase = runTime[i]['phase'] + runTime[i]['driftIncrement'] * runTime[i]['stimFrame']
                                    elif stim[i]['objectType'] == 'Windmill':
                                        if stim[i]['turnDirection'] == 'Clockwise':
                                            runTime[i]['stimulus'].setOri(stim[i]['orientation'] + runTime[i]['driftIncrement'] * runTime[i]['stimFrame'])
                                        elif stim[i]['turnDirection'] == 'Counterclockwise':
                                            runTime[i]['stimulus'].setOri(stim[i]['orientation'] - runTime[i]['driftIncrement'] * runTime[i]['stimFrame'])
                                    else:
                                        if stim[i]['trajectory'] == 'None':
                                            if stim[i]['objectType'] != 'Random Dot':
                                                x = runTime[i]['startX'] + ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.cos(stim[i]['angle'] * np.pi/180)
                                                y = runTime[i]['startY'] + ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.sin(stim[i]['angle'] * np.pi/180)
                                                runTime[i]['stimulus'].setPos((x,y))
                                        else:
                                            runTime[i]['stimulus'].pos = self.getTrajectoryPosition(i,ifi,ppm)
                                
                                elif stim[i]['motionType'] == 'Random Walk':
                                    #ignores the random walk fro gratings and windmills motion for now. Will update in later version.
                                    # if stim[i]['objectType'] == 'Grating':
                                    #     runTime[i]['stimulus'].phase = runTime[i]['phase'] + runTime[i]['driftIncrement'] * runTime[i]['stimFrame']
                                    if stim[i]['objectType'] == 'Windmill':
                                        if stim[i]['turnDirection'] == 'Clockwise':
                                            runTime[i]['stimulus'].setOri(stim[i]['orientation'] + runTime[i]['driftIncrement'] * runTime[i]['stimFrame'])
                                        elif stim[i]['turnDirection'] == 'Counterclockwise':
                                            runTime[i]['stimulus'].setOri(stim[i]['orientation'] - runTime[i]['driftIncrement'] * runTime[i]['stimFrame'])
                                    else:
                                        #ignores all trajectories if random walk is selected

                                        if runTime[i]['randomWalkFrameCount'] > runTime[i]['randomWalkInterval']:
                                            runTime[i]['randomWalkFrameCount'] = 0
                                            
                                            #random angle between 0 and 360 degrees
                                            # runTime[i]['randomWalkAngle'] = randint(0,360)
                                            runTime[i]['randomWalkAngle'] = randomAngles[i]['angles'][randomAngleCount[i]]
                                            randomAngleCount[i] = randomAngleCount[i] + 1
                                            
                                        if stim[i]['objectType'] == 'Grating':
                                            #this will happen on first cycle before an update, start the motion in the original direction
                                            if runTime[i]['randomWalkAngle'] == 0:
                                                runTime[i]['randomWalkAngle'] = 1
                                            runTime[i]['stimulus'].phase += runTime[i]['phase'] + runTime[i]['randomWalkAngle'] * runTime[i]['driftIncrement']
                                        else:
                                            #increments the position of the stimulus according to the new angle
                                            x = ppm * stim[i]['speed'] * ifi * np.cos(runTime[i]['randomWalkAngle'] * np.pi/180)
                                            y = ppm * stim[i]['speed'] * ifi * np.sin(runTime[i]['randomWalkAngle'] * np.pi/180)
                                        

                                        if stim[i]['objectType'] == 'Grating':
                                            pass
                                        else:
                                            if runTime[i]['stimulus'].pos[0] - runTime[i]['startX'] + x > 75 or runTime[i]['stimulus'].pos[0] - runTime[i]['startX'] + x < -75:
                                                x = -x
                                        
                                            if runTime[i]['stimulus'].pos[1] - runTime[i]['startY'] + y > 75 or runTime[i]['stimulus'].pos[1] - runTime[i]['startY'] + y < -75:
                                                y = -y

                                            runTime[i]['stimulus'].pos += (x,y)
                                       

                                        runTime[i]['randomWalkFrameCount'] += 1

                                #Update intensity for modulated stimuli

                                if stim[i]['modulationType'] == 'Square':
                                    #Flip the intensities between light/dark at each cycle
                                    if runTime[i]['stimFrame'] == runTime[i]['halfCycle'] * runTime[i]['cycleCount']:
                                        
                                        if (runTime[i]['cycleCount'] % 2) == 0:
                                            if stim[i]['objectType'] == 'Grating':
                                                gratingArray = self.CalculateGrating(i,1,stim[i]['contrast'])
                                                runTime[i]['stimulus'].tex = gratingArray
                                            else:
                                                runTime[i]['stimulus'].contrast = runTime[i]['firstIntensity']
                                             
                                        else:
                                            if stim[i]['objectType'] == 'Grating':
                                                gratingArray = self.CalculateGrating(i,-1,stim[i]['contrast'])
                                                runTime[i]['stimulus'].tex = gratingArray
                                            else:
                                                runTime[i]['stimulus'].contrast = runTime[i]['secondIntensity']
                                        
                                        runTime[i]['cycleCount'] = runTime[i]['cycleCount'] + 1 #counts which modulation cycle it's on
                                elif stim[i]['modulationType'] == 'Sine':
                                    #out of bounds intensities
                                    if stim[i]['objectType'] == 'Grating':
                                        
                                        contrastScale = (stim[i]['contrast']) * np.sin(2 * np.pi * stim[i]['modulationFreq'] * (runTime[i]['stimFrame'] * ifi))
                                        gratingArray = self.CalculateGrating(i,1,contrastScale)
                                        runTime[i]['stimulus'].tex = gratingArray

                                        #  #Flip the intensities between light/dark at each cycle
                                        # if runTime[i]['stimFrame'] == runTime[i]['halfCycle'] * runTime[i]['cycleCount']:
                                        #     if (runTime[i]['cycleCount'] % 2) == 0:
                                        #         gratingArray = self.CalculateGrating(i,1)
                                        #         runTime[i]['stimulus'].tex = gratingArray
                                        #     else:
                                        #         gratingArray = self.CalculateGrating(i,-1)
                                        #         runTime[i]['stimulus'].tex = gratingArray
                                        #     runTime[i]['cycleCount'] = runTime[i]['cycleCount'] + 1 #counts which modulation cycle it's on
                                    else:
                                        if firstIntensity - bgnd > 1:
                                            firstIntensity = bgnd + 1
                                        elif firstIntensity - bgnd < -1:
                                            firstIntensity = bgnd - 1

                                        runTime[i]['stimulus'].contrast = (stim[i]['contrast']/100.0) * np.sin(2 * np.pi * stim[i]['modulationFreq'] * (runTime[i]['stimFrame'] * ifi))

                                elif stim[i]['modulationType'] == 'Chirp':
                                    if stim[i]['objectType'] == 'Grating':
                                        contrastScale = 100 * chirpWave[runTime[i]['stimFrame']]
                                        gratingArray = self.CalculateGrating(i,1,contrastScale)
                                        runTime[i]['stimulus'].tex = gratingArray
                                    else:
                                        runTime[i]['stimulus'].contrast = chirpWave[runTime[i]['stimFrame']]
                            #
                            # testTimer = 0
                            # testTimer = core.Clock()


                            if stim[i]['objectType'] == 'Snake':
                                for segment in range(currentSegment+1):
                                    snakeStim[i]['segments'][segment].draw()
                            else:
                                #check aperture for each grating object, enables it
                                if stim[i]['objectType'] == 'Grating':
                                    # if stim[i]['objectAperture'] > 0:
                                    #     gratingAperture = visual.Aperture(
                                    #     win = win,
                                    #     units = 'pix',
                                    #     shape = 'circle',
                                    #     size = stim[i]['objectAperture'] * ppm,
                                    #     inverted = False,
                                    #     pos = (xOffset * ppm,yOffset * ppm)
                                    #     )
                                    #     gratingAperture.enabled = True

                                    # This is substitute code to allow the grating aperture to be a rectangle oriented along the motion direction
                                    #and length defined in the GUI,  width is fixed at 50 um
                                    if stim[i]['objectAperture'] > 0:
                                        gratingAperture = visual.Aperture(
                                        win = win,
                                        units = 'pix',
                                        ori = stim[i]['orientation'],
                                        shape = 'circle',
                                        size = [stim[i]['objectAperture'] * ppm,stim[i]['objectAperture'] * ppm],
                                        inverted = False,
                                        pos = (xOffset * ppm,yOffset * ppm)
                                        )
                                        gratingAperture.enabled = True
                                        # gratingAperture.setOri(-stim[i]['orientation'],True,None)
                                elif stim[i]['objectType'] == 'Checkerboard':
                                    if stim[i]['objectAperture'] > 0:
                                        checkerboardAperture = visual.Aperture(
                                        win = win,
                                        units = 'pix',
                                        shape = 'circle',
                                        size = [stim[i]['objectAperture'] * ppm,stim[i]['objectAperture'] * ppm],
                                        inverted = False,
                                        pos = (xOffset * ppm,yOffset * ppm)
                                        )
                                        checkerboardAperture.enabled = True
                                elif stim[i]['objectType'] == 'Cloud':
                                    
                                     #polar coordinates or cartesian coordinates?
                                    if stim[i]['coordinateType'] == 'Cartesian':
                                        xPos = stim[i]['xPos']
                                        yPos = stim[i]['yPos']
                                    elif stim[i]['coordinateType'] == 'Polar':
                                        xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
                                        yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)
                                        
                                    if stim[i]['objectAperture'] > 0:
                                        
                                        if stim[i]['trajectory'] != 'None':

                                            #which segment are we on?
                                            for s in range(trajSegments[i]['numSegments'],0,-1): #count down
                                                if runTime[i]['stimFrame'] >= trajSegments[i]['startFrame'][s-1]:
                                                    currentSegment = s-1
                                                    break
                                                else:
                                                    currentSegment = 0

                                            if int(trajDict[name]['link'][currentSegment]) > 0:
                                                #initial position at the beginning of this segment
                                                initX = trajectoryStim[i]['xPos'][int(trajSegments[i]['startFrame'][currentSegment] - 1)]
                                                initY = trajectoryStim[i]['yPos'][int(trajSegments[i]['startFrame'][currentSegment] - 1)]

                                                x = trajectoryStim[i]['xPos'][runTime[i]['stimFrame']] - initX
                                                y = trajectoryStim[i]['yPos'][runTime[i]['stimFrame']] - initY

                                                #Linked aperture to the trajectory
                                                cloudAperture = visual.Aperture(
                                                win = win,
                                                units = 'pix',
                                                shape = 'circle',
                                                size = stim[i]['objectAperture'] * ppm,
                                                inverted = False,
                                                pos = ((xOffset + xPos)* ppm + x,(yOffset + yPos) * ppm + y)
                                                #pos = (x,y)
                                                )
                                                
                                                cloudAperture.enabled = True
                                            else:
                                                #Static aperture
                                                cloudAperture = visual.Aperture(
                                                win = win,
                                                units = 'pix',
                                                shape = 'circle',
                                                size = stim[i]['objectAperture'] * ppm,
                                                inverted = False,
                                                pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                                                )
                                                cloudAperture.enabled = True
                                        else:
                                             #Static aperture
                                                cloudAperture = visual.Aperture(
                                                win = win,
                                                units = 'pix',
                                                shape = 'circle',
                                                size = stim[i]['objectAperture'] * ppm,
                                                inverted = False,
                                                pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                                                )
                                                cloudAperture.enabled = True
                                    else:
                                        cloudAperture.enabled = False

                                runTime[i]['stimulus'].draw() #draws every frame
     

                                #check aperture for each grating object, disables it after it was drawn as a reset for the next possible object
                                if stim[i]['objectType'] == 'Grating':
                                    if stim[i]['objectAperture'] > 0:
                                        gratingAperture.enabled = False
                                elif stim[i]['objectType'] == "Cloud":
                                    if stim[i]['objectAperture'] > 0:
                                        cloudAperture.enabled = False

                            # print(testTimer.getTime())

                            if stim[i]['gratingType'] == 'Plaid':
                                ortho.draw()

                            #draw the mask if it is defined
                            for index,_ in maskDict.items():
                                mask[index].draw()
                            #     mask[i].draw()

                            #increase stimFrame count if the code has reached here
                            runTime[i]['stimFrame'] = runTime[i]['stimFrame'] + 1

                        #Flip the window every loop no matter what
                        frameTimeStamps[frame][sweep + numSweeps*repeat] = win.flip()

                        if objectON == 1:
                            # t = (time() * 1000)
                            # print((t - startTime)/1000)
                            objectON = -1
                            onTime = time() - startTime
                            objectTimeStamps.append(onTime)
                            writeTimestamps('ON',objectTimeStamps)

                        #Save the frames to disk
                        if exportStimulus == 1:
                            self.exportStimulusFrames(originalStimName,frame)

                        frameCount = frameCount + 1

                    #Normalize first frame of the stimulus onset to zero seconds
                    whichCol = sweep + numSweeps*repeat

                    startValue = frameTimeStamps[0][whichCol]
                    frameTimeStamps[:,whichCol] -= startValue
                
                    #add on the actual measured on time
                    # frameTimeStamps += onTime

                    #flip sync spot back to dark before next sweeep
                    self.drawSyncSpot(syncSpot,-1)
                    win.flip()

                    #Save the frame time stamps to the stimulus log file
                    writeTimestamps('Frames',frameTimeStamps)

                    self.stimCountDown.setText('')
                    self.sweepMonitor.setText('')

                    #Wait for trial time to expire before starting next sweep
                    while totalTimer.getTime() < trialTime:
                        #show a seconds timer for when the trial will actually reset
                        # self.stimCountDown.setText("%.0f" % (totalTimer.getTime()))

                        #flip the sync spot at the end of the sweep
                        self.drawSyncSpot(syncSpot,-1)
                        win.flip()

                #Flip the window to background again
                self.drawSyncSpot(syncSpot,-1)
                win.flip()

    def CalculateGrating(self,i,polarity,contrast):
        # bgnd255 = int(self.background.text())
        # bgnd255 =  (2 * bgnd255/255.) - 1

        type = self.getGratingType(i)

        MaxValue = 2**BitDepth - 1

        bgnd4095 = int(self.background.text())

        if bgnd4095 == 0:
            bgnd4095 = 2047

        bgnd4095 =  (2 * bgnd4095/float(MaxValue)) - 1

        gratingSize = win.size[0]

        rowArray = np.zeros([int(gratingSize)],dtype=float)
        rowArray[:] = np.arange(int(gratingSize))

        # indexArray = bgnd255 + (polarity * contrast / 100.0) * (-1 - bgnd255) * np.sin(2 * np.pi * 1 * rowArray/(gratingSize))
        indexArray = bgnd4095 + (polarity * contrast / 100.0) * (-1 - bgnd4095) * np.sin(2 * np.pi * 1 * rowArray/(gratingSize))

        #convert to 0-255 for gamma correction
        # indexArray255 = 255 * (indexArray + 1.) / 2.
        
        #convert to 0-4095 for gamma correction
        indexArray4095 = MaxValue * (indexArray + 1.) / 2.

        if type == 'sqr':
            maxVal = np.max(indexArray4095)
            minVal = np.min(indexArray4095)
            midVal = (maxVal + minVal) / 2.
            
            indexArray4095 = np.where(indexArray4095 < midVal,minVal,maxVal)

        #Ensure no clipping
        # indexArray255 = np.where(indexArray255 > 255,255,indexArray255)
        # indexArray255 = np.where(indexArray255 < 0,0,indexArray255)

        #gamma correct the grating values
        # with np.nditer(indexArray255,op_flags=['readwrite']) as it:
        #     for x in it:
        #         x[...] = gammaTable[int(x)]

        with np.nditer(indexArray4095,op_flags=['readwrite']) as it:
            for x in it:
                x[...] = gammaTable[int(x)]

        #convert back to -1 to 1 range
        # indexArrayGamma = (2 * indexArray255/255.) - 1
        indexArrayGamma = (2 * indexArray4095/float(MaxValue)) - 1

        gratingArray = np.tile(indexArrayGamma,(int(gratingSize),1))
        
        return gratingArray

    #Defines the stimulus textures
    def defineStimulus(self,runTime,ppm,xOffset,yOffset,i,ifi,sweep):
        global mask, ortho,snakeStim,stimFrames,cloudArray#,stimArray, innerRing, outerRing

        firstIntensity = runTime[i]['firstIntensity']
        secondIntensity = runTime[i]['secondIntensity']
        bgnd = self.getBackground()
        
        MaxValue = 2**BitDepth - 1

        w = win.size[0]/2
        h = win.size[1]/2

        #polar coordinates or cartesian coordinates?
        if stim[i]['coordinateType'] == 'Cartesian':
            xPos = stim[i]['xPos']
            yPos = stim[i]['yPos']
        elif stim[i]['coordinateType'] == 'Polar':
            xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
            yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)

        # if stim[i]['maskCoordinateType'] == 'Cartesian':
        #     xPosMask = stim[i]['maskXPos']
        #     yPosMask = stim[i]['maskYPos']
        # elif stim[i]['maskCoordinateType'] == 'Polar':
        #     xPosMask = stim[i]['maskPolarRadius'] * np.cos(stim[i]['maskPolarAngle'] * pi/180)
        #     yPosMask = stim[i]['maskPolarRadius'] * np.sin(stim[i]['maskPolarAngle'] * pi/180)

        if stim[i]['objectType'] == 'Circle':

            #test draw frames to back buffer and save to an array
            # stimArray = self.getStimulusArray(ppm,i,xOffset,yOffset,xPos,yPos,firstIntensity)
            # return

            stimulus = visual.Circle(
            win = win,
            units = 'pix',
            radius = stim[i]['diameter']*ppm/2,
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = firstIntensity,
            edges = 100,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )


        elif stim[i]['objectType'] == 'Rectangle':
            #resolve masks
            #mask = self.getMask(w,h,i,ppm)

            stimulus = visual.Rect(
            win = win,
            units = 'pix',
            width = stim[i]['width'] * ppm,
            height = stim[i]['length'] * ppm,
            ori = stim[i]['orientation'],
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = firstIntensity,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )
        elif stim[i]['objectType'] == 'Grating':
            #type of grating
            type = self.getGratingType(i)


            #2022 fixes. Generate grating through numpy array, so that it can handle offset
            #backgrounds that aren't around the middle intensity value.
            
            # bgnd255 = int(self.background.text())
            # bgnd255 =  (2 * bgnd255/255.) - 1

            bgnd4095 = int(self.background.text())

            if bgnd4095 == 0:
                bgnd4095 = 2047

            bgnd4095 = (2 * bgnd4095/float(MaxValue)) - 1
            
            gratingSize = win.size[0]

            rowArray = np.zeros([int(gratingSize)],dtype=float)

            #TESTING
            rowArray[:] = np.arange(int(gratingSize))

            # indexArray = bgnd255 + (stim[i]['contrast'] / 100.0) * (-1 - bgnd255) * np.sin(2 * np.pi * 1 * rowArray/(gratingSize))
            indexArray = bgnd4095 + (stim[i]['contrast'] / 100.0) * (-1 - bgnd4095) * np.sin(2 * np.pi * 1 * rowArray/(gratingSize))

            #convert to 0-255 for gamma correction
            # indexArray255 = 255 * (indexArray + 1.) / 2.
            
            #convert to 0-4095 for gamma correction
            indexArray4095 = MaxValue * (indexArray + 1.) / 2.

            if type == 'sqr':
                maxVal = np.max(indexArray4095)
                minVal = np.min(indexArray4095)
                midVal = (maxVal + minVal) / 2.
                
                indexArray4095 = np.where(indexArray4095 < midVal,minVal,maxVal)


            #Ensure no clipping
            # indexArray255 = np.where(indexArray255 > 255,255,indexArray255)
            # indexArray255 = np.where(indexArray255 < 0,0,indexArray255)

            #gamma correct the grating values
            # with np.nditer(indexArray255,op_flags=['readwrite']) as it:
            #     for x in it:
            #         x[...] = gammaTable[int(x)]

            with np.nditer(indexArray4095,op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = gammaTable[int(x)]

            #convert back to -1 to 1 range
            # indexArrayGamma = (2 * indexArray255/255.) - 1
            indexArrayGamma = (2 * indexArray4095/float(MaxValue)) - 1

            gratingArray = np.tile(indexArrayGamma,(int(gratingSize),1))

            # rowArray = np.zeros([int(gratingSize)],dtype=float)
            # rowArray[:] = np.arange(int(gratingSize))
            # indexArray = np.tile(rowArray,(int(gratingSize),1))

            # #calculate the grating as a single cycle
            # gratingArray = bgnd + (stim[i]['contrast'] / 100.0) * (-1 - bgnd) * np.sin(2 * np.pi * 1 * indexArray/(gratingSize))

            stimulus = visual.GratingStim(
            win = win,
            units = 'pix',
            size=[gratingSize,gratingSize],
            tex = gratingArray,
            texRes = 1024,
            #mask = mask,
            #maskParams = {'fringeWidth':0.2},
            sf = stim[i]['spatialFreq'] / (ppm * 1000),
            ori = -stim[i]['orientation'],
            phase = stim[i]['spatialPhase']/360.0,#phase is fractional from 0 to 1
            color = [1,1,1],
            contrast = 1.0,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )

            #resolve masks
            #mask = self.getMask(w,h,i,ppm)

            # stimulus = visual.GratingStim(
            # win = win,
            # units = 'pix',
            # size=[w*2,h*2],
            # tex = type,
            # texRes = 1024,
            # #mask = mask,
            # #maskParams = {'fringeWidth':0.2},
            # sf = stim[i]['spatialFreq'] / (ppm * 1000),
            # ori = stim[i]['orientation'],
            # phase = stim[i]['spatialPhase']/360.0,#phase is fractional from 0 to 1
            # color = [1,1,1],
            # contrast = stim[i]['contrast']/100.0,
            # pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            # )

            #make orthogonal grating

            if stim[i]['gratingType'] == 'Plaid':
                ortho = visual.GratingStim(
                win = win,
                units = 'pix',
                size=[w*2,h*2],
                tex = type,
                texRes = 256,
                #mask = mask,
                #maskParams = {'fringeWidth':0.2},
                sf = stim[i]['spatialFreq'] / (ppm * 1000),
                ori = stim[i]['orientation'] + 90,
                phase = stim[i]['spatialPhase']/360.0,#phase is fractional from 0 to 1
                color = [1,1,1],
                contrast = stim[i]['contrast']/100.0,
                opacity = 0.5,
                pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                )
        elif stim[i]['objectType'] == 'Checkerboard':
            #set the seed for random number generator
            np.random.seed(stim[i]['noiseSeed'])

            # adjustedNoiseSize = round(stim[i]['noiseSize'] * ppm) / ppm
            # self.noiseSize.setText(str(round(adjustedNoiseSize)))

            stimulus = visual.NoiseStim(
            win = win,
            size = [512,512],
            units = 'pix',
            noiseType = stim[i]['noiseType'],
            contrast = stim[i]['contrast']/100.0,
            noiseElementSize = int(stim[i]['noiseSize'] * ppm),
            noiseClip = 1,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )
        
        elif stim[i]['objectType'] == 'Checkerboard 1D':
            #set the seed for random number generator
            np.random.seed(stim[i]['noiseSeed'])
            
            noiseY = int(stim[i]['width'] * ppm)
            noiseX = np.ceil(stim[i]['length'] * ppm)
            pixWidth = int(stim[i]['pixelWidth'] * ppm)

            #adds one extra pixel onto the end to avoid errors. Not sure about why this works yet.
            # mod = np.mod(noiseX,pixWidth)
            # noiseX += (pixWidth - mod) #+ pixWidth

            # print(noiseX,noiseY)
            # print(pixWidth,noiseY)

            stimulus = visual.NoiseStim(
            win = win,
            size = [noiseX,noiseY],
            # size = [512,512],
            units = 'pix',
            noiseType = stim[i]['noiseType'],
            contrast = stim[i]['contrast']/100.0,
            noiseElementSize = (pixWidth,noiseY),
            ori=stim[i]['orientation'],
            noiseClip = 1,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )


        elif stim[i]['objectType'] == 'Cloud':

            #Motion Clouds (keyword) parameters:
            #size    -- power of two to define the frame size (N_X, N_Y)
            #size_T  -- power of two to define the number of frames (N_frame)
            #N_X     -- frame size horizontal dimension [px]
            #N_Y     -- frame size vertical dimension [px]
            #N_frame -- number of frames [frames] (a full period in time frames)
            #alpha   -- exponent for the color envelope.
            #sf_0    -- mean spatial frequency relative to the sampling frequency.
            #ft_0    -- spatiotemporal scaling factor.
            #B_sf    -- spatial frequency bandwidth
            #V_X     -- horizontal speed component
            #V_Y     -- vertical speed component
            #B_V     -- speed bandwidth
            #theta   -- mean orientation of the Gabor kernel
            #B_theta -- orientation bandwidth
            #loggabor-- (boolean) if True it uses a log-Gabor kernel (instead of the traditional gabor)

            #DEFAULTS from MotionClouds.py
            # size of the stimulus
            #size = 8
            #size_T = 8
            #N_X = 2**size ->256 pixels
            #N_Y = N_X ->256 pixels
            #N_frame = 2**size_T ->256 frames

            # default parameters for the "standard Motion Cloud"
            #sf_0 = 0.125
            #B_sf = 0.1
            #V_X = 1.
            #V_Y = 0.
            #B_V = .5
            #theta = 0.
            #B_theta = np.pi/16.

            # define Fourier domain
            frames = int(stim[i]['duration']/ifi)
            #fx, fy, ft = mc.get_grids(mc.N_X, mc.N_Y, mc.N_frame)

             #is this a random walk motion cloud? If so, only generate a single frame
            if stim[i]['motionType'] == "Random Walk":
                frames = 0

            #proportional to 1024 x 768
            fx, fy, ft = mc.get_grids(256, 256, frames+1)
            # define an envelope

            #testTime = 0
            #testTime = core.Clock()

            #this is the most time intensive step - 50%
            
            #7/15/22
            #I've switched the cloudSpeedX and cloudSpeedY parameter inputs to this function becase the actual presentation
            #on the monitor is flipped. Now X is actually referencing horizontal dimension on the monitor/projector.
            envelope = mc.envelope_gabor(fx, fy, ft,
            V_X=stim[i]['cloudSpeedY'], V_Y=stim[i]['cloudSpeedX'], B_V=stim[i]['cloudSpeedBand'],
            sf_0=stim[i]['cloudSF'], B_sf=stim[i]['cloudSFBand'],
            theta=stim[i]['cloudOrient'] * np.pi/180, B_theta=stim[i]['cloudOrientBand'] * np.pi/180, alpha=0.)

            #print(testTime.getTime())

            #testTime = 0
            #testTime = core.Clock()

            #this is the second most time intensive step - 43%
            
            cloudArray[i]['MotionCloud'] = mc.random_cloud(envelope,seed=1)
            
            #print(testTime.getTime())

            #testTime = 0
            #testTime = core.Clock()

            #this is the least time intensive step - 6%
            cloudArray[i]['MotionCloud'] = self.rectif_stimGen( cloudArray[i]['MotionCloud'],contrast=stim[i]['contrast']/100.0,method='Michelson',verbose=False)

            #print(testTime.getTime())
            #doesn't return the stimulus, but sets the array as a global
            return
        elif stim[i]['objectType'] == 'Windmill':
            #type of grating
            type = self.getGratingType(i)

            #resolve masks
            #mask = self.getMask(w,h,i,ppm)

            #radialCycles = stim[i]['angularSpatialPeriod'] / (ppm * 1000) #degrees per cycle

            stimulus = visual.RadialStim(
            win = win,
            units = 'pix',
            size=[w*2,h*2],
            tex = type,
            texRes = 256,
            #mask = mask,
            #maskParams = {'fringeWidth':0.2},
            ori =  stim[i]['orientation'],
            angularCycles = stim[i]['angularCycles'],
            angularRes = 360,
            color = [1,1,1],
            contrast = stim[i]['contrast']/100.0,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )
        elif stim[i]['objectType'] == 'Annulus':
            #inner ring is the background
            innerRing = visual.Circle(
            win = win,
            units = 'pix',
            radius = stim[i]['innerDiameter']*ppm/4,#not sure why, but need divide by 4 for correct scale after converting to imageStim
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            contrast = bgnd,
            edges = 100,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )

            #outer ring is the specified contrast value
            outerRing = visual.Circle(
            win = win,
            units = 'pix',
            radius = stim[i]['outerDiameter']*ppm/4,#not sure why, but need divide by 4 for correct scale after converting to imageStim
            fillColor = [1,1,1],
            lineColor = [1,1,1],
            #contrast = firstIntensity,
            edges = 100,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )

            buffer = visual.BufferImageStim(
            win = win,
            stim = (outerRing,innerRing)
            )

            #work around to allow position changes to both inner and outer rings during stimulus presentation
            stimulus = visual.ImageStim(
            win = win,
            units = 'pix',
            image = buffer.image,
            contrast = firstIntensity
            )
        elif stim[i]['objectType'] == 'Snake':
            #is the snake moving using a trajectory?
            #if so, we need a different snake for every trajectory segment
            if stim[i]['trajectory'] != 'None':
                name = stim[i]['trajectory']
                numSegments = len(trajDict[name]['angle'])
            else:
                numSegments = 1

            numObjects = len(stim)

            #snake dictionary
            snakeStim = {}
            for object in range(numObjects):
                snakeStim[object] = {
                'numSegments':0,
                'segments':{},
                'startFrame':{}
                }

            snakeStim[i]['numSegments'] = numSegments


            snakeStim[i]['startFrame'][0] = 0
            totalFrames = 0
            #Find the starting frames for each segment
            for x in range(1,numSegments):
                snakeStim[i]['startFrame'][x] = totalFrames + round(float(trajDict[name]['duration'][x]) / ifi)
                totalFrames = snakeStim[i]['startFrame'][x]

            for x in range(numSegments):

                # xdist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.cos(stim[i]['angle'] * np.pi/180)
                # ydist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.sin(stim[i]['angle'] * np.pi/180)
                #
                # x = runTime[i]['startX'] + xdist/2.
                # y = runTime[i]['startY'] + ydist/2.
                angle = trajDict[name]['angle'][x]
                if angle.isnumeric():
                    orientation = angle
                    # continue
                elif str(trajDict[name]['angle'][x]) in seqList:
                    #is the entry a sequence?
                    #If so, replace the trajectory segment with the sequence entry for the current sweep
                    theSequence = str(trajDict[name]['angle'][x])
                    orientation = seqDict[theSequence][sweep]
            
                snakeStim[i]['segments'][x] = visual.Rect(
                    win = win,
                    units = 'pix',
                    width = stim[i]['width'] * ppm,
                    height = stim[i]['length'] * ppm,
                    ori = -int(orientation),
                    fillColor = [1,1,1],
                    lineColor = [1,1,1],
                    contrast = firstIntensity,
                    pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                    )
            return

        elif stim[i]['objectType'] == 'Image':
            subfolder = self.subFolder.currentText()
            imagePath = stimPath + subfolder + '/' + self.imagePath.currentText() + '.bmp'

            if imagePath != '':
                stimulus = visual.ImageStim(
                    win=win,
                    units = 'pix',
                    image = imagePath,
                    size = (1280,800),
                    ori = stim[i]['orientation'],
                    pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                    )
        elif stim[i]['objectType'] == 'Frames':
            subfolder = self.subFolder.currentText()
            framePath = stimPath + subfolder + '/Frames/' + self.framePath.currentText() + '/'

            #gets all the images in the folder, these must be .bmps and nothing else in the folder
            frameList = os.listdir(framePath)

            #load the frames into a numpy array
            stimFrames = np.array([np.array(Image.open(framePath + fname)) for fname in frameList])

            #normalize from -1 to 1
            # stimFrames = (stimFrames / 255.) * 2. - 1.
            stimFrames = (stimFrames / float(MaxValue)) * 2. - 1.

            if framePath != '':
                stimulus = visual.ImageStim(
                    win=win,
                    units = 'pix',
                    image = stimFrames[0],
                    size = (1280,800),
                    ori = 0,
                    pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                    )
        elif stim[i]['objectType'] == 'Random Dot':
            stimulus = visual.FixedDirDotStim(
                win = win,
                units = 'pix',
                seed = 1,
                nDots = int(stim[i]['numDots']),
                coherence = float(stim[i]['dotCoherence'] / 100),
                fieldPos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm),
                fieldSize = 1000 * ppm, #1000 micron diameter field size as default
                dotSize = stim[i]['diameter'] * ppm,
                dotLife = -1, #infinite dot life as default
                fieldShape = 'circle', #default shape of the array
                dir = stim[i]['signalDirection'],
                noiseDir = stim[i]['noiseDirection'],
                speed = stim[i]['speed'] * ppm * ifi, #speed is in 'units per frame'
                contrast = firstIntensity,
                signalDots = 'same',
                noiseDots = 'direction'
            )
            
            np.random.seed(1)
            # stimulus = visual.FixedDirDotStim(
            #     win = win,
            #     units = 'pix',
            #     nDots = stim[i]['numDots'],
            #     coherence = float(stim[i]['dotCoherence'] / 100),
            #     fieldPos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm),
            #     fieldSize = 1000 * ppm, #1000 micron diameter field size as default
            #     dotSize = stim[i]['diameter'] * ppm,
            #     dotLife = -1, #infinite dot life as default
            #     dir = stim[i]['signalDirection'],
            #     noiseDir = stim[i]['noiseDirection'],
            #     speed = stim[i]['speed'] * ppm * ifi, #speed is in 'units per frame'
            #     contrast = firstIntensity,
            #     signalDots = 'same',
            #     noiseDots = 'direction'
            # )

        else:
            print('other')

        mask = {}
        for i,_ in maskDict.items():
            if maskDict[i]['maskType'] == 'Circle':
                mask[i] = visual.Circle(
                win = win,
                units = 'pix',
                radius = maskDict[i]['maskDiameter']*ppm/2,
                fillColor = [1,1,1],
                lineColor = [1,1,1],
                contrast = bgnd,
                edges = 100,
                pos = ((xOffset + xPosMask) * ppm,(yOffset + yPosMask) * ppm)
                )
        return stimulus

    #Exports the stimulus into bitmap frames files
    def exportStimulusFrames(self,stimName,frame):
        #Frames are saved to a subfolder in the stimulus bank folder
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + "/Frames/"

        if os.path.isdir(path) == False:
            os.mkdir(path)

        path = path + stimName + "/"

        if os.path.isdir(path) == False:
            os.mkdir(path)

        #save the frame to .bmp file
        exportStimName = path + stimName + "_" + str(frame) + '.bmp'
        win._getFrame().save(exportStimName)

    #calculates the frames for each segent of the trajectory
    def calculateTrajectory(self,name,i,sweep,ifi,ppm,xOffset,yOffset):
        global runTime,trajectoryStim,trajSegments

        #makes a working copy of trajectory dictionary in case it contains a sequence string
        #in this case the working copy needs to be edited to contain the values within the sequence.
        liveTrajDict = copy.deepcopy(trajDict)

        numSegments = len(trajDict[name]['angle'])

        doHold = 0

        #trajectory segment timing dictionary
        
        # trajSegments[i]['numSegments'] = numSegments
        # trajSegments[i]['startFrame'][0] = 0
        # totalFrames = 0

        # #Find the starting frames for each segment
        # for x in range(1,numSegments):
        #     trajSegments[i]['startFrame'][x] = totalFrames + round(float(trajDict[name]['duration'][x-1]) / ifi)
        #     totalFrames = trajSegments[i]['startFrame'][x]

        for segment in range(numSegments):
            #check for sequence assignment for angles and duration
            if trajDict[name]['angle'][segment].isnumeric():
                #numeric entry
                
                pass
            elif str(trajDict[name]['angle'][segment]) in seqList:
                #is the angle entry a sequence?
                #If so, replace the trajectory segment with the sequence entry for the current sweep
                theSequence = str(trajDict[name]['angle'][segment])
                liveTrajDict[name]['angle'][segment] = seqDict[theSequence][sweep]
        
            if trajDict[name]['duration'][segment].isnumeric():
                #numeric entry
                pass
            elif str(trajDict[name]['duration'][segment]) in seqList:
                #is the duration entry a sequence?
                #If so, replace the trajectory segment with the sequence entry for the current sweep
                theSequence = str(trajDict[name]['duration'][segment])
                liveTrajDict[name]['duration'][segment] = seqDict[theSequence][sweep]

            #check for sequence assignment for speed
            if trajDict[name]['speed'][segment].isnumeric():
                #numeric entry
                doHold = 0
                pass
            elif str(trajDict[name]['speed'][segment]) == "*Hold*":
                doHold = 1
            elif str(trajDict[name]['speed'][segment]) == "*Walk*":
                doHold = 2 #triggers random walk to set in
            elif str(trajDict[name]['speed'][segment]) in seqList:
                #is the entry a sequence?
                #If so, replace the trajectory segment with the sequence entry for the current sweep
                theSequence = str(trajDict[name]['speed'][segment])
                liveTrajDict[name]['speed'][segment] = seqDict[theSequence][sweep]
                doHold = 0

         #trajectory segment timing dictionary
        # print(liveTrajDict)

        trajSegments[i]['numSegments'] = numSegments
        trajSegments[i]['startFrame'][0] = 0
        totalFrames = 0

        #Find the starting frames for each segment
        for x in range(1,numSegments):
            trajSegments[i]['startFrame'][x] = totalFrames + round(float(liveTrajDict[name]['duration'][x-1]) / ifi)
            totalFrames = trajSegments[i]['startFrame'][x]


        #make trajectory dictionary for the object
        trajectoryStim[i] = {
        'xPos':np.zeros(0),
        'yPos':np.zeros(0)
        }

        #polar coordinates or cartesian coordinates for start position?
        if stim[i]['coordinateType'] == 'Cartesian':
            xPos = stim[i]['xPos']
            yPos = stim[i]['yPos']
        elif stim[i]['coordinateType'] == 'Polar':
            xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * np.pi/180.)
            yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * np.pi/180.)

        
        for segment in range(numSegments):
            
            #get angles and total frames per segment
            runTime[i]['trajectory']['angle'].append(liveTrajDict[name]['angle'][segment])

            #calculate which frame each segment will start on
            if segment == 0:
                numFrames = int(round(float(liveTrajDict[name]['duration'][segment])/ifi)) #frames in the current segment
                #numFrames = numFrames + (0.5 * stim[i]['width'] / stim[i]['speed']) #add extra frames to account for the center of the starting snake getting to the turn position
                segmentFrames = np.zeros(numFrames+1)

                if str(trajDict[name]['speed'][segment]) == "*Hold*":
                    doHold = 1
                elif str(trajDict[name]['speed'][segment]) == "*Walk*":
                    doHold = 2 #triggers random walk to set in
                else:
                    doHold = 0

                if doHold == 0:
                    segmentSpeed = float(liveTrajDict[name]['speed'][segment])

                runTime[i]['trajectory']['startFrame'].append(0)

                

                if stim[i]['objectType'] == 'Snake':
                    #start position for first segment
                    startX = ppm * (xOffset + xPos) + ppm * stim[i]['startRad'] * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)
                    startY = ppm * (yOffset + yPos) + ppm * stim[i]['startRad'] * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)

                    #X position segment - half as much distance traveled because its a growing rectangle that is also changing its length simultaneously
                    segmentFrames[:] = [startX + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                    #Y position segment
                    segmentFrames[:] = [startY + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                else:
                    #start position for first segment
                    if stim[i]['objectType'] == 'Cloud':
                        #no coordinates, always centered for clouds. 
                        #Entering a coordinate moves the aperture of the cloud around, not the cloud itself.
                        startX = ppm * (xOffset) 
                        startY = ppm * (yOffset)
                    else:
                        startX = ppm * (xOffset + xPos) + ppm * stim[i]['startRad'] * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)
                        startY = ppm * (yOffset + yPos) + ppm * stim[i]['startRad'] * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)

                    #X position segment
                    # segmentFrames[:] = [startX + ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    if doHold == 0:
                        segmentFrames[:] = [startX + ppm * segmentSpeed * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                        trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                        #Y position segment
                        # segmentFrames[:] = [startY + ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                        segmentFrames[:] = [startY + ppm * segmentSpeed * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                        trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                    elif doHold == 1:
                        segmentFrames[:] = [startX for t in np.arange(0,numFrames+1,1)]
                        trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                        #Y position segment
                        # segmentFrames[:] = [startY + ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                        segmentFrames[:] = [startY for t in np.arange(0,numFrames+1,1)]
                        trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                    elif doHold == 2:
                        #random walk
                        randomWalkInterval =  round((1. / stim[i]['walkFreq']) / ifi)
                        randomWalkFrameCount = 0

                        for frame in np.arange(numFrames + 1):
                            
                            #set the angle on the first frame
                            if frame == 0:
                                randomWalkAngle = 0


                            #only reset the random walk angle according to the update frequency
                            if randomWalkFrameCount > randomWalkInterval:
                                randomWalkFrameCount = 0

                                #random angle between 0 and 360 degrees
                                randomWalkAngle = randint(0,360)
                                
                            #coordinates the jitter for all motion clouds:
                            #sets the walk angle to be the same as that of the first cloud definition
                            #if only 1 cloud is defined, this will do nothing
                            # runTime[i]['randomWalkAngle'] = runTime[firstCloud]['randomWalkAngle']
                            
                            #increments the position of the stimulus according to the new angle
                            x = ppm * stim[i]['speed'] * ifi * np.cos(randomWalkAngle * np.pi/180)
                            y = ppm * stim[i]['speed'] * ifi * np.sin(randomWalkAngle * np.pi/180)

                            size = len(trajectoryStim[i]['xPos'])
                            if size > 0:
                                newPosX = trajectoryStim[i]['xPos'][size-1] + x
                                newPosY = trajectoryStim[i]['yPos'][size-1] + y
                            else:
                                newPosX = startX + x
                                newPosY = startY + y

                                #boundary conditions, reverse direction if stimulus begins to overrun the boundary (150 um from center)
                            if newPosX > 150 * ppm or newPosX < -150* ppm:
                                x = -x
                                newPosX = trajectoryStim[i]['xPos'][size-1] + 2*x

                            if newPosY > 150* ppm or newPosY < -150* ppm:
                                y = -y
                                newPosY = trajectoryStim[i]['yPos'][size-1] + 2*y
                            

                            trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],newPosX)
                            trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],newPosY)    
                            
                            randomWalkFrameCount += 1
                            
            else:

                if str(trajDict[name]['speed'][segment]) == "*Hold*":
                    doHold = 1
                elif str(trajDict[name]['speed'][segment]) == "*Walk*":
                    doHold = 2
                else:
                    doHold = 0

                if stim[i]['objectType'] == 'Snake':
                    numFrames = int(round(float(liveTrajDict[name]['duration'][segment])/ifi)) #frames in the current segment
                    segmentFrames = np.zeros(numFrames)

                    size = len(trajectoryStim[i]['xPos'])
                    # trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],trajectoryStim[i]['xPos'][size-1])
                    # size += 1
                    prevStartPos = trajectoryStim[i]['xPos'][size-1] + 0.5 * ppm * (numFrames-1) * stim[i]['speed'] * ifi * np.cos(float(liveTrajDict[name]['angle'][segment-1]) * np.pi/180)
                    segmentFrames[:] = [prevStartPos + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                    trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                    size = len(trajectoryStim[i]['yPos'])
                    # trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],trajectoryStim[i]['yPos'][size-1])
                    # size += 1
                    prevStartPos = trajectoryStim[i]['yPos'][size-1]  + 0.5 * ppm * (numFrames-1) * stim[i]['speed'] * ifi * np.sin(float(liveTrajDict[name]['angle'][segment-1]) * np.pi/180)
                    segmentFrames[:] = [prevStartPos + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                    trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                else:
                    numFrames = int(round(float(liveTrajDict[name]['duration'][segment])/ifi)) #frames in the current segment
                    segmentFrames = np.zeros(numFrames)

                    if doHold == 1:
                        size = len(trajectoryStim[i]['xPos'])
                        prevStartPos = trajectoryStim[i]['xPos'][size-1]
                        segmentFrames[:] = [prevStartPos for t in np.arange(1,numFrames+1,1)]
                        trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                        size = len(trajectoryStim[i]['yPos'])
                        prevStartPos = trajectoryStim[i]['yPos'][size-1]
                        segmentFrames[:] = [prevStartPos for t in np.arange(1,numFrames+1,1)]
                        trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                    elif doHold == 0:
                        segmentSpeed = float(liveTrajDict[name]['speed'][segment])
                        size = len(trajectoryStim[i]['xPos'])
                        prevStartPos = trajectoryStim[i]['xPos'][size-1]
                        # segmentFrames[:] = [prevStartPos + ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                        segmentFrames[:] = [prevStartPos + ppm * segmentSpeed * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                        trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                        size = len(trajectoryStim[i]['yPos'])
                        prevStartPos = trajectoryStim[i]['yPos'][size-1]
                        # segmentFrames[:] = [prevStartPos + ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                        segmentFrames[:] = [prevStartPos + ppm * segmentSpeed * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                        trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                    elif doHold == 2:
                        #random walk
                        randomWalkInterval =  round((1. / stim[i]['walkFreq']) / ifi)
                        randomWalkFrameCount = 0

                        for frame in np.arange(numFrames + 1):
                            
                            if frame == 0:
                                randomWalkAngle = 0
                                
                            if randomWalkFrameCount > randomWalkInterval:
                                randomWalkFrameCount = 0

                                #random angle between 0 and 360 degrees
                                randomWalkAngle = randint(0,360)
                                
                            #coordinates the jitter for all motion clouds:
                            #sets the walk angle to be the same as that of the first cloud definition
                            #if only 1 cloud is defined, this will do nothing
                            # runTime[i]['randomWalkAngle'] = runTime[firstCloud]['randomWalkAngle']

                            #increments the position of the stimulus according to the new angle
                            x = ppm * stim[i]['speed'] * ifi * np.cos(randomWalkAngle * np.pi/180)
                            y = ppm * stim[i]['speed'] * ifi * np.sin(randomWalkAngle * np.pi/180)

                            #boundary conditions, reverse direction if stimulus begins to overrun the boundary (150 um from center)
                            if newPosX + x > 150 or newPosX + x < -150:
                                x = -x
                                newPosX = trajectoryStim[i]['xPos'][size-1] + x
                            if newPosY + y > 150 or newPosY + y < -150:
                                y = -y
                                newPosY = trajectoryStim[i]['yPos'][size-1] + y
                                
                            size = len(trajectoryStim[i]['xPos'])
                            if size > 0:
                                newPosX = trajectoryStim[i]['xPos'][size-1] + x
                                newPosY = trajectoryStim[i]['yPos'][size-1] + y
                            else:
                                newPosX = startX
                                newPosY = startY
                            
                            trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],newPosX)
                            trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],newPosY)    
                            
                            randomWalkFrameCount += 1
            
            
    #returns the X/Y position of the object according to its trajectory
    def getTrajectoryPosition(self,i,ifi,ppm):
        if stim[i]['objectType'] == 'Snake':
            if runTime[i]['stimFrame'] > len(trajectoryStim[i]['xPos']):
                x = trajectoryStim[i]['xPos'][len(trajectoryStim[i]['xPos'])-1]
                y = trajectoryStim[i]['yPos'][len(trajectoryStim[i]['xPos'])-1]
            else:
                x = trajectoryStim[i]['xPos'][runTime[i]['stimFrame']]
                y = trajectoryStim[i]['yPos'][runTime[i]['stimFrame']]

            #xdist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.cos(stim[i]['angle'] * np.pi/180)
            #ydist = ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.sin(stim[i]['angle'] * np.pi/180)

            # x = runTime[i]['startX'] + xdist/2.
            # y = runTime[i]['startY'] + ydist/2.
        else:
            if runTime[i]['stimFrame'] > len(trajectoryStim[i]['xPos']):
                x = trajectoryStim[i]['xPos'][len(trajectoryStim[i]['xPos'])-1]
                y = trajectoryStim[i]['yPos'][len(trajectoryStim[i]['xPos'])-1]
            else:
                x = trajectoryStim[i]['xPos'][runTime[i]['stimFrame']]
                y = trajectoryStim[i]['yPos'][runTime[i]['stimFrame']]

        return (x,y)

    #builds the wave to hold the temporal modulation for a chirp stimulus
    def buildChirp(self,i,ifi,gammaCorrected):
        global gammaTable
        contrast = stim[i]['contrast'] / 100.0 #contrast chirp maximum
        TF_low = 0.5 #low end of the temporal frequency chirp
        TF_high = 8.0 #high end of the temporal frequency chirp
        TF_mid = 3.0 #temporal frequency for the contrast chirp
        duration = int(round(15.0/ifi)) #15 second chirp stimulus

        chirpWave = np.zeros(0) #makes chirp wave of set duration
        
        [firstIntensity,secondIntensity] = self.getIntensity(i)
        bgnd = self.getBackground()

        MaxValue = 2**BitDepth - 1

        bgndRaw = int(self.background.text())
        bgndRaw = (2 * bgndRaw/float(MaxValue)) - 1

        #initial flashes
        if gammaCorrected == 1:
            segment = np.full(int(round(1./ifi)),secondIntensity)
        else:
            segment = np.full(int(round(1./ifi)),-contrast)
        chirpWave = np.append(chirpWave,segment)

        if gammaCorrected == 1:
            segment = np.full(int(round(1./ifi)),firstIntensity)
        else:
            segment = np.full(int(round(1./ifi)),contrast)
        chirpWave = np.append(chirpWave,segment)

        if gammaCorrected == 1:
            segment = np.full(int(round(1./ifi)),secondIntensity)
        else:
            segment = np.full(int(round(1./ifi)),-contrast)
        chirpWave = np.append(chirpWave,segment)

        if gammaCorrected == 1:
            segment = np.full(int(round(1./ifi)),bgnd)
        else:
            segment = np.full(int(round(1./ifi)),bgndRaw)

        chirpWave = np.append(chirpWave,segment)

        frames = int(round(4.0/ifi)) + 1 # length in frames of the temporal frequency and contrast chirps. Set for 4 seconds currently.

        #temporal frequency chirp
        segment = np.zeros(frames)
        segment[:] = [contrast * np.sin(4.0 * 2 * np.pi * 0.5 * ((TF_high * x/frames) + TF_low) * x/frames) for x in np.arange(0,frames,1)]

        #gamma correct the segment
        if gammaCorrected == 1:
            segment4095 = MaxValue * (segment + 1.) / 2.
            with np.nditer(segment4095,op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = gammaTable[int(x)]
            segment = (2 * segment4095/float(MaxValue)) - 1

        chirpWave = np.append(chirpWave,segment)

        #1 second pause in between temporal frequency and contrast chirps
        if gammaCorrected == 1:
            segment = np.full(int(round(1.0/ifi)),bgnd)
        else:
            segment = np.full(int(round(1.0/ifi)),bgndRaw)
        chirpWave = np.append(chirpWave,segment)

        #contrast chirp
        segment = np.zeros(frames)
        segment[:] = [contrast * x/frames * np.sin(4.0 * 2 * np.pi * TF_mid * x/frames) for x in np.arange(0,frames,1)]

        #gamma correct the segment
        if gammaCorrected == 1:
            segment4095 = MaxValue * (segment + 1.) / 2.
            with np.nditer(segment4095,op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = gammaTable[int(x)]
            segment = (2 * segment4095/float(MaxValue)) - 1

        chirpWave = np.append(chirpWave,segment)

        #final flash back to dark
        if gammaCorrected == 1:
            segment = np.full(int(round(1./ifi)),bgnd)
        else:
            segment = np.full(int(round(1./ifi)),bgndRaw)

        chirpWave = np.append(chirpWave,segment)

        # segment = np.full(int(round(1./ifi)),-contrast)
        # chirpWave = np.append(chirpWave,segment)

        return chirpWave

    #returns the type of grating in the GratingType drop down menu
    def getGratingType(self,objectNum):
        if stim[objectNum]['gratingType'] == 'Sine':
            type = 'sin'
        elif stim[objectNum]['gratingType'] == 'Square':
            type = 'sqr'
        elif stim[objectNum]['gratingType'] == 'Plaid':
            type = 'sin'
        return type

    #returns a numpy array as a mask
    def getMask(self,w,h,objectNum,ppm):
        if stim[objectNum]['maskType'] != 'None':
            if stim[objectNum]['maskObjectType'] == 'Circle':
                mask = self.create_circular_mask(w, h, stim[objectNum]['maskType'], [w/2 + stim[objectNum]['maskXPos'] * ppm, h/2 + stim[objectNum]['maskYPos'] * ppm], stim[objectNum]['maskDiameter'] * ppm/2)
            elif stim[objectNum]['maskObjectType'] == 'Gaussian':
                mask = 'gauss'
            elif stim[objectNum]['maskObjectType'] == 'Blur':
                mask = 'raisedCos'
        else:
            mask = 'None'

        return mask

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

        MaxValue = 2**BitDepth - 1

        if stim[i]['contrastType'] == 'Michelson':
            
            if bgnd == 0:
                # bgnd = 127
                if BitDepth == 8:
                    bgnd = 127
                else:
                    bgnd = 2047

            if stim[i]['contrast'] > 100:
                stim[i]['contrast'] = 100
            elif stim[i]['contrast'] < -100:
                stim[i]['contrast'] = -100
                
            firstIntensity = bgnd + bgnd * (stim[i]['contrast']/100.0)
            secondIntensity = bgnd - bgnd * (stim[i]['contrast']/100.0)

            #all situations of out of bounds intensities
            # if firstIntensity > 255.0: #out of range, set to maximum
            #     firstIntensity = 255.0
            #     secondIntensity = bgnd - (255.0 - bgnd) #same amount below background as light is above background
            if firstIntensity > MaxValue:
                firstIntensity = MaxValue
                secondIntensity = bgnd - (MaxValue - bgnd) #same amount below background as light is above background
            elif secondIntensity < 0:
                secondIntensity = 0 #out of range, set to minimum
                firstIntensity = 2 * bgnd #set to 100% contrast

                #reverse case, where firstIntensity is dark
            # elif secondIntensity > 255.0:
            #     secondIntensity = 255.0
            #     firstIntensity = bgnd - (255.0 - bgnd)
            elif secondIntensity > MaxValue:
                secondIntensity = MaxValue
                firstIntensity = bgnd - (MaxValue - bgnd)

            elif firstIntensity < 0:
                secondIntensity = 0
                secondIntensity = 2 * bgnd

        elif stim[i]['contrastType'] == 'Weber':
            firstIntensity = bgnd * (stim[i]['contrast']/100.0) + bgnd

            secondIntensity = bgnd

            #out of bounds intensities
            # if firstIntensity > 255.0:
            #     firstIntensity = 255.0
            if firstIntensity > MaxValue:
                firstIntensity = MaxValue
            elif firstIntensity < 0:
                firstIntensity = 0

        elif stim[i]['contrastType'] == 'Intensity':
            firstIntensity = stim[i]['contrast']
            secondIntensity = bgnd

            #out of bounds intensities
            # if firstIntensity > 255.0:
            #     firstIntensity = 255.0
            if firstIntensity > MaxValue:
                firstIntensity = MaxValue
            elif firstIntensity < 0:
                firstIntensity = 0

        #apply gamma correction for whatever gamma table is loaded
        firstIntensity = gammaTable[int(firstIntensity)]
        secondIntensity = gammaTable[int(secondIntensity)]
        
        #Convert from 0-255 to -1 to 1 range
        # firstIntensity = (2 * firstIntensity/255.0) - 1
        # secondIntensity = (2 * secondIntensity/255.0) - 1

        #Convert from 0-4095 to -1 to 1 range
        firstIntensity = (2 * firstIntensity/float(MaxValue)) - 1
        secondIntensity = (2 * secondIntensity/float(MaxValue)) - 1

        return (firstIntensity,secondIntensity)

    #Aborts stimulus
    def abortStim(self):
        global abortStatus
        abortStatus = 1

        self.stimCountDown.setText('')
        self.sweepMonitor.setText('')

        #send the stop TTL signal out of pin 3
        # port = parallel.ParallelPort(address = 0xE010)
        # port.setPin(3,1)
        # port.setPin(3,0)

    def triggerEphys(self):
         #send the stop TTL signal out of pin 3
        port = parallel.ParallelPort(address = 0xE010)
        port.setPin(3,1)
        sleep(0.5)
        port.setPin(3,0)

    #Adds another stimulus dictionary for the new object
    def addStimDict(self):
        global stim, seqAssign

        numObjects = len(objectList)

        #index is zero offset
        #stimulus parameter dictionary
        stim[numObjects-1] = {
        'objectType':'Circle',
        'gratingType':'Square',
        'coordinateType':'Cartesian',
        'xPos':0,
        'yPos':0,
        'polarRadius':0,
        'polarAngle':0,
        'diameter':0,
        'innerDiameter':0,
        'outerDiameter':0,
        'length':0,
        'width':0,
        'spatialFreq':0,
        'spatialPhase':0,
        'angularCycles':0,
        'orientation':0,
        'objectAperture':0,
        'contrastType':'Weber',
        'contrast':0,
        'modulationType':'Static',
        'modulationFreq':0,
        'motionType':'Static',
        'turnDirection':'Clockwise',
        'speed':0,
        'driftFreq':0,
        'startRad':0,
        'angle':0,
        'walkFreq':0,
        'apertureStatus':'Off',
        'apertureDiam':0,
        'maskCoordinateType':'Cartesian',
        'maskObjectType':'Circle',
        'maskDiameter':0,
        'maskXPos':0,
        'maskYPos':0,
        'maskPolarRadius':0,
        'maskPolarAngle':0,
        'noiseType':'Binary',
        'noiseSize':0,
        'noiseSeed':0,
        'numDots':0,
        'dotCoherence':0,
        'signalDirection':0,
        'noiseDirection':0,
        'PositionalShiftType':'Static',
        'TargetResolution':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBand':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'imagePath':'',
        'batchStimList':[],
        'trajectory':'None',
        'delay':float(self.delay.text()),
        'duration':float(self.duration.text()),
        'trialTime':float(self.trialTime.text())
        }

        seqAssign[numObjects - 1] = {
        'diameterSeq':{
            'control':self.diameterSeq,
            'parent':'diameter',
            'sequence':'None'
            },
        'innerDiameterSeq':{
            'control':self.innerDiameterSeq,
            'parent':'innerDiameter',
            'sequence':'None'
            },
        'outerDiameterSeq':{
            'control':self.outerDiameterSeq,
            'parent':'outerDiameter',
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
        'pixelWidthSeq':{
            'control':self.pixelWidthSeq,
            'parent':'pixelWidth',
            'sequence':'None'
        },
        'objectApertureSeq':{
            'control':self.objectApertureSeq,
            'parent':'objectAperture',
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
        'angularCyclesSeq':{
            'control':self.angularCyclesSeq,
            'parent':'angularCycles',
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
        'polarRadiusSeq':{
            'control':self.polarRadiusSeq,
            'parent':'polarRadius',
            'sequence':'None'
            },
        'polarAngleSeq':{
            'control':self.polarAngleSeq,
            'parent':'polarAngle',
            'sequence':'None'
            },
        'speedSeq':{
            'control':self.speedSeq,
            'parent':'speed',
            'sequence':'None'
            },
        'driftFreqSeq':{
            'control':self.driftFreqSeq,
            'parent':'driftFreq',
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
        'noiseSizeSeq':{
            'control':self.noiseSizeSeq,
            'parent':'noiseSize',
            'sequence':'None'
        },
        'noiseSeedSeq':{
            'control':self.noiseSeedSeq,
            'parent':'noiseSeed',
            'sequence':'None'
        },
        'numDotsSeq':{
            'control':self.numDotsSeq,
            'parent':'numDots',
            'sequence':'None'
            },
        'dotCoherenceSeq':{
            'control':self.dotCoherenceSeq,
            'parent':'dotCoherence',
            'sequence':'None'
            },
        'signalDirectionSeq':{
            'control':self.signalDirectionSeq,
            'parent':'signalDirection',
            'sequence':'None'
            },
        'noiseDirectionSeq':{
            'control':self.noiseDirectionSeq,
            'parent':'noiseDirection',
            'sequence':'None'
            },   
        'TargetResolutionSeq':{
            'control':self.TargetResolutionSeq,
            'parent':'TargetResolution',
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
        'apertureDiamSeq':{
            'control':self.apertureDiamSeq,
            'parent':'apertureDiam',
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
            },
        'maskPolarRadiusSeq':{
            'control':self.maskPolarRadiusSeq,
            'parent':'maskPolarRadius',
            'sequence':'None'
            },
        'maskPolarAngleSeq':{
            'control':self.maskPolarAngleSeq,
            'parent':'maskPolarAngle',
            'sequence':'None'
            },
        'maskDiameterSeq':{
            'control':self.maskDiameterSeq,
            'parent':'maskDiameter',
            'sequence':'None'
            }
        }

    #Initializes the dictionary that holds the global settings
    def setGlobalSettingsDict(self):
        global globalSettings

        globalSettings = {
            'monitor':self.monitor.currentText(),
            'ppm':self.ppm.text(),
            'xOffset':self.xOffset.text(),
            'yOffset':self.yOffset.text(),
            'background':self.background.text(),
            'syncFrames':self.syncFrames.text(),
            'syncSpot':self.syncSpot.isChecked(),
            'gammaTable':self.gammaTable.currentText(),
            'triggerInterface':'Parallel Port',
            'parallelPortAddress':'0xE010',
            'digitalIn':'2',
            'digitalOut':'2'
        } 

    #Loads the global settings from the User's stimulus folder
    def loadGlobalSettings(self):
        global globalSettings

        fileName = 'settings.globals'
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + '/' + fileName

        if os.path.exists(path):
            #open and read stimulus file to dictionaries
            with open(path,'r') as file:
                fileStr = file.read()

                #load in the settings to the global settings dictionary
                globalSettings = json.loads(fileStr)
        else:
            #make a global settings file if one doesn't exist already
            with open(path,'w+') as file:
                print("Creating Global Settings file...")
                settings = json.dumps(globalSettings)
                file.write(settings)

        #update the controls with the global settings

        self.monitor.setCurrentText(str(globalSettings['monitor']))
        self.ppm.setText(str(globalSettings['ppm']))
        self.xOffset.setText(str(int(globalSettings['xOffset'])))
        self.yOffset.setText(str(int(globalSettings['yOffset'])))
        self.background.setText(str(int(globalSettings['background'])))
        self.syncFrames.setText(str(int(globalSettings['syncFrames'])))
        self.syncSpot.setChecked(globalSettings['syncSpot'])
        self.gammaTable.setCurrentText(str(globalSettings['gammaTable']))

    #prints that the settings file is being saved before saving it
    def saveGlobalSettings_Verbose(self):
        print("Saving Global Settings file...")
        self.saveGlobalSettings()
         
    #Saves the current global settings to a .globals file
    def saveGlobalSettings(self):
        fileName = 'settings.globals'
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + '/' + fileName

        with open(path,'w+') as file:

            settings = json.dumps(globalSettings)
            file.write(settings)

    #Creates a new stimulus folder for a new user profile
    def createNewUser(self):
        subfolder, ok = QInputDialog.getText(self, 'New User','User Name:')#,QLineEdit.Normal,stimName)

        if ok == False:
            return

        path = stimPath + subfolder

        #if user profile already exists
        if os.path.exists(path):
            error_dialog = QErrorMessage()
            error_dialog.showMessage('User name is already in use, try a different one.')
            error_dialog.exec_()
            return

        #Make the profile and switch to it's stimulus bank
        os.mkdir(path)
        self.subFolder.addItem(subfolder)
        self.subFolder.setCurrentText(subfolder)

        #update global settings dictionary with current values
        self.setGlobalSettingsDict()
        #save the global settings to the new user profile
        self.saveGlobalSettings()
        #load the profile
        self.loadUserProfile(subfolder)

    #Makes a dictionary containing string references to all the GUI objects
    def setControlDict(self):
        global control

        control = {
        'ppm':self.ppm,
        'objectListBox':self.objectListBox,
        'objectType':self.objectType,
        'gratingType':self.gratingType,
        'coordinateType':self.coordinateType,
        'xPos':self.xPos,
        'xPosLabel':self.xPosLabel,
        'xPosSeq':self.xPosSeq,
        'yPos':self.yPos,
        'yPosLabel':self.yPosLabel,
        'yPosSeq':self.yPosSeq,
        'polarRadius':self.polarRadius,
        'polarRadiusLabel':self.polarRadiusLabel,
        'polarRadiusSeq':self.polarRadiusSeq,
        'polarAngle':self.polarAngle,
        'polarAngleLabel':self.polarAngleLabel,
        'polarAngleSeq':self.polarAngleSeq,
        'maskPolarRadius':self.maskPolarRadius,
        'maskPolarRadiusLabel':self.maskPolarRadiusLabel,
        'maskPolarRadiusSeq':self.maskPolarRadiusSeq,
        'maskPolarAngle':self.maskPolarAngle,
        'maskPolarAngleLabel':self.maskPolarAngleLabel,
        'maskPolarAngleSeq':self.maskPolarAngleSeq,
        'diameter':self.diameter,
        'diameterLabel':self.diameterLabel,
        'diameterSeq':self.diameterSeq,
        'imagePath':self.imagePath,
        'framePath':self.framePath,
        'innerDiameter':self.innerDiameter,
        'innerDiameterLabel':self.innerDiameterLabel,
        'innerDiameterSeq':self.innerDiameterSeq,
        'outerDiameter':self.outerDiameter,
        'outerDiameterLabel':self.outerDiameterLabel,
        'outerDiameterSeq':self.outerDiameterSeq,
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
        'angularCyclesLabel':self.angularCyclesLabel,
        'angularCycles':self.angularCycles,
        'angularCyclesSeq':self.angularCyclesSeq,
        'orientation':self.orientation,
        'orientationLabel':self.orientationLabel,
        'orientationSeq':self.orientationSeq,
        'pixelWidth':self.pixelWidth,
        'pixelWidthLabel':self.pixelWidthLabel,
        'pixelWidthSeq':self.pixelWidthSeq,
        'objectAperture':self.objectAperture,
        'objectApertureLabel':self.objectApertureLabel,
        'objectApertureSeq':self.objectApertureSeq,
        'contrastType':self.contrastType,
        'contrast':self.contrast,
        'contrastLabel':self.contrastLabel,
        'contrastSeq':self.contrastSeq,
        'modulationType':self.modulationType,
        'modulationFreq':self.modulationFreq,
        'modulationFreqLabel':self.modulationFreqLabel,
        'modulationFreqSeq':self.modulationFreqSeq,
        'motionType':self.motionType,
        'turnDirection':self.turnDirection,
        'speed':self.speed,
        'speedLabel':self.speedLabel,
        'speedSeq':self.speedSeq,
        'driftFreqLabel':self.driftFreqLabel,
        'driftFreq':self.driftFreq,
        'driftFreqSeq':self.driftFreqSeq,
        'startRad':self.startRad,
        'startRadLabel':self.startRadLabel,
        'startRadSeq':self.startRadSeq,
        'angle':self.angle,
        'angleLabel':self.angleLabel,
        'angleSeq':self.angleSeq,
        'walkFreq':self.walkFreq,
        'walkFreqLabel':self.walkFreqLabel,
        'walkFreqSeq':self.walkFreqSeq,
        'xOffset':self.xOffset,
        'yOffset':self.yOffset,
        'apertureLabel':self.apertureLabel,
        'apertureStatus':self.apertureStatus,
        'apertureDiamLabel':self.apertureDiamLabel,
        'apertureDiam':self.apertureDiam,
        'apertureDiamSeq':self.apertureDiamSeq,
        'maskObjectType':self.maskObjectType,
        'maskCoordinateType':self.maskCoordinateType,
        'maskXPos':self.maskXPos,
        'maskXPosLabel':self.maskXPosLabel,
        'maskXPosSeq':self.maskXPosSeq,
        'maskYPos':self.maskYPos,
        'maskYPosLabel':self.maskYPosLabel,
        'maskYPosSeq':self.maskYPosSeq,
        'maskDiameter':self.maskDiameter,
        'maskDiameterLabel':self.maskDiameterLabel,
        'maskDiameterSeq':self.maskDiameterSeq,
        'addMask':self.addMask,
        'removeMask':self.removeMask,
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
        'background':self.background,
        'cloudSFLabel':self.cloudSFLabel,
        'cloudSF':self.cloudSF,
        'cloudSFBand':self.cloudSFBand,
        'cloudSpeedLabel':self.cloudSpeedLabel,
        'cloudSpeedX':self.cloudSpeedX,
        'cloudSpeedY':self.cloudSpeedY,
        'cloudSpeedBandLabel':self.cloudSpeedBandLabel,
        'cloudSpeedBand':self.cloudSpeedBand,
        'cloudOrientLabel':self.cloudOrientLabel,
        'cloudOrient':self.cloudOrient,
        'cloudOrientBand':self.cloudOrientBand,
        'noiseType':self.noiseType,
        'noiseSizeLabel':self.noiseSizeLabel,
        'noiseSize':self.noiseSize,
        'noiseSizeSeq':self.noiseSizeSeq,
        'noiseSeedLabel':self.noiseSeedLabel,
        'noiseSeed':self.noiseSeed,
        'noiseSeedSeq':self.noiseSeedSeq,
        # 'noiseFreqLabel':self.noiseFreqLabel,
        # 'noiseFreq':self.noiseFreq,
        # 'noiseFreqSeq':self.noiseFreqSeq,
        'batchStimMenu':self.batchStimMenu,
        'batchStimList':self.batchStimList,
        'batchStimAdd':self.batchStimAdd,
        'batchStimRemove':self.batchStimRemove,
        'numDots':self.numDots,
        'numDotsLabel':self.numDotsLabel,
        'numDotsSeq':self.numDotsSeq,
        'dotCoherence':self.dotCoherence,
        'dotCoherenceLabel':self.dotCoherenceLabel,
        'dotCoherenceSeq':self.dotCoherenceSeq,
        'signalDirection':self.signalDirection,
        'signalDirectionLabel':self.signalDirectionLabel,
        'signalDirectionSeq':self.signalDirectionSeq,
        'noiseDirection':self.noiseDirection,
        'noiseDirectionLabel':self.noiseDirectionLabel,
        'noiseDirectionSeq':self.noiseDirectionSeq,
        'PositionalShiftType':self.PositionalShiftType,
        'TargetResolution':self.TargetResolution,
        'TargetResolutionLabel':self.TargetResolutionLabel,
        'TargetResolutionSeq':self.TargetResolutionSeq
        }

    #Set contextual menu dictionaries
    def setContextualMenus(self):
        global circleSettings,rectangleSettings,gratingSettings,checkerboardSettings,checkerboard1DSettings,cloudSettings,windmillSettings,annulusSettings,imageSettings,frameSettings,batchSettings,snakeSettings
        global staticMotionSettings,randomWalkMotionSettings,randomWalkGratingMotionSettings,dynamicModSettings,noiseModSettings,staticModSettings,windmillMotionSettings,driftGratingMotionSettings,driftMotionSettings
        global cartesianSettings,cartesianMaskSettings,polarSettings,polarMaskSettings,randomDotSettings,randomDotMotionSettings,randomPositionalShiftSettings,staticPositionalShiftSettings
        global allSettings,allCoordinateMaskSettings,allCoordinateSettings,allModulationSettings,allMotionSettings,allPositionalShiftSettings
        
        #First few lists contain all of the controls in different categories: Overall, Motion, Modulation, Coordinates.
        #These lists are iterated over to match up controls that are included in lists for individual object types (Circles, rectangles, gratings, etc.)
        #or types of Motion (Drift, Static, etc.), Modulation (Square, Sine, Chirp, etc.), or Coordinate sytems (Cartesian, polar). 
        
        #Adding a new type of stimulus object will involve adding those controls to the allSettings list if new controls have been created (e.g. in BuildDesignPanel() ),
        #and creating a new settings list for that object, which lists out the controls to use for that object type.

        allSettings = [
            'gratingType',
            'diameter',
            'diameterLabel',
            'diameterSeq',
            'imagePath',
            'framePath',
            'innerDiameter',
            'innerDiameterLabel',
            'innerDiameterSeq',
            'outerDiameter',
            'outerDiameterLabel',
            'outerDiameterSeq',
            'length',
            'lengthLabel',
            'lengthSeq',
            'width',
            'widthLabel',
            'widthSeq',
            'orientation',
            'orientationLabel',
            'orientationSeq',
            'pixelWidth',
            'pixelWidthLabel',
            'pixelWidthSeq',
            'objectAperture',
            'objectAperture',
            'objectApertureLabel',
            'objectApertureSeq',
            'angularCyclesLabel',
            'angularCycles',
            'angularCyclesSeq',
            'spatialPhase',
            'spatialPhaseLabel',
            'spatialPhaseSeq',
            'spatialFreq',
            'spatialFreqLabel',
            'spatialFreqSeq',
            'noiseType',
            'noiseSizeLabel',
            'noiseSize',
            'noiseSizeSeq',
            'cloudSFLabel',
            'cloudSF',
            'cloudSFBand',
            'cloudSpeedLabel',
            'cloudSpeedX',
            'cloudSpeedY',
            'cloudSpeedBandLabel',
            'cloudSpeedBand',
            'cloudOrientLabel',
            'cloudOrient',
            'cloudOrientBand',
            'batchStimMenu',
            'batchStimList',
            'batchStimAdd',
            'batchStimRemove',
            'numDots',
            'numDotsLabel',
            'numDotsSeq',
            'dotCoherence',
            'dotCoherenceLabel',
            'dotCoherenceSeq',
            'PositionalShiftType',
            'TargetResolution',
            'TargetResolutionLabel',
            'TargetResolutionSeq'
        ]

        allMotionSettings = [
            'angle',
            'angleLabel',
            'angleSeq',
            'startRad',
            'startRadLabel',
            'startRadSeq',
            'speed',
            'speedLabel',
            'speedSeq',
            'driftFreqLabel',
            'driftFreq',
            'driftFreqSeq',
            'turnDirection',
            'walkFreq',
            'walkFreqLabel',
            'walkFreqSeq',
            'signalDirection',
            'signalDirectionLabel',
            'signalDirectionSeq',
            'noiseDirection',
            'noiseDirectionLabel',
            'noiseDirectionSeq'
        ]
    
        allModulationSettings = [
            'modulationFreq',
            'modulationFreqLabel',
            'modulationFreqSeq',
            'noiseSeedLabel',
            'noiseSeed',
            'noiseSeedSeq'
        ]
        
        allCoordinateSettings = [
            'xPos',
            'xPosLabel',
            'xPosSeq',
            'yPos',
            'yPosLabel',
            'yPosSeq',
            'polarRadius',
            'polarRadiusLabel',
            'polarRadiusSeq',
            'polarAngle',
            'polarAngleLabel',
            'polarAngleSeq'
        ]

        allCoordinateMaskSettings = [
            'maskXPos',
            'maskXPosLabel',
            'maskXPosSeq',
            'maskYPos',
            'maskYPosLabel',
            'maskYPosSeq',
            'maskPolarRadius',
            'maskPolarRadiusLabel',
            'maskPolarRadiusSeq',
            'maskPolarAngle',
            'maskPolarAngleLabel',
            'maskPolarAngleSeq'
        ]

        allPositionalShiftSettings = [
            'TargetResolution',
            'TargetResolutionLabel',
            'TargetResolutionSeq'
        ]
        ########################################
        ########################################
        #Individual object types each have their own lists of controls
        circleSettings = [
            'diameter',
            'diameterLabel',
            'diameterSeq'
        ]

        annulusSettings = [
            'innerDiameter',
            'innerDiameterLabel',
            'innerDiameterSeq',
            'outerDiameter',
            'outerDiameterLabel',
            'outerDiameterSeq'
        ]

        rectangleSettings = [
            'length',
            'lengthLabel',
            'lengthSeq',
            'width',
            'widthLabel',
            'widthSeq',
            'orientation',
            'orientationLabel',
            'orientationSeq'
        ]

        snakeSettings = [
            'length',
            'lengthLabel',
            'lengthSeq',
            'width',
            'widthLabel',
            'widthSeq'
        ]

        gratingSettings = [
            'gratingType',
            'orientation',
            'orientationLabel',
            'orientationSeq',
            'objectAperture',
            'objectApertureLabel',
            'objectApertureSeq',
            'spatialPhase',
            'spatialPhaseLabel',
            'spatialPhaseSeq',
            'spatialFreq',
            'spatialFreqLabel',
            'spatialFreqSeq'
        ]

        checkerboardSettings = [
            'noiseType',
            'noiseSizeLabel',
            'noiseSize',
            'noiseSizeSeq',
            'PositionalShiftType',
            'TargetResolution',
            'TargetResolutionLabel',
            'TargetResolutionSeq',
            'objectAperture',
            'objectApertureLabel',
            'objectApertureSeq'
        ]

        checkerboard1DSettings = [
            'length',
            'lengthLabel',
            'lengthSeq',
            'width',
            'widthLabel',
            'widthSeq',
            'orientation',
            'orientationLabel',
            'orientationSeq',
            'pixelWidth',
            'pixelWidthLabel',
            'pixelWidthSeq',
            'noiseType'
        ]

        cloudSettings = [
            'objectAperture',
            'objectApertureLabel',
            'objectApertureSeq',
            'cloudSFLabel',
            'cloudSF',
            'cloudSFBand',
            'cloudSpeedLabel',
            'cloudSpeedX',
            'cloudSpeedY',
            'cloudSpeedBandLabel',
            'cloudSpeedBand',
            'cloudOrientLabel',
            'cloudOrient',
            'cloudOrientBand'
        ]

        windmillSettings = [
            'gratingType',
            'orientation',
            'orientationLabel',
            'orientationSeq',
            'angularCyclesLabel',
            'angularCycles',
            'angularCyclesSeq'
        ]

        imageSettings = [
            'imagePath',
            'orientation',
            'orientationLabel',
            'orientationSeq'
        ]

        frameSettings = [
            'framePath'
        ]

        batchSettings = [
            'batchStimMenu',
            'batchStimList',
            'batchStimAdd',
            'batchStimRemove'
        ]

        randomDotSettings = [
            'diameter', #dot size
            'diameterLabel',
            'diameterSeq',
            'numDots', #number of dots
            'numDotsLabel',
            'numDotsSeq',
            'dotCoherence', #coherence
            'dotCoherenceLabel',
            'dotCoherenceSeq',
            'objectAperture',
            'objectApertureLabel',
            'objectApertureSeq'
        ]

##########################################
##########################################
#Individual types of Motion have their own sets of controls
        driftMotionSettings = [
            'angle',
            'angleLabel',
            'angleSeq',
            'startRad',
            'startRadLabel',
            'startRadSeq',
            'speed',
            'speedLabel',
            'speedSeq'
        ]

        driftGratingMotionSettings = [
            'angle',
            'angleLabel',
            'angleSeq',
            'driftFreq',
            'driftFreqLabel',
            'driftFreqSeq'
        ]

        randomDotMotionSettings = [
            'speed',
            'speedLabel',
            'speedSeq',
            'signalDirection', #signal dot direction
            'signalDirectionLabel',
            'signalDirectionSeq',
            'noiseDirection', #noise dot direction
            'noiseDirectionLabel',
            'noiseDirectionSeq',
        ]

        windmillMotionSettings = [
            'driftFreqLabel',
            'driftFreq',
            'driftFreqSeq',
            'turnDirection'
        ]

        staticMotionSettings = []

        randomWalkMotionSettings = [
            'startRad',
            'startRadLabel',
            'startRadSeq',
            'speed',
            'speedLabel',
            'speedSeq',
            'walkFreq',
            'walkFreqLabel',
            'walkFreqSeq'
        ]

        randomWalkGratingMotionSettings = [
            'angle',
            'angleLabel',
            'angleSeq',
            'driftFreq',
            'driftFreqLabel',
            'driftFreqSeq',
            'walkFreq',
            'walkFreqLabel',
            'walkFreqSeq'
        ]

        staticPositionalShiftSettings = []

        randomPositionalShiftSettings = [
            'TargetResolution',
            'TargetResolutionLabel',
            'TargetResolutionSeq'
        ]
##########################################
##########################################
#Individual types of temporal Modulation have their own sets of controls
        staticModSettings = []

        dynamicModSettings = [
            'modulationFreq',
            'modulationFreqLabel',
            'modulationFreqSeq'
        ]

        noiseModSettings = [
            'modulationFreq',
            'modulationFreqLabel',
            'modulationFreqSeq',
            'noiseSeedLabel',
            'noiseSeed',
            'noiseSeedSeq'
        ]

##########################################
##########################################
#Individual types of coordinate systems have their own sets of controls

        cartesianSettings = [
            'xPos',
            'xPosLabel',
            'xPosSeq',
            'yPos',
            'yPosLabel',
            'yPosSeq'
        ]

        polarSettings = [
            'polarRadius',
            'polarRadiusLabel',
            'polarRadiusSeq',
            'polarAngle',
            'polarAngleLabel',
            'polarAngleSeq'
        ]

        cartesianMaskSettings = [
            'maskXPos',
            'maskXPosLabel',
            'maskXPosSeq',
            'maskYPos',
            'maskYPosLabel',
            'maskYPosSeq'
        ]

        polarMaskSettings = [
            'maskPolarRadius',
            'maskPolarRadiusLabel',
            'maskPolarRadiusSeq',
            'maskPolarAngle',
            'maskPolarAngleLabel',
            'maskPolarAngleSeq'
        ]


    #Design Panel
    def buildDesignPanel(self):
        left = 165 * scale_w
        top = 315 * scale_h
        width = 475 * scale_w
        height = 400 * scale_h

        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto Light", 10,weight=QtGui.QFont.Bold)
            large = QtGui.QFont("Roboto Light", 11,weight=QtGui.QFont.Light)
        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
            large = QtGui.QFont("Helvetica", 13)


        #Group box and designPanelLayout layout
        self.designPanel = QGroupBox(self)
        self.designPanelLayout = QGridLayout()

        self.designPanel.setLayout(self.designPanelLayout)
        self.designPanel.move(left,top)
        self.designPanel.resize(width,height)
        self.designPanelLayout.setVerticalSpacing(5* scale_w)

        #Blanks
        self.blank1 = QLabel('',self)
        self.blank2 = QLabel('',self)
        self.blank2.setFixedWidth(15* scale_w)
        self.blank3 = QLabel('',self)
        self.blank3.setFixedWidth(15* scale_w)
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

        #set up drag and drop to reorder stimulu items
        self.objectListBox.setDragDropMode(QAbstractItemView.InternalMove) #only allows internal drag/drops
        self.objectListBox.setDragDropOverwriteMode(False)
        self.objectListBox.setAcceptDrops(True)
        self.objectListBox.setDropIndicatorShown(True)
        self.objectListBox.setDragEnabled(True)


        #insert blank after the object list box row
        # self.blank1.setFixedHeight(20 * scale_h)
        # self.designPanelLayout.addWidget(self.blank1,4,0,1,11)
        # self.designPanelLayout.setRowStretch(14,1)
        # self.blank1.setAlignment(QtCore.Qt.AlignVCenter)

        #Object Type
        self.objectTypeLabel = QLabel('Objects',self)
        self.objectTypeLabel.setFont(bold)
        self.objectTypeLabel.setFixedHeight(20 * scale_h)

        self.objectType = QComboBox(self)
        self.objectType.addItems(['Circle','Rectangle','Grating','Checkerboard','Checkerboard 1D','Random Dot','Cloud','Windmill','Annulus','Snake','Image','Frames','Batch'])
        self.objectType.activated.connect(lambda: self.menuProc('objectType',self.objectType.currentText()))
        self.objectType.setFixedHeight(20 * scale_h)
        self.objectType.setFixedWidth(100 * scale_w)

        self.designPanelLayout.addWidget(self.objectTypeLabel,5,0)
        self.designPanelLayout.addWidget(self.objectType,6,0,1,2)

        #Add blank slot to the right of the object type menu
        self.designPanelLayout.addWidget(self.blank2,7,3)
        #self.blank2.setStyleSheet("QLabel {background-color: blue;}")
        self.blank2.setFixedHeight(20 * scale_h)
        #self.blank2.setFixedWidth(20 * scale_h)
        self.blank2.setAlignment(QtCore.Qt.AlignVCenter)

        #Coordinates
        self.coordinateLabel = QLabel('Coordinates')
        self.coordinateLabel.setFont(bold)
        self.coordinateType = QComboBox()
        self.coordinateType.setFixedHeight(20 * scale_h)
        self.coordinateType.addItems(['Cartesian','Polar'])
        self.coordinateType.activated.connect(lambda: self.menuProc('coordinateType',self.coordinateType.currentText()))

        self.designPanelLayout.addWidget(self.coordinateLabel,0,8,1,2)
        self.designPanelLayout.addWidget(self.coordinateType,1,8,1,2)

        #X offset
        self.xPosLabel = QLabel('X Offset')
        self.xPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.xPos = QLineEdit()
        self.xPos.setAlignment(QtCore.Qt.AlignRight)
        self.xPos.setFixedWidth(40 * scale_w)
        self.xPosSeq = QComboBox()
        self.xPosSeq.addItem('None')
        self.xPosSeq.setFixedWidth(20 * scale_w)
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
        self.yPos.setFixedWidth(40 * scale_w)
        self.yPosSeq = QComboBox()
        self.yPosSeq.addItem('None')
        self.yPosSeq.setFixedWidth(20 * scale_w)
        self.yPos.editingFinished.connect(lambda: self.variableProc('yPos',self.yPos.text()))
        self.yPosSeq.activated.connect(lambda: self.menuProc('yPosSeq',self.yPosSeq.currentText()))

        self.designPanelLayout.addWidget(self.yPosLabel,3,8)
        self.designPanelLayout.addWidget(self.yPos,3,9)
        self.designPanelLayout.addWidget(self.yPosSeq,3,10)

        #Polar Coordinates - Radius
        self.polarRadiusLabel = QLabel('Radius')
        self.polarRadiusLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.polarRadius = QLineEdit()
        self.polarRadius.setAlignment(QtCore.Qt.AlignRight)
        self.polarRadius.setFixedWidth(40 * scale_w)
        self.polarRadiusSeq = QComboBox()
        self.polarRadiusSeq.addItem('None')
        self.polarRadiusSeq.setFixedWidth(20 * scale_w)
        self.polarRadius.editingFinished.connect(lambda: self.variableProc('polarRadius',self.polarRadius.text()))
        self.polarRadiusSeq.activated.connect(lambda: self.menuProc('polarRadiusSeq',self.polarRadiusSeq.currentText()))

        self.designPanelLayout.addWidget(self.polarRadiusLabel,2,8)
        self.designPanelLayout.addWidget(self.polarRadius,2,9)
        self.designPanelLayout.addWidget(self.polarRadiusSeq,2,10)

        #Polar Coordinates - Angle
        self.polarAngleLabel = QLabel('Angle')
        self.polarAngleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.polarAngle = QLineEdit()
        self.polarAngle.setAlignment(QtCore.Qt.AlignRight)
        self.polarAngle.setFixedWidth(40 * scale_w)
        self.polarAngleSeq = QComboBox()
        self.polarAngleSeq.addItem('None')
        self.polarAngleSeq.setFixedWidth(20 * scale_w)
        self.polarAngle.editingFinished.connect(lambda: self.variableProc('polarAngle',self.polarAngle.text()))
        self.polarAngleSeq.activated.connect(lambda: self.menuProc('polarAngleSeq',self.polarAngleSeq.currentText()))

        self.designPanelLayout.addWidget(self.polarAngleLabel,3,8)
        self.designPanelLayout.addWidget(self.polarAngle,3,9)
        self.designPanelLayout.addWidget(self.polarAngleSeq,3,10)

        #Diameter
        self.diameterLabel = QLabel('Diameter',self)
        self.diameterLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.diameter = QLineEdit(self)
        self.diameter.setFixedWidth(40 * scale_w)
        self.diameter.setAlignment(QtCore.Qt.AlignRight)
        self.diameterSeq = QComboBox(self)
        self.diameterSeq.addItem('None')
        self.diameterSeq.setFixedWidth(20 * scale_w)
        self.diameter.editingFinished.connect(lambda: self.variableProc('diameter',self.diameter.text()))
        self.diameterSeq.activated.connect(lambda: self.menuProc('diameterSeq',self.diameterSeq.currentText()))

        self.designPanelLayout.addWidget(self.diameterLabel,7,0)
        self.designPanelLayout.addWidget(self.diameter,7,1)
        self.designPanelLayout.addWidget(self.diameterSeq,7,2)

        #Image Path
        self.imagePath =QComboBox(self)
        self.imagePath.setFixedHeight(20 * scale_h)
        self.imagePath.setFixedWidth(100 * scale_w)

        self.designPanelLayout.addWidget(self.imagePath,7,0,1,2)

        #Frame Path
        self.framePath = QComboBox(self)
        self.framePath.setFixedHeight(20 * scale_h)
        self.framePath.setFixedWidth(100 * scale_w)
        self.designPanelLayout.addWidget(self.framePath,7,0,1,2)

        #Batch stimulation. List all stimuli in drop down menu

        stimList = self.getStimulusBank()

        self.batchStimMenu = QComboBox(self)
        self.batchStimMenu.clear()
        self.batchStimMenu.addItems(stimList)
        self.batchStimMenu.setFixedHeight(20 * scale_h)
        self.batchStimMenu.setFixedWidth(100 * scale_w)
        self.designPanelLayout.addWidget(self.batchStimMenu,7,0,1,2)

        self.batchStimList = QListWidget(self)
        self.designPanelLayout.addWidget(self.batchStimList,8,0,4,3)

        self.batchStimAdd = QPushButton('+',self)
        self.batchStimAdd.setFixedWidth(20 * scale_w)
        self.designPanelLayout.addWidget(self.batchStimAdd,6,2,1,1)
        self.batchStimAdd.clicked.connect(lambda: self.buttonProc("batchStimAdd"))

        self.batchStimRemove = QPushButton('-',self)
        self.batchStimRemove.setFixedWidth(20 * scale_w)
        self.designPanelLayout.addWidget(self.batchStimRemove,7,2,1,1)
        self.batchStimRemove.clicked.connect(lambda: self.buttonProc("batchStimRemove"))

        #Inner Diameter (annulus)
        self.innerDiameterLabel = QLabel('Inner',self)
        self.innerDiameterLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.innerDiameter = QLineEdit(self)
        self.innerDiameter.setFixedWidth(40 * scale_w)
        self.innerDiameter.setAlignment(QtCore.Qt.AlignRight)
        self.innerDiameterSeq = QComboBox(self)
        self.innerDiameterSeq.addItem('None')
        self.innerDiameterSeq.setFixedWidth(20 * scale_w)
        self.innerDiameter.editingFinished.connect(lambda: self.variableProc('innerDiameter',self.innerDiameter.text()))
        self.innerDiameterSeq.activated.connect(lambda: self.menuProc('innerDiameterSeq',self.innerDiameterSeq.currentText()))

        self.designPanelLayout.addWidget(self.innerDiameterLabel,7,0)
        self.designPanelLayout.addWidget(self.innerDiameter,7,1)
        self.designPanelLayout.addWidget(self.innerDiameterSeq,7,2)

        #Outer Diameter (annulus)
        self.outerDiameterLabel = QLabel('Outer',self)
        self.outerDiameterLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.outerDiameter = QLineEdit(self)
        self.outerDiameter.setFixedWidth(40 * scale_w)
        self.outerDiameter.setAlignment(QtCore.Qt.AlignRight)
        self.outerDiameterSeq = QComboBox(self)
        self.outerDiameterSeq.addItem('None')
        self.outerDiameterSeq.setFixedWidth(20 * scale_w)
        self.outerDiameter.editingFinished.connect(lambda: self.variableProc('outerDiameter',self.outerDiameter.text()))
        self.outerDiameterSeq.activated.connect(lambda: self.menuProc('outerDiameterSeq',self.outerDiameterSeq.currentText()))

        self.designPanelLayout.addWidget(self.outerDiameterLabel,8,0)
        self.designPanelLayout.addWidget(self.outerDiameter,8,1)
        self.designPanelLayout.addWidget(self.outerDiameterSeq,8,2)

        #Grating type
        self.gratingType = QComboBox(self)
        self.gratingType.addItems(['Square','Sine','Plaid'])
        self.designPanelLayout.addWidget(self.gratingType,7,0,1,2)
        self.gratingType.setFixedWidth(100 * scale_w)
        self.gratingType.activated.connect(lambda: self.menuProc('gratingType',self.gratingType.currentText()))

        #Checkerboard Type
        self.noiseType = QComboBox(self)
        self.noiseType.addItems(['Binary','Normal','Uniform'])
        self.designPanelLayout.addWidget(self.noiseType,7,0,1,2)
        self.noiseType.activated.connect(lambda: self.menuProc('noiseType',self.noiseType.currentText()))

        #insert blank after the spatial frequency row
        self.blank4.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.blank4,11,0,1,10)
        #self.blank4.setStyleSheet("QLabel {background-color: black;}")
        self.blank4.setAlignment(QtCore.Qt.AlignVCenter)

        #Noise Seed
        self.noiseSeedLabel = QLabel('Seed',self)
        self.noiseSeedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.noiseSeed = QLineEdit(self)
        self.noiseSeed.setFixedWidth(40 * scale_w)
        self.noiseSeed.setAlignment(QtCore.Qt.AlignRight)
        self.noiseSeed.editingFinished.connect(lambda: self.variableProc('noiseSeed',self.noiseSeed.text()))

        self.noiseSeedSeq = QComboBox(self)
        self.noiseSeedSeq.addItem('None')
        self.noiseSeedSeq.setFixedWidth(20 * scale_w)
        self.noiseSeedSeq.activated.connect(lambda: self.menuProc('noiseSeedSeq',self.noiseSeedSeq.currentText()))

        self.designPanelLayout.addWidget(self.noiseSeedLabel,11,4)
        self.designPanelLayout.addWidget(self.noiseSeed,11,5)
        self.designPanelLayout.addWidget(self.noiseSeedSeq,11,6)


        #Noise pixel size
        self.noiseSizeLabel = QLabel('Size',self)
        self.noiseSizeLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.noiseSize = QLineEdit(self)
        self.noiseSize.setFixedWidth(40 * scale_w)
        self.noiseSize.setAlignment(QtCore.Qt.AlignRight)
        self.noiseSize.editingFinished.connect(lambda: self.variableProc('noiseSize',self.noiseSize.text()))

        self.noiseSizeSeq = QComboBox(self)
        self.noiseSizeSeq.addItem('None')
        self.noiseSizeSeq.setFixedWidth(20 * scale_w)
        self.noiseSizeSeq.activated.connect(lambda: self.menuProc('noiseSizeSeq',self.noiseSizeSeq.currentText()))


        self.designPanelLayout.addWidget(self.noiseSizeLabel,8,0)
        self.designPanelLayout.addWidget(self.noiseSize,8,1)
        self.designPanelLayout.addWidget(self.noiseSizeSeq,8,2)

        #Noise positional shifting
        self.PositionalShiftType = QComboBox(self)
        self.PositionalShiftType.addItems(['Static','Random'])
        self.designPanelLayout.addWidget(self.PositionalShiftType,9,0,1,2)
        self.PositionalShiftType.activated.connect(lambda: self.menuProc('PositionalShiftType',self.PositionalShiftType.currentText()))
        self.PositionalShiftType.setFixedHeight(20 * scale_h)
        self.PositionalShiftType.setFixedWidth(100 * scale_w)

        #Target STA resolution for shifted white noise stimulus
        self.TargetResolutionLabel = QLabel('Target Res.',self)
        self.TargetResolutionLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.TargetResolution = QLineEdit(self)
        self.TargetResolution.setFixedWidth(40 * scale_w)
        self.TargetResolution.setAlignment(QtCore.Qt.AlignRight)
        self.TargetResolution.editingFinished.connect(lambda: self.variableProc('TargetResolution',self.TargetResolution.text()))

        self.TargetResolutionSeq = QComboBox(self)
        self.TargetResolutionSeq.addItem('None')
        self.TargetResolutionSeq.setFixedWidth(20 * scale_w)
        self.TargetResolutionSeq.activated.connect(lambda: self.menuProc('TargetResolutionSeq',self.TargetResolutionSeq.currentText()))

        self.designPanelLayout.addWidget(self.TargetResolutionLabel,10,0)
        self.designPanelLayout.addWidget(self.TargetResolution,10,1)
        self.designPanelLayout.addWidget(self.TargetResolutionSeq,10,2)


        #Cloud parameters

        #Cloud - Spatial Frequency and Bandwidth
        self.cloudSFLabel = QLabel('SF / BW',self)
        self.cloudSF = QLineEdit(self)
        self.cloudSFBand = QLineEdit(self)

        self.cloudSFBand.setFixedWidth(40 * scale_w)
        self.cloudSF.setFixedWidth(40 * scale_w)

        self.cloudSFLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.cloudSF.setAlignment(QtCore.Qt.AlignRight)
        self.cloudSFBand.setAlignment(QtCore.Qt.AlignRight)

        self.designPanelLayout.addWidget(self.cloudSFLabel,7,0)
        self.designPanelLayout.addWidget(self.cloudSF,7,1)
        self.designPanelLayout.addWidget(self.cloudSFBand,7,2,1,2)

        self.cloudSF.editingFinished.connect(lambda: self.variableProc('cloudSF',self.cloudSF.text()))
        self.cloudSFBand.editingFinished.connect(lambda: self.variableProc('cloudSFBand',self.cloudSFBand.text()))

        #Cloud - Temporal Frequency and Bandwidth
        self.cloudSpeedLabel = QLabel('TF X/Y',self)
        self.cloudSpeedX = QLineEdit(self)
        self.cloudSpeedY = QLineEdit(self)

        self.cloudSpeedX.setFixedWidth(40 * scale_w)
        self.cloudSpeedY.setFixedWidth(40 * scale_w)

        self.cloudSpeedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.cloudSpeedX.setAlignment(QtCore.Qt.AlignRight)
        self.cloudSpeedY.setAlignment(QtCore.Qt.AlignRight)

        self.designPanelLayout.addWidget(self.cloudSpeedLabel,8,0)
        self.designPanelLayout.addWidget(self.cloudSpeedX,8,1)
        self.designPanelLayout.addWidget(self.cloudSpeedY,8,2,1,2)

        self.cloudSpeedX.editingFinished.connect(lambda: self.variableProc('cloudSpeedX',self.cloudSpeedX.text()))
        self.cloudSpeedY.editingFinished.connect(lambda: self.variableProc('cloudSpeedY',self.cloudSpeedY.text()))

        self.cloudSpeedBandLabel = QLabel('TF BW',self)
        self.cloudSpeedBand = QLineEdit(self)
        self.cloudSpeedBand.setFixedWidth(40 * scale_w)
        self.cloudSpeedBandLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.cloudSpeedBand.setAlignment(QtCore.Qt.AlignRight)

        self.designPanelLayout.addWidget(self.cloudSpeedBandLabel,9,0)
        self.designPanelLayout.addWidget(self.cloudSpeedBand,9,1)

        self.cloudSpeedBand.editingFinished.connect(lambda: self.variableProc('cloudSpeedBand',self.cloudSpeedBand.text()))

        #Cloud - Orientation and Bandwidth
        self.cloudOrientLabel = QLabel('Ang./BW',self)
        self.cloudOrient = QLineEdit(self)
        self.cloudOrientBand = QLineEdit(self)

        self.cloudOrientBand.setFixedWidth(40 * scale_w)
        self.cloudOrient.setFixedWidth(40 * scale_w)

        self.cloudOrientLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.cloudOrient.setAlignment(QtCore.Qt.AlignRight)
        self.cloudOrientBand.setAlignment(QtCore.Qt.AlignRight)

        self.designPanelLayout.addWidget(self.cloudOrientLabel,10,0)
        self.designPanelLayout.addWidget(self.cloudOrient,10,1)
        self.designPanelLayout.addWidget(self.cloudOrientBand,10,2,1,2)

        self.cloudOrient.editingFinished.connect(lambda: self.variableProc('cloudOrient',self.cloudOrient.text()))
        self.cloudOrientBand.editingFinished.connect(lambda: self.variableProc('cloudOrientBand',self.cloudOrientBand.text()))

        #Length
        self.lengthLabel = QLabel('Length',self)
        self.lengthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.length = QLineEdit(self)
        self.length.setFixedWidth(40 * scale_w)
        self.length.setAlignment(QtCore.Qt.AlignRight)
        self.lengthSeq = QComboBox(self)
        self.lengthSeq.addItem('None')
        self.lengthSeq.setFixedWidth(20 * scale_w)
        self.length.editingFinished.connect(lambda: self.variableProc('length',self.length.text()))
        self.lengthSeq.activated.connect(lambda: self.menuProc('lengthSeq',self.lengthSeq.currentText()))

        self.designPanelLayout.addWidget(self.lengthLabel,7,0)
        self.designPanelLayout.addWidget(self.length,7,1)
        self.designPanelLayout.addWidget(self.lengthSeq,7,2)

        #Width
        self.widthLabel = QLabel('Width',self)
        self.widthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.width = QLineEdit(self)
        self.width.setFixedWidth(40 * scale_w)
        self.width.setAlignment(QtCore.Qt.AlignRight)
        self.widthSeq = QComboBox(self)
        self.widthSeq.addItem('None')
        self.widthSeq.setFixedWidth(20 * scale_w)
        self.width.editingFinished.connect(lambda: self.variableProc('width',self.width.text()))
        self.widthSeq.activated.connect(lambda: self.menuProc('widthSeq',self.widthSeq.currentText()))

        self.designPanelLayout.addWidget(self.widthLabel,8,0)
        self.designPanelLayout.addWidget(self.width,8,1)
        self.designPanelLayout.addWidget(self.widthSeq,8,2)

        #Spatial Frequency
        self.spatialFreqLabel = QLabel('Sp. Freq.',self)
        self.spatialFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.spatialFreq = QLineEdit(self)
        self.spatialFreq.setFixedWidth(40 * scale_w)
        self.spatialFreq.setAlignment(QtCore.Qt.AlignRight)
        self.spatialFreqSeq = QComboBox(self)
        self.spatialFreqSeq.addItem('None')
        self.spatialFreqSeq.setFixedWidth(20 * scale_w)
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
        self.orientation.setFixedWidth(40 * scale_w)
        self.orientationSeq = QComboBox(self)
        self.orientationSeq.addItem('None')
        self.orientationSeq.setFixedWidth(20 * scale_w)
        self.orientation.editingFinished.connect(lambda: self.variableProc('orientation',self.orientation.text()))
        self.orientationSeq.activated.connect(lambda: self.menuProc('orientationSeq',self.orientationSeq.currentText()))

        self.designPanelLayout.addWidget(self.orientationLabel,9,0)
        self.designPanelLayout.addWidget(self.orientation,9,1)
        self.designPanelLayout.addWidget(self.orientationSeq,9,2)

        #Pixel Width - 1D checkerboard
        self.pixelWidthLabel = QLabel('Pix. Width',self)
        self.pixelWidthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.pixelWidth = QLineEdit(self)
        self.pixelWidth.setAlignment(QtCore.Qt.AlignRight)
        self.pixelWidth.setFixedWidth(40 * scale_w)
        self.pixelWidthSeq = QComboBox(self)
        self.pixelWidthSeq.addItem('None')
        self.pixelWidthSeq.setFixedWidth(20 * scale_w)
        self.pixelWidth.editingFinished.connect(lambda: self.variableProc('pixelWidth',self.pixelWidth.text()))
        self.pixelWidthSeq.activated.connect(lambda: self.menuProc('pixelWidthSeq',self.pixelWidthSeq.currentText()))

        self.designPanelLayout.addWidget(self.pixelWidthLabel,10,0)
        self.designPanelLayout.addWidget(self.pixelWidth,10,1)
        self.designPanelLayout.addWidget(self.pixelWidthSeq,10,2)

        #Spatial phase
        self.spatialPhaseLabel = QLabel('Phase',self)
        self.spatialPhaseLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.spatialPhase = QLineEdit(self)
        self.spatialPhase.setAlignment(QtCore.Qt.AlignRight)
        self.spatialPhase.setFixedWidth(40 * scale_w)
        self.spatialPhaseSeq = QComboBox(self)
        self.spatialPhaseSeq.addItem('None')
        self.spatialPhaseSeq.setFixedWidth(20 * scale_w)
        self.spatialPhase.editingFinished.connect(lambda: self.variableProc('spatialPhase',self.spatialPhase.text()))
        self.spatialPhaseSeq.activated.connect(lambda: self.menuProc('spatialPhaseSeq',self.spatialPhaseSeq.currentText()))

        self.designPanelLayout.addWidget(self.spatialPhaseLabel,9,0)
        self.designPanelLayout.addWidget(self.spatialPhase,9,1)
        self.designPanelLayout.addWidget(self.spatialPhaseSeq,9,2)


        # #insert blank after the spatial frequency row
        # self.blank4.setFixedHeight(20 * scale_h)
        # self.designPanelLayout.addWidget(self.blank4,11,0,1,10)
        # #self.blank4.setStyleSheet("QLabel {background-color: black;}")
        # self.blank4.setAlignment(QtCore.Qt.AlignVCenter)

        #aperture
        self.objectApertureLabel = QLabel('Aperture',self)
        self.objectApertureLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.objectAperture = QLineEdit(self)
        self.objectAperture.setAlignment(QtCore.Qt.AlignRight)
        self.objectAperture.setFixedWidth(40 * scale_w)
        self.objectApertureSeq = QComboBox(self)
        self.objectApertureSeq.addItem('None')
        self.objectApertureSeq.setFixedWidth(20 * scale_w)
        self.objectAperture.editingFinished.connect(lambda: self.variableProc('objectAperture',self.objectAperture.text()))
        self.objectApertureSeq.activated.connect(lambda: self.menuProc('objectApertureSeq',self.objectApertureSeq.currentText()))

        self.designPanelLayout.addWidget(self.objectApertureLabel,11,0)
        self.designPanelLayout.addWidget(self.objectAperture,11,1)
        self.designPanelLayout.addWidget(self.objectApertureSeq,11,2)
        
        #angular cycles
        self.angularCyclesLabel = QLabel('Cycles',self)
        self.angularCycles = QLineEdit(self)
        self.angularCyclesLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.angularCycles.setAlignment(QtCore.Qt.AlignRight)
        self.angularCycles.setFixedWidth(40 * scale_w)
        self.angularCyclesSeq = QComboBox(self)
        self.angularCyclesSeq.addItem('None')
        self.angularCyclesSeq.setFixedWidth(20 * scale_w)
        self.angularCycles.editingFinished.connect(lambda: self.variableProc('angularCycles',self.angularCycles.text()))
        self.angularCyclesSeq.activated.connect(lambda: self.menuProc('angularCyclesSeq',self.angularCyclesSeq.currentText()))

        self.designPanelLayout.addWidget(self.angularCyclesLabel,8,0)
        self.designPanelLayout.addWidget(self.angularCycles,8,1)
        self.designPanelLayout.addWidget(self.angularCyclesSeq,8,2)


        ###########################
        #Random Dot Kinetogram

        #Number dots, random dot kinetogram
        self.numDotsLabel = QLabel('# Dots',self)
        self.numDotsLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.numDots = QLineEdit(self)
        self.numDots.setFixedWidth(40 * scale_w)
        self.numDots.setAlignment(QtCore.Qt.AlignRight)
        self.numDotsSeq = QComboBox(self)
        self.numDotsSeq.addItem('None')
        self.numDotsSeq.setFixedWidth(20 * scale_w)
        self.numDots.editingFinished.connect(lambda: self.variableProc('numDots',self.numDots.text()))
        self.numDotsSeq.activated.connect(lambda: self.menuProc('numDotsSeq',self.numDotsSeq.currentText()))

        self.designPanelLayout.addWidget(self.numDotsLabel,8,0)
        self.designPanelLayout.addWidget(self.numDots,8,1)
        self.designPanelLayout.addWidget(self.numDotsSeq,8,2)

        #Dot coherence, random dot kinetogram
        self.dotCoherenceLabel = QLabel('Coherence',self)
        self.dotCoherenceLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.dotCoherence = QLineEdit(self)
        self.dotCoherence.setFixedWidth(40 * scale_w)
        self.dotCoherence.setAlignment(QtCore.Qt.AlignRight)
        self.dotCoherenceSeq = QComboBox(self)
        self.dotCoherenceSeq.addItem('None')
        self.dotCoherenceSeq.setFixedWidth(20 * scale_w)
        self.dotCoherence.editingFinished.connect(lambda: self.variableProc('dotCoherence',self.dotCoherence.text()))
        self.dotCoherenceSeq.activated.connect(lambda: self.menuProc('dotCoherenceSeq',self.dotCoherenceSeq.currentText()))

        self.designPanelLayout.addWidget(self.dotCoherenceLabel,9,0)
        self.designPanelLayout.addWidget(self.dotCoherence,9,1)
        self.designPanelLayout.addWidget(self.dotCoherenceSeq,9,2)

        #Signal dot direction, random dot kinetogram
        self.signalDirectionLabel = QLabel('Signal Dir.',self)
        self.signalDirectionLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.signalDirection = QLineEdit(self)
        self.signalDirection.setFixedWidth(40 * scale_w)
        self.signalDirection.setAlignment(QtCore.Qt.AlignRight)
        self.signalDirectionSeq = QComboBox(self)
        self.signalDirectionSeq.addItem('None')
        self.signalDirectionSeq.setFixedWidth(20 * scale_w)
        self.signalDirection.editingFinished.connect(lambda: self.variableProc('signalDirection',self.signalDirection.text()))
        self.signalDirectionSeq.activated.connect(lambda: self.menuProc('signalDirectionSeq',self.signalDirectionSeq.currentText()))

        self.designPanelLayout.addWidget(self.signalDirectionLabel,8,8)
        self.designPanelLayout.addWidget(self.signalDirection,8,9)
        self.designPanelLayout.addWidget(self.signalDirectionSeq,8,10)

        #Noise dot direction, random dot kinetogram
        self.noiseDirectionLabel = QLabel('Noise Dir.',self)
        self.noiseDirectionLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.noiseDirection = QLineEdit(self)
        self.noiseDirection.setFixedWidth(40 * scale_w)
        self.noiseDirection.setAlignment(QtCore.Qt.AlignRight)
        self.noiseDirectionSeq = QComboBox(self)
        self.noiseDirectionSeq.addItem('None')
        self.noiseDirectionSeq.setFixedWidth(20 * scale_w)
        self.noiseDirection.editingFinished.connect(lambda: self.variableProc('noiseDirection',self.noiseDirection.text()))
        self.noiseDirectionSeq.activated.connect(lambda: self.menuProc('noiseDirectionSeq',self.noiseDirectionSeq.currentText()))

        self.designPanelLayout.addWidget(self.noiseDirectionLabel,9,8)
        self.designPanelLayout.addWidget(self.noiseDirection,9,9)
        self.designPanelLayout.addWidget(self.noiseDirectionSeq,9,10)


        #Contrast
        self.contrastTypeLabel = QLabel('Contrast',self)
        self.contrastTypeLabel.setFont(bold)
        self.contrastType = QComboBox(self)
        self.contrastType.addItems(['Weber','Michelson','Intensity'])
        self.contrastType.activated.connect(lambda: self.menuProc('contrastType',self.contrastType.currentText()))
        self.contrastType.setFixedHeight(20 * scale_h)

        self.contrastLabel = QLabel('Contrast',self)
        self.contrastLabel.setFixedHeight(20 * scale_h)
        self.contrastLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.contrast = QLineEdit(self)
        self.contrast.setAlignment(QtCore.Qt.AlignRight)
        self.contrast.setFixedWidth(40 * scale_w)
        self.contrastSeq = QComboBox(self)
        self.contrastSeq.addItem('None')
        self.contrastSeq.setFixedWidth(20 * scale_w)
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
        self.blank3.setFixedHeight(20 * scale_h)
        self.blank3.setAlignment(QtCore.Qt.AlignVCenter)

        #Modulation
        self.modulationTypeLabel = QLabel('Modulation',self)
        self.modulationTypeLabel.setFont(bold)
        self.modulationTypeLabel.setFixedHeight(20 * scale_h)
        self.modulationType = QComboBox(self)
        self.modulationType.activated.connect(lambda: self.menuProc('modulationType',self.modulationType.currentText()))
        self.modulationType.setFixedHeight(20 * scale_h)
        self.modulationType.addItems(['Static','Square','Sine','Chirp','Noise'])

        self.modulationFreqLabel = QLabel('Freq.',self)
        self.modulationFreq =  QLineEdit(self)
        self.modulationFreq.setFixedWidth(40 * scale_w)
        self.modulationFreq.setAlignment(QtCore.Qt.AlignRight)
        self.modulationFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.modulationFreqSeq = QComboBox(self)
        self.modulationFreqSeq.addItem('None')
        self.modulationFreqSeq.setFixedWidth(20 * scale_w)
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
        self.motionTypeLabel.setFixedHeight(20 * scale_h)
        self.motionType = QComboBox(self)
        self.motionType.activated.connect(lambda: self.menuProc('motionType',self.motionType.currentText()))
        self.motionType.addItems(['Static','Drift','Random Walk'])
        self.motionType.setFixedHeight(20 * scale_h)

        self.designPanelLayout.addWidget(self.motionTypeLabel,5,8)
        self.designPanelLayout.addWidget(self.motionType,6,8,1,2)

        #Clockwise/counterclockwise drift option (for spinning windmill)
        self.turnDirection = QComboBox(self)
        self.turnDirection.activated.connect(lambda: self.menuProc('turnDirection',self.turnDirection.currentText()))
        self.turnDirection.addItems(['Clockwise','Counterclockwise'])
        self.turnDirection.setFixedHeight(20 * scale_h)

        self.designPanelLayout.addWidget(self.turnDirection,7,8,1,2)

        #Speed
        self.speedLabel = QLabel('Speed',self)
        self.speedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.speed = QLineEdit(self)
        self.speed.setFixedWidth(40 * scale_w)
        self.speed.setAlignment(QtCore.Qt.AlignRight)
        self.speedSeq = QComboBox(self)
        self.speedSeq.addItem('None')
        self.speedSeq.setFixedWidth(20 * scale_w)
        self.speed.editingFinished.connect(lambda: self.variableProc('speed',self.speed.text()))
        self.speedSeq.activated.connect(lambda: self.menuProc('speedSeq',self.speedSeq.currentText()))

        self.designPanelLayout.addWidget(self.speedLabel,7,8)
        self.designPanelLayout.addWidget(self.speed,7,9)
        self.designPanelLayout.addWidget(self.speedSeq,7,10)

        #Drift frequency
        self.driftFreqLabel = QLabel('Freq.',self)
        self.driftFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.driftFreq = QLineEdit(self)
        self.driftFreq.setFixedWidth(40 * scale_w)
        self.driftFreq.setAlignment(QtCore.Qt.AlignRight)
        self.driftFreqSeq = QComboBox(self)
        self.driftFreqSeq.addItem('None')
        self.driftFreqSeq.setFixedWidth(20 * scale_w)
        self.driftFreq.editingFinished.connect(lambda: self.variableProc('driftFreq',self.driftFreq.text()))
        self.driftFreqSeq.activated.connect(lambda: self.menuProc('driftFreqSeq',self.driftFreqSeq.currentText()))

        self.designPanelLayout.addWidget(self.driftFreqLabel,7,8)
        self.designPanelLayout.addWidget(self.driftFreq,7,9)
        self.designPanelLayout.addWidget(self.driftFreqSeq,7,10)

        #Start Radius
        self.startRadLabel = QLabel('Start Rad.',self)
        self.startRadLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.startRad = QLineEdit(self)
        self.startRad.setFixedWidth(40 * scale_w)
        self.startRad.setAlignment(QtCore.Qt.AlignRight)
        self.startRadSeq = QComboBox(self)
        self.startRadSeq.addItem('None')
        self.startRadSeq.setFixedWidth(20 * scale_w)
        self.startRad.editingFinished.connect(lambda: self.variableProc('startRad',self.startRad.text()))
        self.startRadSeq.activated.connect(lambda: self.menuProc('startRadSeq',self.startRadSeq.currentText()))

        self.designPanelLayout.addWidget(self.startRadLabel,8,8)
        self.designPanelLayout.addWidget(self.startRad,8,9)
        self.designPanelLayout.addWidget(self.startRadSeq,8,10)

        #Angle
        self.angleLabel = QLabel('Angle',self)
        self.angleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.angle = QLineEdit(self)
        self.angle.setFixedWidth(40 * scale_w)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.angleSeq = QComboBox(self)
        self.angleSeq.addItem('None')
        self.angleSeq.setFixedWidth(20 * scale_w)
        self.angle.editingFinished.connect(lambda: self.variableProc('angle',self.angle.text()))
        self.angleSeq.activated.connect(lambda: self.menuProc('angleSeq',self.angleSeq.currentText()))

        self.designPanelLayout.addWidget(self.angleLabel,9,8)
        self.designPanelLayout.addWidget(self.angle,9,9)
        self.designPanelLayout.addWidget(self.angleSeq,9,10)

        #Update Frequency for random walk
        self.walkFreqLabel = QLabel('Walk Freq.',self)
        self.walkFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.walkFreq = QLineEdit(self)
        self.walkFreq.setFixedWidth(40 * scale_w)
        self.walkFreq.setAlignment(QtCore.Qt.AlignRight)
        self.walkFreqSeq = QComboBox(self)
        self.walkFreqSeq.addItem('None')
        self.walkFreqSeq.setFixedWidth(20 * scale_w)
        self.walkFreq.editingFinished.connect(lambda: self.variableProc('walkFreq',self.walkFreq.text()))
        self.walkFreqSeq.activated.connect(lambda: self.menuProc('walkFreqSeq',self.walkFreqSeq.currentText()))

        self.designPanelLayout.addWidget(self.walkFreqLabel,9,8)
        self.designPanelLayout.addWidget(self.walkFreq,9,9)
        self.designPanelLayout.addWidget(self.walkFreqSeq,9,10)



        #blank after angle row so hiding modFrequency doesn't change grid
        self.blank5.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
        #self.blank5.setStyleSheet("QLabel {background-color: green;}")
        self.blank5.setAlignment(QtCore.Qt.AlignVCenter)

        

        #Delay
        self.timingLabel = QLabel('Timing',self)
        self.timingLabel.setFont(bold)
        self.delayLabel = QLabel('Delay',self)
        self.delay = QLineEdit(self)
        self.delay.setFixedWidth(40 * scale_w)
        self.delay.setAlignment(QtCore.Qt.AlignRight)
        self.delayLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.delaySeq = QComboBox(self)
        self.delaySeq.addItem('None')
        self.delaySeq.setFixedWidth(20 * scale_w)
        self.delay.editingFinished.connect(lambda: self.variableProc('delay',self.delay.text()))
        self.delaySeq.activated.connect(lambda: self.menuProc('delaySeq',self.delaySeq.currentText()))

        self.designPanelLayout.addWidget(self.timingLabel,13,0)
        self.designPanelLayout.addWidget(self.delayLabel,14,0)
        self.designPanelLayout.addWidget(self.delay,14,1)
        self.designPanelLayout.addWidget(self.delaySeq,14,2)

        #Duration
        self.durationLabel = QLabel('Duration',self)
        self.duration = QLineEdit(self)
        self.duration.setFixedWidth(40 * scale_w)
        self.duration.setAlignment(QtCore.Qt.AlignRight)
        self.durationLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.durationSeq = QComboBox(self)
        self.durationSeq.addItem('None')
        self.durationSeq.setFixedWidth(20 * scale_w)
        self.duration.editingFinished.connect(lambda: self.variableProc('duration',self.duration.text()))
        self.durationSeq.activated.connect(lambda: self.menuProc('durationSeq',self.durationSeq.currentText()))

        self.designPanelLayout.addWidget(self.durationLabel,15,0)
        self.designPanelLayout.addWidget(self.duration,15,1)
        self.designPanelLayout.addWidget(self.durationSeq,15,2)

        #Trial Time
        self.trialTimeLabel = QLabel('Trial Time',self)
        self.trialTime = QLineEdit(self)
        self.trialTime.setFixedWidth(40 * scale_w)
        self.trialTime.setAlignment(QtCore.Qt.AlignRight)
        self.trialTimeLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.trialTime.editingFinished.connect(lambda: self.variableProc('trialTime',self.trialTime.text()))

        self.designPanelLayout.addWidget(self.trialTimeLabel,16,0)
        self.designPanelLayout.addWidget(self.trialTime,16,1)

          #blank after angle row so hiding modFrequency doesn't change grid
        # self.blank6.setFixedHeight(20 * scale_h)
        # self.designPanelLayout.addWidget(self.blank6,16,8,1,1)
        # #self.blank5.setStyleSheet("QLabel {background-color: green;}")
        # self.blank6.setAlignment(QtCore.Qt.AlignVCenter)
        
        #Repititions
        self.repititionLabel = QLabel('Repititions',self)
        self.repititionLabel.setFont(bold)
        self.repeatsLabel = QLabel('Repeats',self)
        self.repeatsLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.repeats = QLineEdit(self)
        self.repeats.setFixedWidth(40 * scale_w)
        self.repeats.setAlignment(QtCore.Qt.AlignRight)

        self.loopCheckLabel = QLabel('Loop',self)
        self.loopCheckLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.loopCheck = QCheckBox(self)
        self.loopCheck.setChecked(False)

        self.designPanelLayout.addWidget(self.repititionLabel,13,4,1,2)
        self.designPanelLayout.addWidget(self.repeatsLabel,14,4)
        self.designPanelLayout.addWidget(self.repeats,14,5)
        self.designPanelLayout.addWidget(self.loopCheckLabel,15,4)
        self.designPanelLayout.addWidget(self.loopCheck,15,5)

        #Trajectories
        self.trajectoryLabel = QLabel('Trajectories')
        self.trajectoryLabel.setFont(bold)
        self.trajectory = QComboBox()
        self.trajectory.addItem('None')
        self.trajectory.activated.connect(lambda: self.menuProc('trajectory',self.trajectory.currentText()))
        self.trajectory.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.trajectoryLabel,13,8,1,2)
        self.designPanelLayout.addWidget(self.trajectory,14,8,1,2)

        #Triggers
        self.triggerLabel = QLabel('Triggers')
        self.triggerLabel.setFont(bold)
        self.trigger = QComboBox()
        self.trigger.addItems(['None','Wait For Trigger','Send Trigger'])
        self.trigger.setFixedHeight(20 * scale_h)
        self.sendTTL = QPushButton('TTL')
        self.sendTTL.setFixedHeight(20 * scale_h)
        self.sendTTL.setFixedWidth(30 * scale_w)
        self.designPanelLayout.addWidget(self.triggerLabel,15,8,1,2)
        self.designPanelLayout.addWidget(self.trigger,16,8,1,2)
        self.designPanelLayout.addWidget(self.sendTTL,16,7,1,1)
        self.sendTTL.clicked.connect(lambda: self.buttonProc("sendTTL"))

        self.startEphys = QPushButton('E',self)
        self.startEphys.setFixedHeight(20 * scale_h)
        self.startEphys.setFixedWidth(20 * scale_w)
        self.designPanelLayout.addWidget(self.startEphys,16,10)
        self.startEphys.clicked.connect(lambda: self.buttonProc("startEphys"))


    #Masks Panel
    def buildMasksPanel(self):
        left = 165 * scale_w
        top = 315 * scale_h
        width = 475 * scale_w
        height = 205 * scale_h

        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto Light", 10,weight=QtGui.QFont.Bold)
            large = QtGui.QFont("Roboto Light", 11)
        elif system == 'Darwin':
            #fonts
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
        self.apertureLabel = QLabel('Aperture')
        self.apertureLabel.setFont(bold)
        self.apertureLabel.setAlignment(QtCore.Qt.AlignVCenter)
        self.apertureStatus = QComboBox()
        self.apertureStatus.addItems(['On','Off'])
        self.apertureStatus.setFixedHeight(20 * scale_h)
        self.apertureStatus.activated.connect(lambda: self.menuProc('apertureStatus',self.apertureStatus.currentText()))

        self.apertureDiamLabel = QLabel('Diameter')
        self.apertureDiamLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.apertureDiam = QLineEdit()
        self.apertureDiam.setAlignment(QtCore.Qt.AlignRight)
        self.apertureDiam.setFixedWidth(40 * scale_w)
        self.apertureDiam.editingFinished.connect(lambda: self.variableProc('apertureDiam',self.apertureDiam.text()))

        self.apertureDiamSeq = QComboBox()
        self.apertureDiamSeq.addItem('None')
        self.apertureDiamSeq.setFixedWidth(20 * scale_w)
        self.apertureDiamSeq.activated.connect(lambda: self.menuProc('apertureDiamSeq',self.apertureDiamSeq.currentText()))

        maskPanelLayout.addWidget(self.apertureLabel,0,0)
        maskPanelLayout.addWidget(self.apertureStatus,0,1,1,2)
        maskPanelLayout.addWidget(self.apertureDiamLabel,1,0)
        maskPanelLayout.addWidget(self.apertureDiam,1,1)
        maskPanelLayout.addWidget(self.apertureDiamSeq,1,2)

        #Mask Object Types
        self.maskLabel = QLabel('Masks')
        self.maskLabel.setFont(bold)
        self.maskObjectTypeLabel = QLabel('Object')
        self.maskObjectTypeLabel.setFont(bold)

        self.maskObjectType = QComboBox()
        self.maskObjectType.addItems(['Circle','Gaussian','Blur'])
        self.maskObjectType.activated.connect(lambda: self.menuProc('maskObjectType',self.maskObjectType.currentText()))
        self.maskObjectType.setFixedHeight(20 * scale_h)

        maskPanelLayout.addWidget(self.maskLabel,2,0,1,2)
        maskPanelLayout.addWidget(self.maskObjectType,3,0,1,2)

        #Mask Object List Box
        self.maskObjectListBox = QListWidget(self)
        self.maskObjectListBox.setFixedWidth(127 * scale_w)
        self.maskObjectListBox.addItems(maskList)
        self.maskObjectListBox.setFont(large)
        self.maskObjectListBox.setCurrentRow(0)
        self.maskObjectListBox.setSelectionMode(1)
        self.maskObjectListBox.itemClicked.connect(lambda: self.listProc('maskObjectListBox',self.maskObjectListBox.currentRow()))
        maskPanelLayout.addWidget(self.maskObjectListBox,0,4,4,1)


        # #Add blank slot to the right of the object type menu
        # maskPanelLayout.addWidget(self.blank7,7,3)
        # #self.blank2.setStyleSheet("QLabel {background-color: blue;}")
        # self.blank7.setFixedHeight(20 * scale_h)
        # #self.blank2.setFixedWidth(20 * scale_h)
        # self.blank4.setAlignment(QtCore.Qt.AlignVCenter)

        #Mask Coordinates
        self.maskCoordinateLabel = QLabel('Coordinates')
        self.maskCoordinateLabel.setFont(bold)

        self.maskCoordinateType = QComboBox()
        self.maskCoordinateType.addItems(['Cartesian','Polar'])
        self.maskCoordinateType.activated.connect(lambda: self.menuProc('maskCoordinateType',self.maskCoordinateType.currentText()))
        self.maskCoordinateType.setFixedHeight(20 * scale_h)
        maskPanelLayout.addWidget(self.maskCoordinateLabel,0,6,1,2)
        maskPanelLayout.addWidget(self.maskCoordinateType,1,6,1,2)

        #Mask X offset
        self.maskXPosLabel = QLabel('X Offset')
        self.maskXPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskXPos = QLineEdit()
        self.maskXPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskXPos.setFixedWidth(40 * scale_w)
        self.maskXPos.editingFinished.connect(lambda: self.variableProc('maskXPos',self.maskXPos.text()))

        self.maskXPosSeq = QComboBox()
        self.maskXPosSeq.addItem('None')
        self.maskXPosSeq.setFixedWidth(20 * scale_w)
        self.maskXPosSeq.activated.connect(lambda: self.menuProc('maskXPosSeq',self.maskXPosSeq.currentText()))

        maskPanelLayout.addWidget(self.maskXPosLabel,2,6)
        maskPanelLayout.addWidget(self.maskXPos,2,7)
        maskPanelLayout.addWidget(self.maskXPosSeq,2,8)

        #Mask Y offset
        self.maskYPosLabel = QLabel('Y Offset')
        self.maskYPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskYPos = QLineEdit()
        self.maskYPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskYPos.setFixedWidth(40 * scale_w)
        self.maskYPos.editingFinished.connect(lambda: self.variableProc('maskYPos',self.maskYPos.text()))

        self.maskYPosSeq = QComboBox()
        self.maskYPosSeq.addItem('None')
        self.maskYPosSeq.setFixedWidth(20 * scale_w)
        self.maskYPosSeq.activated.connect(lambda: self.menuProc('maskYPosSeq',self.maskYPosSeq.currentText()))

        maskPanelLayout.addWidget(self.maskYPosLabel,3,6)
        maskPanelLayout.addWidget(self.maskYPos,3,7)
        maskPanelLayout.addWidget(self.maskYPosSeq,3,8)

        #Polar Coordinates - Radius
        self.maskPolarRadiusLabel = QLabel('Radius')
        self.maskPolarRadiusLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.maskPolarRadius = QLineEdit()
        self.maskPolarRadius.setAlignment(QtCore.Qt.AlignRight)
        self.maskPolarRadius.setFixedWidth(40 * scale_w)
        self.maskPolarRadiusSeq = QComboBox()
        self.maskPolarRadiusSeq.addItem('None')
        self.maskPolarRadiusSeq.setFixedWidth(20 * scale_w)
        self.maskPolarRadius.editingFinished.connect(lambda: self.variableProc('maskPolarRadius',self.maskPolarRadius.text()))
        self.maskPolarRadiusSeq.activated.connect(lambda: self.menuProc('maskPolarRadiusSeq',self.maskPolarRadiusSeq.currentText()))

        maskPanelLayout.addWidget(self.maskPolarRadiusLabel,2,6)
        maskPanelLayout.addWidget(self.maskPolarRadius,2,7)
        maskPanelLayout.addWidget(self.maskPolarRadiusSeq,2,8)

        #Polar Coordinates - Angle
        self.maskPolarAngleLabel = QLabel('Angle')
        self.maskPolarAngleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.maskPolarAngle = QLineEdit()
        self.maskPolarAngle.setAlignment(QtCore.Qt.AlignRight)
        self.maskPolarAngle.setFixedWidth(40 * scale_w)
        self.maskPolarAngleSeq = QComboBox()
        self.maskPolarAngleSeq.addItem('None')
        self.maskPolarAngleSeq.setFixedWidth(20 * scale_w)
        self.maskPolarAngle.editingFinished.connect(lambda: self.variableProc('maskPolarAngle',self.maskPolarAngle.text()))
        self.maskPolarAngleSeq.activated.connect(lambda: self.menuProc('maskPolarAngleSeq',self.maskPolarAngleSeq.currentText()))

        maskPanelLayout.addWidget(self.maskPolarAngleLabel,3,6)
        maskPanelLayout.addWidget(self.maskPolarAngle,3,7)
        maskPanelLayout.addWidget(self.maskPolarAngleSeq,3,8)

        #Mask Diameter
        self.maskDiameterLabel = QLabel('Diameter')
        self.maskDiameterLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.maskDiameter = QLineEdit()
        self.maskDiameter.setAlignment(QtCore.Qt.AlignRight)
        self.maskDiameter.setFixedWidth(40 * scale_w)
        self.maskDiameter.editingFinished.connect(lambda: self.variableProc('maskDiameter',self.maskDiameter.text()))

        self.maskDiameterSeq = QComboBox()
        self.maskDiameterSeq.addItem('None')
        self.maskDiameterSeq.setFixedWidth(20 * scale_w)
        self.maskDiameterSeq.activated.connect(lambda: self.menuProc('maskDiameterSeq',self.maskDiameterSeq.currentText()))

        maskPanelLayout.addWidget(self.maskDiameterLabel,4,0)
        maskPanelLayout.addWidget(self.maskDiameter,4,1)
        maskPanelLayout.addWidget(self.maskDiameterSeq,4,2)

        self.addMask = QPushButton('Add\nMask')
        self.addMask.setFixedWidth(65 * scale_w)
        maskPanelLayout.addWidget(self.addMask,5,0,2,1)
        self.removeMask = QPushButton('Remove\nMask')
        self.removeMask.setFixedWidth(65 * scale_w)
        maskPanelLayout.addWidget(self.removeMask,5,1,2,2)
        self.addMask.clicked.connect(lambda: self.buttonProc("addMask"))
        self.removeMask.clicked.connect(lambda: self.buttonProc("removeMask"))

        #Spacer
        maskPanelLayout.setColumnStretch(3,1)

        maskPanelLayout.setColumnStretch(5,1)

    #Sequences Panel
    def buildSequencePanel(self):
        left = 165 * scale_w
        top = 315 * scale_h
        width = 475 * scale_w
        height = 400 * scale_h

        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto Light", 10,weight=QtGui.QFont.Bold)
        elif system == 'Darwin':
            #fonts
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
        seqPanelLayout.addWidget(self.seqListBox,0,2,4,4)
        self.seqListBox.itemClicked.connect(lambda: self.listProc('seqListBox',self.seqListBox.currentRow()))

        #Sequence entry
        self.seqEntry = QLineEdit()
        seqPanelLayout.addWidget(self.seqEntry,4,0,1,6)
        self.seqEntry.editingFinished.connect(lambda: self.variableProc('seqEntry',self.seqEntry.text()))
        
        #Spacer
        self.blank1 = QLabel('')
        seqPanelLayout.addWidget(self.blank1,5,0)

        #Trajectory list box label
        self.trajListBoxLabel = QLabel('Trajectories')
        self.trajListBoxLabel.setFont(bold)
        self.trajListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajListBoxLabel,6,2,1,4)

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
        self.trajListBox.itemClicked.connect(lambda: self.listProc('trajListBox',self.trajListBox.currentRow()))
        seqPanelLayout.addWidget(self.trajListBox,7,2,4,4)

        #Angle list box label
        self.angleListBoxLabel = QLabel('Angle')
        self.angleListBoxLabel.setFont(bold)
        self.angleListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.angleListBoxLabel,11,0,1,2)

        #Angle list box
        self.angleListBox = QListWidget()
        self.angleListBox.currentRowChanged.connect(lambda: self.listProc('angleListBox',self.angleListBox.currentRow()))
        seqPanelLayout.addWidget(self.angleListBox,12,0,4,2)

        #Duration list box label
        self.durationListBoxLabel = QLabel('Duration')
        self.durationListBoxLabel.setFont(bold)
        self.durationListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.durationListBoxLabel,11,2,1,2)

        #Duration list box
        self.durationListBox = QListWidget()
        self.durationListBox.currentRowChanged.connect(lambda: self.listProc('durationListBox',self.durationListBox.currentRow()))
        seqPanelLayout.addWidget(self.durationListBox,12,2,4,2)

        #Speed list box label
        self.speedListBoxLabel = QLabel('Speed')
        self.speedListBoxLabel.setFont(bold)
        self.speedListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.speedListBoxLabel,11,4,1,2)

        #Speed list box
        self.speedListBox = QListWidget()
        self.speedListBox.currentRowChanged.connect(lambda: self.listProc('speedListBox',self.speedListBox.currentRow()))
        seqPanelLayout.addWidget(self.speedListBox,12,4,4,2)

        #Link aperture list box label
        self.linkApertureListBoxLabel = QLabel('Link')
        self.linkApertureListBoxLabel.setFont(bold)
        self.linkApertureListBoxLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.linkApertureListBoxLabel,11,6,1,1)

        #link aperture list box
        self.linkApertureListBox = QListWidget()
        self.linkApertureListBox.currentRowChanged.connect(lambda: self.listProc('linkApertureListBox',self.linkApertureListBox.currentRow()))
        seqPanelLayout.addWidget(self.linkApertureListBox,12,6,4,1)

        #Spacer
        # self.blank2 = QLabel('')
        # seqPanelLayout.addWidget(self.blank2,11,7,4,1)

        #Trajectory Angle Label
        self.trajAngleLabel = QLabel('Angle')
        self.trajAngleLabel.setFont(bold)
        self.trajAngleLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajAngleLabel,11,8,1,2)

        #Trajectory Duration Label
        self.trajDurationLabel = QLabel('Duration')
        self.trajDurationLabel.setFont(bold)
        self.trajDurationLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajDurationLabel,11,10,1,2)

        #Trajectory Speed Label
        self.trajSpeedLabel = QLabel('Speed')
        self.trajSpeedLabel.setFont(bold)
        self.trajSpeedLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajSpeedLabel,11,12,1,2)

        #Link Aperture Label
        self.trajSpeedLabel = QLabel('Link')
        self.trajSpeedLabel.setFont(bold)
        self.trajSpeedLabel.setAlignment(QtCore.Qt.AlignCenter)
        seqPanelLayout.addWidget(self.trajSpeedLabel,11,14,1,1)

        #Trajectory Angle Entry
        self.trajAngle = QLineEdit()
        seqPanelLayout.addWidget(self.trajAngle,12,8,1,2)

        #Trajectory Duration Entry
        self.trajDuration = QLineEdit()
        seqPanelLayout.addWidget(self.trajDuration,12,10,1,2)

        #Trajectory Speed Entry
        self.trajSpeed = QLineEdit()
        seqPanelLayout.addWidget(self.trajSpeed,12,12,1,2)

        #Link aperture Entry
        self.trajLink = QLineEdit()
        seqPanelLayout.addWidget(self.trajLink,12,14,1,1)

        #Append Segment Button
        self.appendSegment = QPushButton('Append')
        seqPanelLayout.addWidget(self.appendSegment,13,8,1,3)
        self.appendSegment.clicked.connect(lambda: self.buttonProc("appendSegment"))

        #Append Hold Segment Button
        self.appendHold = QPushButton('Hold')
        seqPanelLayout.addWidget(self.appendHold,13,11,1,3)
        self.appendHold.clicked.connect(lambda: self.buttonProc("appendHold"))

        #Edit Segment Button
        self.editSegment = QPushButton('Edit Segment')
        seqPanelLayout.addWidget(self.editSegment,14,8,1,6)
        self.editSegment.clicked.connect(lambda: self.buttonProc("editSegment"))

        #Remove Segment Button
        self.removeSegment = QPushButton('Remove Segment')
        seqPanelLayout.addWidget(self.removeSegment,15,8,1,6)
        self.removeSegment.clicked.connect(lambda: self.buttonProc("removeSegment"))

    #Path Panel
    def buildPathPanel(self):
        left = 10 * scale_w
        top = 145 * scale_h
        width = 475 * scale_w
        height = 115 * scale_h

        self.pathGroup = QGroupBox(self)
        pathLayout = QGridLayout()

        self.pathGroup.setLayout(pathLayout)
        self.pathGroup.move(left,top)
        self.pathGroup.resize(width,height)

        #Stimulus path
        self.stimPathLabel = QLabel('Path:',self)
        self.stimPathLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.stimPath = QLineEdit(self)
        self.stimPath.setText(stimPath)
        self.stimPathBrowse = QPushButton('...',self)
        self.stimPathBrowse.clicked.connect(lambda: self.buttonProc("stimPathBrowse"))
        self.stimPathBrowse.setFixedWidth(40 * scale_w)
        pathLayout.addWidget(self.stimPathLabel,0,0)
        pathLayout.addWidget(self.stimPath,0,1,1,2)
        pathLayout.addWidget(self.stimPathBrowse,0,3)


        #Save To path
        self.saveToPathLabel = QLabel('Save To:',self)
        self.saveToPathLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.saveToPath = QLineEdit(self)
        self.saveToPath.setText(saveToPath)
        self.saveToPathBrowse = QPushButton('...',self)
        self.saveToPathBrowse.clicked.connect(lambda: self.buttonProc("saveToPathBrowse"))
        self.saveToPathBrowse.setFixedWidth(40 * scale_w)
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
        self.stimID.setFixedWidth(40 * scale_w)
        self.stimID.setAlignment(QtCore.Qt.AlignCenter)
        pathLayout.addWidget(self.stimIDLabel,2,2)
        pathLayout.addWidget(self.stimID,2,3)

    #Globals Panel
    def buildGlobalsPanel(self):
        global BitDepth

        left = 495 * scale_w
        top = 10 * scale_h
        width = 145 * scale_w
        height = 250 * scale_h

        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto Light", 10,weight=QtGui.QFont.Bold)
        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

        self.globalsGroup = QGroupBox(self)
        self.globalsGroup.move(left,top)
        self.globalsGroup.resize(width,height)

        self.globalsLayout =QGridLayout()
        self.globalsGroup.setLayout(self.globalsLayout)
        self.globalsLayout.setContentsMargins(5,0,0,5)

        #Globals label
        self.globalsLabel = QLabel('Globals')
        self.globalsLayout.addWidget(self.globalsLabel,0,0,1,2)
        
        self.globalsLabel.setFont(bold)

        #Monitor

        self.monitor = QComboBox(self)
        self.monitor.setFixedWidth(45)
        self.monitorLabel= QLabel('Monitor')

        #Find number of monitors
        numScreens = QDesktopWidget().screenCount()

        for i in range(0,numScreens):
            self.monitor.addItem(str(i))

        self.globalsLayout.addWidget(self.monitorLabel,1,0,1,3)
        self.monitorLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.monitor,1,3,1,2)
        self.monitor.activated.connect(lambda: self.menuProc('monitor',self.monitor.currentText()))


        #PPM
        self.ppmLabel = QLabel('PPM')
        self.ppm = QLineEdit()
        self.ppm.setFixedWidth(45)
        self.ppm.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.ppmLabel,2,0,1,3)
        self.ppmLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.ppm,2,3,1,2)
        self.ppm.editingFinished.connect(lambda: self.variableProc('ppm',self.ppm.text()))

        #Background
        self.backgroundLabel = QLabel('Background')
        self.background = QLineEdit()
        self.background.setFixedWidth(45)
        self.background.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.backgroundLabel,3,0,1,3)
        self.backgroundLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.background,3,3,1,2)
        self.background.editingFinished.connect(lambda: self.variableProc('background',self.background.text()))


        #X Offset
        self.xOffsetLabel = QLabel('X Offset')
        self.xOffset = QLineEdit()
        self.xOffset.setFixedWidth(45)
        self.xOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.xOffsetLabel,4,0,1,3)
        self.xOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.xOffset,4,3,1,2)
        self.xOffset.editingFinished.connect(lambda: self.variableProc('xOffset',self.xOffset.text()))

        #Y Offset
        self.yOffsetLabel = QLabel('Y Offset')
        self.yOffset = QLineEdit()
        self.yOffset.setFixedWidth(45)
        self.yOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffsetLabel,5,0,1,3)
        self.yOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffset,5,3,1,2)
        self.yOffset.editingFinished.connect(lambda: self.variableProc('yOffset',self.yOffset.text()))

        #Sync Frames
        self.syncFramesLabel = QLabel('Sync Frames')
        self.syncFrames = QLineEdit()
        self.syncFrames.setFixedWidth(45)
        self.syncFrames.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFramesLabel,6,0,1,3)
        self.syncFramesLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFrames,6,3,1,2)
        self.syncFrames.editingFinished.connect(lambda: self.variableProc('syncFrames',self.syncFrames.text()))

        #Sync Spot
        self.syncSpotLabel = QLabel('Sync Spot',self)
        self.syncSpotLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.syncSpot = QCheckBox(self)
        self.syncSpot.setChecked(True)
        self.syncSpot.stateChanged.connect(lambda: self.checkProc('syncSpot',self.syncSpot.isChecked()))
        self.globalsLayout.addWidget(self.syncSpotLabel,7,0,1,3)
        self.globalsLayout.addWidget(self.syncSpot,7,3,1,2)

        #Gamma Table
        self.gammaTableLabel = QLabel('Gamma')
        self.gammaTable = QComboBox()
        self.gammaTable.addItems(['Native','Custom'])
        self.gammaTable.setFixedWidth(65)
        self.gammaTable.activated.connect(lambda: self.menuProc('gammaTable',self.gammaTable.currentText()))

        self.globalsLayout.addWidget(self.gammaTableLabel,8,0,1,1)
        self.gammaTableLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.gammaTable,8,2,1,4)

        #Intensity encoding
        self.encodingLabel = QLabel('Bit Depth')
        self.encoding = QComboBox()
        self.encoding.addItems(['8','12'])
        self.encoding.setFixedWidth(65)
        self.encoding.activated.connect(lambda: self.menuProc('encoding',self.encoding.currentText()))

        self.globalsLayout.addWidget(self.encodingLabel,9,0,1,1)
        self.encodingLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.encoding,9,2,1,4)

        self.encoding.setCurrentText('12')
        BitDepth = 12

    #Stimulus Bank
    def buildStimusBank(self):
        left = 10 * scale_w
        top = 348 * scale_h
        width = 145 * scale_w
        height = 330 * scale_h

        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto Light", 10,weight=QtGui.QFont.Bold)
            large = QtGui.QFont("Roboto Light", 11,weight=QtGui.QFont.Light)
        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
            large = QtGui.QFont("Helvetica", 13)

        #Stimulus Bank Label
        self.stimBankLabel  = QLabel('Stimulus Bank',self)
        self.stimBankLabel.move(left+30 * scale_w,top-95 * scale_h)

        #Stimulus subfolder
        self.subFolder = QComboBox(self)
        self.subFolder.move(left,top-60 * scale_h)
        self.subFolder.resize(width,25 * scale_h)

        #find the available user profiles
        profileList = [profile for profile in os.listdir(stimPath) if os.path.isdir(os.path.join(stimPath,profile))]

        self.subFolder.addItems(profileList)
        self.subFolder.setFont(large)
        self.subFolder.activated.connect(lambda: self.menuProc('subFolder',self.subFolder.currentText()))

        #Stimulus subsubfolder
        self.subsubFolder = QComboBox(self)
        self.subsubFolder.move(left,top-30 * scale_h)
        self.subsubFolder.resize(width,25 * scale_h)

        #find the currently selected user profile
        subfolderPath = os.path.join(stimPath,self.subFolder.currentText())
        #get the subsubfolders within that profile
        subfolderList = [subfolder for subfolder in os.listdir(subfolderPath) if os.path.isdir(os.path.join(subfolderPath,subfolder))]

        self.subsubFolder.addItems(subfolderList)
        self.subsubFolder.setFont(large)
        self.subsubFolder.activated.connect(lambda: self.menuProc('subsubFolder',self.subsubFolder.currentText()))

        #Stimulus Bank
        self.stimBank = QListWidget(self)
        self.stimBank.setFont(large)
        self.stimBank.move(left,top)
        self.stimBank.resize(width,height)
        self.stimBank.itemClicked.connect(lambda: self.listProc('stimBank',self.stimBank.currentRow()))

        #save stimulus
        self.saveStim = QPushButton('Save',self)
        self.saveStim.move(left+5 * scale_w,top + 340 * scale_h)
        self.saveStim.resize(60 * scale_w,20 * scale_h)
        self.saveStim.clicked.connect(lambda: self.buttonProc("saveStim"))

        #delete stimulus
        self.deleteStim = QPushButton('Delete',self)
        self.deleteStim.move(left+80 * scale_w,top + 340 * scale_h)
        self.deleteStim.resize(60 * scale_w,20 * scale_h)
        self.deleteStim.clicked.connect(lambda: self.buttonProc("deleteStim"))

    #save the stimulus to a text file
    def saveStimulus(self):
        #convert stimulus/sequence dictionaries into json string

        #can't save control references using json, so eliminating those in the saved file
        for object,_ in seqAssign.items():
            for item,_ in seqAssign[object].items():
                seqAssign[object][item]['control'] = 0

        stimulus = json.dumps(stim)
        sequence = json.dumps(seqAssign)
        seqDefs = json.dumps(seqDict)
        trajDefs = json.dumps(trajDict)
        maskDefs = json.dumps(maskDict)


        #show input dialog for naming the sequence
        savedStimulus = self.stimBank.currentItem()
        if savedStimulus is None:
            stimName = ''
        else:
            stimName = savedStimulus.text() #current selection is default name

        name, ok = QInputDialog.getText(self, 'Save Stimulus','Stimulus Name:',echo=QLineEdit.Normal,text=stimName)
        
        if name == '':
            return

        fileName = name + '.stim'

        subfolder = self.subFolder.currentText()
        subsubfolder = self.subsubFolder.currentText()

        if len(subsubfolder) > 0:
            path = stimPath + subfolder + '/' + subsubfolder + '/' + fileName
        else:  
            path = stimPath + subfolder + '/' + fileName

        print('Saved Stimulus: ' + path)

        #open and write dictionaries to the file
        with open(path,'w+') as file:
            file.write('Stimulus|')
            file.write(stimulus)
            file.write('|Sequences|')
            file.write(seqDefs)
            file.write('|Assignments|')
            file.write(sequence)
            file.write("|Trajectories|")
            file.write(trajDefs)
            file.write("|Masks|")
            file.write(maskDefs)

        file.close()

        #refresh stimulus bank
        self.changeUserSubFolder(subsubfolder)

        # self.getStimulusBank()

        #set the list box to select the newly saved stimulus
        newItem = self.stimBank.findItems(name,QtCore.Qt.MatchExactly)
        self.stimBank.setCurrentItem(newItem[0])

        self.loadStimulus()

    #save the designed stimulus to bitmap movie on disk
    def saveFramesToDisk(self):
        global abortStatus

        if isOpen == 0:
            self.initializeSession()

        #Reset abort abortStatus
        abortStatus = 0
        self.runStim(1)

    #Returns all of the trigger settings into a tuple
    def getTriggerSettings(self):
        interface = globalSettings['triggerInterface']
        digitalOut = globalSettings['digitalOut']
        digitalIn = globalSettings['digitalIn']
        portAddress = globalSettings['parallelPortAddress']

        return (interface,digitalOut,digitalIn,portAddress)

    #Sends a TTL pulse through pin 2 of the parallel port
    def sendTTLPulse(self,interface,digitalOut,digitalIn,portAddress):
                
        if interface == 'Parallel Port':
            port = parallel.ParallelPort(address = portAddress)
            
            if port:
                port.setPin(int(digitalOut),0) #set low
                port.setPin(int(digitalOut),1) #set high
                port.setPin(int(digitalOut),0) #set low

        elif interface == 'Nidaq Board':
            if digitalOut:
                with ni.Task() as task:
                    task.do_channels.add_do_chan(digitalOut)
                    task.write(False)
                    task.write(True)
                    task.write(False)

        #time stamp the trigger
        return time()

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
        subsubfolder = self.subsubFolder.currentText()

        if len(subsubfolder) > 0:
            path = stimPath + subfolder + '/' + subsubfolder + '/' + fileName
        else:
            path = stimPath + subfolder + '/' + fileName

        #delete the file, remove it from the stimulus bank
        os.remove(path)
        self.stimBank.takeItem(self.stimBank.row(stimulus))

        #refresh stimulus bank
        self.getStimulusBank()

        if index > 0:
            self.stimBank.setCurrentRow(index - 1)
        else:
            self.stimBank.setCurrentRow(0)

    #loads named stimulus into the stimulus dictionaries, without actually changing the control displays
    def fetchStimDict(self,stimName):

        global seqAssign,seqDict,stim
        global objectList,seqList,trajList,trajDict,maskDict

        #path to selected stimulus
        fileName = stimName + '.stim'
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + '/' + fileName

        #open and read stimulus file to dictionaries
        with open(path,'r') as file:
            fileStr = file.read()

            #split up the file into its components
            dictList = fileStr.split('|')
            stimStr = dictList[1]
            seqStr = dictList[3]
            assignmentStr = dictList[5]
            trajStr = dictList[7]
            # maskStr = dictList[9]

            #stim = json.loads(stimStr)

            stimLoaded = json.loads(stimStr)
            seqDict = json.loads(seqStr)
            seqAssignLoaded = json.loads(assignmentStr)
            trajDict = json.loads(trajStr)
            # maskDict = json.loads(maskStr)

            #convert the string keys to integers
            stimLoaded = {int(k):v for k,v in stimLoaded.items()}
            seqAssignLoaded = {int(k):v for k,v in seqAssignLoaded.items()}

            #reinitialize a fresh stim dict with all of the keys
            stim = {}

            objectList = []
            numObjects = len(stimLoaded) #total number of loaded objects
            for i in range(numObjects):
                objectList.append((stimLoaded[i]['objectType'])) #fill out the object list so addStimDict will work correctly
                self.addStimDict()

            #assign the loaded stim dict into the actual stim dict
            #this allows for the loaded stim to have an incomplete stim dictionary, if new controls have been added
            for object,_ in stimLoaded.items():
                for key,value in stimLoaded[object].items():
                    stim[object][key] = value   #some need to be float though

            for object,_ in seqAssignLoaded.items():
                for key,value in seqAssignLoaded[object].items():
                    seqAssign[object][key]['control'] = seqAssignLoaded[object][key]['control']
                    seqAssign[object][key]['parent'] = seqAssignLoaded[object][key]['parent']
                    seqAssign[object][key]['sequence'] = seqAssignLoaded[object][key]['sequence']

            #convert string controls to object controls
            for object,_ in seqAssign.items():
                for controlName,_ in seqAssign[object].items():
                    seqAssign[object][controlName]['control'] = control[controlName]

    #loads stimulus data into variables
    def loadStimulus(self,stimName=''):

        global seqAssign,seqDict,stim,trajDict,maskDict
        global objectList,seqList,trajList

        #which stimulus is selected
        if stimName == '':
            stimulus = self.stimBank.currentItem()
            index = self.stimBank.currentRow()
            stimName = stimulus.text()

        fileName = stimName + '.stim'
        subfolder = self.subFolder.currentText()
        subsubfolder = self.subsubFolder.currentText()

        if len(subsubfolder) > 0:
            path = stimPath + subfolder + "/" + subsubfolder + "/" + fileName
        else:
            path = stimPath + subfolder + '/' + fileName

        #open and read stimulus file to dictionaries
        with open(path,'r') as file:
            fileStr = file.read()

            #split up the file into its components
            dictList = fileStr.split('|')
            stimStr = dictList[1]
            seqStr = dictList[3]
            assignmentStr = dictList[5]
            trajStr = dictList[7]
            # maskStr = dictList[9]

            #stim = json.loads(stimStr)

            stimLoaded = json.loads(stimStr)
            seqDict = json.loads(seqStr)
            seqAssignLoaded = json.loads(assignmentStr)
            trajDict = json.loads(trajStr)

            #convert the string keys to integers
            stimLoaded = {int(k):v for k,v in stimLoaded.items()}
            seqAssignLoaded = {int(k):v for k,v in seqAssignLoaded.items()}

            if len(stimLoaded) != len(seqAssignLoaded):
                seqAssignLoaded.pop(len(stimLoaded),'None')

            #reinitialize a fresh stim dict with all of the keys
            stim = {}
            seqAssign = {}

            objectList = []
            numObjects = len(stimLoaded) #total number of loaded objects

            for i in range(numObjects):
                #Check for Noise objects, rename them to Checkerboards for backwards compatibility
                if stimLoaded[i]['objectType'] == 'Noise':
                    stimLoaded[i]['objectType'] = 'Checkerboard'

                objectList.append((stimLoaded[i]['objectType'])) #fill out the object list so addStimDict will work correctly
                self.addStimDict()

            #assign the loaded stim/seqAssign dict into the actual stim/seqAssign dict
            #this allows for the loaded stim to have an incomplete stim dictionary, if new controls have been added

            #exclude the globals from the stimulus load, back compatability purposes
            globalKeyList = list(globalSettings.keys())

            for object,_ in stimLoaded.items():
                for key,value in stimLoaded[object].items():
                    if key in globalKeyList:
                        continue
                    else:
                        stim[object][key] = value

            for object,_ in seqAssignLoaded.items():
                for key,value in seqAssignLoaded[object].items():
                    
                    if key in seqAssign[object]: 
                        try:
                            seqAssign[object][key]['control'] = seqAssignLoaded[object][key]['control']
                            seqAssign[object][key]['parent'] = seqAssignLoaded[object][key]['parent']
                            seqAssign[object][key]['sequence'] = seqAssignLoaded[object][key]['sequence']
                        except:
                            print('Error loading stimulus. Sequence assignment.')

            #convert string controls to object controls
            for object,_ in seqAssign.items():
                for controlName,_ in seqAssign[object].items():
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
            for key,_ in seqAssign[0].items():
                control[key].clear() #first reset sequence menus
                control[key].addItems(seqList)

            trajList = ['None']
            self.trajListBox.clear()

            for traj in trajDict:
                trajList.append(traj)
                self.trajListBox.addItem(traj)

            if len(trajList) > 1:
                self.trajListBox.setCurrentRow(0)
                item = self.trajListBox.currentItem()
                name = item.text()
                self.updateTrajectory(name)
            else:
                self.angleListBox.clear()
                self.durationListBox.clear()
                self.speedListBox.clear()
                self.linkApertureListBox.clear()
                self.trajAngle.setText('')
                self.trajDuration.setText('')
                self.trajSpeed.setText('')
                self.trajLink.setText('')

            self.trajectory.clear()
            self.trajectory.addItems(trajList)

            #clear object list and repopulate with loaded objects
            # objectList = []
            # numObjects = len(stim)
            # for i in range(numObjects):
            #     objectList.append((stim[i]['objectType']))

            #populate the controls for the first object
            self.objectListBox.clear()
            self.objectListBox.addItems(objectList)
            self.objectListBox.setCurrentRow(0)
            self.setObjectParameters(0)

            self.maskObjectListBox.clear()
            #self.maskObjectListBox.addItems(objectList)
            #self.maskObjectListBox.setCurrentRow(0)

            #display sequence assignment message
            self.displaySeqAssignments(0)

    #find all the stimulus files in the selected subfolder
    def getStimulusBank(self):
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder

        if os.path.isdir(path) == False:
            return        

        fileList = os.listdir(path)
        subfolderList = []
        stimList = []

        #remove all subsubfolder references in the menu
        self.subsubFolder.clear()

        #find all the subfolders
        i = 0
        for _ in fileList:
            folderCheck = os.path.join(path,fileList[i])
            if os.path.isdir(folderCheck):
                subfolderList.append(fileList[i])
            i += 1

        #add subfolder if it is there
        if len(subfolderList) > 0:
            path = stimPath + subfolder + "/" + subfolderList[0]

        self.subsubFolder.addItems(subfolderList)

        #get the files within the first subfolder
        fileList = os.listdir(path)

        i = 0
        for _ in fileList:
            fileList[i],ext = os.path.splitext(fileList[i])

            #only accept .stim files (these are just text files with .stim extension)
            if ext == '.stim':
                stimList.append(fileList[i])
           
            i += 1

        

        #add stimulus files to the stimulus bank
        self.stimBank.clear()

        if len(stimList) > 0:
            self.stimBank.addItems(stimList)

            #alphabetical order
            self.stimBank.sortItems(QtCore.Qt.AscendingOrder)

        return stimList

    #finds all the images in the selected stimulus subfolder with .bmp extensions
    def getImageBank(self):
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder

        if os.path.isdir(path) == False:
            return

        fileList = os.listdir(path)
        imageList = []

        i = 0
        for _ in fileList:
            fileList[i],ext = os.path.splitext(fileList[i])

            #only accept .stim files (these are just text files with .stim extension)
            if ext == '.bmp':
                imageList.append(fileList[i])

            i += 1

        #add the images to the drop down menu
        self.imagePath.addItems(imageList)

    #finds all the frame sequences in the selected stimulus subfolder with .bmp extensions
    def getFrameBank(self):
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + "/Frames/"

        if os.path.isdir(path) == False:
            return

        folderList = os.listdir(path)

        #add the images to the drop down menu
        self.framePath.addItems(folderList)

    #is the string a decimal number?
    def isFloat(self,s):
        return '.' in s

    #creates a numpy array of a circle at the specified center point and radius
    def create_circular_mask(self,h, w, type, center=None, radius=None):
        #mask array is either -1 or 1. -1 is part of the masked area, 1 is part of the windowed area

        if center is None: # use the middle of the image
            center = [int(w/2), int(h/2)]
        if radius is None: # use the smallest distance between the center and image walls
            radius = min(center[0], center[1], w-center[0], h-center[1])

        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
        mask = dist_from_center <= radius

        maskOut = np.ones((w,h))
        #window or mask?
        if type == 'Window':
            maskOut[~mask] = -1
        elif type == 'Mask':
            maskOut[mask] = -1

        return maskOut

    #Default settings
    def setDefaults(self):
        self.monitor.setCurrentIndex(0)
        self.ppm.setText('0.34')
        self.background.setText('0')
        self.xOffset.setText('-105')
        self.yOffset.setText('-25')
        self.syncFrames.setText('0')
        self.xPos.setText('0')
        self.yPos.setText('0')
        self.polarRadius.setText('0')
        self.polarAngle.setText('0')
        self.maskXPos.setText('0')
        self.maskYPos.setText('0')
        self.diameter.setText('0')
        self.innerDiameter.setText('0')
        self.outerDiameter.setText('0')
        self.length.setText('0')
        self.width.setText('0')
        self.spatialFreq.setText('0')
        self.spatialPhase.setText('0')
        self.orientation.setText('0')
        self.contrast.setText('0')
        self.modulationFreq.setText('0')
        self.repeats.setText('1')
        self.speed.setText('0')
        self.driftFreq.setText('0')
        self.startRad.setText('0')
        self.angle.setText('0')
        self.delay.setText('0')
        self.duration.setText('1')
        self.trialTime.setText('0')
        self.apertureDiam.setText('0')
        self.maskDiameter.setText('0')
        self.maskPolarRadius.setText('0')
        self.maskPolarAngle.setText('0')
        self.noiseSize.setText('50')
        self.noiseSeed.setText('0')
        # self.noiseFreq.setText('0')
        self.cloudSF.setText('0.125')
        self.cloudSFBand.setText('0.1')
        self.cloudSpeedX.setText('1.0')
        self.cloudSpeedY.setText('0')
        self.cloudSpeedBand.setText('0.5')
        self.cloudOrient.setText('0')
        self.cloudOrientBand.setText('20')
        self.angularCycles.setText('0')
        self.apertureStatus.setCurrentText('Off')
        self.stimID.setText('0')
        self.saveToPath.setText(saveToPath)

     #saves MotionCloud array as an HDF5
   # def saveCloud(self,cloud):

        #put the file in the stimulus subfolder
        # fileName = 'cloudFile.hdf5'
        # subfolder = self.subFolder.currentText()
        # path = stimPath + subfolder + '/' + fileName

        # file = h5py.File(path,'w')
        # file.create_dataset('MC',data=cloud,compression='gzip',compression_opts=9)
        # file.close()

#Build the trigger menu GUI
class triggerMenu(QMainWindow):
    #initializes the trigger menu class
    def __init__(self):
        super(triggerMenu,self).__init__()

        global globalSettings, NI_FLAG

        #GUI dimensions
        self.title = 'Setup Triggers'
        self.left = 30
        self.top = 30
        self.width = 250
        self.height = 200

        #set default fonts/sizes depending on operating system
        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto", 10,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Roboto", 12,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Roboto Light",28,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Roboto Light",10,weight=QtGui.QFont.Light)
            counterFont = QtGui.QFont('Roboto Light',18,weight=QtGui.QFont.Normal)

        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 12,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Helvetica",32,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Helvetica",12,weight=QtGui.QFont.ExtraLight)
            counterFont = QtGui.QFont('Helvetica',18,weight=QtGui.QFont.Normal)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.triggerPanel = QGroupBox(self)
        self.triggerPanelLayout = QGridLayout()
        self.triggerPanelLayout.setVerticalSpacing(5)

        self.triggerPanel.setLayout(self.triggerPanelLayout)
        self.triggerPanel.move(0,0)
        self.triggerPanel.resize(self.width,self.height)

        #Trigger interface
        row = 0

        if NI_FLAG:
            interfaceItems = ['Nidaq Board','Parallel Port']
        else:
            interfaceItems = ['Parallel Port']

        self.triggerInterfaceLabel = QLabel('Interface')
        self.triggerInterfaceLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.triggerInterface = QComboBox()
        self.triggerInterface.addItems(interfaceItems)
        self.triggerInterface.activated.connect(lambda: self.menuProc('triggerInterface',self.triggerInterface.currentText()))
        self.triggerInterface.setFixedHeight(20)

        self.triggerPanelLayout.addWidget(self.triggerInterfaceLabel,row,0)
        self.triggerPanelLayout.addWidget(self.triggerInterface,row,1,1,1)

        row += 1

        
        if NI_FLAG:
            lineList = []
            s = ni.system.System.local()

            for device in s.devices:
                lineList += [line.name for line in device.di_lines]

            #Nidaq digital lines in
            self.digitalLinesInLabel = QLabel('Digital In')
            self.digitalLinesInLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            self.digitalInLines = QComboBox()
            self.digitalInLines.addItems(lineList)
            self.digitalInLines.activated.connect(lambda: self.menuProc('digitalInLines',self.digitalInLines.currentText()))
            self.digitalInLines.setFixedHeight(20)

            self.triggerPanelLayout.addWidget(self.digitalLinesInLabel,row,0)
            self.triggerPanelLayout.addWidget(self.digitalInLines,row,1,1,1)

            row += 1

            #Nidaq digital lines out
            self.digitalLinesOutLabel = QLabel('Digital Out')
            self.digitalLinesOutLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            self.digitalOutLines = QComboBox()
            self.digitalOutLines.addItems(lineList)
            self.digitalOutLines.activated.connect(lambda: self.menuProc('digitalOutLines',self.digitalOutLines.currentText()))
            self.digitalOutLines.setFixedHeight(20)

            self.triggerPanelLayout.addWidget(self.digitalLinesOutLabel,row,0)
            self.triggerPanelLayout.addWidget(self.digitalOutLines,row,1,1,1)

            #reset the row counter
            row = 1

        #parallel port addresses
        self.parallelPortAddressLabel = QLabel('Port Address')
        self.parallelPortAddressLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.parallelPortAddress = QLineEdit()
        self.parallelPortAddress.setAlignment(QtCore.Qt.AlignRight)
        self.parallelPortAddress.setFixedWidth(80)
        self.parallelPortAddress.editingFinished.connect(lambda: self.variableProc('parallelPortAddress',self.parallelPortAddress.text()))

        self.triggerPanelLayout.addWidget(self.parallelPortAddressLabel,row,0)
        self.triggerPanelLayout.addWidget(self.parallelPortAddress,row,1,1,1)

        row += 1

        #Input parallel port address and pin
        self.inputTriggerLabel = QLabel('Pin In')
        self.inputTriggerLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.inputTrigger = QComboBox()
        self.inputTrigger.addItems(['0','1','2','3','4','5','6','7'])
        self.inputTrigger.setFixedHeight(20)
        self.inputTrigger.setFixedWidth(40)
        self.inputTrigger.activated.connect(lambda: self.menuProc('inputTrigger',self.inputTrigger.currentText()))

        self.triggerPanelLayout.addWidget(self.inputTriggerLabel,row,0)
        self.triggerPanelLayout.addWidget(self.inputTrigger,row,1,1,1)

        row += 1

        #Output parallel port pin
        self.outputTriggerLabel = QLabel('Pin Out')
        self.outputTriggerLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.outputTrigger = QComboBox()
        self.outputTrigger.addItems(['0','1','2','3','4','5','6','7'])
        self.outputTrigger.setFixedHeight(20)
        self.outputTrigger.setFixedWidth(40)
        self.outputTrigger.activated.connect(lambda: self.menuProc('outputTrigger',self.outputTrigger.currentText()))

        self.triggerPanelLayout.addWidget(self.outputTriggerLabel,row,0)
        self.triggerPanelLayout.addWidget(self.outputTrigger,row,1,1,1)

        row += 1

        #insert variable height spacer at the bottom of the panel
        self.rowSpacer = QLabel('',self)
        self.triggerPanelLayout.addWidget(self.rowSpacer,row,0,1,2)
        self.triggerPanelLayout.setRowStretch(5,2)
        self.rowSpacer.setAlignment(QtCore.Qt.AlignVCenter)


        #recall the settings from the global settings file
        self.recallTriggerSettings()

    #Set the triggers according to the global settings file
    def recallTriggerSettings(self):
        global globalSettings

        interface = globalSettings['triggerInterface']

        #if empty, set to first item in the list
        if interface == '':
            self.triggerInterface.setCurrentIndex(0)
            interface = self.triggerInterface.currentText()
            globalSettings['triggerInterface'] = interface
        else:
            self.triggerInterface.setCurrentText(interface)

        if interface == 'Nidaq Board':
            di = globalSettings['digitalIn']

            if di == '':
                self.digitalInLines.setCurrentIndex(0)
                globalSettings['digitalIn'] = self.digitalInLines.currentText()
            else:
                self.digitalInLines.setCurrentText(globalSettings['digitalIn'])

            do = globalSettings['digitalOut']
            if do == '':
                self.digitalOutLines.setCurrentIndex(0)
                globalSettings['digitalOut'] = self.digitalOutLines.currentText()
            else:
                self.digitalOutLines.setCurrentText(globalSettings['digitalOut'])
        elif interface == 'Parallel Port':
            di = globalSettings['digitalIn']
            if di == '':
                self.inputTrigger.setCurrentIndex(0)
                globalSettings['digitalIn'] = self.inputTrigger.currentText()
            else:
                self.inputTrigger.setCurrentText(globalSettings['digitalIn'])

            do = globalSettings['digitalOut']
            if do == '':
                self.outputTrigger.setCurrentIndex(0)
                globalSettings['digitalOut'] = self.outputTrigger.currentText()
            else:
                self.outputTrigger.setCurrentText(globalSettings['digitalOut'])

            
            self.parallelPortAddress.setText(str(globalSettings['parallelPortAddress']))
            
        #switch to the correct control set
        self.switchControls(interface)

    #Handles variable inputs for the trigger panel
    def variableProc(self,controlName,entry):
        global globalSettings
        globalSettings['parallelPortAddress'] = entry

        #auto save any changes to the global settings file
        ex.saveGlobalSettings()

    #Handles menu/combobox inputs for the trigger panel
    def menuProc(self,controlName,selection):
        global globalSettings

        if controlName == 'triggerInterface':
            self.switchControls(selection)
            globalSettings['triggerInterface'] = self.triggerInterface.currentText()
        elif controlName == 'inputTrigger':
            globalSettings['digitalIn'] = self.inputTrigger.currentText()
        elif controlName == 'outputTrigger':
            globalSettings['digitalOut'] = self.outputTrigger.currentText()
        elif controlName == 'digitalInLines':
            globalSettings['digitalIn'] = self.digitalInLines.currentText()
        elif controlName == 'digitalOutLines':
            globalSettings['digitalOut'] = self.digitalOutLines.currentText()

        #auto save any changes to the global settings file
        ex.saveGlobalSettings()

    #Switches the control set depending on the trigger interface
    def switchControls(self,selection):
        global globalSettings, NI_FLAG

        if selection == 'Nidaq Board':
            if(NI_FLAG):
                self.digitalInLines.show()
                self.digitalLinesInLabel.show()
                self.digitalOutLines.show()
                self.digitalLinesOutLabel.show()

                self.inputTriggerLabel.hide()
                self.inputTrigger.hide()
                self.outputTrigger.hide()
                self.outputTriggerLabel.hide()
                self.parallelPortAddressLabel.hide()
                self.parallelPortAddress.hide()

                globalSettings['digitalIn'] = self.digitalInLines.currentText()
                globalSettings['digitalOut'] = self.digitalOutLines.currentText()


        elif selection == 'Parallel Port':
            if NI_FLAG:
                self.digitalInLines.hide()
                self.digitalLinesInLabel.hide()
                self.digitalOutLines.hide()
                self.digitalLinesOutLabel.hide()

            self.inputTriggerLabel.show()
            self.inputTrigger.show()
            self.outputTrigger.show()
            self.outputTriggerLabel.show()
            self.parallelPortAddressLabel.show()
            self.parallelPortAddress.show()

            globalSettings['digitalIn'] = self.inputTrigger.currentText()
            globalSettings['digitalOut'] = self.outputTrigger.currentText()

#Writes the stimulus dictionary to an HDF5 file that can be read from a shared folder
def writeHDF5(stim,seqAssign,seqDict,trajDict,maskDict,stimName):

    fileName = saveToPath +'currentStimulus.h5'
    h = h5py.File(fileName,'w')

    g = h.create_group('StimGen')
    
    stimGroup = g.create_group('Stimulus')
    seqGroup = g.create_group('Sequences')
    seqAssignGroup = g.create_group('Sequence Assignments')
    trajGroup = g.create_group('Trajectories')
    maskGroup = g.create_group('Masks')

    g.create_group('Timestamps')

    a = stimGroup.attrs
    a.create('Name',stimName)
    a.create('Objects',len(stim))

    for objName,obj in stim.items():
        #each stimulus object gets its own group
        objectGroup = stimGroup.create_group(str(objName))

        objectAttr = objectGroup.attrs
        #write the stimulus object attributes
        for k,v in obj.items():
            objectAttr.create(k,v)

    a = seqGroup.attrs
    for k,v in seqDict.items():
        data = str(v)
        a.create(k,data)

    a = seqAssignGroup.attrs
    for objName,obj in seqAssign.items():
        #each stimulus object gets its own group
        objectGroup = seqAssignGroup.create_group(str(objName))

        objectAttr = objectGroup.attrs
        #write the stimulus object attributes
    
        for k,v in obj.items():
            key = str(v['parent'])
            data = str(v['sequence'])    
            objectAttr.create(key,data)

    a = trajGroup.attrs
    for k,v in trajDict.items():
        data = str(v)
        a.create(k,data)

    h.close

def writeTimestamps(group,timestamps):

    #writes trigger timestamps to the current stimulus log file
    fileName = saveToPath + 'currentStimulus.h5'
    h = h5py.File(fileName,'r+')

    g = h['StimGen/Timestamps']

    timestamparray = np.array(timestamps)
    g.create_dataset(group,data=timestamparray)
    
    h.close

#Start the application
if __name__ == '__main__':

    #scaling will transfer to lower res monitors
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    #create instance of application
    StimGen = QApplication([])

    #styles
    StimGen.setStyle('Fusion')

    system = platform.system()
    if system == 'Windows' or system == 'Linux':
        #fonts
        myFont = QtGui.QFont('Roboto Light', 10,weight=QtGui.QFont.Light)

    elif system == 'Darwin':
        #fonts
        myFont = QtGui.QFont('Helvetica', 12,weight=QtGui.QFont.Light)

    StimGen.setFont(myFont)

    ex = App()
    StimGen.exec_()
