import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QFrame, QDialog, QProgressBar
)

from details import MovieDetailsDialog


class MovieCard(QFrame):
    def __init__(self, title, overview, poster, content_type, year, progress, rating, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMaximumSize(16777215, 400)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        poster_label = QLabel()
        if poster:
            pixmap = QPixmap()
            pixmap.loadFromData(poster)
            rounded_pixmap = self.get_rounded_pixmap(pixmap, 200, 300, 10)
            poster_label.setPixmap(rounded_pixmap)
        layout.addWidget(poster_label, alignment=Qt.AlignmentFlag.AlignLeft)

        v_layout = QVBoxLayout()

        label_type = QLabel(content_type)
        label_type.setStyleSheet("font-size: 16px; font-style: italic; color: gray;")
        v_layout.addWidget(label_type)

        label_title = QLabel(f"{title}, {year}")
        label_title.setObjectName("label_title")
        label_title.setStyleSheet("font-size: 26px; font-weight: bold;")
        label_title.setWordWrap(True)
        v_layout.addWidget(label_title)

        if rating > 0:
            label_rating = QLabel(f"⭐ {rating:.1f}/10")
            label_rating.setStyleSheet("font-size: 16px; color: orange;")
            v_layout.addWidget(label_rating)

        label_overview = QLabel(overview)
        label_overview.setStyleSheet("font-size: 14px;")
        label_overview.setWordWrap(True)
        label_overview.setMaximumHeight(80)
        label_overview.setTextFormat(Qt.TextFormat.PlainText)
        label_overview.setText(
            label_overview.text()[:300] + "..." if len(label_overview.text()) > 300 else label_overview.text()
        )
        v_layout.addWidget(label_overview)

        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setTextVisible(True)
        progress_bar.setMaximumWidth(580)

        v_layout.addWidget(progress_bar)

        buttons_layout = QHBoxLayout()

        more_button = QPushButton("Подробнее")
        more_button.setMinimumHeight(40)
        more_button.setMinimumWidth(500)
        more_button.setMaximumHeight(40)
        more_button.setMaximumWidth(500)
        more_button.clicked.connect(self.show_details)
        buttons_layout.addWidget(more_button)

        delete_button = QPushButton("🗑️")
        delete_button.setMinimumHeight(40)
        delete_button.setMaximumHeight(40)
        delete_button.setMinimumWidth(75)
        delete_button.setMaximumWidth(75)
        delete_button.clicked.connect(self.delete_card)
        buttons_layout.addWidget(delete_button)

        v_layout.addLayout(buttons_layout)
        layout.addLayout(v_layout)
        layout.addStretch(1)

    def show_details(self):
        title = self.findChild(QLabel, "label_title").text()
        details_dialog = MovieDetailsDialog(title)
        details_dialog.exec()

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

    def delete_card(self):
        title = self.findChild(QLabel, "label_title").text()
        confirm = QDialog(self)
        confirm.setWindowTitle("Подтверждение удаления")
        question_label = QLabel(f"Вы уверены, что хотите удалить {title}?", confirm)
        buttons_layout = QHBoxLayout()

        yes_button = QPushButton("Да")
        yes_button.setMinimumHeight(40)
        buttons_layout.addWidget(yes_button)

        no_button = QPushButton("Нет")
        no_button.setMinimumHeight(40)
        buttons_layout.addWidget(no_button)

        yes_button.clicked.connect(confirm.accept)
        no_button.clicked.connect(confirm.reject)

        confirm_layout = QVBoxLayout(confirm)
        confirm_layout.addWidget(question_label)
        confirm_layout.addLayout(buttons_layout)

        if confirm.exec() == QDialog.DialogCode.Accepted:
            conn = sqlite3.connect('data/data.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE title=?", (title,))
            conn.commit()
            conn.close()
            self.setParent(None)