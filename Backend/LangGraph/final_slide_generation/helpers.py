from typing import Literal, Sequence
from uuid import uuid4

import settings
from constants.messages import DATA_GATHER_SYSTEM_MESSAGE, JSON_BUILD_SYSTEM_MESSAGE
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from llm_setup import config_strict, llm_structured_final, llm_with_data_tools
from models import (
    ChartData,
    DraftSlide,
    FinalObjectData,
    FinalSlideData,
    Json,
    SlideItem,
    TableData,
    TextData,
    WaterfallData,
)
from nodes import sql_tool_node
from utils import resolve_grid_position

MAX_DATA_GATHER_ITERATIONS = 5


async def gather_slide_data(slide_prompt: str) -> Sequence[BaseMessage]:
    system_message = SystemMessage(content=DATA_GATHER_SYSTEM_MESSAGE)
    data_message = HumanMessage(
        content=f"ОПИСАНИЕ СЛАЙДА и ОБЪЕКТОВ: {slide_prompt}\n\n"
        f"ЗАГОЛОВКИ ТАБЛИЦЫ С ДАННЫМИ: {str(settings.sql_data.columns)}"
    )
    messages = [system_message, data_message]

    for _ in range(MAX_DATA_GATHER_ITERATIONS):
        response = await settings.call_llm(
            llm_with_data_tools, messages, config=config_strict
        )
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            break

        tool_results = await sql_tool_node.ainvoke({"messages": messages})
        messages.extend(tool_results["messages"])

    return messages


async def build_slide_json(
    slide_prompt: str, gathered_messages: Sequence[BaseMessage]
) -> FinalSlideData:
    system_message = SystemMessage(content=JSON_BUILD_SYSTEM_MESSAGE)
    data_message = HumanMessage(content=f"""ИСХОДНОЕ ОПИСАНИЕ СЛАЙДА: {slide_prompt}
СОБРАННЫЕ ДАННЫЕ: {_summarize_tool_results(gathered_messages)}""")

    response: FinalSlideData = await settings.call_llm(
        llm_structured_final, [system_message, data_message], config=config_strict
    )

    return response


def _summarize_tool_results(messages: Sequence[BaseMessage]) -> str:
    return "\n".join(m.content for m in messages if isinstance(m, ToolMessage))


# def _build_final_json(
#     slide_draft: dict[int, DraftSlide],
#     slide_data: dict[int, FinalSlideData],
#     presentation_title: str,
#     common_slide_title: str,
# ) -> Json:
#     return {
#         "meta": {"title": presentation_title, "common_slide_title": common_slide_title},
#         "slides": [
#             _build_final_json_slide(slide_draft, slide_data)
#             for slide_draft, slide_data in zip(
#                 slide_draft.values(), slide_data.values()
#             )
#         ],
#     }


def _build_final_json_slide(
    draft_slides: DraftSlide, slides_data: FinalSlideData, slide_index: int
) -> Json:
    return {
        "meta": {
            "slide_id": f"sld_{uuid4().hex[:12]}",
            "title": draft_slides.name,
            "number": slide_index + 1,
        },
        "objects": [
            _build_final_json_object(object_draft, object_data)
            for object_draft, object_data in zip(
                draft_slides.objects, slides_data.objects.values()
            )
        ],
    }


def _build_final_json_object(
    object_draft: SlideItem, object_data: FinalObjectData
) -> Json:
    obj_type: Literal["TEXT", "TABLE", "CHART", "WATERFALL", None] = (
        "TEXT"
        if isinstance(object_data, TextData)
        else (
            "TABLE"
            if isinstance(object_data, TableData)
            else (
                "CHART"
                if isinstance(object_data, ChartData)
                else ("WATERFALL" if isinstance(object_data, WaterfallData) else None)
            )
        )
    )

    if obj_type is None:
        raise ValueError(f"Unsupported object data type: {type(object_data)}")

    data: dict[str, object] | None = None
    match object_data:
        case TextData():
            data = {
                "kind": object_data.kind,
                "markdown": True,
                "text": object_data.text,
            }
        case TableData():
            data = {
                "kind": object_data.kind,
                "headers": object_data.headers,
                "rows": object_data.rows,
                "caption": object_data.caption,
            }
        case ChartData():
            data = {
                "chart_type": object_data.chart_type,
                "kind": object_data.kind,
                "labels": None,
                "title": object_data.title,
                "series": [
                    {
                        "unit": series_unit.unit,
                        "data": [
                            {"x": series_data.x, "y": series_data.y}
                            for series_data in series_unit.data
                        ],
                    }
                    for series_unit in object_data.series
                ],
            }
        case WaterfallData():
            data = {
                "kind": object_data.kind,
                "data": [
                    {
                        "type": item.type,
                        "name": item.name,
                        "text": item.text,
                        "plan": item.plan,
                        "delta": item.plan - item.fact,
                    }
                    for item in object_data.data
                ],
            }

    return {
        "object_id": f"obj_{uuid4().hex[:12]}",
        "position": resolve_grid_position(
            x=object_draft.position.x,
            y=object_draft.position.y,
            horizontal_span=object_draft.span.horizontal_span,
            vertical_span=object_draft.span.vertical_span,
        ),
        "type": obj_type,
        "data": data,
    }
