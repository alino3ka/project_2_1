import json
from pathlib import Path
from collections import Counter

def inspect_details(json_path: Path):
    """
    Анализирует блок 'details' в movie_details.json и показывает уникальные ключи с примерами и частотой.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"Файл не найден: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        movies = json.load(f)

    all_keys = Counter()
    examples = {}

    for movie in movies:
        details = movie.get("details", {})
        for k, v in details.items():
            all_keys[k] += 1
            if k not in examples:
                examples[k] = v

    print("Поле".ljust(30), "Пример значения".ljust(40), "Встречаемость")
    print("-" * 90)
    for key, count in all_keys.most_common():
        example = examples[key]
        shortened = (example[:37] + "...") if len(example) > 40 else example
        print(f"{key.ljust(30)} {shortened.ljust(40)} {count}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    path_to_json = project_root / "data" / "raw" / "movie_details.json"
    inspect_details(path_to_json)
