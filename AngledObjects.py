from PyQt5 import QtCore, QtGui, QtWidgets


class AngledObject(QtWidgets.QGraphicsView):
    _angle = 0

    def __init__(self, angle=0, parent=None):
        super(AngledObject, self).__init__(parent)
        # to prevent the graphics view to draw its borders or background, set the
        # FrameShape property to 0 and a transparent background
        self.setFrameShape(0)
        self.setStyleSheet("background-color: transparent; border-radius: 7px;")
        self.setScene(QtWidgets.QGraphicsScene())
        # ignore scroll bars!
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def angle(self):
        return self._angle

    def setAngle(self, angle):
        angle %= 360
        if angle == self._angle:
            return
        self._angle = angle
        self._proxy.setTransform(QtGui.QTransform().rotate(-angle))
        self.adjustSize()

    def resizeEvent(self, event):
        super(AngledObject, self).resizeEvent(event)
        # ensure that the scene is fully visible after resizing
        QtCore.QTimer.singleShot(0, lambda: self.centerOn(self.sceneRect().center()))

    def sizeHint(self):
        return self.scene().itemsBoundingRect().size().toSize()

    def minimumSizeHint(self):
        return self.sizeHint()


class AngledLabel(AngledObject):
    def __init__(self, text='', angle=0, parent=None):
        super(AngledLabel, self).__init__(angle, parent)
        self.label = QtWidgets.QLabel(text)
        self._proxy = self.scene().addWidget(self.label)
        self.setStyleSheet("background-color: rgba(24, 28, 36, 150); border-radius: 7px")
        self.label.setStyleSheet(
            "background-color: rgba(24, 28, 36, 0); font: 30pt 'Traffic Arrows 2 Medium normal';color: white;")
        self.setAngle(angle)
        self.alignment = self.label.alignment
        # self.setFixedWidth(40)
        self.setAlignment(QtCore.Qt.AlignCenter)
        # self.label.setScaledContents(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

    def setAlignment(self, alignment):
        # text alignment might affect the text size!
        if alignment == self.label.alignment():
            return
        self.label.setAlignment(alignment)
        self.setMinimumSize(self.sizeHint())

    def text(self):
        return self.label.text()

    def setText(self, text):
        if text == self.label.text():
            return
        self.label.setText(text)
        self.setMinimumSize(self.sizeHint())
