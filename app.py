import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
import qdarktheme, pywinstyles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/library.ui", self)
        self.setWindowTitle("ReelKeeper")
        self.setWindowIcon(QIcon("icons/film_frames.png"))

        self.settingsButton.clicked.connect(lambda: self.load_ui("ui/settings.ui"))
        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))

    def load_ui(self, ui_file):
        size = self.size()
        icon = self.windowIcon()
        title = self.windowTitle()

        uic.loadUi(ui_file, self)

        self.settingsButton.clicked.connect(lambda: self.load_ui("ui/settings.ui"))
        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))

        self.resize(size)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    pywinstyles.apply_style(window, "dark")
    window.show()
    sys.exit(app.exec())