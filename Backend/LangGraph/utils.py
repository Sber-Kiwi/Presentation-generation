import json

from models import DraftSlide, Json, ObjectPosition, ObjectSpan, PromptSlide, SlideItem

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
                type=item["type"],
                prompt=item["text"],
                position=ObjectPosition(
                    x=item["cell_pos"]["x"], y=item["cell_pos"]["y"]
                ),
                span=ObjectSpan(
                    horizontal_span=item["span"]["x"], vertical_span=item["span"]["y"]
                ),
            )
            for item in json_dict["objects"]
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
    return f"""**Название слайда:** {promptSlide.slide_name}
**Основной аналитический тезис:** {promptSlide.idea}
**Примерное содержание слайда:** {promptSlide.contents}"""


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
