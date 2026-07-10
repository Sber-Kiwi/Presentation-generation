import operator
from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from models import DraftSlide, Json, PromptList, PromptSlide, UserChangePrompt


def merge_indexed_dict(current: dict, update: dict) -> dict:
    merged = dict(current)
    merged.update(update)
    return merged


class MetricsAgentState(TypedDict):
    start_prompt: str
    data_anlyze_result: str
    messages: Annotated[Sequence[BaseMessage], add_messages]

    presentation_name: str
    metrics: list[str]  # Transitions to PromptAgentState

    task_id: int
    output_file: str


class PromptAgentState(TypedDict):
    metrics: list[str]
    data_anlyze_result: str

    tasks: list[tuple[int, str]]

    prompts: Annotated[dict[int, PromptList], merge_indexed_dict]
    flat_prompts: PromptList  # Transitions to DraftAgentState


class DraftAgentState(TypedDict):
    flat_prompts: PromptList

    tasks: list[tuple[int, PromptSlide]]
    draft_slides: Annotated[dict[int, Json], merge_indexed_dict]


class EditAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

    slide_changed: bool

    change_prompt: UserChangePrompt
    current_slide: DraftSlide
    slide_versions: list[DraftSlide]


class FinalJsonTaskState(TypedDict):
    slide_index: int
    slide_draft: DraftSlide

    gathered_messages: Sequence[BaseMessage]

    final_slide: Json


class FinalJsonState(TypedDict):
    draft_slides: dict[int, Json]

    tasks: list[FinalJsonTaskState]
    final_slides: Annotated[dict[int, Json], merge_indexed_dict]


class OverallState(TypedDict):
    presentation_name: str
    metrics: list[str]
    data_anlyze_result: str
    flat_prompts: PromptList
    draft_slides: list[Json]
    final_slides: dict[int, Json]

    mode: Literal["start", "edit"]
    edit_route: Literal["export", "edit"]

    output_file: str

    task_id: int
    start_prompt: str
    edit_prompt: str
    current_slide: Json
    recent_versions_history: list[Json]
