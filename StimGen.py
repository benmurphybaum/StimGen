#StimGen python

#import widgets
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLineEdit,QGroupBox,QComboBox,QFrame,QAbstractItemView,QDesktopWidget
from PyQt5.QtWidgets import QLabel,QListWidget,QListWidgetItem,QSpacerItem,QVBoxLayout,QGridLayout,QCheckBox,QInputDialog,QListView,QFontDialog
from PyQt5 import QtCore,QtGui

#from PyQt5.QtGui import QIcon, QPixmap

#timing libraries
from time import sleep

#for monitor specifications
# from win32api import GetSystemMetrics

#for plotting data
#import matplotlib.pyplot as plt

#for browsing file explorer
import tkinter
from tkinter import filedialog, Tk

#triggers
import nidaqmx as ni

#for saving and loading stimuli from disk
import json
import os
import h5py
import csv

#for copying dictionaries
import copy

#PsychoPy
from psychopy import visual, core

import platform

#Motion Clouds
import MotionClouds as mc

import numpy as np

#Build the GUI
class App(QMainWindow):

    #startup code
    def __init__(self):
        global objectList, seqList, trajList, maskList, stim, trajectoryStim, seqAssign, seqDict, trajDict, maskDict, basePath, stimPath, saveToPath, system
        global scale_w,scale_h,device

        super(App,self).__init__()

        #monitor scale factor
        # w = GetSystemMetrics(0)
        # h = GetSystemMetrics(1)

        # w = 2048
        # h = 1536
        self.screen = QDesktopWidget().availableGeometry(1)
        w = self.screen.width()
        h = self.screen.height()

        #coded on 2880x1800 retina display
        scale_h = 1
        scale_w = 1

        #GUI dimensions
        self.title = "StimGen 5.0"
        self.left = 10 * scale_w
        self.top = 10 * scale_h
        self.width = 650 * scale_w
        self.height = 780 * scale_h

        #path to the StimGen.py file
        #basePath = 'C:/Users/jadob/Desktop/StimGenPy_WIN/StimGen/'
        basePath = '/Users/bmb/Documents/GitHub/StimGenPy_WIN/StimGen/'
        stimPath = basePath + 'stimuli/'
        imagePath = basePath + 'images/'
        saveToPath = '/Users/bmb/Documents/GitHub/StimGenPy_WIN/stimulusLog/'

        #operating system
        system = platform.system()

        #set default fonts/sizes depending on operating system
        if system == 'Windows' or system == 'Linux':
            #fonts
            bold = QtGui.QFont("Roboto", 10,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Roboto", 12,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Roboto Light",28,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Roboto Light",10,weight=QtGui.QFont.Light)
        elif system == 'Darwin':
            #fonts
            bold = QtGui.QFont("Helvetica", 12,weight=QtGui.QFont.Normal)
            boldLarge = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)
            titleFont = QtGui.QFont("Helvetica",32,weight=QtGui.QFont.Light)
            subTitleFont = QtGui.QFont("Helvetica",12,weight=QtGui.QFont.ExtraLight)

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
        self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');
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
        self.runStimulus.move(10 * scale_w,720 * scale_h)
        self.runStimulus.resize(75 * scale_w,30 * scale_h)
        self.runStimulus.setFont(boldLarge)
        self.runStimulus.setStyleSheet('QPushButton {background-color: rgba(150, 245, 150, 150)}')
        self.runStimulus.clicked.connect(lambda: self.buttonProc("runStimulus"))

        self.abortStimulus = QPushButton('Abort',self)
        self.abortStimulus.move(90 * scale_w,720 * scale_h)
        self.abortStimulus.resize(75 * scale_w,30 * scale_h)
        self.abortStimulus.setFont(boldLarge)
        self.abortStimulus.setStyleSheet('QPushButton {background-color: rgba(245, 150, 150, 150)}')
        self.abortStimulus.clicked.connect(lambda: self.buttonProc("abortStimulus"))

        self.sequenceMessage = QLabel('',self)
        self.sequenceMessage.move(175 * scale_w,720 * scale_h)
        self.sequenceMessage.resize(300 * scale_w,60 * scale_h)

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
        self.setDefaults()

        #Make first stimulus and sequence assignment dictionaries
        stim = {}
        trajectoryStim = {}

        seqAssign = {} #holds sequence assignments for each control
        seqDict = {} #holds the actual sequence entries
        trajDict = {} #holds the trajectory entries
        maskDict = {} #holds the mask entries

        self.addStimDict()

        #get the stimulus files
        self.getStimulusBank()

        #get the stimulus images
        self.getImageBank()

        if self.stimBank.count() > 0:
            self.stimBank.setCurrentRow(0)
            self.loadStimulus()

        #show the GUI
        self.show()

        #globals
        global isOpen
        isOpen = 0 #stimulus window is closed

    #Handles all variable entries
    def variableProc(self,controlName,entry):
        global stim, seqDict, maskDict

        ppm = float(self.ppm.text())

        #Need to check each variable for validity
        if controlName == 'background':
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
        else:
            #all other variable controls
            #Assign variable entry to the stim dictionary for the selected object
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
            self.designButton.setStyleSheet('QPushButton {background-color: rgba(180, 245, 245, 255)}');

            self.maskPanel.hide()
            self.masksButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            self.sequencePanel.hide()
            self.sequencesButton.setStyleSheet('QPushButton {background-color: rgba(255, 255, 255, 255)}');

            #Bug when masks are changed sometimes grating settings go back to circle settings
            self.setContextualMenus() #ensures that the parameters have the correct settings.


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

            if isOpen == 0:
                return 0

            #Run the stimulus
            self.runStim()

            #save data to stimulus log
            if abortStatus == 0:
                self.writeStimLog()
                stimID = stimID + 1
                self.stimID.setText(str(stimID))

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

        elif controlName == 'addTraj':
            self.addTrajectory()

        elif controlName == 'removeTraj':
            self.removeTrajectory()

        elif controlName == 'appendSegment':
            item = self.trajListBox.currentItem() #which trajectory
            name = item.text()

            trajDict[name]['angle'].append(self.trajAngle.text())
            trajDict[name]['duration'].append(self.trajDuration.text())

            self.updateTrajectory(name)

        elif controlName == 'editSegment':
            item = self.trajListBox.currentItem() #which trajectory
            name = item.text()

            #selected segment is the same for the duration list box
            index = self.angleListBox.currentRow()

            #edit the entry in place
            trajDict[name]['angle'][index] = self.trajAngle.text()
            trajDict[name]['duration'][index] = self.trajDuration.text()

            self.updateTrajectory(name)

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
            stimPath = tkinter.filedialog.askdirectory(initialdir = stimPath)
            self.stimPath.setText(stimPath)

        elif controlName == 'saveToPathBrowse':
            if len(saveToPath) == 0:
                startPath = basePath
            else:
                startPath = saveToPath
            Tk().withdraw()
            saveToPath = tkinter.filedialog.askdirectory(initialdir = startPath)
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
        else:
            #default
            print('other')

    #writes the stimulus that was just run to the stimulus log on disk
    def writeStimLog(self):

        saveToPath = self.saveToPath.text()

        #ensure valid path
        if saveToPath.endswith('/') == False:
            saveToPath = saveToPath + '/'

        fileName = self.fileName.text()
        if len(fileName) == 0:
            return #only save if a file name has been provided
        else:
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

    #Handles all drop down menu selections
    def menuProc(self,controlName,selection):
        global objectList, stim, seqAssign, win, main,subfolder

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
            if selection != 'None':
                seqAssign[object][controlName]['control'].setStyleSheet("background-color: rgba(150, 245, 150, 150)")
            else:
                seqAssign[object][controlName]['control'].setStyleSheet("background-color: white")
                seqAssign[object][controlName]['control'].setStyleSheet("color: black")

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

        elif controlName == 'gammaTable':
            if isOpen:
                #win.gamma = float(selection)
                mon = monitors.Monitor('Generic Non-PnP Monitor')
                mon.setGamma(float(self.gammaTable.currentText()))
                win.flip()

        elif controlName == 'subFolder':
            subfolder = selection
            #get the stimulus files
            self.getStimulusBank()
            if self.stimBank.count() > 0:
                self.stimBank.setCurrentRow(0)
                self.loadStimulus()
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

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]

            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])

        elif controlName == 'durationListBox':
            self.angleListBox.setCurrentRow(index)

            whichTrajectory = self.trajListBox.currentRow()
            name = trajList[whichTrajectory + 1]
            if(name == 'None'):
                return

            self.trajAngle.setText(trajDict[name]['angle'][index])
            self.trajDuration.setText(trajDict[name]['duration'][index])

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
        ppm = float(self.ppm.text())

        if controlName == 'syncSpot':
            #sync spot
            if isChecked:
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

                if isOpen == 1:
                    syncSpot.draw()
                    win.flip()
            else:
                if isOpen == 1:
                    win.flip()

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

        #clear the angle/duration list boxes
        self.angleListBox.clear()
        self.durationListBox.clear()

        #add trajectory to the trajectory menu
        self.trajectory.addItem(name)

        #add empty trajectory to the seqDict
        trajDict[name] = {
        'angle':[],
        'duration':[]
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
            return
        else:
            item = self.trajListBox.currentItem() #new selection
            name = item.text() #trajectory name
            self.updateTrajectory(name)

    #updates the angle/duration list boxes for the selected trajectory
    def updateTrajectory(self,name):
        #clear old values
        self.angleListBox.clear()
        self.durationListBox.clear()

        #update with new values
        angleList = trajDict[name]['angle']
        durList = trajDict[name]['duration']

        self.angleListBox.addItems(angleList)
        self.durationListBox.addItems(durList)

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
                control[key].setCurrentIndex(0)
                control[key].setStyleSheet("background-color: white")
                control[key].setStyleSheet("color: black")
            else:
                #which item in sequence menu is it?
                whichItem = seqList.index(sequence)
                if whichItem == -1:
                    return
                control[key].setCurrentIndex(whichItem+1)
                control[key].setStyleSheet("background-color: rgba(150, 245, 150, 150)")

    #Finds sequence assignments, and displays what they are at the bottom of the GUI
    def displaySeqAssignments(self,objectNum):
        seqDisplay = []

        for key,_ in seqAssign[objectNum].items():
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
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in circleSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Rectangle':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.orientationLabel,9,0)
            self.designPanelLayout.addWidget(self.orientation,9,1)
            self.designPanelLayout.addWidget(self.orientationSeq,9,2)
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in rectangleSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Grating':
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
            for key,value in gratingSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Noise':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in noiseSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Cloud':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in cloudSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Windmill':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.orientationLabel,9,0)
            self.designPanelLayout.addWidget(self.orientation,9,1)
            self.designPanelLayout.addWidget(self.orientationSeq,9,2)
            self.designPanelLayout.addWidget(self.driftFreqLabel,8,8)
            self.designPanelLayout.addWidget(self.driftFreq,8,9)
            self.designPanelLayout.addWidget(self.driftFreqSeq,8,10)
            for key,value in windmillSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            #recursive call to set the motion/drift settings according to object type
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Annulus':
            for key,value in annulusSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Image':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in imageSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Batch':
            index = self.stimBank.currentRow()

            self.batchStimMenu.clear()
            stimList = self.getStimulusBank()
            self.batchStimMenu.addItems(stimList)

            self.stimBank.setCurrentRow(index)

            for key,value in batchSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

        elif selection == 'Snake':
            #some object dependent repositioning
            self.designPanelLayout.addWidget(self.angleLabel,9,8)
            self.designPanelLayout.addWidget(self.angle,9,9)
            self.designPanelLayout.addWidget(self.angleSeq,9,10)
            for key,value in snakeSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
            self.flipControls('motionType',self.motionType.currentText())

        elif selection == 'Static' and controlName == 'motionType':
            #self.designPanelLayout.addWidget(self.blank5,7,8,4,1)
            for key,value in staticMotionSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

        elif selection == 'Drift' and controlName == 'motionType':
            #self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
            #Grating and windmill have different options for motion than other stimuli
            if self.objectType.currentText() == 'Grating':
                for key,value in driftGratingMotionSettings.items():
                    if value == 0:
                        control[key].hide()
                    else:
                        control[key].show()
            elif self.objectType.currentText() == 'Windmill':
                for key,value in windmillMotionSettings.items():
                    if value == 0:
                        control[key].hide()
                    else:
                        control[key].show()
            else:
                for key,value in driftMotionSettings.items():
                    if value == 0:
                        control[key].hide()
                    else:
                        control[key].show()

        elif selection == 'Static' and controlName == 'modulationType':
            for key,value in staticModSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

        elif selection != 'Static' and controlName == 'modulationType':
            for key,value in dynamicModSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Cartesian' and controlName == 'coordinateType':
            for key,value in cartesianSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Cartesian' and controlName == 'maskCoordinateType':
            for key,value in cartesianMaskSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Polar' and controlName == 'coordinateType':
            for key,value in polarSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()
        elif selection == 'Polar' and controlName == 'maskCoordinateType':
            for key,value in polarMaskSettings.items():
                if value == 0:
                    control[key].hide()
                else:
                    control[key].show()

    #Converts 0-255 range to -1 to 1 range
    def getBackground(self):
        bgndStr = self.background.text()
        if len(bgndStr) > 0:
            if bgndStr.isnumeric():
                val = float(self.background.text())
                bgnd = (2 * val/255.) - 1 #normalize from -1 to 1
            else:
                control['background'].setText('0')
                val = 0.0
                bgnd = (2 * val/255.) - 1 #normalize from -1 to 1
            return bgnd
        else:
            return

    #flips the sync spot on or off
    def drawSyncSpot(self,syncSpot,contrastVal):
        if self.syncSpot.isChecked():
            syncSpot.setContrast(contrastVal)
            if isOpen == 1:
                syncSpot.draw()

    #Open a stimulus window
    def initializeSession(self):
        global win,isOpen,ifi,main

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
            gamma = float(self.gammaTable.currentText())
        )


        #Frame rate
        ifi = 1/win.getActualFrameRate(10,100)
        isOpen = 1 #window is open

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

    #Fills out the stimulus parameters into a structure
    def runStim(self):
        global runTime,stimID

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
                }
                }

                timer[i] = 0

            #start at 0 sweeps
            numSweeps = 0

            #check for sequence assignments to get the total number of sweeps
            for i in range(numObjects):
                for key,_ in seqAssign[i].items():
                    sequence = seqAssign[i][key]['sequence']
                    if sequence != 'None':
                        #extract sequence entry
                        entry = seqDict[sequence]

                        #size of entry
                        size = len(entry)
                        if size > numSweeps:
                            numSweeps = size

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

            #What is the total duration of the stimulus, including delays?
            durList = []
            durList = [runTime[i]['delayFrames'] + runTime[i]['frames'] for i in range(numObjects)]
            totalDuration = max(durList)

            #if no sequences are assigned or they are all empty, set sweeps to 1
            if numSweeps == 0:
                numSweeps = 1

            #STIMULUS LOOP #Loop through repeats
            for repeat in range(repeats): #use repeat setting for first object

                #loop through sweeps from sequence assignments
                for sweep in range(numSweeps):

                    #check for abort click
                    if abortStatus:
                        return

                    #reset frame counts
                    frameCount = 0

                    #check for sequence assignments and fill runtime dictionary
                    for i in range(numObjects):
                        for key,_ in seqAssign[i].items():
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
                        runTime[i]['startX'] = ppm * (xOffset + stim[i]['xPos']) + ppm * stim[i]['startRad'] * np.cos(stim[i]['angle'] * np.pi/180.)
                        runTime[i]['startY'] = ppm * (yOffset + stim[i]['yPos']) + ppm * stim[i]['startRad'] * np.sin(stim[i]['angle'] * np.pi/180.)

                        #Motion parameters
                        if stim[i]['motionType'] == 'Drift':
                            #if stim[i]['objectType'] == 'Grating':
                            runTime[i]['driftIncrement'] =  stim[i]['driftFreq'] * ifi
                                    # elif stim[i]['objectType'] == 'Windmill':
                                    #   runTime[i]['driftIncrement'] = stim[i]['driftFreq'] * ifi

                        #Modulation parameters
                        if (stim[i]['modulationType'] == 'Square') or (stim[i]['modulationType'] == 'Sine'):
                            runTime[i]['halfCycle'] = int(round((0.5/stim[i]['modulationFreq'])/ifi)) # number of frames per half cycle
                            runTime[i]['cycleCount'] = 1

                        elif stim[i]['modulationType'] == 'Chirp':
                            chirpWave = self.buildChirp(i,ifi)
                            #make sure total duration matches frame number if the stimulus is a chirp
                            stim[i]['contrast'] = 100
                            totalDuration = chirpWave.shape[0]
                            runTime[i]['frames'] = totalDuration

                        #noise frames per cycle
                        if stim[i]['objectType'] == 'Noise':
                            runTime[i]['halfCycle'] = int(round((0.5/stim[i]['noiseFreq'])/ifi)) # number of frames per half cycle
                            runTime[i]['cycleCount'] = 1

                        runTime[i]['phase'] = stim[i]['spatialPhase'] / 360.

                        #intensities
                        firstIntensity,secondIntensity = self.getIntensity(i)
                        runTime[i]['firstIntensity'] = firstIntensity
                        runTime[i]['secondIntensity'] = secondIntensity

                        #Define stimulus
                        runTime[i]['stimulus'] = self.defineStimulus(runTime,ppm,xOffset,yOffset,i,ifi,sweep)

                        #reset stimulus frame counts
                        runTime[i]['stimFrame'] = 0
                        #reset cycle counts
                        runTime[i]['cycleCount'] = 1

                        #calculate trajectory frames
                        if stim[i]['trajectory'] != 'None':
                            self.calculateTrajectory(stim[i]['trajectory'],i,sweep,ifi,ppm,xOffset,yOffset)
                            runTime[i]['frames'] = len(trajectoryStim[i]['yPos'])


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


                    #Wait for trigger
                    if self.trigger.currentText() == 'Wait For Trigger':
                        with ni.Task() as task:
                            task.di_channels.add_di_chan('PCI6036/port0/line0')
                            trigger = False
                            while trigger == False:
                                #read digital input P0.0 from the ephys board
                                trigger = task.read()
                    elif self.trigger.currentText() == 'Send Trigger':
                        with ni.Task() as task:
                            #send digital pulse through P0.0 from the ephys board
                            task.do_channels.add_do_chan('PCI6036/port0/line0')
                            task.write(False)
                            task.write(True)
                            task.write(False)


                    #overall timer that is started before delay
                    totalTimer = 0
                    totalTimer = core.Clock()

                    #loop through total stimulus duration
                    for frame in range(totalDuration):

                        #flip sync spot to dark as default
                        self.drawSyncSpot(syncSpot,-1)

                        #Loop through each object
                        for i in range(numObjects):

                            #extract stimulus intensity so you only do it once per object
                            firstIntensity = runTime[i]['firstIntensity']
                            secondIntensity = runTime[i]['secondIntensity']

                            #delay
                            if frame < runTime[i]['delayFrames']:
                                continue

                            #duration
                            if frame >= runTime[i]['delayFrames'] + runTime[i]['frames']:
                                continue


                            #sync spot bright
                            self.drawSyncSpot(syncSpot,1)

                            #start timer only on first frame of the stimulus
                            # if runTime[i]['stimFrame'] == 0:
                            #     timer[i] = 0
                            #     timer[i] = core.Clock()

                            #check for abort click
                            if abortStatus:
                                #Flip the window to background again
                                self.drawSyncSpot(syncSpot,-1)
                                win.flip()
                                return

                            #Update stimulus parameters and Draw each stimulus object to the buffer window

                            #MOTION CLOUD STIMULI
                            if stim[i]['objectType'] == 'Cloud':
                                #get the motion cloud frame

                                stimulus = visual.ImageStim(
                                    win=win,
                                    units = 'pix',
                                    image = motionCloud[:,:,runTime[i]['stimFrame']],
                                    size = (1024,768),
                                    ori = stim[i]['orientation'],
                                    pos = ((xOffset + stim[i]['xPos']) * ppm,(yOffset + stim[i]['yPos']) * ppm)
                                    )

                                runTime[i]['stimulus'] = stimulus

                            #NOISE STIMULI
                            elif stim[i]['objectType'] == 'Noise':
                                #Flip the intensities between light/dark at each cycle
                                if runTime[i]['stimFrame'] == runTime[i]['halfCycle'] * runTime[i]['cycleCount']:
                                    #if number of cycles divided by 2 is an even number we need to update the parameters
                                    if (runTime[i]['cycleCount'] % 2) == 0:
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

                                            x = runTime[i]['startX'] + ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.cos(stim[i]['angle'] * np.pi/180)
                                            y = runTime[i]['startY'] + ppm * stim[i]['speed'] * (runTime[i]['stimFrame'] * ifi) * np.sin(stim[i]['angle'] * np.pi/180)
                                            runTime[i]['stimulus'].setPos((x,y))

                                        else:
                                            runTime[i]['stimulus'].pos = self.getTrajectoryPosition(i,ifi,ppm)

                                #Update intensity for modulated stimuli

                                if stim[i]['modulationType'] == 'Square':
                                    #Flip the intensities between light/dark at each cycle
                                    if runTime[i]['stimFrame'] == runTime[i]['halfCycle'] * runTime[i]['cycleCount']:

                                        if (runTime[i]['cycleCount'] % 2) == 0:
                                            runTime[i]['stimulus'].contrast = firstIntensity
                                        else:
                                            runTime[i]['stimulus'].contrast = secondIntensity

                                        runTime[i]['cycleCount'] = runTime[i]['cycleCount'] + 1 #counts which modulation cycle it's on

                                elif stim[i]['modulationType'] == 'Sine':
                                    #out of bounds intensities
                                    if firstIntensity - bgnd > 1:
                                        firstIntensity = bgnd + 1
                                    elif firstIntensity - bgnd < -1:
                                        firstIntensity = bgnd - 1

                                    runTime[i]['stimulus'].contrast = (stim[i]['contrast']/100.0) * np.sin(2 * np.pi * stim[i]['modulationFreq'] * (runTime[i]['stimFrame'] * ifi))

                                elif stim[i]['modulationType'] == 'Chirp':
                                    runTime[i]['stimulus'].contrast = chirpWave[runTime[i]['stimFrame']]
                            #
                            # testTimer = 0
                            # testTimer = core.Clock()


                            if stim[i]['objectType'] == 'Snake':
                                for segment in range(currentSegment+1):
                                    snakeStim[i]['segments'][segment].draw()
                            else:
                                runTime[i]['stimulus'].draw() #draws every frame

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
                        win.flip()


                        frameCount = frameCount + 1

                    #flip sync spot back to dark before next sweeep
                    self.drawSyncSpot(syncSpot,-1)
                    win.flip()

                    #Wait for trial time to expire before starting next sweep
                    while totalTimer.getTime() < trialTime:
                        #flip the sync spot at the end of the sweep
                        self.drawSyncSpot(syncSpot,-1)
                        win.flip()

                #Flip the window to background again
                self.drawSyncSpot(syncSpot,-1)
                win.flip()

    #Defines the stimulus textures
    def defineStimulus(self,runTime,ppm,xOffset,yOffset,i,ifi,sweep):
        global motionCloud, mask, ortho,stimArray,snakeStim#, innerRing, outerRing

        firstIntensity = runTime[i]['firstIntensity']
        secondIntensity = runTime[i]['secondIntensity']
        bgnd = self.getBackground()

        # w = win.size[0]/2
        # h = win.size[1]/2

        #polar coordinates or cartesian coordinates?
        if stim[i]['coordinateType'] == 'Cartesian':
            xPos = stim[i]['xPos']
            yPos = stim[i]['yPos']
        elif stim[i]['coordinateType'] == 'Polar':
            xPos = stim[i]['polarRadius'] * np.cos(stim[i]['polarAngle'] * pi/180)
            yPos = stim[i]['polarRadius'] * np.sin(stim[i]['polarAngle'] * pi/180)

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


            #resolve masks
            #mask = self.getMask(w,h,i,ppm)

            stimulus = visual.GratingStim(
            win = win,
            units = 'pix',
            size=[w*2,h*2],
            tex = type,
            texRes = 256,
            #mask = mask,
            #maskParams = {'fringeWidth':0.2},
            sf = stim[i]['spatialFreq'] / (ppm * 1000),
            ori = stim[i]['orientation'],
            phase = stim[i]['spatialPhase']/360.0,#phase is fractional from 0 to 1
            color = [1,1,1],
            contrast = stim[i]['contrast']/100.0,
            pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
            )

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
        elif stim[i]['objectType'] == 'Noise':
            #set the seed for random number generator
            np.random.seed(stim[i]['noiseSeed'])

            stimulus = visual.NoiseStim(
            win = win,
            size = [512,512],
            units = 'pix',
            noiseType = stim[i]['noiseType'],
            contrast = stim[i]['contrast']/100.0,
            noiseElementSize = stim[i]['noiseSize'] * ppm,
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

            #proportional to 1024 x 768
            fx, fy, ft = mc.get_grids(256, 256, frames+1)
            # define an envelope

            #testTime = 0
            #testTime = core.Clock()

            #this is the most time intensive step - 50%
            envelope = mc.envelope_gabor(fx, fy, ft,
            V_X=stim[i]['cloudSpeedX'], V_Y=stim[i]['cloudSpeedY'], B_V=stim[i]['cloudSpeedBand'],
            sf_0=stim[i]['cloudSF'], B_sf=stim[i]['cloudSFBand'],
            theta=stim[i]['cloudOrient'] * np.pi/180, B_theta=stim[i]['cloudOrientBand'] * np.pi/180, alpha=0.)

            #print(testTime.getTime())

            #testTime = 0
            #testTime = core.Clock()

            #this is the second most time intensive step - 43%
            motionCloud = mc.random_cloud(envelope)

            #print(testTime.getTime())

            #testTime = 0
            #testTime = core.Clock()

            #this is the least time intensive step - 6%
            motionCloud = self.rectif_stimGen(motionCloud,contrast=stim[i]['contrast']/100.0,method='Michelson',verbose=False)


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
                    continue
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
                    size = (1024,768),
                    ori = stim[i]['orientation'],
                    pos = ((xOffset + xPos) * ppm,(yOffset + yPos) * ppm)
                    )
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

    #calculates the frames for each segent of the trajectory
    def calculateTrajectory(self,name,i,sweep,ifi,ppm,xOffset,yOffset):
        global runTime,trajectoryStim

        #makes a working copy of trajectory dictionary in case it contains a sequence string
        #in this case the working copy needs to be edited to contain the values within the sequence.
        liveTrajDict = copy.deepcopy(trajDict)

        numSegments = len(trajDict[name]['angle'])

        for segment in range(numSegments):
            if trajDict[name]['angle'][segment].isnumeric():
                #numeric entry
                continue
            elif str(trajDict[name]['angle'][segment]) in seqList:
                #is the entry a sequence?
                #If so, replace the trajectory segment with the sequence entry for the current sweep
                theSequence = str(trajDict[name]['angle'][segment])
                liveTrajDict[name]['angle'][segment] = seqDict[theSequence][sweep]

        #make trajectory dictionary for the object
        trajectoryStim[i] = {
        'xPos':np.zeros(0),
        'yPos':np.zeros(0)
        }

        for segment in range(numSegments):

            #get angles and total frames per segment
            runTime[i]['trajectory']['angle'].append(liveTrajDict[name]['angle'][segment])

            #calculate which frame each segment will start on
            if segment == 0:
                numFrames = int(round(float(liveTrajDict[name]['duration'][segment])/ifi)) #frames in the current segment
                #numFrames = numFrames + (0.5 * stim[i]['width'] / stim[i]['speed']) #add extra frames to account for the center of the starting snake getting to the turn position
                segmentFrames = np.zeros(numFrames+1)

                runTime[i]['trajectory']['startFrame'].append(0)

                #start position for first segment
                startX = ppm * (xOffset + stim[i]['xPos']) + ppm * stim[i]['startRad'] * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)
                startY = ppm * (yOffset + stim[i]['yPos']) + ppm * stim[i]['startRad'] * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180.)

                if stim[i]['objectType'] == 'Snake':
                    #X position segment - half as much distance traveled because its a growing rectangle that is also changing its length simultaneously
                    segmentFrames[:] = [startX + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                    #Y position segment
                    segmentFrames[:] = [startY + 0.5 * ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
                else:
                    #X position segment
                    segmentFrames[:] = [startX + ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                    #Y position segment
                    segmentFrames[:] = [startY + ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(0,numFrames+1,1)]
                    trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)
            else:
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

                    size = len(trajectoryStim[i]['xPos'])
                    prevStartPos = trajectoryStim[i]['xPos'][size-1]
                    segmentFrames[:] = [prevStartPos + ppm * stim[i]['speed'] * ifi * t * np.cos(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                    trajectoryStim[i]['xPos'] = np.append(trajectoryStim[i]['xPos'],segmentFrames)

                    size = len(trajectoryStim[i]['yPos'])
                    prevStartPos = trajectoryStim[i]['yPos'][size-1]
                    segmentFrames[:] = [prevStartPos + ppm * stim[i]['speed'] * ifi * t * np.sin(float(liveTrajDict[name]['angle'][segment]) * np.pi/180) for t in np.arange(1,numFrames+1,1)]
                    trajectoryStim[i]['yPos'] = np.append(trajectoryStim[i]['yPos'],segmentFrames)

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
    def buildChirp(self,i,ifi):
        contrast = stim[i]['contrast'] / 100.0 #contrast chirp maximum
        TF_low = 0.5 #low end of the temporal frequency chirp
        TF_high = 8.0 #high end of the temporal frequency chirp
        TF_mid = 3.0 #temporal frequency for the contrast chirp
        duration = int(round(15.0/ifi)) #15 second chirp stimulus

        chirpWave = np.zeros(0) #makes chirp wave of set duration

        #initial flashes
        segment = np.full(int(round(1./ifi)),-contrast)
        chirpWave = np.append(chirpWave,segment)

        segment = np.full(int(round(1./ifi)),contrast)
        chirpWave = np.append(chirpWave,segment)

        segment = np.full(int(round(1./ifi)),-contrast)
        chirpWave = np.append(chirpWave,segment)

        segment = np.zeros(int(round(1./ifi)))
        chirpWave = np.append(chirpWave,segment)

        frames = int(round(4.0/ifi)) + 1 # length in frames of the temporal frequency and contrast chirps. Set for 4 seconds currently.

        #temporal frequency chirp
        segment = np.zeros(frames)
        segment[:] = [contrast * np.sin(4.0 * 2 * np.pi * 0.5 * ((TF_high * x/frames) + TF_low) * x/frames) for x in np.arange(0,frames,1)]
        chirpWave = np.append(chirpWave,segment)

        #1 second pause in between temporal frequency and contrast chirps
        segment = np.zeros(int(round(1.0/ifi)))
        chirpWave = np.append(chirpWave,segment)

        #contrast chirp
        segment = np.zeros(frames)
        segment[:] = [contrast * x/frames * np.sin(4.0 * 2 * np.pi * TF_mid * x/frames) for x in np.arange(0,frames,1)]
        chirpWave = np.append(chirpWave,segment)

        #final flash back to dark
        segment = np.zeros(int(round(1./ifi)))
        chirpWave = np.append(chirpWave,segment)

        segment = np.full(int(round(1./ifi)),-contrast)
        chirpWave = np.append(chirpWave,segment)

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
        'apertureStatus':'Off',
        'apertureDiam':0,
        'maskCoordinateType':'Cartesian',
        'maskObjectType':'Circle',
        'maskDiameter':0,
        'maskXPos':0,
        'maskYPos':0,
        'maskPolarRadius':0,
        'maskPolarAngle':0,
        'apertureStatus':'Off',
        'apertureDiam':0,
        'noiseType':'Binary',
        'noiseSize':0,
        'noiseSeed':0,
        'noiseFreq':0,
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
        'noiseFreqSeq':{
            'control':self.noiseFreqSeq,
            'parent':'noiseFreq',
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
        'coordinateType':self.coordinateType,
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
        'noiseFreqLabel':self.noiseFreqLabel,
        'noiseFreq':self.noiseFreq,
        'noiseFreqSeq':self.noiseFreqSeq,
        'batchStimMenu':self.batchStimMenu,
        'batchStimList':self.batchStimList,
        'batchStimAdd':self.batchStimAdd,
        'batchStimRemove':self.batchStimRemove
        }

    #Set contextual menu dictionaries
    def setContextualMenus(self):
        global circleSettings,rectangleSettings,gratingSettings,noiseSettings,cloudSettings,windmillSettings,annulusSettings,imageSettings,batchSettings,snakeSettings
        global staticMotionSettings,dynamicModSettings,staticModSettings,windmillMotionSettings,driftGratingMotionSettings,driftMotionSettings
        global cartesianSettings,cartesianMaskSettings,polarSettings,polarMaskSettings

        circleSettings = {
        'gratingType':0,
        'diameter':1,
        'diameterLabel':1,
        'diameterSeq':1,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        annulusSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':1,
        'innerDiameterLabel':1,
        'innerDiameterSeq':1,
        'outerDiameter':1,
        'outerDiameterLabel':1,
        'outerDiameterSeq':1,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        rectangleSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':1,
        'lengthLabel':1,
        'lengthSeq':1,
        'width':1,
        'widthLabel':1,
        'widthSeq':1,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        snakeSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':1,
        'lengthLabel':1,
        'lengthSeq':1,
        'width':1,
        'widthLabel':1,
        'widthSeq':1,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        gratingSettings = {
        'gratingType':1,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':1,
        'spatialPhaseLabel':1,
        'spatialPhaseSeq':1,
        'spatialFreq':1,
        'spatialFreqLabel':1,
        'spatialFreqSeq':1,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        noiseSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':1,
        'noiseSeedLabel':1,
        'noiseSeed':1,
        'noiseSeedSeq':1,
        'noiseSizeLabel':1,
        'noiseSize':1,
        'noiseSizeSeq':1,
        'noiseFreqLabel':1,
        'noiseFreq':1,
        'noiseFreqSeq':1,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        cloudSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':1,
        'cloudSF':1,
        'cloudSFBand':1,
        'cloudSpeedLabel':1,
        'cloudSpeedX':1,
        'cloudSpeedY':1,
        'cloudSpeedBandLabel':1,
        'cloudSpeedBand':1,
        'cloudOrientLabel':1,
        'cloudOrient':1,
        'cloudOrientBand':1,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        windmillSettings = {
        'gratingType':1,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'angularCyclesLabel':1,
        'angularCycles':1,
        'angularCyclesSeq':1,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        imageSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':1,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':1,
        'orientationLabel':1,
        'orientationSeq':1,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':0,
        'batchStimList':0,
        'batchStimAdd':0,
        'batchStimRemove':0
        }

        batchSettings = {
        'gratingType':0,
        'diameter':0,
        'diameterLabel':0,
        'diameterSeq':0,
        'imagePath':0,
        'innerDiameter':0,
        'innerDiameterLabel':0,
        'innerDiameterSeq':0,
        'outerDiameter':0,
        'outerDiameterLabel':0,
        'outerDiameterSeq':0,
        'length':0,
        'lengthLabel':0,
        'lengthSeq':0,
        'width':0,
        'widthLabel':0,
        'widthSeq':0,
        'orientation':0,
        'orientationLabel':0,
        'orientationSeq':0,
        'angularCyclesLabel':0,
        'angularCycles':0,
        'angularCyclesSeq':0,
        'spatialPhase':0,
        'spatialPhaseLabel':0,
        'spatialPhaseSeq':0,
        'spatialFreq':0,
        'spatialFreqLabel':0,
        'spatialFreqSeq':0,
        'noiseType':0,
        'noiseSeedLabel':0,
        'noiseSeed':0,
        'noiseSeedSeq':0,
        'noiseSizeLabel':0,
        'noiseSize':0,
        'noiseSizeSeq':0,
        'noiseFreqLabel':0,
        'noiseFreq':0,
        'noiseFreqSeq':0,
        'cloudSFLabel':0,
        'cloudSF':0,
        'cloudSFBand':0,
        'cloudSpeedLabel':0,
        'cloudSpeedX':0,
        'cloudSpeedY':0,
        'cloudSpeedBandLabel':0,
        'cloudSpeedBand':0,
        'cloudOrientLabel':0,
        'cloudOrient':0,
        'cloudOrientBand':0,
        'batchStimMenu':1,
        'batchStimList':1,
        'batchStimAdd':1,
        'batchStimRemove':1
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
        'driftFreqLabel':0,
        'driftFreq':0,
        'driftFreqSeq':0,
        'turnDirection':0
        }

        driftGratingMotionSettings = {
        'angle':1,
        'angleLabel':1,
        'angleSeq':1,
        'startRad':0,
        'startRadLabel':0,
        'startRadSeq':0,
        'speed':0,
        'speedLabel':0,
        'speedSeq':0,
        'driftFreq':1,
        'driftFreqLabel':1,
        'driftFreqSeq':1,
        'turnDirection':0
        }

        windmillMotionSettings = {
        'angle':0,
        'angleLabel':0,
        'angleSeq':0,
        'startRad':0,
        'startRadLabel':0,
        'startRadSeq':0,
        'speed':0,
        'speedLabel':0,
        'speedSeq':0,
        'driftFreqLabel':1,
        'driftFreq':1,
        'driftFreqSeq':1,
        'turnDirection':1
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
        'driftFreqLabel':0,
        'driftFreq':0,
        'driftFreqSeq':0,
        'turnDirection':0
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

        cartesianSettings ={
        'xPos':1,
        'xPosLabel':1,
        'xPosSeq':1,
        'yPos':1,
        'yPosLabel':1,
        'yPosSeq':1,
        'polarRadius':0,
        'polarRadiusLabel':0,
        'polarRadiusSeq':0,
        'polarAngle':0,
        'polarAngleLabel':0,
        'polarAngleSeq':0
        }

        polarSettings ={
        'xPos':0,
        'xPosLabel':0,
        'xPosSeq':0,
        'yPos':0,
        'yPosLabel':0,
        'yPosSeq':0,
        'polarRadius':1,
        'polarRadiusLabel':1,
        'polarRadiusSeq':1,
        'polarAngle':1,
        'polarAngleLabel':1,
        'polarAngleSeq':1
        }

        cartesianMaskSettings ={
        'maskXPos':1,
        'maskXPosLabel':1,
        'maskXPosSeq':1,
        'maskYPos':1,
        'maskYPosLabel':1,
        'maskYPosSeq':1,
        'maskPolarRadius':0,
        'maskPolarRadiusLabel':0,
        'maskPolarRadiusSeq':0,
        'maskPolarAngle':0,
        'maskPolarAngleLabel':0,
        'maskPolarAngleSeq':0
        }

        polarMaskSettings ={
        'maskXPos':0,
        'maskXPosLabel':0,
        'maskXPosSeq':0,
        'maskYPos':0,
        'maskYPosLabel':0,
        'maskYPosSeq':0,
        'maskPolarRadius':1,
        'maskPolarRadiusLabel':1,
        'maskPolarRadiusSeq':1,
        'maskPolarAngle':1,
        'maskPolarAngleLabel':1,
        'maskPolarAngleSeq':1
        }

    #Design Panel
    def buildDesignPanel(self):
        left = 165 * scale_w
        top = 300 * scale_h
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
        self.blank1.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.blank1,4,0,1,11)
        self.designPanelLayout.setRowStretch(14,1)
        self.blank1.setAlignment(QtCore.Qt.AlignVCenter)

        #Object Type
        self.objectTypeLabel = QLabel('Objects',self)
        self.objectTypeLabel.setFont(bold)
        self.objectTypeLabel.setFixedHeight(20 * scale_h)

        self.objectType = QComboBox(self)
        self.objectType.addItems(['Circle','Rectangle','Grating','Noise','Cloud','Windmill','Annulus','Snake','Image','Batch'])
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

        self.designPanelLayout.addWidget(self.imagePath,7,0,1,2)

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
        self.gratingType.activated.connect(lambda: self.menuProc('gratingType',self.gratingType.currentText()))

        #Noise Type
        self.noiseType = QComboBox(self)
        self.noiseType.addItems(['Binary','Normal','Uniform'])
        self.designPanelLayout.addWidget(self.noiseType,7,0,1,2)
        self.noiseType.activated.connect(lambda: self.menuProc('noiseType',self.noiseType.currentText()))

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

        self.designPanelLayout.addWidget(self.noiseSeedLabel,8,0)
        self.designPanelLayout.addWidget(self.noiseSeed,8,1)
        self.designPanelLayout.addWidget(self.noiseSeedSeq,8,2)

        self.designPanelLayout.addWidget(self.noiseSizeLabel,9,0)
        self.designPanelLayout.addWidget(self.noiseSize,9,1)
        self.designPanelLayout.addWidget(self.noiseSizeSeq,9,2)

        #Noise frequency
        self.noiseFreqLabel = QLabel('Freq.',self)
        self.noiseFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.noiseFreq = QLineEdit(self)
        self.noiseFreq.setFixedWidth(40 * scale_w)
        self.noiseFreq.setAlignment(QtCore.Qt.AlignRight)
        self.noiseFreq.editingFinished.connect(lambda: self.variableProc('noiseFreq',self.noiseFreq.text()))

        self.noiseFreqSeq = QComboBox(self)
        self.noiseFreqSeq.addItem('None')
        self.noiseFreqSeq.setFixedWidth(20 * scale_w)
        self.noiseFreqSeq.activated.connect(lambda: self.menuProc('noiseFreqSeq',self.noiseFreqSeq.currentText()))

        self.designPanelLayout.addWidget(self.noiseFreqLabel,10,0)
        self.designPanelLayout.addWidget(self.noiseFreq,10,1)
        self.designPanelLayout.addWidget(self.noiseFreqSeq,10,2)

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

        #Contrast
        self.contrastTypeLabel = QLabel('Contrast',self)
        self.contrastTypeLabel.setFont(bold)
        self.contrastType = QComboBox(self)
        self.contrastType.addItems(['Weber','Michelson','Intensity'])
        self.contrastType.activated.connect(lambda: self.menuProc('contrastType',self.contrastType.currentText()))
        self.contrastType.setFixedHeight(20 * scale_h)

        self.contrastLabel = QLabel('% Contrast',self)
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
        self.modulationType.addItems(['Static','Square','Sine','Chirp'])

        self.modulationFreqLabel = QLabel('Frequency',self)
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
        self.motionType.addItems(['Static','Drift'])
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

        #blank after angle row so hiding modFrequency doesn't change grid
        self.blank5.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.blank5,10,8,1,1)
        #self.blank5.setStyleSheet("QLabel {background-color: green;}")
        self.blank5.setAlignment(QtCore.Qt.AlignVCenter)

        #insert blank after the spatial frequency row
        self.blank4.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.blank4,11,0,1,10)
        #self.blank4.setStyleSheet("QLabel {background-color: black;}")
        self.blank4.setAlignment(QtCore.Qt.AlignVCenter)

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

        self.designPanelLayout.addWidget(self.timingLabel,12,0)
        self.designPanelLayout.addWidget(self.delayLabel,13,0)
        self.designPanelLayout.addWidget(self.delay,13,1)
        self.designPanelLayout.addWidget(self.delaySeq,13,2)

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

        self.designPanelLayout.addWidget(self.durationLabel,14,0)
        self.designPanelLayout.addWidget(self.duration,14,1)
        self.designPanelLayout.addWidget(self.durationSeq,14,2)

        #Trial Time
        self.trialTimeLabel = QLabel('Trial Time',self)
        self.trialTime = QLineEdit(self)
        self.trialTime.setFixedWidth(40 * scale_w)
        self.trialTime.setAlignment(QtCore.Qt.AlignRight)
        self.trialTimeLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.trialTime.editingFinished.connect(lambda: self.variableProc('trialTime',self.trialTime.text()))

        self.designPanelLayout.addWidget(self.trialTimeLabel,15,0)
        self.designPanelLayout.addWidget(self.trialTime,15,1)

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
        self.trajectory.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.trajectoryLabel,12,8,1,2)
        self.designPanelLayout.addWidget(self.trajectory,13,8,1,2)

        #Triggers
        self.triggerLabel = QLabel('Triggers')
        self.triggerLabel.setFont(bold)
        self.trigger = QComboBox()
        self.trigger.addItems(['None','Wait For Trigger','Send Trigger'])
        self.trigger.setFixedHeight(20 * scale_h)
        self.designPanelLayout.addWidget(self.triggerLabel,14,8,1,2)
        self.designPanelLayout.addWidget(self.trigger,15,8,1,2)

    #Masks Panel
    def buildMasksPanel(self):
        left = 165 * scale_w
        top = 300 * scale_h
        width = 475 * scale_w
        height = 190 * scale_h

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
        top = 300 * scale_h
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
        self.trajListBox.itemClicked.connect(lambda: self.listProc('trajListBox',self.trajListBox.currentRow()))
        seqPanelLayout.addWidget(self.trajListBox,7,2,4,2)

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
        left = 10 * scale_w
        top = 135 * scale_h
        width = 475 * scale_w
        height = 125 * scale_h

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
        self.syncSpot.stateChanged.connect(lambda: self.checkProc('syncSpot',self.syncSpot.isChecked()))
        self.globalsLayout.addWidget(self.syncSpotLabel,7,0,1,2)
        self.globalsLayout.addWidget(self.syncSpot,7,2)

        #Gamma Table
        self.gammaTableLabel = QLabel('Gamma')
        self.gammaTable = QComboBox()
        self.gammaTable.addItems(['1.0','2.2'])
        self.gammaTable.setFixedWidth(45)
        self.gammaTable.activated.connect(lambda: self.menuProc('gammaTable',self.gammaTable.currentText()))

        self.globalsLayout.addWidget(self.gammaTableLabel,8,0,1,2)
        self.gammaTableLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.gammaTable,8,2)

    #Stimulus Bank
    def buildStimusBank(self):
        left = 10 * scale_w
        top = 318 * scale_h
        width = 145 * scale_w
        height = 350 * scale_h

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
        self.stimBankLabel.move(left+30 * scale_w,top-55 * scale_h)

        #Stimulus subfolder
        self.subFolder = QComboBox(self)
        self.subFolder.move(left,top-30 * scale_h)
        self.subFolder.resize(width,25 * scale_h)
        self.subFolder.addItems(['Ben','Geoff'])
        self.subFolder.setFont(large)
        self.subFolder.activated.connect(lambda: self.menuProc('subFolder',self.subFolder.currentText()))

        #Stimulus Bank
        self.stimBank = QListWidget(self)
        self.stimBank.setFont(large)
        self.stimBank.move(left,top)
        self.stimBank.resize(width,height)
        self.stimBank.itemClicked.connect(lambda: self.listProc('stimBank',self.stimBank.currentRow()))

        #save stimulus
        self.saveStim = QPushButton('Save',self)
        self.saveStim.move(left+5 * scale_w,top + 360 * scale_h)
        self.saveStim.resize(60 * scale_w,20 * scale_h)
        self.saveStim.clicked.connect(lambda: self.buttonProc("saveStim"))

        #delete stimulus
        self.deleteStim = QPushButton('Delete',self)
        self.deleteStim.move(left+80 * scale_w,top + 360 * scale_h)
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
        #stimulus = self.stimBank.currentItem()
        #stimName = stimulus.text() #current selection is default name

        name, ok = QInputDialog.getText(self, 'Save Stimulus','Stimulus Name:')#,QLineEdit.Normal,stimName)

        if name == '':
            return

        fileName = name + '.stim'

        subfolder = self.subFolder.currentText()

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
        self.getStimulusBank()

        #set the list box to select the newly saved stimulus
        newItem = self.stimBank.findItems(name,QtCore.Qt.MatchExactly)
        self.stimBank.setCurrentItem(newItem[0])

    #saves MotionCloud array as an HDF5
    def saveCloud(self,cloud):

        #put the file in the stimulus subfolder
        fileName = 'cloudFile.hdf5'
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder + '/' + fileName

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
                objectList.append((stimLoaded[i]['objectType'])) #fill out the object list so addStimDict will work correctly
                self.addStimDict()

            #assign the loaded stim/seqAssign dict into the actual stim/seqAssign dict
            #this allows for the loaded stim to have an incomplete stim dictionary, if new controls have been added

            for object,_ in stimLoaded.items():
                for key,value in stimLoaded[object].items():
                    stim[object][key] = value

            for object,_ in seqAssignLoaded.items():
                for key,value in seqAssignLoaded[object].items():
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
                self.trajAngle.setText('')
                self.trajDuration.setText('')

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

        return stimList

    #finds all the images in the selected stimulus subfolder with .bmp extensions
    def getImageBank(self):
        subfolder = self.subFolder.currentText()
        path = stimPath + subfolder

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
        self.ppm.setText('0.717')
        self.background.setText('0')
        self.xOffset.setText('0')
        self.yOffset.setText('0')
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
        self.noiseFreq.setText('0')
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
