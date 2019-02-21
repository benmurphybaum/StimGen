#StimGen python3

from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QVBoxLayout
StimGen = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QApplication('Bottom'))
window.setLayout(layout)
window.show()
app.exec_()