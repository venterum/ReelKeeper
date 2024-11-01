from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class MovieCard(QFrame):
    def __init__(self, title, overview, poster, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMaximumSize(300, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Обложка
        label_image = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(poster)
        label_image.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))  # Масштабируем изображение
        label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_image)

        # Название
        label_title = QLabel(title)
        label_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        label_title.setWordWrap(True)
        layout.addWidget(label_title)

        # Описание
        label_overview = QLabel(overview)
        label_overview.setStyleSheet("font-size: 12px;")
        label_overview.setWordWrap(True)
        label_overview.setMaximumHeight(80)
        label_overview.setTextFormat(Qt.TextFormat.PlainText)
        label_overview.setWordWrap(True)
        label_overview.setText(label_overview.text()[:100] + "..." if len(label_overview.text()) > 100 else label_overview.text())
        layout.addWidget(label_overview)