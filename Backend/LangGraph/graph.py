import asyncio

from _save_stage import dev_cache
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from models import PromptList
from nodes import (
    combine_drafts,
    combine_prompts,
    data_agent,
    draft_prepare_tasks,
    draft_route_tasks,
    final_json_route_tasks,
    generate_draft,
    generate_prompt,
    metrics_splitter,
    prompt_prepare_tasks,
    prompt_route_tasks,
    review_and_edit,
    setupper,
    should_continue_metrics,
    sql_tool_node,
)
from state import (
    DraftAgentState,
    FinalJsonState,
    MetricsAgentState,
    OverallState,
    PromptAgentState,
)


def build_metrics_graph() -> CompiledStateGraph:
    subgraph = StateGraph(MetricsAgentState)
    subgraph.add_node("setup", setupper)
    subgraph.add_node("data_agent", data_agent)
    subgraph.add_node("extract_metrics", metrics_splitter)
    subgraph.add_node("metrics_tools", sql_tool_node)

    subgraph.add_edge(START, "setup")
    subgraph.add_edge("setup", "data_agent")
    subgraph.add_edge("metrics_tools", "data_agent")
    subgraph.add_conditional_edges(
        "data_agent",
        should_continue_metrics,
        {False: "extract_metrics", True: "metrics_tools"},
    )
    subgraph.add_edge("extract_metrics", END)

    return subgraph.compile()


def build_prompts_subgraph() -> CompiledStateGraph:
    subgraph = StateGraph(PromptAgentState)
    subgraph.add_node("prepare_tasks", prompt_prepare_tasks)
    subgraph.add_node("generate_prompt", generate_prompt)
    subgraph.add_node("combine_prompts", combine_prompts)

    subgraph.add_edge(START, "prepare_tasks")
    subgraph.add_conditional_edges(
        "prepare_tasks", prompt_route_tasks, ["generate_prompt"]
    )
    subgraph.add_edge("generate_prompt", "combine_prompts")
    subgraph.add_edge("combine_prompts", END)

    return subgraph.compile()


def build_draft_subgraph() -> CompiledStateGraph:
    subgraph = StateGraph(DraftAgentState)

    subgraph.add_node("prepare_tasks", draft_prepare_tasks)
    subgraph.add_node("generate_draft", generate_draft)
    subgraph.add_node("combine_drafts", combine_drafts)

    subgraph.add_edge(START, "prepare_tasks")
    subgraph.add_conditional_edges(
        "prepare_tasks", draft_route_tasks, ["generate_draft"]
    )
    subgraph.add_edge("generate_draft", "combine_drafts")
    subgraph.add_edge("combine_drafts", END)

    return subgraph.compile()


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(OverallState)
    graph.add_node("metrics_agent", run_metrics_agent)
    graph.add_node("prompt_agent", run_prompt_agent)
    graph.add_node("draft_agent", run_draft_agent)
    graph.add_node("edit_agent", review_and_edit)

    graph.add_edge(START, "metrics_agent")
    graph.add_edge("metrics_agent", "prompt_agent")
    graph.add_edge("prompt_agent", "draft_agent")
    graph.add_edge("draft_agent", "edit_agent")
    graph.add_edge("edit_agent", END)

    return graph.compile()


metrics_subgraph = build_metrics_graph()
prompt_subgraph = build_prompts_subgraph()
draft_subgraph = build_draft_subgraph()


@dev_cache("metrics")
async def run_metrics_agent(state: OverallState) -> dict:
    sub_input: MetricsAgentState = {
        "start_prompt": state["start_prompt"],
        "messages": [],
        "presentation_name": "",
        "metrics": [],
    }
    result = await asyncio.to_thread(metrics_subgraph.invoke, sub_input)
    return {
        "presentation_name": result["presentation_name"],
        "metrics": result["metrics"],
    }


@dev_cache("prompt")
async def run_prompt_agent(state: OverallState) -> dict:
    sub_input: PromptAgentState = {
        "presentation_name": state["presentation_name"],
        "metrics": state["metrics"],
        "tasks": [],
        "prompts": {},
        "flat_prompts": PromptList(prompts=[]),
    }
    result = await prompt_subgraph.ainvoke(sub_input)
    return {"flat_prompts": result["flat_prompts"]}


@dev_cache("draft")
async def run_draft_agent(state: OverallState) -> dict:
    sub_input: DraftAgentState = {
        "flat_prompts": state["flat_prompts"],
        "tasks": [],
        "draft_slides": {},
    }

    result = await draft_subgraph.ainvoke(sub_input)
    return {"draft_slides": result["draft_slides"]}
