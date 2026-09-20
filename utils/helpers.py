import json
from pathlib import Path

_LOCALE_DIR = Path(__file__).resolve().parent.parent / 'locales'


def load_locale(lang='ar'):
    path = _LOCALE_DIR / f'{lang}.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_text(lang, key, **kwargs):
    data = load_locale(lang)
    value = data.get(key, key)
    return value.format(**kwargs) if kwargs else value
