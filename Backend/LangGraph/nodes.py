from asyncio import Semaphore, to_thread

import settings
from constants.messages import (
    DRAFT_SYSTEM_MESSAGE,
    METRICS_SYSTEM_MESSAGE,
    OBJECT_TYPE_EXPLAIN_MESSAGE,
    PROMPTS_SYSTEM_MESSAGE,
    SPLIT_INTO_LIST_MESSAGE,
)
from csv_preprocessor import analyze, convert_analyze_result_to_message
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Send
from llm_setup import (
    config_creative,
    config_strict,
    llm_structured_drafts,
    llm_structured_metrics,
    llm_structured_prompts,
    llm_with_data_tools,
)
from models import Json, PresentationNameAndMetricsList, PromptList
from settings import WORKERS_POOL_SIZE, call_llm, call_llm_sync
from slide_editing.manager import EditRequestManager
from state import (
    DraftAgentState,
    FinalJsonState,
    MetricsAgentState,
    OverallState,
    PromptAgentState,
)
from tools import data_tools
from utils import (
    build_promt_message,
    create_draft_json,
    normalize_draft_slides,
    parse_json_to_draft,
    print_help,
    print_slide,
)

semaphore = Semaphore(WORKERS_POOL_SIZE)


def setupper(state: MetricsAgentState) -> MetricsAgentState:
    if settings.sql_data is None:
        raise AttributeError("sql_data not provided, unable to process data")

    analyze_result = analyze(settings.sql_data.to_df())

    return {"data_anlyze_result": convert_analyze_result_to_message(analyze_result)}


def data_agent(state: MetricsAgentState) -> dict:
    """Агент с доступом к данным через инструмент. Основная задача -- выделение из промпта пользователя и таблицы с данными показателей, по которым позже будет построена таблица."""
    if settings.sql_data is None:
        raise AttributeError("sql_data not provided, unable to process data")

    system_message = SystemMessage(content=METRICS_SYSTEM_MESSAGE)
    data_message = HumanMessage(content=f"""ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {state["start_prompt"]}

ЗАГОЛОВКИ ТАБЛИЦЫ С ДАННЫМИ: {str(settings.sql_data.columns)}

ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}""")

    response = call_llm_sync(
        llm_with_data_tools,
        [system_message, data_message] + state["messages"],
        config=config_creative,
    )

    return {"messages": [response]}


def metrics_splitter(state: MetricsAgentState) -> dict:
    system_message = SystemMessage(content=SPLIT_INTO_LIST_MESSAGE)
    data_message = HumanMessage(content=f"{state["messages"][-1]}")

    response: PresentationNameAndMetricsList = call_llm_sync(
        llm_structured_metrics, [system_message, data_message], config=config_strict
    )

    # DEBUG
    print(f"SELECTED METRICS: {response.metrics}")

    return {
        "metrics": response.metrics,
        "presentation_name": response.presentation_name,
    }


def prompt_prepare_tasks(state: PromptAgentState) -> dict:
    return {"tasks": [(i, metric) for i, metric in enumerate(state["metrics"])]}


async def generate_prompt(state: dict) -> dict:
    async with semaphore:
        response: PromptList = await call_llm(
            llm_structured_prompts,
            [
                SystemMessage(content=PROMPTS_SYSTEM_MESSAGE),
                HumanMessage(
                    content=f"ПОКАЗАТЕЛЬ: {state["metric"]}\n\n"
                    f"ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}"
                ),
            ],
            config=config_creative,
        )

        return {"prompts": {state["idx"]: response}}


def combine_prompts(state: PromptAgentState) -> PromptAgentState:
    prompts_dict = state.get("prompts", {})

    prompt_list = []
    for i in sorted(prompts_dict.keys()):
        prompt_list += prompts_dict[i].prompts

    return {"flat_prompts": PromptList(prompts=prompt_list)}


def draft_prepare_tasks(state: DraftAgentState) -> DraftAgentState:
    return {
        "tasks": [
            (i, promptSlide)
            for i, promptSlide in enumerate(state["flat_prompts"].prompts)
        ]
    }


async def generate_draft(state: dict) -> dict:
    async with semaphore:
        response = await call_llm(
            llm_structured_drafts,
            [
                SystemMessage(
                    content=f"{DRAFT_SYSTEM_MESSAGE}\n\n{OBJECT_TYPE_EXPLAIN_MESSAGE}"
                ),
                HumanMessage(
                    content=f"ПРОМПТ ДЛЯ СЛАЙДА: {state["prompt"]}\n\n"
                    # f"ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}"
                ),
            ],
            config=config_creative,
        )

        return {"draft_slides": {state["idx"]: response}}


def combine_drafts(state: dict) -> DraftAgentState:
    drafts = normalize_draft_slides(state.get("draft_slides", {}))

    return {
        "draft_slides": {
            idx: [create_draft_json(slide)] for idx, slide in drafts.items()
        }
    }


async def review_and_edit(state: OverallState) -> dict:
    draft_slides: dict[int, list[Json]] = state["draft_slides"]
    manager = EditRequestManager(max_concurrent=WORKERS_POOL_SIZE)
    slide_nums = sorted(draft_slides.keys())
    current = slide_nums[0]

    def on_complete(slide_num, updated_slide, err):
        if err:
            print(f"\n[ERROR] Change request for slide {slide_num} failed: {err}")
        else:
            draft_slides[slide_num] += [create_draft_json(updated_slide)]
            print(f"\n[DONE] Slide {slide_num} updated.")
        print(f"[slide {current}] > ", end="", flush=True)

    print_help()
    print_slide(draft_slides[current][-1], current)

    while True:
        cmd = (await to_thread(input, f"[slide {current}] > ")).strip().lower()

        match cmd:
            case "q" | "quit" | "exit" | "done":
                pending = len(manager.pending_tasks)
                if pending:
                    print(
                        f"Waiting for {pending} pending change request(s) to finish..."
                    )
                    await manager.wait_all()
                break

            case "n" | "next":
                idx = slide_nums.index(current)
                current = slide_nums[min(idx + 1, len(slide_nums) - 1)]
                print_slide(draft_slides[current][-1], current)

            case "p" | "prev":
                idx = slide_nums.index(current)
                current = slide_nums[max(idx - 1, 0)]
                print_slide(draft_slides[current][-1], current)

            case cmd if cmd.startswith("goto "):
                try:
                    idx = int(cmd.split(" ", 1)[1])
                    if idx in draft_slides:
                        current = idx
                        print_slide(draft_slides[current][-1], current)
                    else:
                        print("Invalid slide number.")
                except ValueError:
                    print("Usage: goto <index>")

            case "s" | "show":
                print_slide(draft_slides[current][-1], current)

            case "status" | "st":
                print(
                    f"Active: {manager._active}/{manager.max_concurrent}, "
                    f"pending tasks: {len(manager.pending_tasks)}"
                )

            case cmd if cmd.startswith("edit "):
                change_prompt = cmd[len("edit ") :].strip()
                if not change_prompt:
                    print("Empty change request ignored.")
                    continue

                accepted = await manager.submit(
                    current,
                    parse_json_to_draft(draft_slides[current][-1]),
                    change_prompt,
                    on_complete,
                )

                if accepted:
                    print(
                        f"Change request for slide {current} submitted "
                        f"({manager._active}/{manager.max_concurrent} active)."
                    )
                else:
                    print(
                        f"[LIMIT REACHED] {manager.max_concurrent} concurrent edit requests "
                        f"already running. Wait for one to finish and try again."
                    )

            case "h" | "?" | "help":
                print_help()

            case _:
                print("Unknown command. Type 'help' for commands.")

    return {"draft_slides": draft_slides}


# Edge decision
def prompt_route_tasks(state: PromptAgentState) -> list[Send]:
    return [
        Send(
            "generate_prompt",
            {
                "idx": idx,
                "metric": metric,
                "data_anlyze_result": state["data_anlyze_result"],
            },
        )
        for idx, metric in state["tasks"]
    ]


def draft_route_tasks(state: DraftAgentState) -> list[Send]:
    return [
        Send(
            "generate_draft",
            {
                "idx": idx,
                "prompt": build_promt_message(promptSlide),
                "data_anlyze_result": state["data_anlyze_result"],
            },
        )
        for idx, promptSlide in state["tasks"]
    ]


def final_json_route_tasks(state: FinalJsonState) -> list[Send]:
    return [
        Send("generate_final_json", {"idx": idx, "draft_slide": draft})
        for idx, draft in state["draft_slides"].values()
    ]


def should_continue_metrics(state: MetricsAgentState) -> bool:
    last = state["messages"][-1]
    return bool(getattr(last, "tool_calls", None))


sql_tool_node = ToolNode(tools=data_tools)
