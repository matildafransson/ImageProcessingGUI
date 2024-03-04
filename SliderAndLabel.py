
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QSlider, QWidget, QLabel, QHBoxLayout

class SliderAndLabel(QWidget):
    def __init__(self,parent=None, Orientation=1):
        QWidget.__init__(self, parent)

        self.time_array = []

        self.slider=QSlider(1)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)

        self.Label=QLabel("0")
        self.Label.setFixedSize(45,45)

        self.layout=QHBoxLayout()
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.Label)
        self._changeLabel()


        self.slider.valueChanged.connect(self._changeLabel)
        self.setLayout(self.layout)

    def _changeLabel(self):
        if len(self.time_array) != 0 :
            string_to_display = str(round(self.time_array[self.slider.value()])) + ' s'
            self.Label.setText(string_to_display)

    def _setOrientation(self):
        self.slider.setOrientation(1)

    def _setRange(self,mini,maxi):
        self.slider.setMinimum(mini)
        self.slider.setValue(mini)
        self.slider.setMaximum(maxi)
        self._changeLabel();

    def value(self):
        return self.slider.value()

class SliderAndLabelSpecificScale(QWidget):
    def __init__(self,parent=None, Orientation=1) :
        QWidget.__init__(self, parent)
        self.slider=QSlider(1)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.Coef = 1.0
        self.Label=QLabel("0")
        self.Label.setFixedSize(45,10)
        self.layout=QHBoxLayout()
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.Label)
        self._changeLabel()
        self.slider.valueChanged.connect(self._changeLabel)
        self.setLayout(self.layout)

    def _changeLabel(self):
        self.Label.setText(str(self.slider.value()/self.Coef))

    def _setStepPrecision(self,Pres):
        self.Coef = 1.0/Pres

    def _defaultValue(self,Value):
        self.slider.setValue(Value*self.Coef)
        self._changeLabel()

    def _setOrientation(self):
        self.slider.setOrientation(1)

    def _setRange(self,mini,maxi):
        self.slider.setMinimum(mini*self.Coef)
        self.slider.setMaximum(maxi*self.Coef)
        self._changeLabel()

    def value(self):
        return self.slider.value() / self.Coef