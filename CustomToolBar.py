from DoubleSlider import DoubleSlider

from PyQt5.QtWidgets import QToolBar, QAction, QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

class CustomToolBar(QToolBar):
    """
    Widget to have a tool bar in top of visualiser for different actions
    Include : Reset zoom button, double slider for contrast, button to jump to the first frame
    """
    def __init__(self, parent):

        QToolBar.__init__(self, parent)
        self.setIconSize(QSize(25, 25))

        self.zoomAutoAction = QAction(QIcon('icon/autozoom.png'), '&Zoom', self)
        self.zoomAutoAction.setStatusTip('Fit window')
        self.zoomAutoAction.setCheckable(False)
        self.zoomAutoAction.setChecked(False)
        self.zoomActive = False

        self.doubleSlider = DoubleSlider(self)
        self.setMinAndMaxToolBar(0, 0)
        self.doubleSlider.setMaximumWidth(800)

        self.addAction(self.zoomAutoAction)
        self.addSeparator()
        self.addWidget(self.doubleSlider)


    def setMinAndMaxToolBar(self, min, max):
        """
        Change min and max double slider values for contrast
        :param min: Min pixel value to display on the double slider for contrast
        :param max: Max pixel value to display on the double slider for contrast
        :return:
        """
        self.doubleSlider.minSlider.setRange(min, max)
        self.doubleSlider.minSlider.setValue(min)
        self.doubleSlider.maxSlider.setRange(min, max)
        self.doubleSlider.maxSlider.setValue(max)
        self.doubleSlider.setMinMax(min, max)





