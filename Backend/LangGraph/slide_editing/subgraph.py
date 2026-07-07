from langgraph.graph.state import CompiledStateGraph, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage

from constants.messages import CHANGE_REQUEST_SYSTEM_MESSAGE
from settings import call_llm
from llm_setup import llm_with_edit_tools
from tools import slide_tools
from state import EditAgentState

edit_tool_node = ToolNode(tools=slide_tools)


async def edit_agent(state: EditAgentState) -> dict:
    system_message = SystemMessage(content=CHANGE_REQUEST_SYSTEM_MESSAGE)
    data_message = HumanMessage(
        content=f"""ПРОМПТ НА ИЗМЕНЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ: [{state["change_prompt"]}]

ТЕКУЩИЙ СЛАЙД, НА КОТОРОМ НЕОБХОДИМЫ ИЗМЕНЕНИЯ: [{str(state["current_slide"])}]

ИСТОРИЯ ИЗМЕНЕНИЙ СЛАЙДА: [{str(state["slide_versions"])}]"""
    )

    response = await call_llm(
        llm_with_edit_tools,
        [system_message, data_message] + state["messages"],
    )

    return {"messages": [response]}


def should_continue_edit(state: EditAgentState) -> bool:
    last = state["messages"][-1]
    return bool(getattr(last, "tool_calls", None))


def build_edit_subgraph() -> CompiledStateGraph:
    subgraph = StateGraph(EditAgentState)
    subgraph.add_node("edit_agent", edit_agent)
    subgraph.add_node("edit_tools", edit_tool_node)
    subgraph.add_edge(START, "edit_agent")
    subgraph.add_conditional_edges(
        "edit_agent", should_continue_edit, {True: "edit_tools", False: END}
    )
    subgraph.add_edge("edit_tools", "edit_agent")
    return subgraph.compile()
