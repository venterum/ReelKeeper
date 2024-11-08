from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class AddMovieDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/add_movie.ui", self)
        self.choosePosterButton.clicked.connect(self.choose_poster)
        self.addButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.poster_path = None

    def choose_poster(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать постер", "", "Обложка (*.png *.jpg *.jpeg)")
        if file_name:
            self.poster_path = file_name
            pixmap = QPixmap(file_name)
            self.posterPreview.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def get_data(self):
        if self.poster_path:
            with open(self.poster_path, 'rb') as f:
                poster = f.read()
        else:
            poster = None
        return self.movieTitle.text(), self.movieOverview.toPlainText(), poster