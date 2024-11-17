import sys
import qdarktheme, pywinstyles
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QDialog
from PyQt6.QtGui import QIcon
from card import MovieCard
from add_movie import AddMovieDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/library.ui", self)
        self.setWindowTitle("ReelKeeper")
        self.setWindowIcon(QIcon("icons/film_frames.png"))

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))
        self.addButton.clicked.connect(self.add_movie)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.cardsLayout.addWidget(self.scroll_area)

        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.scroll_area.setWidget(self.cards_widget)

        self.load_cards()

    def load_ui(self, ui_file):
        size = self.size()
        icon = self.windowIcon()
        title = self.windowTitle()

        uic.loadUi(ui_file, self)

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))
        self.addButton.clicked.connect(self.add_movie)

        self.resize(size)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)

        if ui_file == "ui/library.ui":
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.cardsLayout.addWidget(self.scroll_area)
            self.cards_widget = QWidget()
            self.cards_layout = QVBoxLayout(self.cards_widget)
            self.scroll_area.setWidget(self.cards_widget)
            self.load_cards()

    def add_movie(self):
        dialog = AddMovieDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            movie_data = dialog.get_data()
            conn = sqlite3.connect('data/data.sqlite')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO movies (title, overview, poster, type_id, genre_id, year, director, rating, progress) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                movie_data["title"],
                movie_data["overview"],
                movie_data["poster"],
                movie_data["type_id"],
                movie_data["genre_id"],
                movie_data["year"],
                movie_data["director"],
                0,  # рейтинг
                0   # прогресс просмотра
            ))

            conn.commit()
            conn.close()
            self.load_cards()

    def load_cards(self):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.title, m.overview, m.poster, t.type_name, m.progress
            FROM movies m
            JOIN types t ON m.type_id = t.type_id
        """)
        rows = cursor.fetchall()
        conn.close()

        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        for row in rows:
            title, overview, poster, type_name, progress = row
            card = MovieCard(title, overview, poster, type_name, progress)
            self.cards_layout.insertWidget(0, card)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    dialog = AddMovieDialog()
    pywinstyles.apply_style(window, "dark")
    pywinstyles.apply_style(dialog, "dark")
    window.show()
    sys.exit(app.exec())