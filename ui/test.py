import sys

from PIL import Image, ImageFilter, ImageQt
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel
from PyQt5 import QtGui


app = QApplication(sys.argv)
mw = QMainWindow()
layout = QVBoxLayout(mw)
lbl_picture = QLabel()
image = Image.open("hills.jpeg")
img = image.filter(ImageFilter.GaussianBlur(3))
#pixmap = ImageQt.toqpixmap(img)

im2 = img.convert("RGBA")
data = im2.tobytes("raw", "BGRA")
qim = QtGui.QImage(data, img.width, img.height, QtGui.QImage.Format_ARGB32)
pixmap = QtGui.QPixmap.fromImage(qim)

lbl_picture.setPixmap(pixmap)

mw.show()
sys.exit(app.exec_())