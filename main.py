import argparse
import os
import sys
import numpy as np

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtWidgets import QListWidget, QPushButton, QLabel, QListWidgetItem, QGridLayout
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColorConstants
from PyQt6.QtCore import Qt, QPoint

try:
    DIR_TARGETS = sys.argv[1]
    DIR_OUTPUT = sys.argv[2]
except:
    sys.exit('Provide arguments: python main.py <input_image_dir> <output_landmark_dir>')

os.makedirs(DIR_OUTPUT, exist_ok=True)

app = QApplication([])

class Window(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        listw = QListWidget()
        listw.itemDoubleClicked.connect(self.load)
        self.label_coord = QLabel()
        self.view_image = QLabel()
        self.view_image.mousePressEvent = self.on_image_click
        self.view_image.mouseMoveEvent = self.on_image_move
        self.view_image.mouseReleaseEvent = self.on_image_release

        btn_save = QPushButton('Save')
        btn_save.clicked.connect(self.save)
        btn_back = QPushButton('Back')
        btn_back.clicked.connect(self.back)

        layout = QGridLayout()
        layout.addWidget(listw, 3, 0)
        layout.addWidget(btn_save, 0, 0)
        layout.addWidget(btn_back, 1, 0)
        layout.addWidget(self.label_coord, 2, 0)
        layout.addWidget(self.view_image, 0, 1, 4, 1)
        self.setLayout(layout)

        paths = os.listdir(DIR_TARGETS)
        for path in paths:
            QListWidgetItem(path, listw)


        self.points = []
        self.selected_file = 'test'
        self.pixmap_bg = None
        self.grab_index = None

    def load(self, item):
        path = item.text()
        path_img = os.path.join(DIR_TARGETS, path)
        self.pixmap_bg = QPixmap(path_img)
        self.view_image.setPixmap(self.pixmap_bg.copy())

        self.save()

        self.selected_file = path
        path_lmk = os.path.join(DIR_OUTPUT, os.path.splitext(self.selected_file)[0]+'.txt')
        if os.path.exists(path_lmk):
            self.points = np.loadtxt(path_lmk).tolist()
            self.update_points()
        else:
            self.points = []

    def save(self):
        pts = np.array(self.points)
        path_output = os.path.join(DIR_OUTPUT, os.path.splitext(self.selected_file)[0]+'.txt')
        np.savetxt(path_output, pts)
        self.label_coord.setText(f'Saved: {path_output}')

    def back(self):
        if len(self.points) > 0:
            self.points.pop()
            self.update_points()

    def on_image_click(self, ev):
        flags = ev.flags()
        pos = ev.pos()
        x = pos.x()
        y = pos.y()

        if ev.button() == Qt.MouseButton.LeftButton:
            self.label_coord.setText(f'[{len(self.points)+1}] X: {x} / Y: {y}')
            self.points.append([x, y])
            self.update_points()

        elif ev.button() == Qt.MouseButton.RightButton:
            if len(self.points) > 0:
                pts = np.array(self.points)
                query = np.array([x, y])
                dists = np.linalg.norm(pts - query, axis=1)
                selected = np.argmin(dists)
                self.grab_index = selected
                self.on_image_move(ev)

        else:
            pass

    def on_image_move(self, ev):
        pos = ev.pos()
        x = pos.x()
        y = pos.y()
        if self.grab_index is not None:
            self.points[self.grab_index][0] = x
            self.points[self.grab_index][1] = y
            self.label_coord.setText(f'[{self.grab_index}] X: {x} / Y: {y}')
            self.update_points()

    def on_image_release(self, ev):
        if ev.button() == Qt.MouseButton.RightButton:
            self.grab_index = None

    def update_points(self):
        pix = self.pixmap_bg.copy()
        painter = QPainter()
        painter.begin(pix)
        painter.setPen(QPen(QColorConstants.Blue, 8))
        for i, p in enumerate(self.points):
            x = p[0]
            y = p[1]
            painter.drawPoint(QPoint(int(x), int(y)))
            painter.drawText(int(x), int(y), str(i+1))
        painter.end()
        self.view_image.setPixmap(pix)

w = Window()
w.show()
app.exec()
