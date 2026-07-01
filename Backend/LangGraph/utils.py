from state import json
from models import DraftSlide
from uuid import uuid4


def create_draft_json(draftSlide: DraftSlide) -> json:
    return {
        "meta": {
            "slide_id": f"sld_{uuid4().hex[:12]}",
            "title": draftSlide.name,
        },
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
