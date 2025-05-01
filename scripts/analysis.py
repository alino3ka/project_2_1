import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

def plot_avg_rating_by_genre(df: pd.DataFrame, min_count: int = 5, top_n: int = 20):
    """
    Строит график средних рейтингов по жанрам (в виде горизонтального barplot).

    :param df: DataFrame с колонками 'Жанр' и 'rating'
    :param min_count: минимальное количество фильмов на жанр для включения в график
    :param top_n: максимальное количество жанров для отображения (по частоте)
    """
    genre_rating = []
    for _, row in df.iterrows():
        rating = row["rating"]
        genres = row.get("Жанр", [])
        for g in genres:
            if g:
                genre_rating.append((g, rating))

    # Собираем в датафрейм
    genre_df = pd.DataFrame(genre_rating, columns=["Жанр", "Рейтинг"])

    # Группируем
    grouped = genre_df.groupby("Жанр").agg(
        Средний_рейтинг=("Рейтинг", "mean"),
        Количество=("Рейтинг", "count")
    )

    # Фильтруем по количеству
    grouped = grouped[grouped["Количество"] >= min_count]
    grouped = grouped.sort_values("Средний_рейтинг", ascending=False).head(top_n)

    # Визуализация
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="Средний_рейтинг",
        y=grouped.index,
        data=grouped,
        hue=grouped.index,
        palette="viridis",
        legend=False
    )
    plt.title(f"Средний рейтинг по жанрам (только жанры с ≥ {min_count} фильмами)")
    plt.xlabel("Средний рейтинг")
    plt.ylabel("Жанр")
    plt.grid(True, axis="x")
    plt.tight_layout()


def plot_avg_rating_by_director(df: pd.DataFrame, min_count: int = 3, top_n: int = 20):
    """
    Строит график средних рейтингов по режиссёрам (barplot), учитывая только тех,
    у кого не менее min_count фильмов. Отображает топ-N по среднему рейтингу.

    :param df: DataFrame с колонками 'Режиссер' и 'rating'
    :param min_count: минимальное количество фильмов у режиссёра
    :param top_n: количество топ-режиссёров для отображения
    """
    director_rating = []
    for _, row in df.iterrows():
        rating = row["rating"]
        directors = row.get("Режиссер", [])
        for d in directors:
            if d:
                director_rating.append((d, rating))

    # В датафрейм
    dir_df = pd.DataFrame(director_rating, columns=["Режиссер", "Рейтинг"])

    # Группировка
    grouped = dir_df.groupby("Режиссер").agg(
        Средний_рейтинг=("Рейтинг", "mean"),
        Количество=("Рейтинг", "count")
    )

    # Фильтрация и сортировка
    grouped = grouped[grouped["Количество"] >= min_count]
    grouped = grouped.sort_values("Средний_рейтинг", ascending=False).head(top_n).reset_index()

    # Построение графика
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="Средний_рейтинг",
        y="Режиссер",
        data=grouped,
        hue="Режиссер",
        palette="mako",
        legend=False
    )
    plt.title(f"Средний рейтинг по режиссёрам (≥ {min_count} фильмов)")
    plt.xlabel("Средний рейтинг")
    plt.ylabel("Режиссёр")
    plt.grid(True, axis="x")
    plt.tight_layout()


def plot_avg_rating_by_country(df: pd.DataFrame, min_count: int = 3, top_n: int = 20, ascending: bool = False):
    """
    Строит график средних рейтингов по странам.

    :param df: DataFrame с колонками 'Страна' и 'rating'
    :param min_count: минимальное количество фильмов на страну
    :param top_n: количество стран для отображения
    :param ascending: если True — показать страны с наименьшими рейтингами
    """
    country_rating = []
    for _, row in df.iterrows():
        rating = row["rating"]
        countries = row.get("Страна", [])
        for c in countries:
            if c:
                country_rating.append((c, rating))

    country_df = pd.DataFrame(country_rating, columns=["Страна", "Рейтинг"])

    grouped = country_df.groupby("Страна").agg(
        Средний_рейтинг=("Рейтинг", "mean"),
        Количество=("Рейтинг", "count")
    )

    grouped = grouped[grouped["Количество"] >= min_count]
    grouped = grouped.sort_values("Средний_рейтинг", ascending=ascending).head(top_n).reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="Средний_рейтинг",
        y="Страна",
        data=grouped,
        hue="Страна",
        palette="cubehelix",
        legend=False
    )
    direction = "наивысшими" if not ascending else "наименьшими"
    plt.title(f"Средний рейтинг по странам (с {direction} оценками, ≥ {min_count} фильмов)")
    plt.xlabel("Средний рейтинг")
    plt.ylabel("Страна")
    plt.grid(True, axis="x")
    plt.tight_layout()


def plot_rating_vs_votes(df: pd.DataFrame, log_scale: bool = False):
    """
    Строит scatterplot зависимости рейтинга от количества голосов.

    :param df: DataFrame с колонками 'rating' и 'votes'
    :param log_scale: если True — использовать log10(votes + 1) по оси X
    """
    x = df["votes"]
    y = df["rating"]

    if log_scale:
        x = np.log10(x + 1)
        xlabel = "log10(Число голосов + 1)"
        title = "Рейтинг vs логарифм количества голосов"
    else:
        xlabel = "Число голосов"
        title = "Рейтинг vs количество голосов"

    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=x, y=y, color="orange", edgecolor="black", alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel("Рейтинг")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()


def plot_rating_vs_runtime(df: pd.DataFrame, min_runtime: int = 30, max_runtime: int = 240):
    """
    Строит scatterplot зависимости рейтинга от хронометража (длительности фильма).

    :param df: DataFrame с колонками 'Хронометраж' и 'rating'
    :param min_runtime: нижняя граница длительности (для фильтрации выбросов)
    :param max_runtime: верхняя граница длительности
    """
    filtered = df[df["Хронометраж"].between(min_runtime, max_runtime)]

    plt.figure(figsize=(8, 5))
    sns.scatterplot(
        data=filtered,
        x="Хронометраж",
        y="rating",
        color="mediumseagreen",
        edgecolor="black",
        alpha=0.7
    )
    plt.title("Рейтинг vs Хронометраж фильма")
    plt.xlabel("Длительность (минуты)")
    plt.ylabel("Рейтинг")
    plt.grid(True)
    plt.tight_layout()


def plot_rating_vs_popularity(df: pd.DataFrame, column: str, log_scale: bool = True):
    """
    Строит scatterplot зависимости рейтинга от популярности (сборы или число зрителей).

    :param df: DataFrame с колонкой 'rating' и одной из: 'Сборы в России', 'Зрители в России'
    :param column: имя числовой колонки популярности
    :param log_scale: логарифмировать ось X (по умолчанию да — данные сильно скошены)
    """
    if column not in df.columns:
        raise ValueError(f"Колонка '{column}' не найдена")

    data = df[[column, "rating"]].dropna()

    x = data[column]
    if log_scale:
        x = np.log10(x + 1)
        xlabel = f"log10({column} + 1)"
        title = f"Рейтинг vs логарифм {column}"
    else:
        xlabel = column
        title = f"Рейтинг vs {column}"

    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=x, y=data["rating"], color="slateblue", edgecolor="black", alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel("Рейтинг")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()


def plot_rating_vs_title_length(df: pd.DataFrame):
    """
    Строит два графика:
    - Рейтинг vs длина названия в символах
    - Рейтинг vs количество лемм в названии

    :param df: DataFrame с колонками 'title' и 'title_lemmas'
    """
    df = df.copy()
    df["Длина_в_символах"] = df["title"].str.len()
    df["Длина_в_словах"] = df["title_lemmas"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.scatterplot(data=df, x="Длина_в_символах", y="rating", ax=axes[0], color="coral", edgecolor="black", alpha=0.6)
    axes[0].set_title("Рейтинг vs длина названия (в символах)")
    axes[0].set_xlabel("Длина названия (символы)")
    axes[0].set_ylabel("Рейтинг")
    axes[0].grid(True)

    sns.scatterplot(data=df, x="Длина_в_словах", y="rating", ax=axes[1], color="darkgreen", edgecolor="black", alpha=0.6)
    axes[1].set_title("Рейтинг vs длина названия (в леммах)")
    axes[1].set_xlabel("Длина названия (слова)")
    axes[1].set_ylabel("Рейтинг")
    axes[1].grid(True)

    plt.tight_layout()


def plot_top_lemmas(df: pd.DataFrame, top_n: int = 20):
    """
    Строит график самых частых лемм в названиях всех фильмов.

    :param df: DataFrame с колонкой 'title_lemmas' (список слов)
    :param top_n: сколько слов отобразить
    """
    all_lemmas = []

    for lemmas in df["title_lemmas"]:
        if isinstance(lemmas, list):
            all_lemmas.extend(lemmas)

    counter = Counter(all_lemmas)
    most_common = counter.most_common(top_n)
    lemmas, counts = zip(*most_common)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=list(counts),
        y=list(lemmas),
        hue=list(lemmas),  # задаём hue = y
        palette="crest",
        legend=False
    )
    plt.title(f"Топ-{top_n} самых частых лемм в названиях фильмов")
    plt.xlabel("Частота")
    plt.ylabel("Лемма")
    plt.grid(True, axis="x")
    plt.tight_layout()


def compare_lemmas_by_rating(df: pd.DataFrame, high_thresh: float = 8.5, low_thresh: float = 6.0, top_n: int = 15):
    """
    Сравнивает частотность лемм в названиях фильмов с высоким и низким рейтингом.

    :param df: DataFrame с колонками 'title_lemmas' и 'rating'
    :param high_thresh: порог для высокого рейтинга (>=)
    :param low_thresh: порог для низкого рейтинга (<=)
    :param top_n: количество топ-лемм для отображения
    """
    from collections import Counter

    def get_lemma_counter(subset: pd.DataFrame) -> Counter:
        lemmas = []
        for row in subset["title_lemmas"]:
            if isinstance(row, list):
                lemmas.extend(row)
        return Counter(lemmas)

    # Разделение на группы
    high = df[df["rating"] >= high_thresh]
    low = df[df["rating"] <= low_thresh]

    high_counter = get_lemma_counter(high)
    low_counter = get_lemma_counter(low)

    top_high = high_counter.most_common(top_n)
    top_low = low_counter.most_common(top_n)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Высокий рейтинг
    if top_high:
        lemmas_h, counts_h = zip(*top_high)
        sns.barplot(x=list(counts_h), y=list(lemmas_h), ax=axes[0], hue=list(lemmas_h), palette="Greens", legend=False)
        axes[0].set_title(f"Частые слова в названиях фильмов с рейтингом ≥ {high_thresh}")
        axes[0].set_xlabel("Частота")
        axes[0].set_ylabel("Лемма")
        axes[0].grid(True, axis="x")
    else:
        axes[0].text(0.5, 0.5, "Нет данных для фильмов с высоким рейтингом", ha="center", va="center")
        axes[0].axis("off")

    # Низкий рейтинг
    if top_low:
        lemmas_l, counts_l = zip(*top_low)
        sns.barplot(x=list(counts_l), y=list(lemmas_l), ax=axes[1], hue=list(lemmas_l), palette="Reds", legend=False)
        axes[1].set_title(f"Частые слова в названиях фильмов с рейтингом ≤ {low_thresh}")
        axes[1].set_xlabel("Частота")
        axes[1].set_ylabel("Лемма")
        axes[1].grid(True, axis="x")
    else:
        axes[1].text(0.5, 0.5, f"Нет фильмов с рейтингом ≤ {low_thresh}", ha="center", va="center")
        axes[1].axis("off")

    plt.tight_layout()
