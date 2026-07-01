from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langgraph.prebuilt import ToolNode

from state import MetricsAgentState, PromptAgentState, DraftAgentState
from models import PresentationNameAndMetricsList
from constants.messages import (
    METRICS_SYSTEM_MESSAGE,
    SPLIT_INTO_LIST_MESSAGE,
    PROMPTS_SYSTEM_MESSAGE,
    JSON_SYSTEM_MESSAGE,
)
import settings
from settings import call_llm, WORKERS_POOL_SIZE
from llm_setup import (
    llm_with_tools,
    llm_structured_metrics,
    llm_structured_prompts,
    llm_structured_jsons,
    config_creative,
    config_strict,
)
from tools import tools
from utils import create_draft_json


def setupper(state: MetricsAgentState) -> MetricsAgentState:
    return state


def data_agent(state: MetricsAgentState) -> MetricsAgentState:
    """Агент с доступом к данным через инструмент. Основная задача -- выделение из промпта пользователя и таблицы с данными показателей, по которым позже будет построена таблица."""
    if settings.sql_data is None:
        raise AttributeError("sql_data not provided, unable to process data")

    system_message = SystemMessage(content=METRICS_SYSTEM_MESSAGE)
    data_message = HumanMessage(
        content=f"""ЗАГОЛОВКИ ТАБЛИЦЫ С ДАННЫМИ: {str(settings.sql_data.columns)}
ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {state["start_prompt"]}"""
    )

    response = call_llm(
        llm_with_tools,
        [system_message, data_message] + state["messages"],
        config=config_creative,
    )

    return {"messages": [response]}


def metrics_splitter(state: MetricsAgentState) -> MetricsAgentState:
    system_message = SystemMessage(content=SPLIT_INTO_LIST_MESSAGE)
    data_message = HumanMessage(content=f"{state["messages"][-1]}")

    response: PresentationNameAndMetricsList = call_llm(
        llm_structured_metrics, [system_message, data_message], config=config_strict
    )

    # DEBUG
    print(f"SELECTED METRICS: {response.metrics}")

    return {
        "metrics": response.metrics,
        "presentation_name": response.presentation_name,
    }


def funcGen_slide_promt_generator(index: int):
    def slide_promt_generator(state: PromptAgentState) -> PromptAgentState:
        idx: int = state["prompt_gen_idx"][index]
        if idx >= len(state["metrics"]):
            return {"prompt_gen_idx": {index: -1}}

        system_message = SystemMessage(content=PROMPTS_SYSTEM_MESSAGE)
        data_message = HumanMessage(content=f"ПОКАЗАТЕЛЬ: {state["metrics"][idx]}")

        response = call_llm(
            llm_structured_prompts,
            [system_message, data_message],
            config=config_creative,
        )

        return {
            "prompts": {idx: response},
            "prompt_gen_idx": {
                index: state["prompt_gen_idx"][index] + WORKERS_POOL_SIZE
            },
        }

    return slide_promt_generator


# Transition to draft state
def flatten_prompts(state: PromptAgentState) -> PromptAgentState:
    for metric_prompts in state["prompts"].values():
        state["flat_prompts"].prompts += metric_prompts.prompts

    return {"flat_prompts": state["flat_prompts"]}


def funcGen_slide_json_generator(index: int):
    def slide_json_generator(state: DraftAgentState) -> DraftAgentState:
        idx: int = state["json_gen_idx"][index]
        if idx >= len(state["flat_prompts"].prompts):
            return {"json_gen_idx": {index: -1}}

        response = call_llm(
            llm_structured_jsons,
            [
                HumanMessage(content=state["flat_prompts"].prompts[idx]),
                SystemMessage(content=JSON_SYSTEM_MESSAGE),
            ],
            config=config_creative,
        )

        return {
            "draft_slides": {idx: create_draft_json(response)},
            "json_gen_idx": {index: state["json_gen_idx"][index] + WORKERS_POOL_SIZE},
        }

    return slide_json_generator


def do_nothing_node(state: dict) -> dict:
    return {}


# Edge decision
def should_continue_prompts_gen(state: PromptAgentState) -> bool:
    return any([idx != -1 for idx in state["prompt_gen_idx"].values()])


def should_continue_json_gen(state: DraftAgentState) -> bool:
    return any([idx != -1 for idx in state["json_gen_idx"].values()])


def should_continue_metrics(state: MetricsAgentState) -> bool:
    return bool(state["messages"][-1].tool_calls)


metrics_tools_node = ToolNode(tools=tools)
