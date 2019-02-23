#StimGen python3

#import widgets
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLineEdit,QGroupBox,QComboBox,QLabel,QVBoxLayout,QGridLayout
from PyQt5 import QtCore,QtGui 

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "StimGen 5.0"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 780
        self.buildDesignPanel()

    def buildDesignPanel(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        left = 165
        top = 300

        bold = QtGui.QFont()
        bold.setBold(True)


        self.objectTypeLabel = QLabel('Type',self)
        self.objectTypeLabel.setFont(bold)
        self.objectType = QComboBox(self)
        self.objectType.addItem('Circle')
        self.objectType.addItem('Rectangle')
        self.objectType.addItem('Grating')

        self.diamLabel = QLabel('Diameter',self)
        self.lengthLabel = QLabel('Length',self)
        self.widthLabel = QLabel('Width',self)
        self.spatialFreqLabel = QLabel('Spatial Freq.',self)
       
        self.diameter = QLineEdit(self)
        self.length = QLineEdit(self)
        self.width = QLineEdit(self)
        self.spatialFreq = QLineEdit(self)

       # objectType.move(left+35,top)
        #objectType.resize(125,25)

       # diamLabel.move(left,top+30)
       # diameter.move(left+110,top+30)
       # diameter.resize(40,20)
      #  lengthLabel.move(left,top+55)
      #  length.move(left+110,top+55)
       # length.resize(40,20)
      #  widthLabel.move(left,top+80)
      #  width.move(left+110,top+80)
      #  width.resize(40,20)
      #  spatialFreqLabel.move(left,top+105)
      #  spatialFreq.move(left+110,top+105)
      #  spatialFreq.resize(40,20)

        self.blank1 = QLabel('',self)
        self.blank2 = QLabel('',self)
        #blank3 = QLabel('',self)

        self.diamLabel.setAlignment(QtCore.Qt.AlignRight)
        self.lengthLabel.setAlignment(QtCore.Qt.AlignRight)
        self.widthLabel.setAlignment(QtCore.Qt.AlignRight)
        self.spatialFreqLabel.setAlignment(QtCore.Qt.AlignRight)

        self.objectGroup = QGroupBox(self)
        grid = QGridLayout()

        self.objectGroup.setLayout(grid)
        self.objectGroup.move(left,top)
        self.objectGroup.resize(475,185)

        grid.addWidget(self.objectTypeLabel,0,0)
        grid.addWidget(self.objectType,1,0,1,2)
        grid.addWidget(self.diameter,2,1)
        grid.addWidget(self.diamLabel,2,0)
        grid.addWidget(self.length,3,1)
        grid.addWidget(self.lengthLabel,3,0)
        grid.addWidget(self.width,4,1)
        grid.addWidget(self.widthLabel,4,0)
        grid.addWidget(self.spatialFreq,5,1)
        grid.addWidget(self.spatialFreqLabel,5,0)


        self.contrastTypeLabel = QLabel('Contrast',self)
        self.contrastTypeLabel.setFont(bold)

        self.contrastType = QComboBox(self)
        self. contrastType.addItem('Weber')
        self.contrastType.addItem('Michelson')
        self.contrastType.addItem('Intensity')

        self.contrast = QLineEdit(self)
        
        self.modulationTypeLabel = QLabel('Modulation',self)
        self.modulationTypeLabel.setFont(bold)
        self.modulationType = QComboBox(self)
        self.modulationType.addItem('Static')
        self.modulationType.addItem('Square')
        self.modulationType.addItem('Sine')

        self.modulationFreqLabel = QLabel('Frequency',self)
        self.modulationFreq =  QLineEdit(self)

        self.modulationFreqLabel.setAlignment(QtCore.Qt.AlignRight)

        grid.addWidget(self.blank1,0,3)
        grid.addWidget(self.contrastTypeLabel,0,4)
        grid.addWidget(self.contrastType,1,4,1,2)
        grid.addWidget(self.contrast,1,6)
        grid.addWidget(self.modulationTypeLabel,2,4)
        grid.addWidget(self.modulationType,3,4,1,2)
        grid.addWidget(self.modulationFreqLabel,4,4)
        grid.addWidget(self.modulationFreq,4,5)

        self.motionTypeLabel = QLabel('Motion',self)
        self.motionTypeLabel.setFont(bold)
        self.motionType = QComboBox(self)
        self.motionType.addItem('Static')
        self.motionType.addItem('Drift')

        self.speedLabel = QLabel('Speed',self)
        self.speed = QLineEdit(self)
        self.startRadLabel = QLabel('Start Rad.',self)
        self.startRad = QLineEdit(self)
        self.angleLabel = QLabel('Angle',self)
        self.angle = QLineEdit(self)

        self.speedLabel.setAlignment(QtCore.Qt.AlignRight)
        self.startRadLabel.setAlignment(QtCore.Qt.AlignRight)
        self.angleLabel.setAlignment(QtCore.Qt.AlignRight)

        grid.addWidget(self.blank2,0,7)
        grid.addWidget(self.motionTypeLabel,0,8)
        grid.addWidget(self.motionType,1,8,1,2)
        grid.addWidget(self.speedLabel,2,8)
        grid.addWidget(self.speed,2,9)
        grid.addWidget(self.startRadLabel,3,8)
        grid.addWidget(self.startRad,3,9)
        grid.addWidget(self.angleLabel,4,8)
        grid.addWidget(self.angle,4,9)
        
        self.setDefaults()

        self.show()

    def setDefaults(self):
        controls = [
            'diameter','length','width'
        ]
        




if __name__ == '__main__':
    #create instance of application
    StimGen = QApplication([])
    ex = App()
    StimGen.exec_()
    #styles
    StimGen.setStyle('Fusion')

#Create a window
#window = QWidget()

#Create a layout with 2 buttons
#circleLayout = QVBoxLayout()



#circleLayout.addWidget(diamLabel)
#circleLayout.addWidget(lengthLabel)
##circleLayout.addWidget(spatialFreqLabel)

#apply the layout to the window
#window.setLayout(circleLayout)
#window.resize(500,800)

#show the window and execute application
#window.show()
#StimGen.exec_()