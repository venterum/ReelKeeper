from PyQt6.QtWidgets import QDialog, QMessageBox, QRadioButton, QSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialogButtonBox
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt
from PyQt6 import uic
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
        self.progressButton.clicked.connect(self.update_progress)
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
        self.ratingSpin.setRange(0.0, 10.0)
        self.ratingSpin.setSingleStep(0.1)
        self.ratingSpin.setValue(self.data[7])

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
        rating = self.ratingSpin.value()

        try:
            conn = sqlite3.connect('data/data.sqlite')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE movies
                SET title = ?, overview = ?, type_id = ?, genre_id = ?, year = ?, director = ?, rating = ?
                WHERE title = ?
            """, (title, overview, type_id, genre_id, year, director, rating, self.data[0]))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Данные успешно обновлены!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def update_progress(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить прогресс")
        layout = QVBoxLayout(dialog)

        # Радиокнопки
        episodes_button = QRadioButton("Количество серий")
        minutes_button = QRadioButton("Количество минут")
        layout.addWidget(episodes_button)
        layout.addWidget(minutes_button)

        # Поля ввода для серий
        episodes_layout = QHBoxLayout()
        episodes_label = QLabel("Серий просмотрено:")
        episodes_spin = QSpinBox()
        episodes_spin.setRange(0, 1000)
        episodes_spin.setEnabled(False)
        episodes_layout.addWidget(episodes_label)
        episodes_layout.addWidget(episodes_spin)

        total_episodes_layout = QHBoxLayout()
        total_episodes_label = QLabel("Всего серий:")
        total_episodes_spin = QSpinBox()
        total_episodes_spin.setRange(1, 1000)
        total_episodes_spin.setEnabled(False)
        total_episodes_layout.addWidget(total_episodes_label)
        total_episodes_layout.addWidget(total_episodes_spin)

        # Поля ввода для минут
        minutes_layout = QVBoxLayout()
        watched_minutes_layout = QHBoxLayout()
        total_minutes_layout = QHBoxLayout()

        minutes_label = QLabel("Минут просмотрено:")
        minutes_spin = QSpinBox()
        minutes_spin.setRange(0, 10000)
        minutes_spin.setEnabled(False)
        watched_minutes_layout.addWidget(minutes_label)
        watched_minutes_layout.addWidget(minutes_spin)

        total_minutes_label = QLabel("Всего минут:")
        total_minutes_spin = QSpinBox()
        total_minutes_spin.setRange(1, 10000)
        total_minutes_spin.setEnabled(False)
        total_minutes_layout.addWidget(total_minutes_label)
        total_minutes_layout.addWidget(total_minutes_spin)

        minutes_layout.addLayout(watched_minutes_layout)
        minutes_layout.addLayout(total_minutes_layout)

        layout.addLayout(episodes_layout)
        layout.addLayout(total_episodes_layout)
        layout.addLayout(minutes_layout)

        # Обработчики для радио-кнопок
        def enable_episode_fields():
            episodes_spin.setEnabled(True)
            total_episodes_spin.setEnabled(True)
            minutes_spin.setEnabled(False)
            total_minutes_spin.setEnabled(False)

        def enable_minute_fields():
            episodes_spin.setEnabled(False)
            total_episodes_spin.setEnabled(False)
            minutes_spin.setEnabled(True)
            total_minutes_spin.setEnabled(True)

        episodes_button.toggled.connect(enable_episode_fields)
        minutes_button.toggled.connect(enable_minute_fields)

        # Кнопки подтверждения
        button_box = QDialogButtonBox()
        ok_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        ok_button.setMinimumSize(75, 75)
        cancel_button.setMinimumSize(75, 75)
        button_box.addButton(ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(button_box)

        # Подтверждение или отмена
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            if episodes_button.isChecked():
                watched = episodes_spin.value()
                total = total_episodes_spin.value()
                progress = int((watched / total) * 100) if total > 0 else 0
            elif minutes_button.isChecked():
                watched = minutes_spin.value()
                total = total_minutes_spin.value()
                progress = int((watched / total) * 100) if total > 0 else 0
            else:
                return

            try:
                conn = sqlite3.connect('data/data.sqlite')
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE movies
                    SET progress = ?
                    WHERE title = ?
                """, (progress, self.title))
                conn.commit()
                conn.close()
                self.progressBar.setValue(progress)
                QMessageBox.information(self, "Успех", "Прогресс успешно обновлён!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить прогресс: {str(e)}")