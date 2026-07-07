import re
import sqlparse
from typing import Annotated
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId, BaseTool
from langchain_core.messages import ToolMessage
from copy import deepcopy

import settings
from models import (
    HORIZONTAL_SIZE,
    VERTICAL_SIZE,
    DraftSlide,
    ObjectPosition,
    ObjectType,
    ObjectSpan,
    SlideItem,
)
from constants.mapping import ALLOWED_OBJECT_TRANSFORMATION
from state import EditAgentState


@tool
def sql_query_dataframe(question: str) -> str:
    """Отвечает на вопрос о данных, выполняя SQL-запрос к таблице sql_data.

    Преобразует вопрос пользователя, заданный на естественном языке, в
    SQL-запрос с единственной операцией SELECT, выполняет его на таблице
    sql_data и возвращает результат в виде CSV (не более 50 строк).

    Args:
        question: Вопрос о данных на естественном языке -- например, запрос
            на фильтрацию, агрегацию, сортировку или выборку значений из
            таблицы sql_data. Схема таблицы (список колонок) передаётся
            автоматически при генерации SQL-запроса.

    Вызывай этот инструмент только когда для ответа пользователю требуется
    обратиться к данным таблицы sql_data (например, посчитать показатель,
    получить конкретные значения или отфильтровать строки). Разрешены
    только запросы SELECT -- любые попытки изменения данных (INSERT, UPDATE,
    DELETE, DROP, ALTER, TRUNCATE, CREATE, MERGE) будут отклонены. Если
    соединение с данными не настроено, запрос некорректен или не возвращает
    результат, инструмент вернёт соответствующее текстовое сообщение об
    ошибке вместо CSV.
    """
    if settings.sql_data is None or settings.con is None:
        return "SQL данные или соединение не определены, запрос невозможен."

    sql_data = settings.sql_data

    sql_prompt = f"""
Ты -- SQL-генератор для анализа данных.
Разрешен только один запрос SELECT.

Схема таблицы sql_data:
{list(settings.sql_data.columns)}

Вопрос:
{question}

Ответь строго одним SQL-запросом.
Запрещено:
- писать пояснения;
- использовать markdown;
- использовать несколько запросов;
- использовать INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, MERGE.

Если для ответа нужен фильтр, агрегация или сортировка -- используй только SELECT."""

    sql_request = settings.call_llm_sync(
        llm=settings.thinking_llm, messages=sql_prompt
    ).content.strip()

    # Удаляем комментарии и лишние символы
    sql_request = re.sub(r"--.*?$", "", sql_request, flags=re.MULTILINE)
    sql_request = re.sub(r"/\*.*?\*/", "", sql_request, flags=re.DOTALL)
    sql_request = sql_request.strip()

    # Извлекаем часть с SELECT, если есть лишний текст
    match = re.search(r"(SELECT\s+.*?)(;|$)", sql_request, re.IGNORECASE | re.DOTALL)
    if not match:
        return "Не удалось найти SELECT в запросе."
    sql_request = match.group(1).strip()

    # Проверяем через sqlparse, что это именно SELECT
    parsed = sqlparse.parse(sql_request)
    if not parsed:
        return "Не удалось разобрать SQL-запрос."
    stmt = parsed[0]
    if not stmt.get_type() == "SELECT":
        return f"Разрешены только SELECT-запросы, получен тип: {stmt.get_type()}"

    # Добавляем LIMIT, если его нет
    if not re.search(r"\bLIMIT\b", sql_request, re.IGNORECASE):
        sql_request += " LIMIT 50"

    # Выполняем запрос
    try:
        result = settings.con.execute(sql_request).df()
    except Exception as e:
        return f"Ошибка выполнения SQL: {e}"

    if result is None:
        return "Запрос выполнен, но результат равен None."
    if result.empty:
        return "Запрос выполнен, но данные не найдены (пустой результат)."

    return result.head(50).to_csv(index=False)


@tool
def change_object_pos(
    originalPosition: ObjectPosition,
    newPosition: ObjectPosition,
    newSize: ObjectSpan | None = None,
    state: Annotated[EditAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Изменяет позицию и/или размер объекта на слайде в пределах сетки 4x3.

    Найди на текущем слайде объект, точно соответствующий originalPosition,
    и перемести его в newPosition. Если указан newSize, также изменяет размер
    объекта; если newSize не указан, размер объекта остаётся прежним.

    Args:
        originalPosition: Текущая позиция объекта на слайде (координаты x, y
            в сетке 4x3). Должна точно совпадать с позицией существующего
            объекта на слайде.
        newPosition: Новая позиция, в которую нужно переместить объект.
            Должна укладываться в границы сетки 4x3 с учётом размера объекта.
        newSize: Новый размер объекта (ширина, высота в ячейках сетки).
            Необязательный параметр -- если не указан, используется текущий
            размер объекта.

    Вызывай этот инструмент только когда запрос пользователя явно требует
    переместить объект и/или изменить его размер. Если объект с указанной
    originalPosition не найден на слайде, изменение не будет применено.
    """
    try:
        slide = deepcopy(state["current_slide"])

        obj = _find_object(slide, originalPosition)

        if newSize is not None:
            obj.span = newSize
        obj.position = newPosition

        _validate_slide_no_collisions(slide)

        return Command(
            update={
                "current_slide": slide,
                "slide_changed": True,
                "messages": [
                    ToolMessage(
                        content=f"Moved object to {newPosition}, size {newSize}.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Change failed: {e}", tool_call_id=tool_call_id
                    )
                ],
            }
        )


@tool
def change_object_type(
    originalType: ObjectType,
    newType: ObjectType,
    originalPosition: ObjectPosition,
    state: Annotated[EditAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Изменяет тип объекта на слайде на другой разрешённый тип.

    Найди на текущем слайде объект в позиции originalPosition с типом
    originalType и заменяет его тип на newType. Смена типа допускается
    только если newType входит в список разрешённых трансформаций для
    originalType (ALLOWED_OBJECT_TRANSFORMATION).

    Аргументы:
        originalType: Текущий тип объекта (например, текст, изображение,
            диаграмма и т.д.), который требуется изменить.
        newType: Новый тип, в который нужно преобразовать объект. Должен
            входить в список допустимых трансформаций для originalType.
        originalPosition: Позиция объекта на слайде (координаты x, y в
            сетке 4x3), используемая для точного определения нужного
            объекта среди прочих на слайде.

    Вызывай этот инструмент только когда запрос пользователя явно требует
    сменить тип объекта. Если трансформация из originalType в newType не
    входит в список разрешённых, либо объект с указанными типом и позицией
    не найден на слайде, изменение не будет применено.
    """
    try:
        slide = deepcopy(state["current_slide"])

        if newType not in ALLOWED_OBJECT_TRANSFORMATION.get(originalType, []):
            raise ValueError(
                f"Преобразования {originalType} -> {newType} недопустимо. "
                f"Допустимые: {ALLOWED_OBJECT_TRANSFORMATION.get(originalType, [])}"
            )

        obj = _find_object(slide, originalPosition)

        if obj.type != originalType:
            raise ValueError(
                f"Объект на позиции {originalPosition} имеет тип {obj.type}, "
                f"ожидаемый тип {originalType.value}"
            )

        obj.type = newType

        return Command(
            update={
                "current_slide": slide,
                "slide_changed": True,
                "messages": [
                    ToolMessage(
                        content=f"Тип объекта изменен с {originalType} на {newType}.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Изменение не было завершено: {e}. Попробуйте сначало внести другое изменение, после попробуйте снова",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )


@tool
def change_object_swap(
    positionA: ObjectPosition,
    positionB: ObjectPosition,
    state: Annotated[EditAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Меняет местами позиции двух объектов на слайде, сохраняя их размеры.

    Находит объекты, расположенные в positionA и positionB, и меняет их
    позиции местами — объект из positionA перемещается в positionB и
    наоборот. Размеры объектов (span) не изменяются. Полезно, когда нужно
    поменять местами два объекта без необходимости временно увеличивать
    или уменьшать их размеры.

    Args:
        positionA: Позиция первого объекта на слайде (координаты x, y в
            сетке {HORIZONTAL_SIZE}x{VERTICAL_SIZE}).
        positionB: Позиция второго объекта на слайде.

    Если после обмена местами хотя бы один из объектов выходит за границы
    сетки или пересекается с каким-либо другим объектом на слайде, изменение
    не будет применено.
    """
    try:
        slide = deepcopy(state["current_slide"])

        obj_a = _find_object(slide, positionA)
        obj_b = _find_object(slide, positionB)

        obj_a.position, obj_b.position = positionB, positionA

        _validate_slide_no_collisions(slide)

        return Command(
            update={
                "current_slide": slide,
                "slide_changed": True,
                "messages": [
                    ToolMessage(
                        content=f"Swapped objects: {positionA} <-> {positionB}.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(content=f"Swap failed: {e}", tool_call_id=tool_call_id)
                ],
            }
        )


def _validate_grid_bounds(pos: ObjectPosition, size: ObjectSpan) -> None:
    if not (1 <= pos.x <= HORIZONTAL_SIZE and 1 <= pos.y <= VERTICAL_SIZE):
        raise ValueError(
            f"Позиция {pos} находится за границами {HORIZONTAL_SIZE}x{VERTICAL_SIZE} решетки"
        )

    # Position starts from 1, so -1
    if (
        pos.x + size.horizontal_span - 1 > HORIZONTAL_SIZE
        or pos.y + size.vertical_span - 1 > VERTICAL_SIZE
    ):
        raise ValueError(
            f"Объект на позиции {pos} с размером {size} выходит за границы"
        )


def _validate_slide_no_collisions(slide: DraftSlide) -> None:
    """Проверяет, что ни один объект на слайде не пересекается с другим
    и не выходит за границы сетки, помечая занятые ячейки сетки.
    Вызывается ПОСЛЕ применения изменений к копии слайда — если проверка
    не пройдена, изменения не сохраняются.
    """
    occupied: dict[tuple[int, int], SlideItem] = {}

    for obj in slide.objects:
        _validate_grid_bounds(obj.position, obj.span)

        for dx in range(obj.span.horizontal_span):
            for dy in range(obj.span.vertical_span):
                cell = (obj.position.x + dx, obj.position.y + dy)

                if cell in occupied:
                    other = occupied[cell]
                    raise ValueError(
                        f"После применения изменения объект типа '{obj.type}' "
                        f"(позиция {obj.position}, размер {obj.span}) "
                        f"пересекается с объектом типа '{other.type}' "
                        f"(позиция {other.position}, размер {other.span}) "
                        f"в ячейке {cell}."
                    )

                occupied[cell] = obj


def _find_object(slide: DraftSlide, position: ObjectPosition) -> SlideItem:
    for obj in slide.objects:
        if obj.position == position:
            return obj

    raise ValueError(f"На позиции {position} не был найден объект")


data_tools: list[BaseTool] = [sql_query_dataframe]

slide_tools: list[BaseTool] = [
    change_object_pos,
    change_object_swap,
    change_object_type,
]
