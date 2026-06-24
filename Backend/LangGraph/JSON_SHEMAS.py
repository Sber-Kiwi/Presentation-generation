JSON_SCHEMA_DRAFT = {
    "$defs": {
        "DataBinding": {
            "description": "Описание запроса к данным. Resolver исполняет его как запрос к "
            "pandas DataFrame и строит нужный data-блок "
            "(TextData/TableData/ChartData/WaterfallData).",
            "properties": {
                "aggregation": {
                    "description": "Агрегация значений внутри "
                    "группы. none — без агрегации "
                    "(берём строки как есть)",
                    "enum": ["sum", "mean", "last", "none"],
                    "type": "string",
                },
                "chart_type": {
                    "description": "Определяет тип визуализации и "
                    "соответствующий data-блок в "
                    "Final JSON: TABLE → TableData, "
                    "WATERFALL → WaterfallData, "
                    "LINE/BAR/PIE → ChartData с "
                    "соответствующим chart_type",
                    "enum": ["LINE", "BAR", "PIE", "WATERFALL", "TABLE"],
                    "type": "string",
                },
                "filters": {
                    "additionalProperties": True,
                    "description": "Фильтры по строкам. Ключ — имя "
                    "колонки, значение — одно значение "
                    "или массив. Например: "
                    '{"Федеральный округ РФ": '
                    '"Северо-Западный ФО", '
                    '"Показатель": "Доход банка"}',
                    "type": "object",
                },
                "group_by": {
                    "description": "Колонки для группировки "
                    "(например ['Отчетный период'] "
                    "для временного ряда)",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "source_columns": {
                    "description": "Колонки CSV, которые нужны "
                    "для построения (например "
                    "['Отчетный период', "
                    "'Значение', "
                    "'Показатель']). Если пусто "
                    "— Resolver берёт все "
                    "колонки.",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "top_n": {
                    "description": "Ограничить вывод топ-N строками по "
                    "значению. null — без ограничений. "
                    "Актуально для TABLE и WATERFALL с "
                    "большим числом статей.",
                    "type": ["integer", "null"],
                },
            },
            "required": ["chart_type"],
            "type": "object",
        },
        "DraftObject": {
            "description": "Один объект на слайде. Нейронка указывает только тип, начальную "
            "ячейку и откуда брать данные — финальные размеры считает Resolver.",
            "else": {"required": ["data_binding"]},
            "if": {"properties": {"type": {"const": "TEXT"}}},
            "properties": {
                "cell": {
                    "description": "Стартовая ячейка объекта в "
                    "фиксированной сетке 3x3. Нумерация:\n"
                    "  0 | 1 | 2\n"
                    "  3 | 4 | 5\n"
                    "  6 | 7 | 8\n"
                    "Если объект единственный на слайде — "
                    "Resolver растягивает его на весь "
                    "контентный блок. Resolver "
                    "автоматически заполняет все смежные "
                    "свободные ячейки согласно span_hint.",
                    "maximum": 8,
                    "minimum": 0,
                    "type": "integer",
                },
                "data_binding": {
                    "$ref": "#/$defs/DataBinding",
                    "description": "Только для type=TABLE или "
                    "CHART. Семантическое "
                    "описание того, какие данные "
                    "нужно извлечь из исходной "
                    "CSV. Реальные числа Resolver "
                    "подставит при конвертации в "
                    "Final JSON.",
                },
                "markdown": {"default": True, "type": "boolean"},
                "object_id": {
                    "description": "Уникальный ID объекта. "
                    "Генерировать как 'obj_' + 12 "
                    "hex-символов",
                    "type": "string",
                },
                "span_hint": {
                    "default": "auto",
                    "description": "Подсказка Resolver'у о "
                    "приоритете расширения объекта "
                    "на свободные ячейки:\n"
                    "  auto — алгоритм решает сам "
                    "(по умолчанию)\n"
                    "  horizontal — расширяться в "
                    "первую очередь по строке "
                    "(типично для LINE/BAR "
                    "графиков)\n"
                    "  vertical — расширяться по "
                    "столбцу (типично для текстовых "
                    "колонок-комментариев)\n"
                    "  full — занять всё доступное "
                    "пространство независимо от "
                    "формы",
                    "enum": ["auto", "horizontal", "vertical", "full"],
                    "type": "string",
                },
                "text": {
                    "description": "Только для type=TEXT. Аналитический "
                    "комментарий или описание, "
                    "генерируемый нейронкой. Поддерживает "
                    "markdown.",
                    "type": "string",
                },
                "type": {"enum": ["TEXT", "TABLE", "CHART"], "type": "string"},
            },
            "required": ["object_id", "type", "cell"],
            "then": {"required": ["text"]},
            "type": "object",
        },
    },
    "$id": "https://example.com/schemas/presentation_draft_slide.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Описание ОДНОГО слайда-черновика. Нейронка 2 генерирует по одному такому объекту за вызов. Слайды "
    "одного показателя (indicator) Resolver затем объединяет в финальный JSON по порядку. Реальных "
    "данных (чисел) нет — только ссылки на источник через data_binding.",
    "properties": {
        "meta": {
            "properties": {
                "indicator": {
                    "description": "Имя показателя по которому "
                    "строятся слайды. По нему Resolver "
                    "группирует и сортирует слайды "
                    "одной метрики перед сборкой "
                    "финала",
                    "type": "string",
                },
                "notes": {"default": None, "type": ["string", "null"]},
                "slide_id": {
                    "description": "Уникальный ID слайда. Генерировать "
                    "как 'sld_' + 12 hex-символов",
                    "type": "string",
                },
                "title": {
                    "description": "Заголовок слайда. Всегда отображается "
                    "в шапке — отдельная зона над сеткой, "
                    "не входит в ячейки",
                    "type": "string",
                },
            },
            "required": ["slide_id", "indicator", "title"],
            "type": "object",
        },
        "objects": {
            "description": "Объекты на слайде. Каждый занимает одну или более ячеек "
            "фиксированной сетки 3x3. Resolver сам вычислит финальные размеры "
            "и позиции исходя из занятых и свободных ячеек.",
            "items": {"$ref": "#/$defs/DraftObject"},
            "minItems": 1,
            "type": "array",
        },
    },
    "required": ["meta", "objects"],
    "title": "PresentationDraftSlide",
    "type": "object",
}


JSON_SCHEMA_FINAL = {
    "$defs": {
        "ChartData": {
            "properties": {
                "chart_type": {"enum": ["LINE", "BAR", "PIE"], "type": "string"},
                "kind": {"const": "ChartData"},
                "label": {"type": ["string", "null"]},
                "series": {
                    "items": {
                        "properties": {
                            "color": {"type": "string"},
                            "data": {
                                "items": {
                                    "properties": {
                                        "x": {"type": "string"},
                                        "y": {"type": "number"},
                                    },
                                    "required": ["x", "y"],
                                    "type": "object",
                                },
                                "type": "array",
                            },
                            "unit": {"type": "string"},
                        },
                        "required": ["data", "unit", "color"],
                        "type": "object",
                    },
                    "type": "array",
                },
                "title": {"type": "string"},
            },
            "required": ["kind", "title", "chart_type", "label", "series"],
            "type": "object",
        },
        "FinalObject": {
            "description": "Объект на слайде с явной абсолютной позицией, вычисленной "
            "Resolver'ом.",
            "properties": {
                "data": {
                    "oneOf": [
                        {"$ref": "#/$defs/TextData"},
                        {"$ref": "#/$defs/TableData"},
                        {"$ref": "#/$defs/ChartData"},
                        {"$ref": "#/$defs/WaterfallData"},
                    ]
                },
                "object_id": {
                    "description": "Сохраняется из черновика",
                    "type": "string",
                },
                "position": {
                    "height": {
                        "description": "Высота объекта, " "дюймы",
                        "type": "number",
                    },
                    "width": {
                        "description": "Ширина объекта, " "дюймы",
                        "type": "number",
                    },
                    "x": {
                        "description": "Отступ от левого края " "слайда, дюймы",
                        "type": "number",
                    },
                    "y": {
                        "description": "Отступ от верхнего края "
                        "слайда (ниже "
                        "заголовка), дюймы",
                        "type": "number",
                    },
                },
                "type": {"enum": ["TEXT", "TABLE", "CHART"], "type": "string"},
            },
            "required": ["object_id", "type", "position", "data"],
            "type": "object",
        },
        "Slide": {
            "properties": {
                "meta": {
                    "properties": {
                        "indicator": {
                            "description": "Сохраняется "
                            "из "
                            "черновика. "
                            "Генератором "
                            "pptx не "
                            "используется.",
                            "type": "string",
                        },
                        "notes": {"default": None, "type": ["string", "null"]},
                        "number": {
                            "description": "Порядковый "
                            "номер "
                            "слайда в "
                            "финальной "
                            "презентации, "
                            "проставляется "
                            "Resolver'ом",
                            "type": "integer",
                        },
                        "slide_id": {
                            "description": "Сохраняется " "из " "черновика",
                            "type": "string",
                        },
                        "title": {
                            "description": "Заголовок " "слайда",
                            "type": "string",
                        },
                    },
                    "required": ["slide_id", "title", "number", "indicator"],
                    "type": "object",
                },
                "objects": {
                    "items": {"$ref": "#/$defs/FinalObject"},
                    "minItems": 1,
                    "type": "array",
                },
            },
            "required": ["meta", "objects"],
            "type": "object",
        },
        "TableData": {
            "properties": {
                "caption": {"type": ["string", "null"]},
                "headers": {"items": {"type": "string"}, "type": "array"},
                "kind": {"const": "TableData"},
                "rows": {"items": {"type": "array"}, "type": "array"},
            },
            "required": ["kind", "headers", "rows", "caption"],
            "type": "object",
        },
        "TextData": {
            "properties": {
                "kind": {"const": "TextData"},
                "markdown": {"default": True, "type": "boolean"},
                "text": {"type": "string"},
            },
            "required": ["kind", "text"],
            "type": "object",
        },
        "WaterfallData": {
            "properties": {
                "data": {
                    "items": {
                        "properties": {
                            "delta": {"type": "number"},
                            "name": {"type": "string"},
                            "plan": {"type": "number"},
                            "text": {"type": "string"},
                            "type": {
                                "enum": ["START", "COMMON", "END"],
                                "type": "string",
                            },
                        },
                        "required": ["name", "plan", "delta", "type", "text"],
                        "type": "object",
                    },
                    "type": "array",
                },
                "kind": {"const": "WaterfallData"},
            },
            "required": ["kind", "data"],
            "type": "object",
        },
    },
    "$id": "https://example.com/schemas/presentation_final.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Финальный JSON для генерации pptx. Содержит всю презентацию со всеми слайдами. Блок data "
    "(TextData/TableData/ChartData/WaterfallData) переносится из исходных данных без изменений.",
    "properties": {
        "meta": {
            "properties": {
                "common_slide_title": {
                    "description": "Общий надзаголовок, "
                    "отображаемый на всех "
                    "слайдах (например, "
                    "название "
                    "банка/подразделения)",
                    "type": "string",
                },
                "title": {
                    "description": "Имя файла или заголовок всей " "презентации",
                    "type": "string",
                },
            },
            "required": ["title"],
            "type": "object",
        },
        "slides": {"items": {"$ref": "#/$defs/Slide"}, "minItems": 1, "type": "array"},
    },
    "required": ["meta", "slides"],
    "title": "PresentationFinal",
    "type": "object",
}
