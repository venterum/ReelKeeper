from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QMenuBar, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
import qdarktheme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle("ReelKeeper")

        # Central Widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Main Layout
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setStretch(0, 1)

        # Left Area
        self.leftArea = QFrame(self.centralwidget)
        self.leftArea.setFrameShape(QFrame.Shape.StyledPanel)
        self.leftArea.setFrameShadow(QFrame.Shadow.Raised)
        self.leftVerticalLayout = QVBoxLayout(self.leftArea)

        # ReelKeeper Logo
        self.reelkeeperLogo = QLabel(" 🎞️ReelKeeper", self.leftArea)
        font = QFont("Google Sans Medium", 28)
        self.reelkeeperLogo.setFont(font)
        self.leftVerticalLayout.addWidget(self.reelkeeperLogo)

        # Library Button
        self.libButton = QPushButton("Библиотека 📚", self.leftArea)
        self.libButton.setMinimumSize(75, 75)
        self.libButton.setFont(QFont("Google Sans", 12))
        self.leftVerticalLayout.addWidget(self.libButton)

        # Settings Button
        self.settingsButton = QPushButton("Настройки 🛠️", self.leftArea)
        self.settingsButton.setMinimumSize(75, 75)
        self.settingsButton.setFont(QFont("Google Sans", 12))
        self.leftVerticalLayout.addWidget(self.settingsButton)

        # Help Button
        self.helpButton = QPushButton("Помощь 🆘", self.leftArea)
        self.helpButton.setMinimumSize(75, 75)
        self.helpButton.setFont(QFont("Google Sans", 12))
        self.leftVerticalLayout.addWidget(self.helpButton)

        self.horizontalLayout.addWidget(self.leftArea, 1)

        # Right Area
        self.rightArea = QFrame(self.centralwidget)
        self.rightArea.setFrameShape(QFrame.Shape.StyledPanel)
        self.rightArea.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.rightArea)
        self.gridLayout_3 = QGridLayout()

        # Search Button
        self.searchButton = QPushButton("🔎", self.rightArea)
        self.searchButton.setMinimumSize(75, 75)
        self.gridLayout_3.addWidget(self.searchButton, 1, 1)

        # Add Button
        self.addButton = QPushButton("➕", self.rightArea)
        self.addButton.setMinimumSize(75, 75)
        self.gridLayout_3.addWidget(self.addButton, 1, 2)

        # Spacers
        self.horizontalDownSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.gridLayout_3.addItem(self.horizontalDownSpacer, 1, 0)

        self.verticalSpacer_1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.gridLayout_3.addItem(self.verticalSpacer_1, 0, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.gridLayout_3.addItem(self.verticalSpacer_2, 0, 2)

        self.verticalLayout_2.addLayout(self.gridLayout_3)
        self.horizontalLayout.addWidget(self.rightArea, 3)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())