import sqlite3
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFileDialog

class AddMovieDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("resources/ui/add_movie.ui", self)
        
        self.choosePosterButton.clicked.connect(self.choose_poster)
        self.addButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        self.poster_path = None
        self.load_combobox_data()

    def load_combobox_data(self):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()

        cursor.execute("SELECT type_id, type_name FROM types")
        types = cursor.fetchall()
        for type_id, type_name in types:
            self.comboBoxTypes.addItem(type_name, type_id)

        cursor.execute("SELECT genre_id, genre_name FROM genres")
        genres = cursor.fetchall()
        for genre_id, genre_name in genres:
            self.comboBoxGenres.addItem(genre_name, genre_id)

        conn.close()

    def choose_poster(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать постер", "", "Обложка (*.png *.jpg *.jpeg)")
        if file_name:
            self.poster_path = file_name
            pixmap = QPixmap(file_name)
            self.posterPreview.setPixmap(pixmap.scaled(300, 450, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def get_data(self):
        if self.poster_path:
            with open(self.poster_path, 'rb') as f:
                poster = f.read()
        else:
            poster = None
        return {
            "title": self.movieTitle.text(),
            "overview": self.movieOverview.toPlainText(),
            "poster": poster,
            "type_id": self.comboBoxTypes.currentData(),
            "genre_id": self.comboBoxGenres.currentData(),
            "year": self.spinBoxYear.value(),
            "director": self.lineEdit.text()
        }