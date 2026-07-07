import duckdb
import asyncio

from graph import build_graph, CompiledStateGraph
import settings


async def main() -> None:
    settings.con = duckdb.connect()
    settings.sql_data = settings.con.read_csv("Backend/LangGraph/data/data.csv")

    agent: CompiledStateGraph = build_graph()

    # from IPython.display import Image

    # image = Image(agent.get_graph().draw_mermaid_png())
    # with open("saved_image.png", "wb") as f:
    #     f.write(image.data)
    # exit()

    # user_input = input("Enter: ")
    user_input = (
        "Создай мне презентацию на основе таблицы с данными, которую я тебе передал"
    )
    while user_input != "exit":
        await settings.call_llm(agent, {"start_prompt": user_input})
        user_input = input("Enter: ")


if __name__ == "__main__":
    asyncio.run(main())
