import json

from models import DraftSlide, Json, ObjectPosition, ObjectSpan, PromptSlide, SlideItem


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
