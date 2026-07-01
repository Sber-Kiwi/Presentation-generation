from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from models import PromptList


def merge_indexed_dict(current: dict, update: dict) -> dict:
    merged = dict(current)
    merged.update(update)
    return merged


json = Annotated[dict, "This is a dict representing json"]


class MetricsAgentState(TypedDict):
    start_prompt: str
    messages: Annotated[Sequence[BaseMessage], add_messages]

    presentation_name: str  # Transitions to PromptAgentState
    metrics: list[str]  # Transitions to PromptAgentState


class PromptAgentState(TypedDict):
    presentation_name: str
    metrics: list[str]

    prompt_gen_idx: Annotated[dict[int, int], merge_indexed_dict]

    prompts: Annotated[dict[int, PromptList], merge_indexed_dict]
    flat_prompts: PromptList  # Transitions to DraftAgentState


class DraftAgentState(TypedDict):
    flat_prompts: PromptList

    json_gen_idx: Annotated[dict[int, int], merge_indexed_dict]

    draft_slides: Annotated[dict[int, json], merge_indexed_dict]


class OverallState(TypedDict):
    start_prompt: str
    presentation_name: str
    metrics: list[str]
    flat_prompts: PromptList
    draft_slides: dict[int, json]
