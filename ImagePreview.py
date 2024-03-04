import sys
import numpy as np

from PyQt5.QtWidgets import QWidget, QGraphicsScene, QHBoxLayout,QVBoxLayout, QApplication, QGraphicsPixmapItem, QLabel, QPushButton, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QPoint
from PyQt5.QtGui import QImage, QPixmap, qRgba, qRgb,QBrush, QColor, QFont, QPainter

from CustomGraphicView import CustomGraphicView
from SliderAndLabel import SliderAndLabel
from CustomToolBar import CustomToolBar


class ImageVisualizer(QWidget):
    """
    Widget to display image with a slider to change images
    """
    MovedOnVisualizer = pyqtSignal(dict)

    def __init__(self, ImageType, parent=None):
        QWidget.__init__(self, parent)

        self.imageType = ImageType
        self.scene = QGraphicsScene()
        self.view = CustomGraphicView(self.scene, self)

        self.hLayoutBotom = QHBoxLayout()

        self.sliceSlider = SliderAndLabel(self)
        self.pixelPosLabel = QLabel('')
        self.playButton = QPushButton()
        self.playButton.setCheckable(True)

        self.hLayoutBotom.addWidget(self.playButton)
        self.hLayoutBotom.addWidget(self.sliceSlider)
        self.hLayoutBotom.addWidget(self.pixelPosLabel)


        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(self.hLayoutBotom)
        self.createColorTable()
        self.setLayout(layout)

        self.sliceSlider.slider.valueChanged.connect(self._changeSlice)
        self.view.CustomGraphicsViewEvent.connect(self.mouseMoved)

        self.delay = 0
        self.ratiofps = 1
        ###
        self.frame_rate = 1
        self.sizeScaleBar= 1
        self.textstr1 = ''
        self.textstr2 = ''
        self.textstr3 = ''
        self.flagTime = False
        self.flagtxt1 = False
        self.flagtxt2 = False
        self.flagtxt3 = False

        self.textItem1 = QGraphicsTextItem('')
        self.textItem2 = QGraphicsTextItem('')
        self.textItem3 = QGraphicsTextItem('')
        self.scale_rect = QGraphicsRectItem(0,0,1,1)

        self.Item1Pos = QPoint(0,0)
        self.Item2Pos =  QPoint(0,0)
        self.Item3Pos =  QPoint(0,0)
        self.scaleBarPos =  QPoint(0,0)
        self.starting_time = '0'
        self.current_time = self.starting_time

        self.mean_value = 0


    def mouseMoved(self,ddict):
        """
        Catch the mouse movement to display the pixel coordiante and value
        :param ddict: dictionary of event generated
        """

        x_pos = int(ddict['y'])
        y_pos = int(ddict['x'])
        try:
            size_sliceX = self.slice.shape[0]
            size_sliceY = self.slice.shape[1]

            if (x_pos >= 0) and (y_pos >= 0) and (x_pos < size_sliceX) and (y_pos < size_sliceY):

                value_pos = self.slice[int(x_pos), int(y_pos)]
                self.pixelPosLabel.setText('( '+str(y_pos)+' , '+str(x_pos)+' ) : ' + str(round(value_pos,3)) )
            else:
                self.pixelPosLabel.setText('')

            if self.flagtxt1:
                self.Item1Pos = self.textItem1.pos()
                self.scaleBarPos = self.scale_rect.pos()
            if self.flagtxt2:
                self.Item2Pos = self.textItem2.pos()
            if self.flagtxt3:
                self.Item3Pos = self.textItem3.pos()
        except:
            pass


    def createColorTable(self):
        """
        Create a colormap qt colormap for the image display colormap is define in the tempColorTable file
        """

        f = open("./tempColorTable",'r')
        lines = f.readlines()
        self.tempColorTable = []

        for line in lines:
            r = int(line.split('\t')[1])
            g = int(line.split('\t')[2])
            b = int(line.split('\t')[3])
            self.tempColorTable.append(qRgba(r, g, b, 255))


        f.close()

    def _changeSlice(self):
        """
        Method to display a slice on 255 values, min and max of the contrast are defined by the double slider
        :return:
        """

        self.scene.clear()

        self.slice = self.dataVolume[int(self.sliceSlider.value()), :, :]
        self.mean_value = np.mean(self.slice)
        self.slice.squeeze()
        self.data = 255 * (self.slice - self.minimumValue) / (self.maximumValue - self.minimumValue)
        self.data[self.data >= 255] = 255
        self.data[self.data <= 0] = 0
        self.data = np.array(self.data, dtype=np.uint8)
        self.display_image()




    def _doubleSliderValueChanged(self, ddict):
        """
        If the contrast double slider is changed redraw the image with the correct contrast
        :param ddict:
        :return:
        """

        try:
            self.maximumValue = float(ddict['max'])
            self.minimumValue = float(ddict['min'])
        except:
            self.maximumValue = self.slice.max()
            self.maximumValue = self.slice.min()

        try:
            self.data = 255 * (self.slice - self.minimumValue) / (self.maximumValue - self.minimumValue)
            self.data[self.data >= 255] = 255
            self.data[self.data <= 0] = 0
            self.data = np.array(self.data, dtype=np.uint8)
            self.display_image()
        except:
            pass

    def _setDataVolume(self,dataVolume, minValue = -1, maxValue = -1):
        """
        Set the volume data to display
        :param dataVolume: 3D numpy array with slice index in the first axis
        :param minValue: min value of volume to display at initialisation
        :param maxValue: max value of volume to display at initialisation
        """
        self.dataShape = dataVolume.shape
        self.dataVolume = dataVolume

        if (minValue != -1) and (maxValue != -1):
            self.maximumValue = maxValue
            self.minimumValue = minValue
        else:
            self.maximumValue = self.dataVolume.max()
            self.minimumValue = self.dataVolume.min()

        max_slider  = dataVolume.shape[0]
        self.sliceSlider._setRange(0,max_slider-1)


        self._changeSlice()
        #self.scene.update()


    def display_image(self):
        """
        Initialisation of the Qt display with the correct colormap
        :return:
        """
        self.image = QImage(self.data, self.data.shape[1], self.data.shape[0], self.data.shape[1], QImage.Format_Indexed8)
        if self.imageType == 'Temp':
            self.image.setColorTable(self.tempColorTable)

        color = qRgba(255, 255, 255, 255)
        font_size = int(self.dataVolume.shape[1]/50)
        font = QFont("Times", font_size, QFont.Bold)

        pixMap = QPixmap.fromImage(self.image)
        self.pixItem = QGraphicsPixmapItem(pixMap)
        self.pixItem.setZValue(-1)


        if self.flagtxt1:
            self.textItem1 = QGraphicsTextItem(self.textstr1)
            self.textItem1.setDefaultTextColor(QColor(color))
            self.textItem1.setFont(font)
            self.textItem1.setFlag(self.textItem1.ItemIsMovable)
            print('Display',self.Item1Pos)
            self.textItem1.setPos(self.Item1Pos)
            self.textItem1.setZValue(0)
            self.scale_rect = QGraphicsRectItem()
            self.scale_rect.setBrush(QBrush(QColor(color)))
            bar_size = int(self.dataVolume.shape[1] / 50)
            self.scale_rect.setRect(0, 0, self.sizeScaleBar, bar_size)
            self.scale_rect.setPos(self.scaleBarPos)
            self.scale_rect.setZValue(0)
            self.scale_rect.setFlag(self.scale_rect.ItemIsMovable)


        if self.flagtxt2:
            self.textItem2 = QGraphicsTextItem()
            htmlTxt = "<div style='background:rgba(0, 0, 0, 100%);'>" +self.textstr2 + "</div>"
            self.textItem2.setHtml(htmlTxt)
            self.textItem2.setDefaultTextColor(QColor(color))
            self.textItem2.setFont(font)
            self.textItem2.setPos(self.Item2Pos)
            self.textItem2.setFlag(self.textItem2.ItemIsMovable)
            self.textItem2.setZValue(0)

        if self.flagtxt3:
            time_to_display = self.sliceSlider.slider.value() / self.frame_rate + float(self.starting_time)
            time_to_display = f'{time_to_display:.5f}'
            plain_text = 't = ' + time_to_display + ' s'
            self.current_time = time_to_display
            htmlTxt = "<div style='background:rgba(0, 0, 0, 100%);'>" +plain_text + "</div>"
            self.textItem3 = QGraphicsTextItem()
            self.textItem3.setHtml(htmlTxt)
            self.textItem3.setDefaultTextColor(QColor(color))
            self.textItem3.setFont(font)
            self.textItem3.setPos(self.Item3Pos)
            self.textItem3.setFlag(self.textItem3.ItemIsMovable)
            self.textItem3.setZValue(0)

        self.scene.clear()

        self.scene.addItem(self.pixItem)

        if self.flagtxt1:
            self.scene.addItem(self.scale_rect)
            self.scene.addItem(self.textItem1)
        if self.flagtxt2:
            self.scene.addItem(self.textItem2)
        if self.flagtxt3:
            self.scene.addItem(self.textItem3)
        self.scene.setSceneRect(0,0, self.image.width(),self.image.height()+100)
        self.scene.update()



class ImageDisplayWidget(QWidget):
    """
    Widget that include image visualisation, toolbar,  slider to change the slice and volume initialisation
    """
    def __init__(self, ImageType):
        super().__init__()
        self.toolBar = CustomToolBar(self)

        self.imageVisualizer = ImageVisualizer(ImageType,self)
        layoutTop = QHBoxLayout()
        layoutTop.addWidget(self.toolBar)

        layout = QVBoxLayout()
        layout.addLayout(layoutTop)
        layout.addWidget(self.imageVisualizer)

        self.toolBar.doubleSlider.sigDoubleSliderValueChanged.connect(self.imageVisualizer._doubleSliderValueChanged)
        self.toolBar.zoomAutoAction.triggered.connect(self.imageVisualizer.view.autofit)

        self.setLayout(layout)
        self.show()



    def _setDataVolume(self, dataVolume, minValue=-1, maxValue=-1):
        """
        Set the Volume to the visualiser
        :param dataVolume: numpy 3D array to display with axis 0 for the slices
        :param minValue: min value to display at initialisation
        :param maxValue: max value to display at initialisation
        """
        self.dataShape = dataVolume.shape
        self.dataVolume = dataVolume

        self.dataVolume[self.dataVolume == np.inf] = 1.0


        self.maximumValue = self.dataVolume.max()
        self.minimumValue = self.dataVolume.min()


        maxValue3Char = '%3.3f' % self.maximumValue
        minValue3Char = '%3.3f' % self.minimumValue

        self.toolBar.setMinAndMaxToolBar(float(minValue3Char), float(maxValue3Char))

        if (minValue != -1) and (maxValue != -1):
            self.toolBar.doubleSlider.maxSlider.setValue(maxValue)
            self.toolBar.doubleSlider.minSlider.setValue(minValue)

        self.imageVisualizer._setDataVolume(self.dataVolume, minValue, maxValue)


    def _autofit(self):
        """
        Call the Autofit
        :return:
        """
        self.imageVisualizer.view.autofit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    a = np.random.rand(10,50,100)

    testWindow = ImageDisplayWidget('')
    testWindow._setDataVolume(a)
    app.exec()




