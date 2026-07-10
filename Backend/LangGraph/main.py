import argparse
import asyncio

import duckdb
import settings
from dto import (
    ExportFileOut,
    ExportResponse,
    OutputAction,
    OutputError,
    send_message,
    write_result,
)
from graph import CompiledStateGraph, build_graph
from langgraph.types import Command
from nodes import _can_accept_request
from server_input import ProtocolError, read_action_request


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        help="Mode of runnig the script",
        choices=["start", "edit"],
        default="start",
    )
    parser.add_argument("-f", "--file", type=str, help="Path to the CSV file")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    agent: CompiledStateGraph = build_graph()
    print("agent started")
    config = {"configurable": {"thread_id": "test-session"}}

    if args.file is None:
        raise ValueError(
            "Please provide a path to the CSV file using the -f or --file argument."
        )

    from csv_preprocessor import load_csv
    settings.con = duckdb.connect()
    df = load_csv(args.file)
    settings.con.register("sql_data", df)
    settings.sql_data = settings.con.table("sql_data")

    result = await agent.ainvoke({"mode": args.mode}, config=config)

    while "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        waiting_for = interrupt_info["waiting_for"]

        try:
            action = await read_action_request(waiting_for)
        except ProtocolError as e:
            send_message(OutputError(task_id=-1, error_message=str(e)))
            continue

        expected_actions = {
            "generate_request": ("generate",),
            "edit_request": ("edit", "export"),
        }.get(waiting_for, ())

        if action["action"] not in expected_actions:
            send_message(OutputAction(task_id=action["task_id"], status="rejected"))
            continue

        if not _can_accept_request(action):
            send_message(OutputAction(task_id=action["task_id"], status="notready"))
            continue

        # Резюмируем узел заголовком запроса — сам узел решит, что делать
        # дальше (edit или export), отправит "ready" и прочитает тело запроса.
        result = await agent.ainvoke(Command(resume=action), config=config)

    write_result(
        data=ExportFileOut(final_slides=result["final_slides"]),
        file=result["output_file"],
    )

    send_message(
        ExportResponse(task_id=action["task_id"], output_file=result["output_file"])
    )


if __name__ == "__main__":
    asyncio.run(main())
