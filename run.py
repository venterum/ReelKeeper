import sys
import os

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)

from core.app import MainWindow, QApplication
from core.settings import load_config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    from PyQt6.QtGui import QFontDatabase, QFont, QIcon
    import qdarktheme
    
    font_files = [
        "resources/fonts/Jost-Bold.ttf",
        "resources/fonts/Jost-BoldItalic.ttf",
        "resources/fonts/Jost-Italic.ttf",
        "resources/fonts/Jost-Medium.ttf",
        "resources/fonts/Jost-MediumItalic.ttf",
        "resources/fonts/Jost-Regular.ttf",
    ]
    
    for font_file in font_files:
        font_path = os.path.join(root_path, font_file)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Не удалось загрузить шрифт {font_file}")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family))
    
    config = load_config()
    qdarktheme.setup_theme(config.get("theme", "auto"))
    app.setWindowIcon(QIcon(os.path.join(root_path, "resources/icons/film_frames.png")))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec()) 