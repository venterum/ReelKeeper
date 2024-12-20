import sqlite3
import random
import qdarktheme
from core.settings import load_config, save_config

from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QDialog, QPushButton, QMessageBox,
    QGraphicsBlurEffect
)
from PyQt6.QtCore import QTimer

from modules.card import MovieCard
from modules.add_movie import AddMovieDialog
from modules.filter import FilterDialog
from modules.kinopoisk import KinopoiskDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("resources/ui/library.ui", self)
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(0)
        self.centralWidget().setGraphicsEffect(self.blur_effect)
        self.setWindowTitle("ReelKeeper")
        self.setWindowIcon(QIcon("resources/icons/film_frames.png"))

        self.set_slogan()
        self.sloganLabel.setWordWrap(True)
        self.sloganLabel.setFixedWidth(300)
        self.sloganLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reelkeeperLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        config = load_config()
        if not config.get("show_quotes", True):
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignCenter)
        else:
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignBottom)

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))
        self.settingsButton.clicked.connect(lambda: self.load_ui("ui/settings.ui"))
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
        self.blur_effect.setBlurRadius(10)
        
        size = self.size()
        icon = self.windowIcon()
        title = self.windowTitle()

        uic.loadUi(f"resources/{ui_file}", self)

        self.centralWidget().setGraphicsEffect(self.blur_effect)

        self.set_slogan()
        self.sloganLabel.setWordWrap(True)
        self.sloganLabel.setFixedWidth(300)
        self.sloganLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reelkeeperLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        config = load_config()
        if not config.get("show_quotes", True):
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignCenter)
        else:
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignBottom)

        self.libButton.clicked.connect(lambda: self.load_ui("ui/library.ui"))
        self.helpButton.clicked.connect(lambda: self.load_ui("ui/info.ui"))
        self.settingsButton.clicked.connect(lambda: self.load_ui("ui/settings.ui"))

        self.resize(size)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)

        if ui_file == "ui/library.ui":
            self.settingsButton.clicked.connect(lambda: self.load_ui("ui/settings.ui"))
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

        if ui_file == "ui/settings.ui":
            self.setup_settings_page()

        QTimer.singleShot(70, self.remove_blur)

    def remove_blur(self):
        self.blur_effect.setBlurRadius(0)

    def setup_settings_page(self):
        config = load_config()
        
        theme_map = {"light": 0, "dark": 1, "auto": 2}
        theme_index = theme_map.get(config["theme"], 2)
        self.themeComboBox.setCurrentIndex(theme_index)
        self.themeComboBox.currentIndexChanged.connect(self.change_theme)
        
        self.apiKeyInput.setText(config.get("kinopoisk_api_key", ""))
        self.apiKeyInput.textChanged.connect(self.save_api_key)
        
        self.showQuotesCheckBox.setChecked(config.get("show_quotes", True))
        self.showQuotesCheckBox.stateChanged.connect(self.toggle_quotes)

    def change_theme(self):
        theme_map = {0: "light", 1: "dark", 2: "auto"}
        selected_theme = theme_map[self.themeComboBox.currentIndex()]
        
        config = load_config()
        config["theme"] = selected_theme
        save_config(config)
        
        qdarktheme.setup_theme(selected_theme)

    def save_api_key(self):
        config = load_config()
        config["kinopoisk_api_key"] = self.apiKeyInput.text()
        save_config(config)

    def toggle_quotes(self):
        config = load_config()
        config["show_quotes"] = self.showQuotesCheckBox.isChecked()
        save_config(config)
        
        self.sloganLabel.setVisible(config["show_quotes"])
        if config["show_quotes"]:
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignBottom)
        else:
            self.verticalLayout.setAlignment(self.reelkeeperLogo, Qt.AlignmentFlag.AlignCenter)

    def set_slogan(self):
        config = load_config()
        if not config.get("show_quotes", True):
            self.sloganLabel.setVisible(False)
            return
        
        try:
            with open("resources/slogans.txt", "r", encoding="utf-8") as file:
                slogans = file.readlines()
                if slogans:
                    random_slogan = random.choice(slogans).strip()
                    self.sloganLabel.setText(f'{random_slogan}')
                else:
                    self.sloganLabel.setText("Добро пожаловать в ReelKeeper!")
            self.sloganLabel.setVisible(True)
        except FileNotFoundError:
            self.sloganLabel.setText("Добро пожаловать в ReelKeeper!")
            self.sloganLabel.setVisible(True)

    def check_if_exists(self, title):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM movies WHERE LOWER(title) = LOWER(?)", (title,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def add_movie(self):
        choice_dialog = QDialog(self)
        choice_dialog.setWindowTitle("Каким способом хотите добавить?")
        choice_dialog.setMinimumWidth(300)
        layout = QVBoxLayout(choice_dialog)
        manual_button = QPushButton("Добавить данные вручную")
        manual_button.setMinimumHeight(75)
        kinopoisk_button = QPushButton("Импорт из КиноПоиск")
        kinopoisk_button.setMinimumHeight(75)
        
        layout.addWidget(manual_button)
        layout.addWidget(kinopoisk_button)
        
        def open_manual_dialog():
            choice_dialog.accept()
            dialog = AddMovieDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                movie_data = dialog.get_data()
                if self.check_if_exists(movie_data["title"]):
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Контент с таким названием уже существует, добавить его снова не получится!"
                    )
                    return
                
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
            choice_dialog.accept()
            dialog = KinopoiskDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                movie_data = dialog.get_data()
                if movie_data:
                    if self.check_if_exists(movie_data["title"]):
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            "Такая карточка уже существует!"
                        )
                        return
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
            conditions.append("""(
                LOWER(m.title) LIKE LOWER(?) OR 
                LOWER(m.overview) LIKE LOWER(?) OR 
                LOWER(m.director) LIKE LOWER(?) OR 
                CAST(m.year AS TEXT) LIKE ?
            )""")
            search_pattern = f"%{search_query.lower()}%"
            params.extend([search_pattern] * 4)
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
        search_query = self.queryLine.text().strip().lower()
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
        