from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import OverallState, MetricsAgentState, PromptAgentState, DraftAgentState
from nodes import (
    setupper,
    data_agent,
    metrics_splitter,
    funcGen_slide_promt_generator,
    funcGen_slide_json_generator,
    do_nothing_node,
    should_continue_json_gen,
    should_continue_metrics,
    should_continue_prompts_gen,
    flatten_prompts,
    metrics_tools_node,
)
from models import PromptList
from settings import WORKERS_POOL_SIZE


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(OverallState)
    graph.add_node("metrics_agent", run_metrics_agent)
    graph.add_node("prompt_agent", run_prompt_agent)
    graph.add_node("draft_agent", run_draft_agent)

    graph.add_edge(START, "metrics_agent")
    graph.add_edge("metrics_agent", "prompt_agent")
    graph.add_edge("prompt_agent", "draft_agent")
    graph.add_edge("draft_agent", END)

    return graph.compile()


def build_metrics_graph() -> CompiledStateGraph:
    subgraph = StateGraph(MetricsAgentState)
    subgraph.add_node("setup", setupper)
    subgraph.add_node("data_agent", data_agent)
    subgraph.add_node("extract_metrics", metrics_splitter)
    subgraph.add_node("metrics_tools", metrics_tools_node)

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
    subgraph.add_node("separate_prompts", do_nothing_node)
    for idx in range(WORKERS_POOL_SIZE):
        subgraph.add_node(f"generate_prompt{idx}", funcGen_slide_promt_generator(idx))
        subgraph.add_edge("separate_prompts", f"generate_prompt{idx}")
        subgraph.add_edge(f"generate_prompt{idx}", "combine_prompts")
    subgraph.add_node("combine_prompts", do_nothing_node)
    subgraph.add_node("flatten_prompts", flatten_prompts)

    subgraph.add_edge(START, "separate_prompts")
    subgraph.add_conditional_edges(
        "combine_prompts",
        should_continue_prompts_gen,
        {False: "flatten_prompts", True: "separate_prompts"},
    )
    subgraph.add_edge("flatten_prompts", END)

    return subgraph.compile()


def build_draft_subgraph() -> CompiledStateGraph:
    subgraph = StateGraph(DraftAgentState)
    subgraph.add_node("separate_draft", do_nothing_node)
    for idx in range(WORKERS_POOL_SIZE):
        subgraph.add_node(f"generate_draft{idx}", funcGen_slide_json_generator(idx))
        subgraph.add_edge("separate_draft", f"generate_draft{idx}")
        subgraph.add_edge(f"generate_draft{idx}", "combine_draft")
    subgraph.add_node("combine_draft", do_nothing_node)

    subgraph.add_edge(START, "separate_draft")
    subgraph.add_conditional_edges(
        "combine_draft", should_continue_json_gen, {False: END, True: "separate_draft"}
    )

    return subgraph.compile()


metrics_subgraph = build_metrics_graph()
prompt_subgraph = build_prompts_subgraph()
draft_subgraph = build_draft_subgraph()


def run_metrics_agent(state: OverallState) -> dict:
    sub_input: MetricsAgentState = {
        "start_prompt": state["start_prompt"],
        "messages": [],
        "presentation_name": "",
        "metrics": [],
    }
    result = metrics_subgraph.invoke(sub_input)
    return {
        "presentation_name": result["presentation_name"],
        "metrics": result["metrics"],
    }


def run_prompt_agent(state: OverallState) -> dict:
    sub_input: PromptAgentState = {
        "presentation_name": state["presentation_name"],
        "metrics": state["metrics"],
        "prompt_gen_idx": {i: i for i in range(WORKERS_POOL_SIZE)},
        "prompts": {i: PromptList(prompts=[]) for i in range(len(state["metrics"]))},
        "flat_prompts": PromptList(prompts=[]),
    }
    result = prompt_subgraph.invoke(sub_input)
    return {"flat_prompts": result["flat_prompts"]}


def run_draft_agent(state: OverallState) -> dict:
    sub_input: DraftAgentState = {
        "flat_prompts": state["flat_prompts"],
        "json_gen_idx": {i: i for i in range(WORKERS_POOL_SIZE)},
        "draft_slides": {i: {} for i in range(len(state["metrics"]))},
    }
    result = draft_subgraph.invoke(sub_input)
    return {"draft_slides": result["draft_slides"]}
