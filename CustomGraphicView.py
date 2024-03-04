
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QGraphicsView

class CustomGraphicView(QGraphicsView):
    """
    Class to display image and handle zoom action and mouse movement
    """
    CustomGraphicsViewEvent = pyqtSignal(dict)

    def __init__(self, scene, parent):
        self.scene = scene
        QGraphicsView.__init__(self, scene, parent)
        self.setMouseTracking(True)
        self.setBackgroundBrush(Qt.black);
        self.setAcceptDrops(True)
        self.zoomScale = 1
        self.FlagWheellEvent = True


    def mouseMoveEvent(self, event):
        """ Catch the mouse image position to display later
        :param event: QEvent
        :return:
        """
        if (event.button() == Qt.NoButton):
            dx = event.pos().x()
            dy = event.pos().y()

            clickPosition = self.mapToScene(dx, dy)
            ddict = {}
            ddict['event'] = "MouseMoved"
            ddict['x'] = clickPosition.x()
            ddict['y'] = clickPosition.y()

            self.CustomGraphicsViewEvent.emit(ddict)

        return QGraphicsView.mouseMoveEvent(self, event)


    def wheelEvent(self, event):
        """ Catch the mouse wheel event to zoom in and out
        :param event: QEvent
        :return:
        """

        factor = float(event.angleDelta().y()) / 100.0

        if factor < 0:
            factor = -factor
            factor = 1.0 / factor

        self.zoomScale *= factor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(factor, factor)

    def autofit(self):
        """
        Method to reset zoom to initial one
        :return:
        """
        self.zoomScale = 1
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)