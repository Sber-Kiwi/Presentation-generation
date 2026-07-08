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
                    horizontal_span=item["span"]["x"], vertical_span=item["span"]["y"]
                ),
            )
            for idx, item in enumerate(json_dict["objects"])
        ],
    )


def resolve_grid_position(x: int, y: int, horizontal_span: int = 1, vertical_span: int = 1) -> dict:
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


# TODO REMOVE. not used for debugging purposes
def print_slide(slide: dict, idx: int):
    print(f"\n--- Slide {idx} ---")
    print(json.dumps(slide, ensure_ascii=False, indent=2))


# TODO REMOVE. not used for debugging purposes
def print_help():
    print("""
Commands:
  n / next          next slide
  p / prev          previous slide
  goto <i>          jump to slide i
  s / show          reprint current slide
  edit <text>       submit a change request for current slide (async, LLM call)
  status            show active/pending change requests
  q / quit / done    finish — waits for pending requests, then exits
  help              show this message
""")


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


def normalize_draft_slides(
    draft_slides: dict[int, DraftSlide],
) -> dict[int, DraftSlide]:
    """Проходит по всем черновым слайдам и исправляет объекты, которые
    выходят за границы сетки или пересекаются друг с другом, обрезая их
    до максимально допустимого размера. Слайды, уже корректно размещённые,
    не изменяются.
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
        pass  # обнаружено пересечение или выход за границы — нормализуем

    occupied: set[tuple[int, int]] = set()
    for obj in slide.objects:
        _clamp_object_to_fit(obj, occupied)


def _clamp_object_to_fit(obj: SlideItem, occupied: set[tuple[int, int]]) -> None:
    """Обрезает объект до максимального размера, который помещается в
    сетку и не пересекается с уже размещёнными (occupied) объектами,
    сохраняя его исходную позицию верхнего левого угла.
    """
    x = max(0, min(obj.position.x, HORIZONTAL_SIZE - 1))
    y = max(0, min(obj.position.y, VERTICAL_SIZE - 1))

    max_w = HORIZONTAL_SIZE - x
    max_h = VERTICAL_SIZE - y
    orig_w = min(obj.span.horizontal_span, max_w)
    orig_h = min(obj.span.vertical_span, max_h)

    best_w, best_h, best_area = 1, 1, 0

    for w in range(1, orig_w + 1):
        for h in range(1, orig_h + 1):
            cells = [(x + dx, y + dy) for dx in range(w) for dy in range(h)]
            if all(cell not in occupied for cell in cells):
                area = w * h
                if area > best_area:
                    best_area, best_w, best_h = area, w, h

    if best_area == 0:
        # Даже 1x1 в этой позиции занято — сетка переполнена в этом месте.
        # Оставляем объект 1x1 с пересечением, чтобы не потерять его совсем.
        print(
            f"[WARNING] Не удалось разместить объект типа '{obj.type}' "
            f"в позиции ({x}, {y}) без пересечения — сетка переполнена."
        )
        best_w, best_h = 1, 1

    obj.position = ObjectPosition(x=x, y=y)
    obj.span = ObjectSpan(horizontal_span=best_w, vertical_span=best_h)

    for dx in range(best_w):
        for dy in range(best_h):
            occupied.add((x + dx, y + dy))


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
