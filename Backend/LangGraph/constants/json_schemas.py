JSON_SCHEMA_DRAFT = {
    "$defs": {
        "DataBinding": {
            "description": "Описание запроса к данным. Resolver исполняет его как запрос к "
            "pandas DataFrame и строит нужный data-блок "
            "(TextData/TableData/ChartData/WaterfallData).",
            "properties": {
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
                "data_description": {
                    "description": "Описание объекта и "
                    "данных, которые в нем "
                    "записаны, с указанием "
                    "параметров и названием "
                    "столбцов/параметров.",
                    "type": "string",
                },
                "title": {
                    "description": "Название DATA-объекта слайда " "(таблица/график).",
                    "type": "string",
                },
            },
            "required": ["chart_type"],
            "type": "object",
        },
        "DraftObject": {
            "description": "Один объект на слайде. Нейронка указывает только тип, начальную "
            "ячейку и откуда брать данные - финальные размеры считает Resolver.",
            "else": {"required": ["data_binding"]},
            "if": {"properties": {"type": {"const": "TEXT"}}},
            "properties": {
                "cell_pos": {
                    "description": "Стартовая позиция объекта в "
                    "фиксированной сетке 4x3 (4 "
                    "колонки, 3 строки).",
                    "properties": {
                        "x": {
                            "description": "Колонка старта (0 - крайняя левая, 3 - крайняя правая).",
                            "maximum": 3,
                            "minimum": 0,
                            "type": "integer",
                        },
                        "y": {
                            "description": "Строка старта (0 - верхняя, 2 - нижняя).",
                            "maximum": 2,
                            "minimum": 0,
                            "type": "integer",
                        },
                    },
                    "required": ["x", "y"],
                    "type": "object",
                },
                "data_binding": {
                    "$ref": "#/$defs/DataBinding",
                    "description": "Только для type=TABLE или "
                    "CHART. Семантическое "
                    "описание того, какие данные "
                    "нужно извлечь из исходной "
                    "CSV. Реальные числа "
                    "подставятся при конвертации "
                    "в Final JSON (нейронкой или "
                    "Resolver'ом).",
                },
                "object_id": {
                    "description": "Уникальный ID объекта. "
                    "Генерировать как 'obj_' + 12 "
                    "hex-символов",
                    "type": "string",
                },
                "span": {
                    "description": "Размер объекта в ячейках сетки, "
                    "считая от cell_pos.",
                    "properties": {
                        "x": {
                            "default": 1,
                            "description": "Сколько "
                            "колонок "
                            "занимает "
                            "объект (1 "
                            "= одна "
                            "ячейка по "
                            "горизонтали).",
                            "maximum": 4,
                            "minimum": 1,
                            "type": "integer",
                        },
                        "y": {
                            "default": 1,
                            "description": "Сколько "
                            "строк "
                            "занимает "
                            "объект (1 "
                            "= одна "
                            "ячейка по "
                            "вертикали).",
                            "maximum": 3,
                            "minimum": 1,
                            "type": "integer",
                        },
                    },
                    "type": "object",
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
            "required": ["object_id", "type", "cell_pos", "span"],
            "then": {"required": ["text"]},
            "type": "object",
        },
    },
    "$id": "https://example.com/schemas/presentation_draft_slide.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Описание одного слайда-черновика. Нейронка 2 генерирует объекты по этой схеме. Слайды одного "
    "показателя (indicator) Resolver затем объединяет в финальный JSON по порядку. Только ссылки на "
    "источник через data_binding.",
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
                    "в шапке - отдельная зона над сеткой, "
                    "не входит в ячейки",
                    "type": "string",
                },
            },
            "required": ["slide_id", "indicator", "title"],
            "type": "object",
        },
        "objects": {
            "description": "Объекты на слайде. Каждый занимает одну или более ячеек "
            "фиксированной сетки 4x3. Resolver сам вычислит финальные размеры "
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


if __name__ == "__main__":
    from jsf import JSF
    from pprint import pformat

    faker = JSF(JSON_SCHEMA_DRAFT)
    example = faker.generate()

    py_dict_string = pformat(example, indent=4, width=120)

    with open("JSON_SHEMA_EXAMPLE.py", "w+", encoding="utf-8") as py_file:
        py_file.write(f"JSON_SCHEMA = {py_dict_string}\n")
