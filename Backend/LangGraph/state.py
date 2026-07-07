import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from models import DraftSlide, Json, PromptList, PromptSlide, UserChangePrompt


def merge_indexed_dict(current: dict, update: dict) -> dict:
    merged = dict(current)
    merged.update(update)
    return merged


class MetricsAgentState(TypedDict):
    start_prompt: str
    messages: Annotated[Sequence[BaseMessage], add_messages]

    presentation_name: str  # Transitions to PromptAgentState
    metrics: list[str]  # Transitions to PromptAgentState


class PromptAgentState(TypedDict):
    presentation_name: str
    metrics: list[str]

    tasks: list[tuple[int, str]]

    prompts: Annotated[dict[int, PromptList], merge_indexed_dict]
    flat_prompts: PromptList  # Transitions to DraftAgentState


class DraftAgentState(TypedDict):
    flat_prompts: PromptList

    tasks: list[tuple[int, PromptSlide]]
    draft_slides: Annotated[
        dict[int, Annotated[list[Json], operator.add]], merge_indexed_dict
    ]  # Transitions to FinalJsonState (but flat without versions)


class EditAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

    slide_changed: bool

    change_prompt: UserChangePrompt
    current_slide: DraftSlide
    slide_versions: list[DraftSlide]


class OverallState(TypedDict):
    start_prompt: str
    presentation_name: str
    metrics: list[str]
    flat_prompts: PromptList
    draft_slides: Annotated[dict[int, list[Json]], merge_indexed_dict]
