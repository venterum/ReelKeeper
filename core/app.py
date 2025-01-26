import sqlite3
import random
import qdarktheme
from core.settings import load_config, save_config

from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QIcon, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QDialog, QPushButton, QMessageBox,
    QGraphicsBlurEffect, QStackedWidget, QButtonGroup, QMenu, QWidgetAction, QLabel
)
from PyQt6.QtCore import QTimer

from modules.card import MovieCard
from modules.add_movie import AddMovieDialog
from modules.filter import FilterDialog
from modules.kinopoisk import KinopoiskDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("resources/ui/main.ui", self)
        self.setWindowTitle("ReelKeeper")
        self.setWindowIcon(QIcon("resources/icons/film_frames.png"))

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.libButton)
        self.button_group.addButton(self.helpButton)
        self.button_group.addButton(self.settingsButton)
        self.button_group.addButton(self.luckyButton)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_library_page()
        self.setup_settings_page()
        
        self.active_filters = {}
        self.current_sort = "id ASC"
        self.load_cards()

    def setup_ui(self):
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

    def setup_connections(self):
        self.libButton.clicked.connect(lambda: self.switch_page(0))
        self.helpButton.clicked.connect(lambda: self.switch_page(1))
        self.settingsButton.clicked.connect(lambda: self.switch_page(2))
        self.luckyButton.clicked.connect(self.show_random_movie)

        self.addButton.clicked.connect(self.add_movie)
        self.filterButton.clicked.connect(self.open_filter_dialog)
        self.queryLine.returnPressed.connect(self.apply_search)
        self.updateButton.clicked.connect(self.reset_filters)

        self.themeComboBox.currentIndexChanged.connect(self.change_theme)
        self.apiKeyInput.textChanged.connect(self.save_api_key)
        self.showQuotesCheckBox.stateChanged.connect(self.toggle_quotes)

        self.sortButton.clicked.connect(self.show_sort_menu)

    def setup_library_page(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.cardsLayout.addWidget(self.scroll_area)

        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.scroll_area.setWidget(self.cards_widget)

    def setup_settings_page(self):
        config = load_config()
        
        theme_map = {"light": 0, "dark": 1, "auto": 2}
        theme_index = theme_map.get(config["theme"], 2)
        self.themeComboBox.setCurrentIndex(theme_index)
        
        self.apiKeyInput.setText(config.get("kinopoisk_api_key", ""))
        self.showQuotesCheckBox.setChecked(config.get("show_quotes", True))
        
        self.clearLibraryButton.clicked.connect(self.clear_library)

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

    def change_theme(self):
        theme_map = {0: "light", 1: "dark", 2: "auto"}
        selected_theme = theme_map[self.themeComboBox.currentIndex()]
        
        config = load_config()
        config["theme"] = selected_theme
        save_config(config)
        
        app = QApplication.instance()
        app.setStyleSheet(qdarktheme.load_stylesheet(config.get("theme", selected_theme)))

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

    def load_cards(self, filters=None):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        query = """
            SELECT m.title, m.overview, m.poster, t.type_name, g.genre_name, m.year, m.progress, m.rating, m.director
            FROM movies m
            JOIN types t ON m.type_id = t.type_id
            JOIN genres g ON m.genre_id = g.genre_id
        """
        conditions = []
        params = []

        if filters:
            if "type_id" in filters:
                conditions.append("m.type_id = ?")
                params.append(filters["type_id"])
            if "genre_id" in filters:
                conditions.append("m.genre_id = ?")
                params.append(filters["genre_id"])
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
        
        query += f" ORDER BY m.{self.current_sort}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        filtered_rows = []
        if filters and "search" in filters:
            search_query = filters["search"].lower()
            for row in rows:
                title, overview, poster, type_name, genre_name, year, progress, rating, director = row
                if (search_query in title.lower() or 
                    search_query in overview.lower() or 
                    search_query in director.lower() or 
                    search_query in str(year)):
                    filtered_rows.append(row)
        else:
            filtered_rows = rows

        for row in filtered_rows:
            title, overview, poster, type_name, genre_name, year, progress, rating, director = row
            card = MovieCard(title, overview, poster, type_name, genre_name, year, progress, rating)
            self.cards_layout.insertWidget(0, card)

    def open_filter_dialog(self):
        dialog = FilterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.active_filters = dialog.get_filters()
            self.load_cards(filters=self.active_filters)

    def apply_search(self):
        search_query = self.queryLine.text().strip()
        if search_query:
            self.active_filters["search"] = search_query
        elif "search" in self.active_filters:
            del self.active_filters["search"]
        self.load_cards(filters=self.active_filters)

    def reset_filters(self):
        self.active_filters = {}
        self.current_sort = "id ASC"
        self.queryLine.clear()
        self.load_cards()
        
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
        
        def manual_dialog():
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
        
        manual_button.clicked.connect(manual_dialog)
        kinopoisk_button.clicked.connect(kinopoisk)
        choice_dialog.exec()
        
    def switch_page(self, index):
        self.stackedWidget.setCurrentIndex(index)
        buttons = [self.libButton, self.helpButton, self.settingsButton]
        for i, button in enumerate(buttons):
            button.setChecked(i == index)
        
    def show_random_movie(self):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.title, m.overview, m.poster, t.type_name, g.genre_name, m.year, m.progress, m.rating, m.director
            FROM movies m
            JOIN types t ON m.type_id = t.type_id
            JOIN genres g ON m.genre_id = g.genre_id
            ORDER BY RANDOM()
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            for i in reversed(range(self.cards_layout.count())):
                self.cards_layout.itemAt(i).widget().setParent(None)

            title, overview, poster, type_name, genre_name, year, progress, rating, director = row
            card = MovieCard(title, overview, poster, type_name, genre_name, year, progress, rating)
            self.cards_layout.insertWidget(0, card)

            return_button = QPushButton("Вернуться к библиотеке")
            return_button.setMinimumHeight(75)
            return_button.clicked.connect(self.reset_filters)
            self.cards_layout.addWidget(return_button)

            self.stackedWidget.setCurrentIndex(0)
            self.libButton.setChecked(True)
        else:
            QMessageBox.warning(self, "Упс!", "В базе данных нет фильмов!")
        
    def show_sort_menu(self):
        menu = QMenu(self)
        menu.setMinimumWidth(200)
        
        label = QLabel("  Сортировать по:")
        label.setStyleSheet("color: gray; padding: 5px;")
        label_action = QWidgetAction(menu)
        label_action.setDefaultWidget(label)
        menu.addAction(label_action)
        menu.addSeparator()
        
        date_menu = menu.addMenu("По дате добавления")
        date_menu.addAction("Сначала новые").triggered.connect(lambda: self.apply_sort("id ASC"))
        date_menu.addAction("Сначала старые").triggered.connect(lambda: self.apply_sort("id DESC"))
        
        title_menu = menu.addMenu("По названию")
        title_menu.addAction("От А до Я").triggered.connect(lambda: self.apply_sort("title DESC"))
        title_menu.addAction("От Я до А").triggered.connect(lambda: self.apply_sort("title ASC"))
        
        year_menu = menu.addMenu("По году выпуска")
        year_menu.addAction("Сначала новые").triggered.connect(lambda: self.apply_sort("year ASC"))
        year_menu.addAction("Сначала старые").triggered.connect(lambda: self.apply_sort("year DESC"))
        
        director_menu = menu.addMenu("По режиссёру")
        director_menu.addAction("От А до Я").triggered.connect(lambda: self.apply_sort("director DESC"))
        director_menu.addAction("От Я до А").triggered.connect(lambda: self.apply_sort("director ASC"))
        
        rating_menu = menu.addMenu("По рейтингу")
        rating_menu.addAction("Сначала высокий").triggered.connect(lambda: self.apply_sort("rating ASC"))
        rating_menu.addAction("Сначала низкий").triggered.connect(lambda: self.apply_sort("rating DESC"))
        
        progress_menu = menu.addMenu("По прогрессу просмотра")
        progress_menu.addAction("Сначала высокий").triggered.connect(lambda: self.apply_sort("progress ASC"))
        progress_menu.addAction("Сначала низкий").triggered.connect(lambda: self.apply_sort("progress DESC"))
        
        menu.exec(self.sortButton.mapToGlobal(QPoint(0, self.sortButton.height())))

    def apply_sort(self, sort_order):
        self.current_sort = sort_order
        self.load_cards(filters=self.active_filters)
        
    def clear_library(self):
        from PyQt6.QtWidgets import QMessageBox
        
        warning = QMessageBox()
        warning.setIcon(QMessageBox.Icon.Warning)
        warning.setWindowTitle("Внимание!")
        warning.setText("Вы уверены, что хотите очистить библиотеку?")
        warning.setInformativeText("Это действие удалит ВСЕ карточки из вашей библиотеки НАВСЕГДА!\nОтменить это действие будет невозможно.")
        warning.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        warning.setDefaultButton(QMessageBox.StandardButton.No)
        warning.button(QMessageBox.StandardButton.Yes).setText("Да, удалить всё")
        warning.button(QMessageBox.StandardButton.No).setText("Отмена")
        warning.button(QMessageBox.StandardButton.Yes).setMinimumWidth(150)
        warning.button(QMessageBox.StandardButton.No).setMinimumWidth(150)
        
        if warning.exec() == QMessageBox.StandardButton.Yes:
            final_warning = QMessageBox()
            final_warning.setIcon(QMessageBox.Icon.Critical)
            final_warning.setWindowTitle("Последнее предупреждение!")
            final_warning.setText("Вы АБСОЛЮТНО уверены?")
            final_warning.setInformativeText("Это последнее предупреждение!\nВся ваша коллекция будет удалена без возможности восстановления.\nПродолжить?")
            final_warning.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            final_warning.setDefaultButton(QMessageBox.StandardButton.No)
            final_warning.button(QMessageBox.StandardButton.Yes).setText("Да, удалите всё!")
            final_warning.button(QMessageBox.StandardButton.No).setText("Нет, я передумал")
            final_warning.button(QMessageBox.StandardButton.Yes).setMinimumWidth(200)
            final_warning.button(QMessageBox.StandardButton.No).setMinimumWidth(200)
            
            if final_warning.exec() == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect('data/data.sqlite')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM movies")
                    conn.commit()
                    conn.close()
                    
                    self.load_cards()
                    
                    QMessageBox.information(
                        self,
                        "Успешно",
                        "Библиотека успешно очищена"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось очистить библиотеку: {str(e)}"
                    )
        