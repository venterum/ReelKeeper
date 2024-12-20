import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTextEdit, QSpinBox, QPushButton, QHBoxLayout, QFileDialog

class AddMovieDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить фильм")
        self.setGeometry(100, 100, 400, 526)
        
        layout = QVBoxLayout(self)

        self.labelName = QLabel("Название:")
        self.movieTitle = QLineEdit()
        layout.addWidget(self.labelName)
        layout.addWidget(self.movieTitle)

        self.labelType = QLabel("Тип:")
        self.comboBoxTypes = QComboBox()
        layout.addWidget(self.labelType)
        layout.addWidget(self.comboBoxTypes)

        self.labelOverview = QLabel("Описание:")
        self.movieOverview = QTextEdit()
        layout.addWidget(self.labelOverview)
        layout.addWidget(self.movieOverview)

        self.labelDirector = QLabel("Режиссёр:")
        self.lineEdit = QLineEdit()
        layout.addWidget(self.labelDirector)
        layout.addWidget(self.lineEdit)

        self.labelGenre = QLabel("Жанр:")
        self.comboBoxGenres = QComboBox()
        layout.addWidget(self.labelGenre)
        layout.addWidget(self.comboBoxGenres)

        self.labelYear = QLabel("Год выпуска:")
        self.spinBoxYear = QSpinBox()
        self.spinBoxYear.setRange(1895, 2100)
        self.spinBoxYear.setValue(2000)
        layout.addWidget(self.labelYear)
        layout.addWidget(self.spinBoxYear)

        self.choosePosterButton = QPushButton("Выбрать постер")
        self.choosePosterButton.clicked.connect(self.choose_poster)
        self.choosePosterButton.setMinimumSize(75, 75)
        layout.addWidget(self.choosePosterButton)

        self.posterPreview = QLabel()
        layout.addWidget(self.posterPreview, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.addButton = QPushButton("Добавить карточку")
        self.addButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Отмена")
        self.cancelButton.clicked.connect(self.reject)
        self.addButton.setMinimumSize(75, 75)
        self.cancelButton.setMinimumSize(75, 75)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.addButton)
        buttons_layout.addWidget(self.cancelButton)
        layout.addLayout(buttons_layout)

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
            self.posterPreview.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

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