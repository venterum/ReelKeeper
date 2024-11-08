from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QDialog, QDialogButtonBox
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt, QSize
import sqlite3


class MovieCard(QFrame):
    def __init__(self, title, overview, poster, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMaximumSize(16777215, 400)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        poster_label = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(poster)
        rounded_pixmap = self.get_rounded_pixmap(pixmap, 200, 300, 10)
        poster_label.setPixmap(rounded_pixmap)
        layout.addWidget(poster_label)
        v_layout = QVBoxLayout()

        # Название
        label_title = QLabel(title)
        label_title.setObjectName("label_title")
        label_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        label_title.setWordWrap(True)
        v_layout.addWidget(label_title)

        # Описание
        label_overview = QLabel(overview)
        label_overview.setStyleSheet("font-size: 14px;")
        label_overview.setWordWrap(True)
        label_overview.setMaximumHeight(80)
        label_overview.setTextFormat(Qt.TextFormat.PlainText)
        label_overview.setText(label_overview.text()[:200] + "..." if len(label_overview.text()) > 200 else label_overview.text())
        v_layout.addWidget(label_overview)

        buttons_layout = QHBoxLayout()

        more_button = QPushButton("Подробнее")
        more_button.setMinimumHeight(40)
        buttons_layout.addWidget(more_button)

        delete_button = QPushButton("🗑️")
        delete_button.setMinimumHeight(40)
        delete_button.setMaximumWidth(75)
        delete_button.clicked.connect(self.delete_card)
        buttons_layout.addWidget(delete_button)

        v_layout.addLayout(buttons_layout)
        layout.addLayout(v_layout)

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
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No, confirm)
        buttons.accepted.connect(confirm.accept)
        buttons.rejected.connect(confirm.reject)
        confirm_layout = QVBoxLayout(confirm)
        confirm_layout.addWidget(question_label)
        confirm_layout.addWidget(buttons)
        if confirm.exec() == QDialog.DialogCode.Accepted:
            conn = sqlite3.connect('data/data.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE title=?", (title,))
            conn.commit()
            conn.close()
            self.setParent(None)