from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
import sqlite3


class MovieDetailsDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        uic.loadUi("ui/movie_details.ui", self)
        self.title = title
        self.data = None
        self.load_data()
        self.populate_fields()

        # Подключение кнопок
        self.saveButton.clicked.connect(self.save_changes)
        self.closeButton.clicked.connect(self.reject)

    def get_rounded_pixmap(self, pixmap, width, height, radius):
        scaled_pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        rounded = QPixmap(width, height)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(scaled_pixmap))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rounded.rect(), radius, radius)
        painter.end()
        return rounded

    def load_data(self):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.title, m.overview, m.poster, t.type_name, g.genre_name, m.year, m.director, m.rating, m.progress
            FROM movies m
            JOIN types t ON m.type_id = t.type_id
            JOIN genres g ON m.genre_id = g.genre_id
            WHERE m.title = ?
        """, (self.title,))
        self.data = cursor.fetchone()
        conn.close()

    def populate_fields(self):
        # Постер
        if self.data[2]:  # poster
            pixmap = QPixmap()
            pixmap.loadFromData(self.data[2])
            self.posterLabel.setPixmap(self.get_rounded_pixmap(pixmap, 300, 450, 10))

        # Название
        self.titleEdit.setText(self.data[0])

        # Описание
        self.overviewEdit.setPlainText(self.data[1])

        # Рейтинг
        self.ratingLabel.setText(f"Рейтинг: {self.data[7]:.1f}/10")

        # Прогресс
        self.progressBar.setValue(self.data[8])

        # Тип
        self.populate_combobox(self.typeCombo, "types", self.data[3])

        # Жанр
        self.populate_combobox(self.genreCombo, "genres", self.data[4])

        # Год
        self.yearSpin.setValue(self.data[5])

        # Режиссёр
        self.directorEdit.setText(self.data[6])

    def populate_combobox(self, combobox, table, selected_item):
        conn = sqlite3.connect('data/data.sqlite')
        cursor = conn.cursor()
        cursor.execute(f"SELECT {table[:-1]}_id, {table[:-1]}_name FROM {table}")
        items = cursor.fetchall()
        for item_id, item_name in items:
            combobox.addItem(item_name, item_id)
        conn.close()
        combobox.setCurrentText(selected_item)

    def save_changes(self):
        title = self.titleEdit.text()
        overview = self.overviewEdit.toPlainText()
        type_id = self.typeCombo.currentData()
        genre_id = self.genreCombo.currentData()
        year = self.yearSpin.value()
        director = self.directorEdit.text()

        try:
            conn = sqlite3.connect('data/data.sqlite')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE movies
                SET title = ?, overview = ?, type_id = ?, genre_id = ?, year = ?, director = ?
                WHERE title = ?
            """, (title, overview, type_id, genre_id, year, director, self.data[0]))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Данные успешно обновлены!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")