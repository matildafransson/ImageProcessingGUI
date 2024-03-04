
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QSlider, QLabel
from PyQt5.QtCore import pyqtSignal, Qt

class DoubleSlider(QWidget):
    """
    Widget to display a double slider used for the contrast in the image visualiser
    """
    sigDoubleSliderValueChanged = pyqtSignal(object)

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(6, 6, 6, 6)
        self.mainLayout.setSpacing(1)
        orientation = Qt.Horizontal

        self.minSlider = Slider(self, orientation)
        self.minSlider.setRange(0, 100)
        self.minSlider.setValue(0)
        self.maxSlider = Slider(self, orientation)
        self.maxSlider.setRange(0, 100)
        self.maxSlider.setValue(100)
        self.mainLayout.addWidget(self.maxSlider)
        self.mainLayout.addWidget(self.minSlider)
        self.minSlider.sigValueChanged.connect(self._sliderChanged)
        self.maxSlider.sigValueChanged.connect(self._sliderChanged)

    def __getDict(self):
        """
        Create a dictionary to catch slider user event
        """
        ddict = {}
        ddict['event'] = "doubleSliderValueChanged"
        m   = self.minSlider.value()
        M   = self.maxSlider.value()
        if m > M:
            ddict['max'] = m
            ddict['min'] = M
        else:
            ddict['min'] = m
            ddict['max'] = M
        return ddict

    def _sliderChanged(self, value):
        """
        Method to emit a signal when the slider is changed
        :param value:
        """
        ddict = self.__getDict()
        self.sigDoubleSliderValueChanged.emit(ddict)

    def setMinMax(self, m, M):
        """
        Set the double slider min and max values
        :param m: minimum
        :param M: maximum
        """
        self.minSlider.setValue(m)
        self.maxSlider.setValue(M)

    def getMinMax(self):
        """
        Return the true value of the slider
        :return: min, max
        """
        m = self.minSlider.value()
        M = self.maxSlider.value()
        if m > M:
            return M, m
        else:
            return m, M


class Slider(QWidget):
    """
    Personalize slider for contrast management in the image visualiser
    """
    sigValueChanged = pyqtSignal(float)

    def __init__(self, parent = None, orientation=Qt.Horizontal):
        QWidget.__init__(self, parent)
        if orientation == Qt.Horizontal:
            alignment = Qt.AlignHCenter | Qt.AlignTop
            layout = QHBoxLayout(self)
        else:
            alignment = Qt.AlignVCenter | Qt.AlignLeft
            layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.slider = QSlider(self)
        self.slider.setOrientation(orientation)
        self.label  = QLabel("0", self)
        self.label.setAlignment(alignment)
        self.label.setFixedWidth(self.label.fontMetrics().width('100000.99'))

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.slider.valueChanged.connect(self.setNum)

    def setNum(self, value):
        """
        Method to emit a signal when the slider value is changed and set the label display
        :param value:  value to emmit
        """
        value = value / 100.
        self.label.setText('%.2f' % value)
        self.sigValueChanged.emit(value)

    def setRange(self, minValue, maxValue):
        """
        Method to set the value of the slider min and max to the true values
        :param minValue: min value of the slider
        :param maxValue: max value of the slider
        """
        self.slider.setRange(int(minValue * 100), int(maxValue * 100))

    def setValue(self, value):
        """
        Method to set the value of the slider
        :param value: true value to give to the slider
        :return:
        """
        self.slider.setValue(int(value * 100))

    def value(self):
        """
        Convert slider value to the true one
        :return: true slider value
        """
        return self.slider.value()/100.

