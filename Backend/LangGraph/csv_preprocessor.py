from __future__ import annotations

import json
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = [
    "Отчетный период",
    "Федеральный округ РФ",
    "Субъект РФ",
    "Показатель",
    "Мера измерения",
    "Значение",
]

MONTHS_RU = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
}

# Pie-диаграмма читаема, только пока категорий немного.
PIE_MAX_CATEGORIES = 8
PIE_MIN_CATEGORIES = 2

# Line имеет смысл, только если есть хотя бы 2 точки во времени (может выкрутим на 1, не знаю).
LINE_MIN_PERIODS = 2

# Для bar достаточно 2 сопоставимых значений хоть по какому-то измерению (в целом тоже можем выкрутить на 1).
BAR_MIN_CATEGORIES = 2

# Если строк для одной таблицы больше этого - на слайде она не влезет как есть, нужно резать.
TABLE_ROWS_COMFORTABLE_LIMIT = 15


# ---------------------------------------------------------------------------
# Утилиты парсинга
# ---------------------------------------------------------------------------


def parse_period(period_str: str) -> tuple[int, int] | None:
    """
    Парсит период вида 'Январь 25' или 'Январь 2025' в (год, месяц) для сортировки.
    Возвращает None, если формат не распознан (например, квартал/год без месяца) -
    в этом случае период всё равно останется в данных, просто не будет
    хронологически упорядочен.
    """
    if not isinstance(period_str, str):
        return None
    parts = period_str.strip().split()
    if len(parts) < 2:
        return None
    month_name, year_raw = parts[0].lower(), parts[1]
    month = MONTHS_RU.get(month_name)
    if month is None:
        return None
    try:
        year = int(year_raw)
    except ValueError:
        return None
    if year < 100:
        year += 2000
    return (year, month)


def load_csv(path: str) -> pd.DataFrame:
    """
    Загружает CSV с автоопределением разделителя (',' или ';') (я замучался чутка с этим, нейронка так подсказала)
    Приводит колонку 'Значение' к float, поддерживая запятую как десятичный разделитель.
    """
    df = pd.read_csv(path, sep=None, engine="python", dtype=str)
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"В CSV не хватает обязательных колонок: {missing}. "
            f"Найденные колонки: {list(df.columns)}"
        )

    for col in REQUIRED_COLUMNS:
        if col != "Значение":
            df[col] = df[col].astype(str).str.strip()

    # Числа с запятой как десятичным разделителем -> точка
    df["Значение_raw"] = df["Значение"]
    df["Значение"] = (
        df["Значение"].astype(str).str.strip().str.replace(",", ".", regex=False)
    )
    df["Значение"] = pd.to_numeric(df["Значение"], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Статистика и флаги по одному показателю
# ---------------------------------------------------------------------------


def _round(x: float, ndigits: int = 4) -> float:
    return round(float(x), ndigits)


def analyze_metric(metric_name: str, df_metric: pd.DataFrame) -> dict[str, Any]:
    notes: list[str] = []

    units = df_metric["Мера измерения"].dropna().unique().tolist()
    unit = units[0] if units else None
    if len(units) > 1:
        notes.append(
            f"У показателя встречается несколько единиц измерения: {units}. "
            f"Взята первая: '{unit}'. Стоит проверить исходные данные."
        )

    total_rows = len(df_metric)
    values = df_metric["Значение"].dropna()
    invalid_count = total_rows - len(values)
    if invalid_count > 0:
        notes.append(
            f"Не удалось распарсить как число {invalid_count} значений из {total_rows}."
        )

    has_negative = bool((values < 0).any()) if len(values) else False

    # Периоды
    raw_periods = df_metric["Отчетный период"].unique().tolist()
    parsed = {p: parse_period(p) for p in raw_periods}
    periods_sorted = sorted(
        raw_periods,
        key=lambda p: (parsed[p] is None, parsed[p] if parsed[p] else (0, 0)),
    )
    num_periods = len(raw_periods)

    subjects = df_metric["Субъект РФ"].unique().tolist()
    num_subjects = len(subjects)

    districts = df_metric["Федеральный округ РФ"].unique().tolist()
    num_districts = len(districts)

    # --- статистика значений ---
    if len(values) > 0:
        value_stats = {
            "count": int(len(values)),
            "min": _round(values.min()),
            "max": _round(values.max()),
            # "mean": _round(values.mean()),
            # "sum": _round(values.sum()),
            # "std": _round(values.std()) if len(values) > 1 else 0.0,
        }
    else:
        value_stats = {
            "count": 0,
            "min": None,
            "max": None,
            # "mean": None,
            # "sum": None,
            # "std": None,
        }
        notes.append("Нет валидных числовых значений для этого показателя.")

    # --- флаг LINE: нужно хотя бы LINE_MIN_PERIODS периодов ---
    can_line = num_periods >= LINE_MIN_PERIODS
    if can_line and num_subjects > 1:
        notes.append(
            "line_chart: по времени данные есть по нескольким субъектам РФ, стоит"
            " зафиксировать субъект/округ либо агрегировать"
        )

    # --- флаг BAR: нужно >= BAR_MIN_CATEGORIES сопоставимых категории по любому измерению ---
    can_bar = (num_periods >= BAR_MIN_CATEGORIES) or (
        num_subjects >= BAR_MIN_CATEGORIES
    )

    # --- флаг PIE: ищем "срез", где для одного периода есть несколько субъектов
    #     без отрицательных значений и с разумным числом категорий ---
    can_pie = False
    pie_reference_period = None
    pie_num_categories = 0

    if not has_negative and len(values) > 0:
        # группируем по периоду и считаем, сколько субъектов есть в каждом периоде
        counts_by_period = (
            df_metric.dropna(subset=["Значение"])
            .groupby("Отчетный период")["Субъект РФ"]
            .nunique()
        )
        if len(counts_by_period) > 0:
            best_period = counts_by_period.idxmax()
            best_count = int(counts_by_period.max())
            if PIE_MIN_CATEGORIES <= best_count <= PIE_MAX_CATEGORIES:
                can_pie = True
                pie_reference_period = best_period
                pie_num_categories = best_count
            elif best_count > PIE_MAX_CATEGORIES:
                notes.append(
                    f"Категорий слишком много ({best_count} > {PIE_MAX_CATEGORIES}) - PIE нечитаемо."
                )
    elif has_negative:
        notes.append("Есть отрицательные значения - pie_chart исключена.")

    # --- флаг TABLE: почти всегда можно, но с заметкой про объём ---
    can_table = total_rows > 0
    table_recommended_pagination = total_rows > TABLE_ROWS_COMFORTABLE_LIMIT
    if table_recommended_pagination:
        notes.append(
            f"Строк для таблицы много ({total_rows} > {TABLE_ROWS_COMFORTABLE_LIMIT}), "
            f"рассмотреть агрегацию или разбивку на несколько таблиц."
        )

    return {
        "name": metric_name,
        "unit": unit,
        "total_rows": total_rows,
        "num_periods": num_periods,
        # "periods": periods_sorted,
        "num_subjects": num_subjects,
        # "subjects": subjects,
        "num_federal_districts": num_districts,
        # "federal_districts": districts,
        "has_negative": has_negative,
        "value_stats": value_stats,
        "chart_flags": {
            "line": can_line,
            "bar": can_bar,
            "pie": can_pie,
            "table": can_table,
        },
        "pie_details": (
            {
                "reference_period": pie_reference_period,
                "num_categories": pie_num_categories,
            }
            if can_pie
            else None
        ),
        "table_details": {
            "rows": total_rows,
            "recommend_pagination_or_aggregation": table_recommended_pagination,
        },
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Общий анализ всего файла
# ---------------------------------------------------------------------------


def analyze(df: pd.DataFrame) -> dict[str, Any]:
    unique_periods_raw = df["Отчетный период"].unique().tolist()
    parsed = {p: parse_period(p) for p in unique_periods_raw}
    unique_periods_sorted = sorted(
        unique_periods_raw,
        key=lambda p: (parsed[p] is None, parsed[p] if parsed[p] else (0, 0)),
    )

    unique_districts = df["Федеральный округ РФ"].unique().tolist()
    unique_subjects = df["Субъект РФ"].unique().tolist()
    unique_metrics = df["Показатель"].unique().tolist()
    unique_units = df["Мера измерения"].unique().tolist()

    metrics_report = {}
    for metric_name in unique_metrics:
        df_metric = df[df["Показатель"] == metric_name]
        metrics_report[metric_name] = analyze_metric(metric_name, df_metric)

    result = {
        "summary": {
            "total_rows": int(len(df)),
            "unique_periods": unique_periods_sorted,
            "num_periods": len(unique_periods_sorted),
            "unique_federal_districts": unique_districts,
            "unique_subjects": unique_subjects,
            "unique_metrics": unique_metrics,
            "unique_units": unique_units,
            "is_multi_period": len(unique_periods_sorted) > 1,
            "is_multi_region": len(unique_subjects) > 1,
            "is_multi_metric": len(unique_metrics) > 1,
        },
        "metrics": metrics_report,
    }
    return result


def process_csv(input_csv: str, output_json: str) -> None:
    """
    Читает input_csv, считает статистику и флаги графиков, сохраняет в output_json.
    """
    df = load_csv(input_csv)

    # Вот эта переменная - и есть вся структура (обычный dict).
    result: dict[str, Any] = analyze(df)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def convert_analyze_result_to_message(result: dict[str, Any]) -> str:
    """Конвертирует результат analyze() в текстовое сообщение для LLM."""
    return str(result)


if __name__ == "__main__":
    process_csv("test_data.csv", "result.json")
