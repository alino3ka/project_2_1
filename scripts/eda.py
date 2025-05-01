import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def describe_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает расширенную сводку по датафрейму:
    - тип данных (dtype)
    - количество пропущенных значений (учитываются также пустые списки)
    - доля пропущенных значений в % и в формате n/N

    :param df: исходный DataFrame
    :return: таблица с описанием всех колонок
    """
    total_rows = len(df)
    missing_counts = {}

    for col in df.columns:
        # Стандартные пропуски
        null_mask = df[col].isnull()

        # Дополнительно считаем пустые списки как пропуски
        if df[col].apply(lambda x: isinstance(x, list)).any():
            empty_list_mask = df[col].apply(lambda x: isinstance(x, list) and len(x) == 0)
            null_mask = null_mask | empty_list_mask

        missing_counts[col] = null_mask.sum()

    missing = pd.Series(missing_counts)
    missing_percent = (missing / total_rows * 100).round(2)

    summary = pd.DataFrame({
        "Тип данных": df.dtypes,
        "Количество пропусков": missing,
        "Доля пропусков (%)": missing_percent
    })

    summary.index.name = f"Всего фильмов: {total_rows}"
    summary = summary.sort_values("Количество пропусков", ascending=False)

    return summary




def plot_rating_distribution(df: pd.DataFrame, bins: int = 20):
    """
    Строит гистограмму распределения рейтингов фильмов.

    :param df: DataFrame с колонкой 'rating'
    :param bins: количество корзин для гистограммы
    """
    plt.figure(figsize=(8, 5))
    sns.histplot(df["rating"].dropna(), bins=bins, kde=True, color="skyblue", edgecolor="black")
    plt.title("Распределение рейтингов фильмов")
    plt.xlabel("Рейтинг")
    plt.ylabel("Количество фильмов")
    plt.grid(True)
    plt.tight_layout()


def plot_vote_distribution(df: pd.DataFrame, bins: int = 30):
    """
    Строит гистограмму распределения количества оценок (votes).

    :param df: DataFrame с колонкой 'votes'
    :param bins: количество корзин для гистограммы
    """
    plt.figure(figsize=(8, 5))
    sns.histplot(df["votes"].dropna(), bins=bins, kde=False, color="salmon", edgecolor="black")
    plt.title("Распределение количества голосов")
    plt.xlabel("Число голосов")
    plt.ylabel("Количество фильмов")
    plt.grid(True)
    plt.tight_layout()


def plot_log_vote_distribution(df: pd.DataFrame, bins: int = 30):
    """
    Строит гистограмму логарифмированного распределения количества голосов (log10(votes + 1)).

    :param df: DataFrame с колонкой 'votes'
    :param bins: количество корзин
    """
    votes = df["votes"].dropna()
    log_votes = np.log10(votes + 1)

    plt.figure(figsize=(8, 5))
    sns.histplot(log_votes, bins=bins, color="teal", edgecolor="black")
    plt.title("Логарифмированное распределение количества голосов")
    plt.xlabel("log10(число голосов + 1)")
    plt.ylabel("Количество фильмов")
    plt.grid(True)
    plt.tight_layout()


def plot_year_distribution(df: pd.DataFrame, column: str, title: str = None):
    """
    Строит распределение количества фильмов по указанному году (барплот по годам).

    :param df: DataFrame с данными
    :param column: имя колонки, содержащей год (например, 'Год' или 'Мировая премьера')
    :param title: заголовок графика (по умолчанию формируется из имени колонки)
    """
    if column not in df.columns:
        raise ValueError(f"Колонка '{column}' не найдена в датафрейме")

    year_counts = df[column].dropna().astype(int).value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    sns.barplot(x=year_counts.index, y=year_counts.values, color="steelblue")
    plt.title(title or f"Количество фильмов по году: {column}")
    plt.xlabel("Год")
    plt.ylabel("Количество фильмов")
    plt.xticks(rotation=45)
    plt.grid(True, axis="y")
    plt.tight_layout()
