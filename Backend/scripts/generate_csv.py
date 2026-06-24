import csv
import random

# random.seed(42)  # для воспроизводимости

# Федеральные округа и субъекты РФ
regions = {
    "Центральный ФО": ["г. Москва", "Московская обл.", "Тверская обл."],
    "Северо-Западный ФО": [
        "Мурманская обл.",
        "Ленинградская обл.",
        "Архангельская обл.",
    ],
    "Приволжский ФО": ["Республика Татарстан", "Нижегородская обл.", "Самарская обл."],
    "Уральский ФО": ["Свердловская обл.", "Челябинская обл.", "Тюменская обл."],
    "Сибирский ФО": ["Новосибирская обл.", "Красноярский край", "Иркутская обл."],
}

# Отчётные периоды
periods = ["Январь 25", "Февраль 25", "Март 25", "Апрель 25", "Май 25"]

# Показатели и их единицы измерения
indicators = [
    ("Доход банка", "Руб."),
    ("Средний тариф банка", "%"),
    ("Объем транзакций", "Руб."),
    ("Средняя стоимость обеда", "Руб."),
    ("Количество клиентов", "Кл."),
    ("Общее количество людей в ВУЗе", "Кл."),
    ("Доля людей, питающихся в столовой", "%"),
    ("Студенты", "Кл."),
    ("Административный персонал", "Кл."),
]


def generate_value(indicator_name):
    match (indicator_name):
        case "Доход банка":
            return round(random.uniform(10000, 100000), 1)
        case "Средний тариф банка":
            return round(random.uniform(1, 10), 1)
        case "Объем транзакций":
            return round(random.uniform(100000, 1000000), 1)
        case "Средняя стоимость обеда":
            return round(random.uniform(150, 400), 1)
        case "Количество клиентов":
            return random.randint(500, 5000)
        case "Общее количество людей в ВУЗе":
            return random.randint(1000, 10000)
        case "Доля людей, питающихся в столовой":
            return random.randint(30, 90)
        case "Студенты":
            return random.randint(800, 8000)
        case "Административный персонал":
            return random.randint(50, 500)
        case _:
            return 0


# Формируем все возможные комбинации
all_rows = []
for district, subjects in regions.items():
    for subject in subjects:
        for period in periods:
            for indicator_name, measure in indicators:
                all_rows.append(
                    {
                        "Отчетный период": period,
                        "Федеральный округ РФ": district,
                        "Субъект РФ": subject,
                        "Показатель": indicator_name,
                        "Мера измерения": measure,
                        "Значение": generate_value(indicator_name),
                    }
                )

# Перемешиваем и берем первые 500 строк
random.shuffle(all_rows)
selected_rows = all_rows[:500]

# Записываем в CSV
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "Отчетный период",
        "Федеральный округ РФ",
        "Субъект РФ",
        "Показатель",
        "Мера измерения",
        "Значение",
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    writer.writerows(selected_rows)

print("CSV-файл 'data.csv' успешно создан с 500 строками.")
