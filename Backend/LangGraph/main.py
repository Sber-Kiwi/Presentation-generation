from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from pydantic import SecretStr, BaseModel, Field
import pandas as pd
from os import getenv
from io import StringIO
from collections import deque

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_experimental.agents import create_pandas_dataframe_agent

from JSON_SHEMAS import JSON_SCHEMA_FINAL, JSON_SCHEMA_DRAFT
from MESSAGES import *

json = Annotated[str, "This is a json formatted string."]


class MetricsList(BaseModel):
    metrics: list[str] = Field(
        description="Список показателей финансового анализа, выделенных из основного"
        " промта. Нужен для состовления презентации."
    )


class PromptList(BaseModel):
    prompts: dict[str, list[str]] = Field(
        description="Список промптов для нейронной сети для каждого показателя, по "
        "каждому из которых составляется один слайд презентации. Содержит словесное "
        "описание содержания слайда. Каждый элемент массива - промпт для отдельного слайда."
    )


class AgentState(TypedDict):
    current_message: str
    messages: Annotated[Sequence[BaseMessage], add_messages]

    metrics: MetricsList  # Node AI-1 answer

    prompts: PromptList

    draft_slides: list[json]

    # last_five_versions: list[json]
    # related_slides: list[json]

    # result_slides: list[json]  # Node AI-2 answer


load_dotenv()


@tool
def get_financial_data(request: str) -> str:
    """Функция для получения данных из таблицы CSV по текстовому запросу.
    С помощью нее можно по заголовкам получить необходимые данные из таблицы.

    Args:
        request (str): текст запроса к данным, который нужно выполнить.
    Returns:
        str: Ответ на запрос"""
    global csv_data
    data = pd.read_csv(StringIO(csv_data), sep=";")
    agent = create_pandas_dataframe_agent(
        llm, data, verbose=True, agent_type="tool-calling", allow_dangerous_code=True
    )

    response = agent.invoke([AIMessage(content=request)])

    return response["output"]


tools = [get_financial_data]

llm = ChatOpenAI(
    model="qwen2.5-7b-instruct",
    # base_url="http://192.168.50.81:1234/v1",
    base_url="http://127.0.0.1:1234/v1",
    api_key=SecretStr("lm-studio"),
    temperature=0.1,
)


llm_structured_metrics = llm.with_structured_output(MetricsList)

llm_structured_prompts = llm.with_structured_output(PromptList)

llm_structured_jsons = llm.with_structured_output(
    JSON_SCHEMA_DRAFT, method="json_schema"
)


llm_with_tools = llm.bind_tools(tools)

csv_data: str = ""


def setupper(state: AgentState) -> AgentState:
    state["metrics"] = MetricsList(metrics=list())
    state["prompts"] = PromptList(prompts=dict())

    return state


def data_agent(state: AgentState) -> AgentState:
    """Agent that can query the CSV data via the tool."""
    global csv_data

    system_message = SystemMessage(content=DATA_AGENT_SYSTEM_MESSAGE)
    data_message = HumanMessage(content=csv_data[: csv_data.find("\n")])

    response = llm_with_tools.invoke([system_message, data_message] + state["messages"])

    print(f"MESSAGES: {state["messages"]}")
    return {"messages": [response]}


def metrics_splitter(state: AgentState) -> AgentState:
    state["messages"] = state["messages"][-1]

    global csv_data
    user_message = HumanMessage(content=state["current_message"])
    data_message = HumanMessage(
        content=f"ЗАГОЛОВКИ ТАБЛИЦЫ С ДАННЫМИ: {csv_data[:csv_data.find("\n")]}"
    )

    system_message = SystemMessage(content=METRICS_SYSTEM_MESSAGE)

    state["metrics"] = llm_structured_metrics.invoke(
        [system_message, data_message, user_message]
    )

    print(f"SELECTED METRICS: {state["metrics"]}")
    return state


def slide_promt_generator(state: AgentState) -> AgentState:
    system_message = SystemMessage(content=PROMPTS_SYSTEM_MESSAGE)

    state["prompts"] = llm_structured_prompts.invoke([system_message])

    return state


def slide_json_generator(state: AgentState) -> AgentState:
    system_message = SystemMessage(content=JSON_SYSTEM_MESSAGE)
    for metric, prompts in state["prompts"].prompts:
        for prompt in prompts:
            human_message = HumanMessage(content=prompt)

            response = llm_structured_prompts.invoke([human_message, system_message])
            state["draft_slides"] += [response]

    return state


def should_continue_metrics(state: AgentState) -> bool:
    return bool(state["messages"][-1].tool_calls)


# def should_continue_promts(state: AgentState) -> bool:
#     return state["current_metric"] < len(state["metrics"].metrics) - 1


def should_continue_jsons(state: AgentState) -> bool:
    return len(state["prompts"].prompts) != 0


def main() -> None:
    graph = StateGraph(AgentState)

    graph.add_node("setup", setupper)
    graph.add_node("data_agent", data_agent)
    graph.add_node("extract_metrics", metrics_splitter)
    graph.add_node("metrics_tools", ToolNode(tools=tools))
    graph.add_node("generate_prompts", slide_promt_generator)
    graph.add_node("generate_draft", slide_json_generator)

    graph.add_edge(START, "setup")

    graph.add_edge("setup", "data_agent")

    graph.add_edge("metrics_tools", "data_agent")
    graph.add_conditional_edges(
        "data_agent",
        should_continue_metrics,
        {False: "extract_metrics", True: "metrics_tools"},
    )
    graph.add_edge("extract_metrics", "generate_prompts")
    graph.add_edge("generate_prompts", "generate_draft")

    graph.add_conditional_edges(
        "generate_draft",
        should_continue_jsons,
        {False: END, True: "generate_draft"},
    )

    agent = graph.compile()

    global csv_data
    with open("data/data.csv", "r") as file:
        csv_data = file.read()

    # from IPython.display import Image, display
    # display(Image(agent.get_graph().draw_mermaid_png()))
    # exit()

    user_input = input("Enter: ")
    while user_input != "exit":
        agent.invoke({"current_message": user_input})
        user_input = input("Enter: ")


if __name__ == "__main__":
    main()
