import sys
import sqlite3
import os
import random

import qdarktheme
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFontDatabase, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QDialog, QPushButton, QMessageBox
)

from card import MovieCard
from add_movie import AddMovieDialog
from filter import FilterDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/library.ui", self)
        self.setWindowTitle("ReelKeeper")
        self.setWindowIcon(QIcon("icons/film_frames.png"))

        self.set_slogan()
        self.sloganLabel.setWordWrap(True)
        self.sloganLabel.setFixedWidth(300)
        self.sloganLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))
        self.addButton.clicked.connect(self.add_movie)
        self.filterButton.clicked.connect(self.open_filter_dialog)
        self.queryLine.textChanged.connect(self.apply_search)
        self.updateButton.clicked.connect(self.reset_filters)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.cardsLayout.addWidget(self.scroll_area)

        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.scroll_area.setWidget(self.cards_widget)

        self.active_filters = {}
        self.load_cards()

    def load_ui(self, ui_file):
        size = self.size()
        icon = self.windowIcon()
        title = self.windowTitle()

        uic.loadUi(ui_file, self)

        self.set_slogan()
        self.sloganLabel.setWordWrap(True)
        self.sloganLabel.setFixedWidth(300)
        self.sloganLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))

        self.resize(size)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)

        if ui_file == "ui/library.ui":
            self.updateButton.clicked.connect(self.reset_filters)
            self.addButton.clicked.connect(self.add_movie)
            self.filterButton.clicked.connect(self.open_filter_dialog)
            self.queryLine.textChanged.connect(self.apply_search)
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.cardsLayout.addWidget(self.scroll_area)
            self.cards_widget = QWidget()
            self.cards_layout = QVBoxLayout(self.cards_widget)
            self.scroll_area.setWidget(self.cards_widget)
            self.load_cards()

    def set_slogan(self):
        try:
            with open("slogans.txt", "r", encoding="utf-8") as file:
                slogans = file.readlines()
                if slogans:
                    random_slogan = random.choice(slogans).strip()
                    self.sloganLabel.setText(f'{random_slogan}')
                else:
                    self.sloganLabel.setText("Добро пожаловать в ReelKeeper!")
        except FileNotFoundError:
            self.sloganLabel.setText("Добро пожаловать в ReelKeeper!")

    def add_movie(self):
        choice_dialog = QDialog(self)
        choice_dialog.setWindowTitle("Каким способом хотите добавить?")
        choice_dialog.setMinimumWidth(300)
        layout = QVBoxLayout(choice_dialog)
        manual_button = QPushButton("Добавить данные вручную")
        manual_button.setMinimumHeight(75)
        kinopoisk_button = QPushButton("Импорт из КиноПоиска")
        kinopoisk_button.setMinimumHeight(75)
        
        layout.addWidget(manual_button)
        layout.addWidget(kinopoisk_button)
        
        def open_manual_dialog():
            choice_dialog.accept()
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
                    0   # прогресс
                ))

                conn.commit()
                conn.close()
                self.load_cards()
                
        def kinopoisk():
            QMessageBox.information(
                self,
                "В разработке...",
                "Функция добавления по ссылке из КиноПоиска пока ещё находится в разработке."
            )
            choice_dialog.reject()
        
        manual_button.clicked.connect(open_manual_dialog)
        kinopoisk_button.clicked.connect(kinopoisk)
        
        choice_dialog.exec()

    def load_cards(self, search_query="", filters=None):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        query = """
            SELECT m.title, m.overview, m.poster, t.type_name, m.year, m.progress, m.rating
            FROM movies m
            JOIN types t ON m.type_id = t.type_id
        """
        conditions = []
        params = []

        if search_query:
            conditions.append("(m.title LIKE ? OR m.overview LIKE ? OR m.year LIKE ?)")
            params.extend([f"%{search_query}%"] * 3)
        if filters:
            if "genre_id" in filters:
                conditions.append("m.genre_id = ?")
                params.append(filters["genre_id"])
            if "type_id" in filters:
                conditions.append("m.type_id = ?")
                params.append(filters["type_id"])
            if "years" in filters:
                year_from, year_to = filters["years"]
                conditions.append("m.year BETWEEN ? AND ?")
                params.extend([year_from, year_to])
            if "rating" in filters:
                rating_from, rating_to = filters["rating"]
                conditions.append("m.rating BETWEEN ? AND ?")
                params.extend([rating_from, rating_to])
            if "progress" in filters:
                progress_from, progress_to = filters["progress"]
                conditions.append("m.progress BETWEEN ? AND ?")
                params.extend([progress_from, progress_to])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        for row in rows:
            title, overview, poster, type_name, year, progress, rating = row
            card = MovieCard(title, overview, poster, type_name, year, progress, rating)
            self.cards_layout.insertWidget(0, card)

    def apply_search(self):
        search_query = self.queryLine.text().strip()
        self.load_cards(search_query=search_query, filters=self.active_filters)

    def open_filter_dialog(self):
        dialog = FilterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.active_filters = dialog.get_filters()
            self.load_cards(filters=self.active_filters)

    def reset_filters(self):
        self.active_filters = {}
        self.queryLine.clear()
        self.load_cards()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font_files = [
        "fonts/Jost-Bold.ttf",
        "fonts/Jost-BoldItalic.ttf",
        "fonts/Jost-Italic.ttf",
        "fonts/Jost-Medium.ttf",
        "fonts/Jost-MediumItalic.ttf",
        "fonts/Jost-Regular.ttf",
    ]
    
    for font_file in font_files:
        font_path = os.path.join(font_file)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Не удалось загрузить шрифт {font_file}")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family))
    
    app.setStyleSheet(qdarktheme.load_stylesheet())
    app.setWindowIcon(QIcon("icons/film_frames.png"))
    window = MainWindow()
    dialog = AddMovieDialog()
    window.show()
    sys.exit(app.exec())