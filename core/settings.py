import json
from pathlib import Path

CONFIG_PATH = Path("data/config.json")

def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "theme": "auto",
            "kinopoisk_api_key": "",
            "show_quotes": True
        }
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        return {
            "theme": "auto",
            "kinopoisk_api_key": "",
            "show_quotes": True
        }

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")