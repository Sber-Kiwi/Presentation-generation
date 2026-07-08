from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send
from nodes import semaphore
from state import FinalJsonState, FinalJsonTaskState
from utils import format_slide_for_llm, parse_json_to_draft

from .helpers import _build_final_json_slide, build_slide_json, gather_slide_data


def final_json_prepare_tasks(state: FinalJsonState) -> dict:
    return {
        "tasks": [
            (slide_num, parse_json_to_draft(slide_versions))
            for slide_num, slide_versions in state["draft_slides"].items()
        ]
    }


async def build_final_json(state: FinalJsonTaskState) -> dict:
    slide_index = state["slide_index"]
    slide_draft = state["slide_draft"]
    slide_prompt = format_slide_for_llm(slide_draft)

    async with semaphore:
        # Phase 1: ReAct loop with sql_query_dataframe
        gathered_messages = await gather_slide_data(slide_prompt)

        # Phase 2: single structured-output call, no tools
        final_slide_structured_data = await build_slide_json(
            slide_prompt, gathered_messages
        )

    final_slide = _build_final_json_slide(
        slide_draft, final_slide_structured_data, slide_index
    )

    return {"final_slides": {slide_index: final_slide}}


def combine_final_jsons(state: FinalJsonState) -> dict:
    jsons = state.get("final_slides")

    return {"final_slides": jsons}


def route_final_json_tasks(state: FinalJsonState) -> list[Send]:
    drafts = state.get("draft_slides", {})
    return [
        Send(
            "build_final_json",
            {
                "slide_index": task["slide_index"],
                "slide_draft": drafts[task["slide_index"]],
                "gathered_messages": [],
                "final_slide": None,
            },
        )
        for task in state["tasks"]
    ]


def build_final_json_subgraph() -> CompiledStateGraph:
    subgraph = StateGraph(FinalJsonState)

    subgraph.add_node("prepare_tasks", final_json_prepare_tasks)
    subgraph.add_node("build_final_json", build_final_json)
    subgraph.add_node("combine_results", combine_final_jsons)

    subgraph.add_edge(START, "prepare_tasks")
    subgraph.add_conditional_edges(
        "prepare_tasks", route_final_json_tasks, ["build_final_json"]
    )
    subgraph.add_edge("build_final_json", "combine_results")
    subgraph.add_edge("combine_results", END)

    return subgraph.compile()
