#StimGen python

#Must use python 2.7, not 3
#pygame, pyglet, and psychopy

#import widgets
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLineEdit,QGroupBox,QComboBox
from PyQt5.QtWidgets import QLabel,QListWidget,QSpacerItem,QVBoxLayout,QGridLayout,QCheckBox
from PyQt5 import QtCore,QtGui

import math

#import PsychoPy
from psychopy import visual, clock, core

class App(QMainWindow):

    def __init__(self):
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

        #Build Control Panels
        self.buildStimusList()
        self.buildDesignPanel()
        self.buildMasksPanel()
        self.buildSequencePanel()
        self.buildPathPanel()
        self.buildGlobalsPanel()

        self.setDefaults()

        self.show()

        #globals
        global isOpen #stimulus window is closed
        isOpen = 0

    #Handles all variable entries
    def variableProc(self,controlName):

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
        else:
            return

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
        else:
            #default
            print('other')

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
            size=[1440, 900],
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

        #gets the stimulus parameters
        stim = self.getStimDict()

        #Timing
        frames = int(round(stim['duration']/ifi)) #round to nearest integer

        #Motion parameters
        startX = stim['xOffset'] + stim['xPos'] + stim['startRad'] * math.cos(stim['angle'] * math.pi/180)
        startY = stim['yOffset'] + stim['yPos'] + stim['startRad'] * math.sin(stim['angle'] * math.pi/180)

        #Modulation parameters
        if stim['modulationType'] != 'Static':
            halfCycle = int(round((0.5/stim['modulationFreq'])/ifi)) #in number of frames
            cycleCount = 1

        #Intensity
        firstIntensity,secondIntensity = self.getIntensity(stim)
        #print(firstIntensity)
        #print(secondIntensity)

        #Define stimulus
        if stim['objectType'] == 'Circle':
            stimulus = visual.Circle(
            win = win,
            units = 'pix',
            radius = stim['diameter']/2,
            fillColor = [firstIntensity,firstIntensity,firstIntensity],
            lineColor = [firstIntensity,firstIntensity,firstIntensity],
            edges = 100,
            pos = (stim['xOffset'] + stim['xPos'],stim['yOffset'] + stim['yPos'])
            )

        #elif stim['objectType'] == 'Rectangle':

        #elif stim['objectType'] == 'Grating':

        else:
            print('other')

        #Run the stimulus
        try:
            #Loop through repeats
            for sweep in range(stim['repeats']):

                #check for abort click
                if abortStatus:
                    return

                #overall timer that is started before delay
                totalTimer = core.Clock()

                #delay
                core.wait(stim['delay'])

                #start timer
                timer = core.Clock()

# STIMULUS LOOP
                for frame in range(frames):
                #while timer.getTime() < stim['duration']:
                    #print(modTimer.getTime())
                    #check for abort click
                    if abortStatus:
                        win.flip()
                        return

                    #Update position for moving stimuli
                    if stim['motionType'] == 'Drift':
                        x = startX + stim['speed'] * timer.getTime() * math.cos(stim['angle'] * math.pi/180)
                        y = startY + stim['speed'] * timer.getTime() * math.sin(stim['angle'] * math.pi/180)
                        stimulus.pos = (x,y)

                    #Update intensity for modulated stimuli
                    if stim['modulationType'] == 'Square':
                        #Flip the intensities between light/dark
                        if frame == halfCycle * cycleCount:
                            if (cycleCount % 2) == 0:
                                stimulus.fillColor = [firstIntensity,firstIntensity,firstIntensity]
                                stimulus.lineColor = [firstIntensity,firstIntensity,firstIntensity]
                            else:
                                stimulus.fillColor = [secondIntensity,secondIntensity,secondIntensity]
                                stimulus.lineColor = [secondIntensity,secondIntensity,secondIntensity]
                            cycleCount = cycleCount + 1

                    #Draw stimulus to buffer window
                    stimulus.draw() #redraws every frame
                    #Flip the window
                    win.flip()
#################

                #Flip the window to background again
                win.flip()

                #Wait for trial time to expire before starting next sweep
                while totalTimer.getTime() < stim['trialTime']:
                    win.flip()
        except:
            return

    #Returns positive and negative contrast values around the background
    def getIntensity(self,stim):
        bgnd = stim['background']

        if stim['contrastType'] == 'Michelson':
            firstIntensity = bgnd + bgnd * (stim['contrast']/100)
            secondIntensity = bgnd - bgnd * (stim['contrast']/100)

            #all situations of out of bounds intensities
            if firstIntensity > 255: #out of range, set to maximum
                firstIntensity = 255
                secondIntensity = bgnd - (255 - bgnd) #same amount below background as light is above background
            elif secondIntensity < 0:
                secondIntensity = 0 #out of range, set to minimum
                firstIntensity = 2 * bgnd #set to 100% contrast

                #reverse case, where firstIntensity is dark
            elif secondIntensity > 255:
                secondIntensity = 255
                firstIntensity = bgnd - (255 - bgnd)
            elif firstIntensity < 0:
                secondIntensity = 0
                secondIntensity = 2 * bgnd

        elif stim['contrastType'] == 'Weber':
            firstIntensity = bgnd * (stim['contrast']/100) + bgnd
            secondIntensity = bgnd

            #out of bounds intensities
            if firstIntensity > 255:
                firstIntensity = 255
            elif firstIntensity < 0:
                firstIntensity = 0

        elif stim['contrastType'] == 'Intensity':
            firstIntensity = stim['contrast']
            secondIntensity = bgnd

            #out of bounds intensities
            if firstIntensity > 255:
                firstIntensity = 255
            elif firstIntensity < 0:
                firstIntensity = 0

        #Convert from 0-255 to -1 to 1 range
        firstIntensity = (2 * firstIntensity/255) - 1
        secondIntensity = (2 * secondIntensity/255) - 1

        return (firstIntensity,secondIntensity)

    #Aborts stimulus
    def abortStim(self):
        global abortStatus
        abortStatus = 1

    #Returns dictionary containing current stimulus parameters
    def getStimDict(self):
        stim = {
        'background':float(self.background.text()),
        'objectType':self.objectType.currentText(),
        'coordinateType':self.coordinateType.currentText(),
        'xOffset':float(self.xOffset.text()),
        'yOffset':float(self.yOffset.text()),
        'xPos':float(self.xPos.text()),
        'yPos':float(self.yPos.text()),
        'diameter':float(self.diameter.text()),
        'length':float(self.length.text()),
        'width':float(self.width.text()),
        'spatialFreq':float(self.spatialFreq.text()),
        'contrastType':self.contrastType.currentText(),
        'contrast':float(self.contrast.text()),
        'modulationType':self.modulationType.currentText(),
        'modulationFreq':float(self.modulationFreq.text()),
        'motionType':self.motionType.currentText(),
        'speed':float(self.speed.text()),
        'startRad':float(self.startRad.text()),
        'angle':float(self.angle.text()),
        'delay':float(self.delay.text()),
        'duration':float(self.duration.text()),
        'repeats':int(self.repeats.text()),
        'trialTime':float(self.trialTime.text())

        }

        return stim

    #Design Panel
    def buildDesignPanel(self):
        left = 165
        top = 300
        width = 475
        height = 400

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)


        #Group box and designPanelLayout layout
        self.designPanel = QGroupBox(self)
        designPanelLayout = QGridLayout()

        self.designPanel.setLayout(designPanelLayout)
        self.designPanel.move(left,top)
        self.designPanel.resize(width,height)

        #Blanks
        self.blank1 = QLabel('',self)
        self.blank2 = QLabel('',self)
        self.blank2.setFixedWidth(15)
        self.blank3 = QLabel('',self)
        self.blank3.setFixedWidth(15)
        self.blank4 = QLabel('',self)

        #Add/Remove Objects
        self.addObject = QPushButton('Add\nObject',self)
        designPanelLayout.addWidget(self.addObject,0,0,2,2)
        self.removeObject = QPushButton('Remove\nObject',self)
        designPanelLayout.addWidget(self.removeObject,2,0,2,2)
        self.addObject.clicked.connect(lambda: self.buttonProc("addObject"))
        self.removeObject.clicked.connect(lambda: self.buttonProc("removeObject"))

        #Object List Box
        self.objectListBox = QListWidget(self)
        designPanelLayout.addWidget(self.objectListBox,0,3,4,3)

        #insert blank after the object list box row
        designPanelLayout.addWidget(self.blank1,4,0)
       # self.blank1.setStyleSheet("QLabel {background-color: red;}")

        #Object Type
        self.objectTypeLabel = QLabel('Type',self)
        self.objectTypeLabel.setFont(bold)
        self.objectType = QComboBox(self)
        self.objectType.addItem('Circle')
        self.objectType.addItem('Rectangle')
        self.objectType.addItem('Grating')
        designPanelLayout.addWidget(self.objectTypeLabel,6,0)
        designPanelLayout.addWidget(self.objectType,7,0,1,2)

        #Add blank slot to the right of the object type menu
        designPanelLayout.addWidget(self.blank2,6,3)
        #self.blank2.setStyleSheet("QLabel {background-color: blue;}")

        #Coordinates
        self.coordinateLabel = QLabel('Coordinates')
        self.coordinateLabel.setFont(bold)
        self.coordinateType = QComboBox()
        self.coordinateType.addItem('Cartesian')
        self.coordinateType.addItem('Polar')

        designPanelLayout.addWidget(self.coordinateLabel,0,9,1,2)
        designPanelLayout.addWidget(self.coordinateType,1,9,1,2)

        #X offset
        self.xPosLabel = QLabel('X Offset')
        self.xPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.xPos = QLineEdit()
        self.xPos.setAlignment(QtCore.Qt.AlignRight)
        self.xPos.setFixedWidth(40)
        self.xPosSeq = QComboBox()
        self.xPosSeq.addItem('None')
        self.xPosSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.xPosLabel,2,9)
        designPanelLayout.addWidget(self.xPos,2,10)
        designPanelLayout.addWidget(self.xPosSeq,2,11)

        #Y offset
        self.yPosLabel = QLabel('Y Offset')
        self.yPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.yPos = QLineEdit()
        self.yPos.setAlignment(QtCore.Qt.AlignRight)
        self.yPos.setFixedWidth(40)
        self.yPosSeq = QComboBox()
        self.yPosSeq.addItem('None')
        self.yPosSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.yPosLabel,3,9)
        designPanelLayout.addWidget(self.yPos,3,10)
        designPanelLayout.addWidget(self.yPosSeq,3,11)

        #Diameter
        self.diamLabel = QLabel('Diameter',self)
        self.diamLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.diameter = QLineEdit(self)
        self.diameter.setFixedWidth(40)
        self.diameter.setAlignment(QtCore.Qt.AlignRight)
        self.diameterSeq = QComboBox(self)
        self.diameterSeq.addItem('None')
        self.diameterSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.diamLabel,8,0)
        designPanelLayout.addWidget(self.diameter,8,1)
        designPanelLayout.addWidget(self.diameterSeq,8,2)

        #Length
        self.lengthLabel = QLabel('Length',self)
        self.lengthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.length = QLineEdit(self)
        self.length.setFixedWidth(40)
        self.length.setAlignment(QtCore.Qt.AlignRight)
        self.lengthSeq = QComboBox(self)
        self.lengthSeq.addItem('None')
        self.lengthSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.lengthLabel,9,0)
        designPanelLayout.addWidget(self.length,9,1)
        designPanelLayout.addWidget(self.lengthSeq,9,2)

        #Width
        self.widthLabel = QLabel('Width',self)
        self.widthLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.width = QLineEdit(self)
        self.width.setFixedWidth(40)
        self.width.setAlignment(QtCore.Qt.AlignRight)
        self.widthSeq = QComboBox(self)
        self.widthSeq.addItem('None')
        self.widthSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.widthLabel,10,0)
        designPanelLayout.addWidget(self.width,10,1)
        designPanelLayout.addWidget(self.widthSeq,10,2)

        #Spatial Frequency
        self.spatialFreqLabel = QLabel('Spat. Freq.',self)
        self.spatialFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.spatialFreq = QLineEdit(self)
        self.spatialFreq.setFixedWidth(40)
        self.spatialFreq.setAlignment(QtCore.Qt.AlignRight)
        self.spatialFreqSeq = QComboBox(self)
        self.spatialFreqSeq.addItem('None')
        self.spatialFreqSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.spatialFreqLabel,11,0)
        designPanelLayout.addWidget(self.spatialFreq,11,1)
        designPanelLayout.addWidget(self.spatialFreqSeq,11,2)

        #Contrast
        self.contrastTypeLabel = QLabel('Contrast',self)
        self.contrastTypeLabel.setFont(bold)
        self.contrastType = QComboBox(self)
        self.contrastType.addItem('Weber')
        self.contrastType.addItem('Michelson')
        self.contrastType.addItem('Intensity')

        self.contrastLabel = QLabel('% Contrast',self)
        self.contrast = QLineEdit(self)
        self.contrast.setAlignment(QtCore.Qt.AlignRight)
        self.contrast.setFixedWidth(40)
        self.contrastSeq = QComboBox(self)
        self.contrastSeq.addItem('None')
        self.contrastSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.contrastTypeLabel,6,4,1,2)
        designPanelLayout.addWidget(self.contrastType,7,4,1,2)
        designPanelLayout.addWidget(self.contrastLabel,8,4)
        designPanelLayout.addWidget(self.contrast,8,5)
        designPanelLayout.addWidget(self.contrastSeq,8,6)

        #Add blank slot to the right of the contrast edit box
        designPanelLayout.addWidget(self.blank3,6,8)
        #self.blank3.setStyleSheet("QLabel {background-color: green;}")

        #Modulation
        self.modulationTypeLabel = QLabel('Modulation',self)
        self.modulationTypeLabel.setFont(bold)
        self.modulationType = QComboBox(self)

        self.modulationType.addItem('Static')
        self.modulationType.addItem('Square')
        self.modulationType.addItem('Sine')

        self.modulationFreqLabel = QLabel('Frequency',self)
        self.modulationFreq =  QLineEdit(self)
        self.modulationFreq.setFixedWidth(40)
        self.modulationFreq.setAlignment(QtCore.Qt.AlignRight)
        self.modulationFreqLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.modulationFreqSeq = QComboBox(self)
        self.modulationFreqSeq.addItem('None')
        self.modulationFreqSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.modulationTypeLabel,9,4,1,2)
        designPanelLayout.addWidget(self.modulationType,10,4,1,2)
        designPanelLayout.addWidget(self.modulationFreqLabel,11,4)
        designPanelLayout.addWidget(self.modulationFreq,11,5)
        designPanelLayout.addWidget(self.modulationFreqSeq,11,6)

        #Motion Type
        self.motionTypeLabel = QLabel('Motion',self)
        self.motionTypeLabel.setFont(bold)
        self.motionType = QComboBox(self)
        self.motionType.addItem('Static')
        self.motionType.addItem('Drift')

        designPanelLayout.addWidget(self.motionTypeLabel,6,9)
        designPanelLayout.addWidget(self.motionType,7,9,1,2)

        #Speed
        self.speedLabel = QLabel('Speed',self)
        self.speedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.speed = QLineEdit(self)
        self.speed.setFixedWidth(40)
        self.speed.setAlignment(QtCore.Qt.AlignRight)
        self.speedSeq = QComboBox(self)
        self.speedSeq.addItem('None')
        self.speedSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.speedLabel,8,9)
        designPanelLayout.addWidget(self.speed,8,10)
        designPanelLayout.addWidget(self.speedSeq,8,11)

        #Start Radius
        self.startRadLabel = QLabel('Start Rad.',self)
        self.startRadLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.startRad = QLineEdit(self)
        self.startRad.setFixedWidth(40)
        self.startRad.setAlignment(QtCore.Qt.AlignRight)
        self.startRadSeq = QComboBox(self)
        self.startRadSeq.addItem('None')
        self.startRadSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.startRadLabel,9,9)
        designPanelLayout.addWidget(self.startRad,9,10)
        designPanelLayout.addWidget(self.startRadSeq,9,11)

        #Angle
        self.angleLabel = QLabel('Angle',self)
        self.angleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.angle = QLineEdit(self)
        self.angle.setFixedWidth(40)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.angleSeq = QComboBox(self)
        self.angleSeq.addItem('None')
        self.angleSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.angleLabel,10,9)
        designPanelLayout.addWidget(self.angle,10,10)
        designPanelLayout.addWidget(self.angleSeq,10,11)

        #insert blank after the spatial frequency row
        designPanelLayout.addWidget(self.blank4,12,0)
        #self.blank4.setStyleSheet("QLabel {background-color: black;}")

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

        designPanelLayout.addWidget(self.timingLabel,13,0)
        designPanelLayout.addWidget(self.delayLabel,14,0)
        designPanelLayout.addWidget(self.delay,14,1)
        designPanelLayout.addWidget(self.delaySeq,14,2)

        #Duration
        self.durationLabel = QLabel('Duration',self)
        self.duration = QLineEdit(self)
        self.duration.setFixedWidth(40)
        self.duration.setAlignment(QtCore.Qt.AlignRight)
        self.durationLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.durationSeq = QComboBox(self)
        self.durationSeq.addItem('None')
        self.durationSeq.setFixedWidth(20)

        designPanelLayout.addWidget(self.durationLabel,15,0)
        designPanelLayout.addWidget(self.duration,15,1)
        designPanelLayout.addWidget(self.durationSeq,15,2)

        #Trial Time
        self.trialTimeLabel = QLabel('Trial Time',self)
        self.trialTime = QLineEdit(self)
        self.trialTime.setFixedWidth(40)
        self.trialTime.setAlignment(QtCore.Qt.AlignRight)
        self.trialTimeLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        designPanelLayout.addWidget(self.trialTimeLabel,16,0)
        designPanelLayout.addWidget(self.trialTime,16,1)

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

        designPanelLayout.addWidget(self.repititionLabel,13,4,1,2)
        designPanelLayout.addWidget(self.repeatsLabel,14,4)
        designPanelLayout.addWidget(self.repeats,14,5)
        designPanelLayout.addWidget(self.loopCheckLabel,15,4)
        designPanelLayout.addWidget(self.loopCheck,15,5)

        #Trajectories
        self.trajectoryLabel = QLabel('Trajectories')
        self.trajectoryLabel.setFont(bold)
        self.trajectory = QComboBox()
        self.trajectory.addItem('None')

        designPanelLayout.addWidget(self.trajectoryLabel,13,9,1,2)
        designPanelLayout.addWidget(self.trajectory,14,9,1,2)

        #Triggers
        self.triggerLabel = QLabel('Triggers')
        self.triggerLabel.setFont(bold)
        self.trigger = QComboBox()
        self.trigger.addItem('None')
        self.trigger.addItem('Wait For Trigger')
        self.trigger.addItem('Send Trigger')

        designPanelLayout.addWidget(self.triggerLabel,15,9,1,2)
        designPanelLayout.addWidget(self.trigger,16,9,1,2)

    #Masks Panel
    def buildMasksPanel(self):
        left = 165
        top = 300
        width = 475
        height = 164

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

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
        self.maskType.addItem('None')
        self.maskType.addItem('Mask')
        self.maskType.addItem('Window')

        maskPanelLayout.addWidget(self.maskTypeLabel,0,0)
        maskPanelLayout.addWidget(self.maskType,1,0)

        #Mask Object Types
        self.maskObjectTypeLabel = QLabel('Object')
        self.maskObjectTypeLabel.setFont(bold)

        self.maskObjectType = QComboBox()
        self.maskObjectType.addItem('Circle')
        self.maskObjectType.addItem('Rectangle')
        self.maskObjectType.setFixedWidth(106)

        maskPanelLayout.addWidget(self.maskObjectTypeLabel,2,0)
        maskPanelLayout.addWidget(self.maskObjectType,3,0)

        #Mask Object List Box
        self.maskObjectListBox = QListWidget(self)
        self.maskObjectListBox.setFixedWidth(127)
        maskPanelLayout.addWidget(self.maskObjectListBox,0,2,4,1)

        #Mask Coordinates
        self.maskCoordinateLabel = QLabel('Coordinates')
        self.maskCoordinateLabel.setFont(bold)

        self.maskCoordinateType = QComboBox()
        self.maskCoordinateType.setFixedWidth(106)
        self.maskCoordinateType.addItem('Cartesian')
        self.maskCoordinateType.addItem('Polar')

        maskPanelLayout.addWidget(self.maskCoordinateLabel,0,4,1,2)
        maskPanelLayout.addWidget(self.maskCoordinateType,1,4,1,2)

        #Mask X offset
        self.maskXPosLabel = QLabel('X Offset')
        self.maskXPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskXPos = QLineEdit()
        self.maskXPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskXPos.setFixedWidth(40)

        self.maskXPosSeq = QComboBox()
        self.maskXPosSeq.addItem('None')
        self.maskXPosSeq.setFixedWidth(20)

        maskPanelLayout.addWidget(self.maskXPosLabel,2,4)
        maskPanelLayout.addWidget(self.maskXPos,2,5)
        maskPanelLayout.addWidget(self.maskXPosSeq,2,6)

        #Mask Y offset
        self.maskYPosLabel = QLabel('Y Offset')
        self.maskYPosLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.maskYPos = QLineEdit()
        self.maskYPos.setAlignment(QtCore.Qt.AlignRight)
        self.maskYPos.setFixedWidth(40)

        self.maskYPosSeq = QComboBox()
        self.maskYPosSeq.addItem('None')
        self.maskYPosSeq.setFixedWidth(20)

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

        #Sequence entry
        self.seqEntry = QLineEdit()
        seqPanelLayout.addWidget(self.seqEntry,4,0,1,4)

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
        self.background.textEdited.connect(lambda: self.variableProc('background'))


        #X Offset
        self.xOffsetLabel = QLabel('X Offset')
        self.xOffset = QLineEdit()
        self.xOffset.setFixedWidth(45)
        self.xOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.xOffsetLabel,4,0,1,2)
        self.xOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.globalsLayout.addWidget(self.xOffset,4,2)

        #Y Offset
        self.yOffsetLabel = QLabel('Y Offset')
        self.yOffset = QLineEdit()
        self.yOffset.setFixedWidth(45)
        self.yOffset.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffsetLabel,5,0,1,2)
        self.yOffsetLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.yOffset,5,2)

        #Sync Frames
        self.syncFramesLabel = QLabel('Sync Frames')
        self.syncFrames = QLineEdit()
        self.syncFrames.setFixedWidth(45)
        self.syncFrames.setAlignment(QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFramesLabel,6,0,1,2)
        self.syncFramesLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.syncFrames,6,2)

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
        self.gammaTable.addItem('1.0')
        self.gammaTable.addItem('2.2')
        self.gammaTable.setFixedWidth(45)

        self.globalsLayout.addWidget(self.gammaTableLabel,8,0,1,2)
        self.gammaTableLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.globalsLayout.addWidget(self.gammaTable,8,2)

    #Stimulus Bank
    def buildStimusList(self):
        left = 10
        top = 318
        width = 145
        height = 350

        bold = QtGui.QFont("Helvetica", 14,weight=QtGui.QFont.Normal)

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
        self.stimBank.move(left,top)
        self.stimBank.resize(width,height)

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

    #styles
    StimGen.setStyle('Fusion')
    myFont = QtGui.QFont('Helvetica', 12,weight=QtGui.QFont.Light)
    StimGen.setFont(myFont)
   # StimGen.setStyleSheet("QPushButton {border-radius: 20px;}")
    #StimGen.setStyleSheet("QPushButton {background-color: blue;}")
    ex = App()
    StimGen.exec_()
