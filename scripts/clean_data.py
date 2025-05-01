"""
Модуль очистки и подготовки данных о фильмах.
Читает данные из data/raw/movie_details.json, преобразует поля к нужному формату,
выполняет лемматизацию и токенизацию названий фильмов, сохраняет в CSV.
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import List, Dict
import spacy

# Загрузка spaCy-модели для русского языка
nlp = spacy.load("ru_core_news_sm")

# Пути
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "movie_details.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "movies_clean.csv"


def clean_money(value: str) -> int:
    """Очищает строку с денежным значением (например, '$ 1 000 000') и преобразует в int."""
    if not value:
        return None
    value = value.replace("$", "").replace("₽", "").replace(",", "").replace(" ", "")
    try:
        return int(value)
    except ValueError:
        return None


def extract_year(value: str) -> int:
    """Извлекает год из строки формата '7 февраля 2019'."""
    match = re.search(r"\b(19|20)\d{2}\b", value)
    if match:
        return int(match.group())
    return None


def clean_runtime(value: str) -> int:
    """Извлекает количество минут из строки формата '100 мин.'"""
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def to_list(value: str) -> List[str]:
    """Преобразует строку с перечислением элементов в список, разделённый по запятой."""
    return [v.strip() for v in value.split(",")] if value else []


import spacy
nlp = spacy.load("ru_core_news_sm")

def lemmatize_title(title: str) -> List[str]:
    """
    Лемматизирует название фильма, удаляет пунктуацию и стоп-слова.

    :param title: строка с названием
    :return: список лемм без стоп-слов
    """
    doc = nlp(title)
    return [
        token.lemma_
        for token in doc
        if token.is_alpha and not token.is_stop
    ]


def clean_movie_data(raw_data: List[Dict]) -> pd.DataFrame:
    """
    Очищает и форматирует данные о фильмах.

    :param raw_data: список словарей с данными
    :return: очищенный pandas DataFrame
    """
    processed = []

    for movie in raw_data:
        item = {
            "title": movie.get("title"),
            "url": movie.get("url"),
            "rating": float(movie["rating"]) if movie.get("rating") else None,
            "votes": int(movie["votes"]) if movie.get("votes") else None,
            "title_lemmas": lemmatize_title(movie.get("title", "")),
        }

        details = movie.get("details", {})

        # Преобразуем поля по категориям
        for field in [
            "Жанр", "Режиссер", "Продюсер", "Сценарист",
            "Композитор", "Страна", "Монтажер", "Художник-постановщик",
            "Оператор", "Формат"
        ]:
            item[field] = to_list(details.get(field, ""))

        for field, func in {
            "Год": lambda x: pd.to_numeric(x, errors="coerce"),
            "Хронометраж": clean_runtime,
            "Сборы в России": clean_money,
            "Зрители в России": clean_money,
            "Бюджет": clean_money,
            "Сборы в мире": clean_money,
            "Сборы в США": clean_money,
            "Дата релиза в РФ": extract_year,
            "Мировая премьера": extract_year,
            "Релиз на DVD": extract_year,
            "Релиз на Blu-Ray": extract_year,
            "Дата ре-релиза в РФ": extract_year
        }.items():
            value = details.get(field)
            result = func(value) if value else None
            # Приводим к int, если значение не пропущено
            item[field] = int(result) if pd.notna(result) else None

        processed.append(item)

    return pd.DataFrame(processed)


def save_clean_data(df: pd.DataFrame, path: Path = OUTPUT_FILE):
    """
    Сохраняет DataFrame в CSV.

    :param df: pandas DataFrame
    :param path: путь к выходному файлу
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
