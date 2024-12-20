import requests
import re
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from core.settings import load_config

class KinopoiskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт из КиноПоиска")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("Вставьте ссылку на фильм с КиноПоиска...")
        layout.addWidget(self.link_edit)
        
        import_button = QPushButton("Импортировать")
        import_button.clicked.connect(self.import_movie)
        layout.addWidget(import_button)
        
        self.movie_data = None

    def extract_id(self, url):
        match = re.search(r'(?:film|series)/(\d+)', url)
        return match.group(1) if match else None

    def download_poster(self, url):
        try:
            response = requests.get(url)
            return response.content if response.status_code == 200 else None
        except:
            return None

    def get_genre_id(self, genres):
        if not genres:
            return 1
        return 1

    def get_director_name(self, persons):
        if not persons or not isinstance(persons, list):
            return ""
        
        for person in persons:
            if isinstance(person, dict):
                profession = person.get("profession")
                if isinstance(profession, dict):
                    if profession.get("value") == "режиссеры":
                        return person.get("name", "")
                elif isinstance(profession, str):
                    if profession == "режиссеры":
                        return person.get("name", "")
                elif isinstance(profession, list):
                    for prof in profession:
                        if isinstance(prof, dict) and prof.get("value") == "режиссеры":
                            return person.get("name", "")
        return ""

    def import_movie(self):
        url = self.link_edit.text().strip()
        movie_id = self.extract_id(url)
        
        if not movie_id:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Неверный формат ссылки. Используйте ссылку вида:\nhttps://www.kinopoisk.ru/film/123456/"
            )
            return
        
        config = load_config()
        api_key = config.get("kinopoisk_api_key", "")
        if not api_key:
            QMessageBox.warning(
                self,
                "Ошибка",
                "API ключ не настроен. Пожалуйста, добавьте его в настройках."
            )
            return
        
        try:
            response = requests.get(
                f'https://api.kinopoisk.dev/v1.4/movie/{movie_id}',
                headers={'X-API-KEY': api_key}
            )
            if response.status_code == 404:
                QMessageBox.warning(self, "Ошибка", "Фильм не найден")
                return
            elif response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", f"Ошибка API: {response.status_code}")
                return 
            
            data = response.json()
            
            content_type = 2 if data.get("isSeries") else 1
            genres = data.get("genres", [])
            if any(genre.get("name", "").lower() == "аниме" for genre in genres):
                content_type = 4
            
            persons = data.get("persons", [])
            director = self.get_director_name(persons)
            
            self.movie_data = {
                "title": data.get("name"),
                "overview": data.get("description", ""),
                "poster": self.download_poster(data.get("poster", {}).get("url")) if data.get("poster") else None,
                "type_id": content_type,
                "genre_id": self.get_genre_id(data.get("genres", [])),
                "year": data.get("year", 2000),
                "director": director
            }
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def get_data(self):
        return self.movie_data