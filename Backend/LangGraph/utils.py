import json

from models import (
    HORIZONTAL_SIZE,
    VERTICAL_SIZE,
    DraftSlide,
    Json,
    ObjectPosition,
    ObjectSpan,
    PromptSlide,
    SlideItem,
)

GRID_ORIGIN_X = 0.03
GRID_ORIGIN_Y = 0.20
GRID_WIDTH = 0.94
GRID_HEIGHT = 0.79
# небольшой зазор между соседними ячейками сетки
CELL_GAP = 0.01


def create_draft_json(draftSlide: DraftSlide) -> Json:
    return {
        "meta": {"title": draftSlide.name},
        "objects": [
            {
                "type": slide_object.type,
                "text": slide_object.prompt,
                "cell_pos": {
                    "x": slide_object.position.x,
                    "y": slide_object.position.y,
                },
                "span": {
                    "x": slide_object.span.horizontal_span,
                    "y": slide_object.span.vertical_span,
                },
            }
            for slide_object in draftSlide.objects
        ],
    }


def parse_json_to_draft(json_dict: Json) -> DraftSlide:
    try:
        return DraftSlide(
            name=json_dict["meta"]["title"],
            objects=[
                SlideItem(
                    id=idx,
                    type=item["type"],
                    prompt=item["text"],
                    position=ObjectPosition(
                        x=item["cell_pos"]["x"], y=item["cell_pos"]["y"]
                    ),
                    span=ObjectSpan(
                        horizontal_span=item["span"]["x"],
                        vertical_span=item["span"]["y"],
                    ),
                )
                for idx, item in enumerate(json_dict["objects"])
            ],
        )
    except Exception as e:
        raise ValueError(f"Unable to parse json to draft: {e}")


def resolve_grid_position(
    x: int, y: int, horizontal_span: int = 1, vertical_span: int = 1
) -> dict:
    cell_w = (GRID_WIDTH - (HORIZONTAL_SIZE - 1) * CELL_GAP) / HORIZONTAL_SIZE
    cell_h = (GRID_HEIGHT - (VERTICAL_SIZE - 1) * CELL_GAP) / VERTICAL_SIZE

    abs_x = GRID_ORIGIN_X + (x - 1) * (cell_w + CELL_GAP)
    abs_y = GRID_ORIGIN_Y + (y - 1) * (cell_h + CELL_GAP)
    width = horizontal_span * cell_w + (horizontal_span - 1) * CELL_GAP
    height = vertical_span * cell_h + (vertical_span - 1) * CELL_GAP

    return {"x": abs_x, "y": abs_y, "width": width, "height": height}


def build_promt_message(promptSlide: PromptSlide) -> str:
    return f"""НАЗВАНИЕ СЛАЙДА: {promptSlide.slide_name}
ОСНОВНОЙ АНАЛИТИЧЕСКИЙ АНАЛИЗ: {promptSlide.idea}
ПРИМЕРНОЕ СОДРЕЖАНИЕ СЛАЙДА: {promptSlide.contents}"""


def format_slide_for_llm(slide_draft: DraftSlide) -> str:
    """Строит текстовое представление слайда со всеми объектами для LLM,
    сохраняя привязку данных к конкретному объекту через индекс и позицию."""
    lines = [f"СЛАЙД: {slide_draft.name}", "ОБЪЕКТЫ НА СЛАЙДЕ:"]

    for idx, obj in enumerate(slide_draft.objects):
        lines.append(
            f"[{idx}] Тип: {obj.type.value}, "
            f"Позиция: {obj.position}, Размер: {obj.span}\n"
            f"    Описание: {obj.prompt}"
        )

    return "\n".join(lines)


from collections import defaultdict


def normalize_draft_slides(
    draft_slides: dict[int, DraftSlide],
) -> dict[int, DraftSlide]:
    """Проходит по всем черновым слайдам и исправляет объекты, которые
    выходят за границы сетки или пересекаются друг с другом. Слайды,
    уже корректно размещённые, не изменяются.
    """
    for slide in draft_slides.values():
        _normalize_slide(slide)
    return draft_slides


def _normalize_slide(slide: DraftSlide) -> None:
    try:
        for obj in slide.objects:
            _validate_grid_bounds(obj.position, obj.span)
        _validate_slide_no_collisions(slide)
        return  # слайд уже корректен, ничего менять не нужно
    except ValueError:
        pass  # обнаружено пересечение или выход за границы -- нормализуем

    occupied: set[tuple[int, int]] = set()
    dropped_ids: set[int] = set()

    # Группируем объекты по точной начальной позиции -- те, что совпадают
    # позицией, нужно рассадить (разделить пространство), остальные
    # обрабатываем по одному в исходном порядке.
    position_groups: dict[tuple[int, int], list[SlideItem]] = defaultdict(list)
    for obj in slide.objects:
        position_groups[(obj.position.x, obj.position.y)].append(obj)

    handled: set[int] = set()

    for obj in slide.objects:
        if id(obj) in handled:
            continue

        group = position_groups[(obj.position.x, obj.position.y)]
        handled.update(id(o) for o in group)

        if len(group) > 1:
            _place_group(group, occupied, dropped_ids)
        else:
            _place_single(obj, occupied, dropped_ids)

    slide.objects = [obj for obj in slide.objects if id(obj) not in dropped_ids]


def _cells(x: int, y: int, w: int, h: int) -> set[tuple[int, int]]:
    return {(x + dx, y + dy) for dx in range(w) for dy in range(h)}


def _find_max_fit(
    x: int, y: int, pref_w: int, pref_h: int, occupied: set[tuple[int, int]]
) -> tuple[int, int] | None:
    """Ищет наибольшую по площади пару (w, h) не больше (pref_w, pref_h),
    которая укладывается в границы сетки от анкора (x, y) и не пересекает
    занятые ячейки. Возвращает None, если даже 1x1 не помещается.
    """
    max_w = HORIZONTAL_SIZE - x + 1
    max_h = VERTICAL_SIZE - y + 1
    w0 = min(pref_w, max_w)
    h0 = min(pref_h, max_h)

    if w0 < 1 or h0 < 1:
        return None

    best: tuple[int, int, int] = (0, 0, 0)

    for w in range(w0, 0, -1):
        for h in range(h0, 0, -1):
            if _cells(x, y, w, h).isdisjoint(occupied):
                area = w * h
                if area > best[2]:
                    best = (w, h, area)

    if best[2] == 0:
        return None
    return best[0], best[1]


def _place_single(
    obj: SlideItem, occupied: set[tuple[int, int]], dropped_ids: set[int]
) -> None:
    x = max(1, min(obj.position.x, HORIZONTAL_SIZE))
    y = max(1, min(obj.position.y, VERTICAL_SIZE))

    fit = _find_max_fit(
        x, y, obj.span.horizontal_span, obj.span.vertical_span, occupied
    )

    if fit is None:
        print(
            f"[WARNING] Объект типа '{obj.type}' в позиции ({x}, {y}) "
            f"не удалось разместить -- место полностью занято. Объект удалён."
        )
        dropped_ids.add(id(obj))
        return

    w, h = fit
    obj.position = ObjectPosition(x=x, y=y)
    obj.span = ObjectSpan(horizontal_span=w, vertical_span=h)
    occupied.update(_cells(x, y, w, h))


def _place_group(
    group: list[SlideItem], occupied: set[tuple[int, int]], dropped_ids: set[int]
) -> None:
    """Разделяет место между объектами с одинаковой исходной позицией.

    Пытается разделить доступное пространство по горизонтали (если хотя
    бы один объект шире 1 клетки и места хватает на всех), иначе по
    вертикали. Каждому объекту отводится доля пространства, после чего
    его итоговый размер определяется через _find_max_fit относительно
    уже занятых ячеек (включая те, что заняли другие объекты этой же
    группы). Объекты, которым не хватило места даже 1x1, удаляются.
    """
    x = max(1, min(group[0].position.x, HORIZONTAL_SIZE))
    y = max(1, min(group[0].position.y, VERTICAL_SIZE))
    n = len(group)

    max_w = HORIZONTAL_SIZE - x + 1
    max_h = VERTICAL_SIZE - y + 1

    wants_wide = any(o.span.horizontal_span > 1 for o in group)

    if wants_wide and max_w >= n:
        width_each = max(1, max_w // n)
        cur_x = x
        for obj in group:
            fit = _find_max_fit(cur_x, y, width_each, obj.span.vertical_span, occupied)
            if fit is None:
                print(
                    f"[WARNING] Объект типа '{obj.type}' в позиции ({cur_x}, {y}) "
                    f"не удалось разместить при горизонтальном разделении. Удалён."
                )
                dropped_ids.add(id(obj))
                cur_x += width_each
                continue

            w, h = fit
            obj.position = ObjectPosition(x=cur_x, y=y)
            obj.span = ObjectSpan(horizontal_span=w, vertical_span=h)
            occupied.update(_cells(cur_x, y, w, h))
            cur_x += width_each
        return

    if max_h >= n:
        height_each = max(1, max_h // n)
        cur_y = y
        for obj in group:
            fit = _find_max_fit(
                x, cur_y, obj.span.horizontal_span, height_each, occupied
            )
            if fit is None:
                print(
                    f"[WARNING] Объект типа '{obj.type}' в позиции ({x}, {cur_y}) "
                    f"не удалось разместить при вертикальном разделении. Удалён."
                )
                dropped_ids.add(id(obj))
                cur_y += height_each
                continue

            w, h = fit
            obj.position = ObjectPosition(x=x, y=cur_y)
            obj.span = ObjectSpan(horizontal_span=w, vertical_span=h)
            occupied.update(_cells(x, cur_y, w, h))
            cur_y += height_each
        return

    # Ни горизонтальное, ни вертикальное разделение не вмещает всех объектов
    # группы - размещаем по одному (1x1 каждый), пока есть место, остальные
    # удаляем.
    for obj in group:
        fit = _find_max_fit(x, y, 1, 1, occupied)
        if fit is None:
            print(
                f"[WARNING] Объект типа '{obj.type}' в позиции ({x}, {y}) "
                f"не удалось разместить -- сетка переполнена. Объект удалён."
            )
            dropped_ids.add(id(obj))
            continue

        w, h = fit
        obj.position = ObjectPosition(x=x, y=y)
        obj.span = ObjectSpan(horizontal_span=w, vertical_span=h)
        occupied.update(_cells(x, y, w, h))


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
    Вызывается ПОСЛЕ применения изменений к копии слайда -- если проверка
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


if __name__ == "__main__":
    import json
    import sys

    raw_input = sys.stdin.read()

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Некорректный JSON: {e}")

    try:
        slide = parse_json_to_draft(payload)
    except Exception as e:
        print(f"[ERROR] JSON не соответствует схеме DraftSlide: {e}")

    normalized = normalize_draft_slides({0: slide})[0]

    print(json.dumps(create_draft_json(normalized), ensure_ascii=False, indent=2))
