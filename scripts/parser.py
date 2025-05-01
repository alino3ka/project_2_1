import logging
import time
import json
import re
from pathlib import Path
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === ПУТИ К ПРОЕКТУ ===
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)


def init_driver(headless: bool = True) -> webdriver.Chrome:
    """Инициализирует и возвращает Selenium WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")

    logging.info("Инициализация Chrome WebDriver")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_top_movies(num_pages: int = 1, delay: float = 1.0, headless: bool = True) -> List[Dict[str, str]]:
    """
    Парсит топ фильмов с сайта https://www.filmpro.ru/movies/top?page=N

    :param num_pages: количество страниц для парсинга (>=1)
    :param delay: задержка между страницами
    :param headless: режим без отображения браузера
    :return: список словарей: {'title': ..., 'url': ...}
    """
    if not isinstance(num_pages, int) or num_pages < 1:
        raise ValueError("num_pages должен быть положительным целым числом (>= 1)")

    logging.info(f"Начинаем парсинг {num_pages} страниц (headless={headless})")
    driver = init_driver(headless=headless)
    all_movies = []

    try:
        for page in range(1, num_pages + 1):
            url = f"https://www.filmpro.ru/movies/top?page={page}"
            logging.info(f"Загружается страница {page}: {url}")
            driver.get(url)
            time.sleep(delay)

            # === ПОВТОРНЫЕ ПОПЫТКИ ПРИ ОТСУТСТВИИ КАРТОЧЕК ===
            retry_attempts = 2
            movie_cards = []
            for attempt in range(retry_attempts + 1):
                movie_cards = driver.find_elements(By.CLASS_NAME, "b-maintopfilms__item")
                if movie_cards:
                    break
                logging.warning(f"Карточки фильмов не найдены (попытка {attempt + 1}/{retry_attempts + 1}). Повтор через 5 секунд...")
                time.sleep(5)

            logging.info(f"Найдено карточек фильмов: {len(movie_cards)}")

            for card in movie_cards:
                try:
                    link_elem = card.find_element(By.CLASS_NAME, "b-maintopfilms__titlelink")
                    title = link_elem.text.strip()
                    href = link_elem.get_attribute("href")
                    all_movies.append({"title": title, "url": href})
                    logging.debug(f"→ {title} | {href}")
                except NoSuchElementException:
                    logging.warning("Не удалось найти ссылку на фильм внутри карточки")
    finally:
        driver.quit()
        logging.info("Браузер закрыт")

    logging.info(f"Всего фильмов собрано: {len(all_movies)}")

    # Автоматическое сохранение
    save_movies_list_to_json(all_movies)

    return all_movies


def scrape_movie_details(json_input: str = "movies_list.json",
                         output_file: str = "movie_details.json",
                         delay: float = 1.0,
                         headless: bool = True) -> None:
    """
    Парсит страницы каждого фильма из JSON и сохраняет детальную информацию.

    :param json_input: имя входного файла со списком фильмов (в data/raw)
    :param output_file: имя выходного JSON (в data/raw)
    :param delay: задержка между фильмами
    :param headless: использовать headless режим браузера
    """
    input_path = RAW_DATA_PATH / json_input
    if not input_path.exists():
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        movies = json.load(f)

    logging.info(f"Загружено фильмов: {len(movies)}")

    driver = init_driver(headless=headless)
    detailed_movies = []

    try:
        for idx, movie in enumerate(movies, start=1):
            url = movie["url"]
            title = movie["title"]
            logging.info(f"[{idx}/{len(movies)}] Парсинг: {title} | {url}")

            result = {
                "title": title,
                "url": url,
                "rating": None,
                "votes": None,
                "details": {}
            }

            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    driver.get(url)
                    time.sleep(delay)

                    # --- Парсинг рейтинга и голосов ---
                    try:
                        stats_block = driver.find_element(By.CLASS_NAME, "b-film-rate__stats")
                        h3 = stats_block.find_element(By.TAG_NAME, "h3")
                        rating_text = h3.text.strip()

                        match = re.match(r"([\d.]+)\s*\((\d+)", rating_text)
                        if match:
                            result["rating"] = match.group(1)
                            result["votes"] = match.group(2)
                        else:
                            result["rating"] = rating_text
                            logging.warning(f"Не удалось извлечь рейтинг/голоса из: {rating_text}")
                    except NoSuchElementException:
                        logging.debug("Рейтинг не найден")

                    # --- Парсинг характеристик ---
                    try:
                        info_items = driver.find_elements(By.CLASS_NAME, "b-film-imprint__item")
                        for item in info_items:
                            try:
                                key = item.find_element(By.CLASS_NAME, "b-film-imprint__var").text.strip(": \n")
                                val = item.find_element(By.CLASS_NAME, "b-film-imprint__val").text.strip()
                                result["details"][key] = val
                            except NoSuchElementException:
                                continue
                    except NoSuchElementException:
                        logging.warning("Блок характеристик не найден")

                    break  # успех — выходим из попыток

                except Exception as e:
                    logging.warning(f"Ошибка при парсинге ({attempt + 1}/{max_attempts}): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                    else:
                        logging.error("Не удалось получить данные после 3 попыток")

            detailed_movies.append(result)

    finally:
        driver.quit()
        logging.info("Браузер закрыт")

    # --- Сохраняем результат в data/raw ---
    raw_path = PROJECT_ROOT / "data" / "raw"
    raw_path.mkdir(parents=True, exist_ok=True)
    output_path = raw_path / output_file

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_movies, f, ensure_ascii=False, indent=2)

    logging.info(f"Сохранено {len(detailed_movies)} фильмов в {output_path}")


def save_movies_list_to_json(movies: List[Dict[str, str]], filename: str = "movies_list.json") -> None:
    """
    Сохраняет список фильмов (название + ссылка) в JSON-файл.

    :param movies: список словарей с фильмами
    :param filename: имя выходного файла
    """
    filepath = RAW_DATA_PATH / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    logging.info(f"Сохранено {len(movies)} фильмов в {filepath}")
