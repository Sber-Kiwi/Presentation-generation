import asyncio

import settings
from constants.messages import (
    DRAFT_SYSTEM_MESSAGE,
    METRICS_SYSTEM_MESSAGE,
    OBJECT_TYPE_EXPLAIN_MESSAGE,
    PROMPTS_SYSTEM_MESSAGE,
    SPLIT_INTO_LIST_MESSAGE,
)
from csv_preprocessor import analyze, convert_analyze_result_to_message
from dto import (
    EditFileIn,
    EditFileOut,
    EditResponse,
    ExportFileIn,
    InputAction,
    OutputAction,
    OutputError,
    read_file_input,
    send_message,
    write_result,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Send, interrupt
from llm_setup import (
    config_creative,
    config_strict,
    llm_structured_drafts,
    llm_structured_metrics,
    llm_structured_prompts,
    llm_with_data_tools,
)
from models import PresentationNameAndMetricsList, PromptList
from server_input import _read_json_line, _validate_body
from settings import WORKERS_POOL_SIZE, call_llm, call_llm_sync
from slide_editing.manager import EditRequestManager
from sqlalchemy import ExceptionContext
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
)

MAX_METRIC_RETRIES = 2
MAX_SLIDE_RETRIES = 2

semaphore = asyncio.Semaphore(WORKERS_POOL_SIZE)

edit_manager = EditRequestManager(WORKERS_POOL_SIZE)


def _can_accept_request(action: InputAction) -> bool:
    """Решает, готов ли сейчас граф принять запрос данного типа —
    например, если менеджер редактирования уже занят max_concurrent
    задачами, или граф сейчас не в состоянии, ожидающем этот action.
    """
    if action["action"] == "edit":
        return edit_manager._active < edit_manager.max_concurrent
    return True


async def setup_generate_request(state: OverallState) -> dict:
    if settings.sql_data is None:
        raise AttributeError("sql_data not provided, unable to process data")

    analyze_result = analyze(settings.sql_data.to_df())

    action = interrupt({"waiting_for": "generate_request"})
    
    send_message(OutputAction(task_id=action["task_id"], status="ready"))

    body_payload = await _read_json_line(f"тело запроса для action=generate")
    body = _validate_body(
        body_payload,
        InputAction(task_id=action["task_id"], action="generate"),
    )
    send_message(OutputAction(task_id=action["task_id"], status="accepted"))

    return {
        "data_anlyze_result": convert_analyze_result_to_message(analyze_result),
        "start_prompt": body["prompt"],
        "task_id": action["task_id"],
        "output_file": body["output_file"],
    }


async def data_agent(state: MetricsAgentState) -> dict:
    """Агент с доступом к данным через инструмент. Основная задача -- выделение из промпта пользователя и таблицы с данными показателей, по которым позже будет построена таблица."""
    if settings.sql_data is None:
        raise AttributeError("sql_data not provided, unable to process data")

    system_message = SystemMessage(content=METRICS_SYSTEM_MESSAGE)
    data_message = HumanMessage(content=f"""ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {state["start_prompt"]}

ЗАГОЛОВКИ ТАБЛИЦЫ С ДАННЫМИ: {str(settings.sql_data.columns)}

ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}""")

    for attempt in range(MAX_METRIC_RETRIES + 1):
        try:
            response = await call_llm(
                llm_with_data_tools,
                [system_message, data_message] + state["messages"],
                config=config_creative,
            )
            return {"messages": [response]}
        except Exception as e:
            print(f"[WARNING] Ошибка в data_agent (попытка {attempt + 1}/{MAX_METRIC_RETRIES + 1}): {e}")
            if attempt == MAX_METRIC_RETRIES + 1:
                raise e
            await asyncio.sleep(2**attempt)


async def metrics_splitter(state: MetricsAgentState) -> dict:
    system_message = SystemMessage(content=SPLIT_INTO_LIST_MESSAGE)
    data_message = HumanMessage(content=f"{state['messages'][-1]}")

    for attempt in range(MAX_METRIC_RETRIES + 1):
        try:
            response: PresentationNameAndMetricsList = await call_llm(
                llm_structured_metrics, [system_message, data_message], config=config_strict
            )
            return {
                "metrics": response.metrics,
                "presentation_name": response.presentation_name,
            }
        except Exception as e:
            print(f"[WARNING] Ошибка в metrics_splitter (попытка {attempt + 1}/{MAX_METRIC_RETRIES + 1}): {e}")
            if attempt == MAX_METRIC_RETRIES:
                raise e
            await asyncio.sleep(2**attempt)


def prompt_prepare_tasks(state: PromptAgentState) -> dict:
    return {"tasks": [(i, metric) for i, metric in enumerate(state["metrics"])]}


async def generate_prompt(state: dict) -> dict:
    async with semaphore:
        for attempt in range(MAX_METRIC_RETRIES + 1):
            try:
                response: PromptList = await call_llm(
                    llm_structured_prompts,
                    [
                        SystemMessage(content=PROMPTS_SYSTEM_MESSAGE),
                        HumanMessage(
                            content=f"ПОКАЗАТЕЛЬ: {state['metric']}\n\n"
                            f"ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}"
                        ),
                    ],
                    config=config_creative,
                )
                return {"prompts": {state["idx"]: response}}

            except Exception as e:
                print(
                    f"[WARNING] Ошибка генерации промпта для показателя "
                    f"'{state['metric']}' (попытка {attempt + 1}/{MAX_METRIC_RETRIES + 1}): {e}"
                )
                if attempt == MAX_METRIC_RETRIES:
                    print(
                        f"[SKIPPED] Показатель '{state['metric']}' пропущен "
                        f"после {MAX_METRIC_RETRIES + 1} неудачных попыток."
                    )
                    return {"prompts": {}}


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
        for attempt in range(MAX_SLIDE_RETRIES + 1):
            try:
                response = await call_llm(
                    llm_structured_drafts,
                    [
                        SystemMessage(
                            content=f"{DRAFT_SYSTEM_MESSAGE}\n\n{OBJECT_TYPE_EXPLAIN_MESSAGE}"
                        ),
                        HumanMessage(
                            content=f"ПРОМПТ ДЛЯ СЛАЙДА: {state['prompt']}\n\n"
                            # f"ВЫБОРКА ВСПОМОГАТЕЛЬНЫХ ДАННЫХ ИЗ ТАБЛИЦЫ: {state['data_anlyze_result']}"
                        ),
                    ],
                    config=config_creative,
                )
                return {"draft_slides": {state["idx"]: response}}

            except Exception as e:
                print(
                    f"[WARNING] Ошибка генерации черновика слайда для "
                    f"idx={state['idx']} (попытка {attempt + 1}/{MAX_SLIDE_RETRIES + 1}): {e}"
                )
                if attempt == MAX_SLIDE_RETRIES:
                    print(
                        f"[SKIPPED] Слайд idx={state['idx']} пропущен "
                        f"после {MAX_SLIDE_RETRIES + 1} неудачных попыток."
                    )
                    return {"draft_slides": {}}


def combine_drafts(state: dict) -> DraftAgentState:
    drafts = normalize_draft_slides(state.get("draft_slides", {}))

    return {
        "draft_slides": {idx: create_draft_json(slide) for idx, slide in drafts.items()}
    }


async def review_and_edit(state: OverallState) -> dict:
    """Обрабатывает один запрос на изменение слайда от сервера.
    Ограничивает число одновременно выполняемых запросов до
    max_concurrent -- если лимит достигнут, немедленно возвращает
    сообщение об ошибке без выполнения LLM-запроса.
    """
    action = interrupt({"waiting_for": "edit_request"})
    state["task_id"] = action["task_id"]

    if _can_accept_request(action):
        send_message(OutputAction(task_id=action["task_id"], status="ready"))
    else:
        send_message(OutputAction(task_id=action["task_id"], status="notready"))
        return {"edit_route": "edit"}

    body_payload = await _read_json_line(f"тело запроса для action={action["action"]}")
    body = _validate_body(body_payload, action)

    if action["action"] == "export":
        send_message(OutputAction(task_id=action["task_id"], status="accepted"))
        return {
            "task_id": action["task_id"],
            "edit_route": "export",
            "draft_slides": read_file_input(body["input_file"], "export").get(
                "slides", {}
            ),
            "output_file": body["output_file"],
        }

    # action["action"] == "edit"
    input_data = read_file_input(body["input_file"], "edit")
    current_slide = parse_json_to_draft(input_data["current_slide"])
    slide_versions = [
        parse_json_to_draft(version)
        for version in input_data["recent_versions_history"]
    ]
    change_prompt = input_data["edit_prompt"]

    result_holder: dict = {}
    done_event = asyncio.Event()

    def on_complete(updated_slide, err):
        if err:
            result_holder["error"] = str(err)
        else:
            result_holder["current_slide"] = updated_slide
        done_event.set()

    if _can_accept_request(action):
        send_message(OutputAction(task_id=state["task_id"], status="accepted"))

    accepted = await edit_manager.submit(
        current_slide=current_slide,
        change_prompt=change_prompt,
        versions=slide_versions,
        on_complete=on_complete,
    )

    if not accepted:
        send_message(OutputAction(task_id=state["task_id"], status="rejected"))
        return {"edit_route": "edit"}

    await done_event.wait()

    if "error" in result_holder:
        send_message(OutputError(task_id=state["task_id"], error_message=result_holder["error"]))
        return {"edit_route": "edit"}

    write_result(
        data=EditFileOut(
            edited_slide=create_draft_json(result_holder["current_slide"])
        ),
        file=body["output_file"],
    )

    send_message(
        EditResponse(task_id=state["task_id"], output_file=body["output_file"])
    )
    return {"edit_route": "edit"}


# Edge decision
def route_by_mode(state: OverallState) -> str:
    return "edit" if state["mode"] == "edit" else "generate"


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
            },
        )
        for idx, promptSlide in state["tasks"]
    ]


def route_after_edit(state: OverallState) -> str:
    if state["edit_route"] == "export":
        return "final_json_agent"
    return "edit_agent"


def final_json_route_tasks(state: FinalJsonState) -> list[Send]:
    return [
        Send("generate_final_json", {"idx": idx, "draft_slide": draft})
        for idx, draft in state["draft_slides"].values()
    ]


def should_continue_metrics(state: MetricsAgentState) -> bool:
    last = state["messages"][-1]
    return bool(getattr(last, "tool_calls", None))


sql_tool_node = ToolNode(tools=data_tools)
