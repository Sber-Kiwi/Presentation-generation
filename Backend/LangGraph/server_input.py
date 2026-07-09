import asyncio
import json
import sys

from dto import (
    EditRequest,
    ExportRequest,
    GenerateRequest,
    InputAction,
    _action_adapters,
)
from pydantic import ValidationError


class ProtocolError(Exception):
    """Ошибка протокола обмена сообщениями с сервером."""


async def _read_json_line(prompt_label: str) -> dict:
    line = await asyncio.to_thread(sys.stdin.readline)
    line = line.strip()

    if not line:
        raise ProtocolError(f"Получен пустой ввод при ожидании: {prompt_label}")

    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        raise ProtocolError(f"Некорректный JSON при ожидании {prompt_label}: {e}")


def _validate_action(payload: dict) -> InputAction:
    if "task_id" not in payload or "action" not in payload:
        raise ProtocolError(f"Отсутствуют обязательные поля task_id/action: {payload}")

    if payload["action"] not in ("generate", "edit", "export"):
        raise ProtocolError(f"Неизвестное действие action: {payload['action']}")

    return {"task_id": payload["task_id"], "action": payload["action"]}


def _validate_body(
    payload: dict, action: InputAction
) -> GenerateRequest | EditRequest | ExportRequest:
    body_task_id = payload.get("task_id")

    if body_task_id != action["task_id"]:
        raise ProtocolError(
            f"task_id не совпадает: в заголовке {action['task_id']}, "
            f"в теле запроса {body_task_id}"
        )

    adapter = _action_adapters[action["action"]]

    try:
        return adapter.validate_python(payload)
    except ValidationError as e:
        raise ProtocolError(
            f"Некорректное тело запроса для action={action['action']}: {e}"
        )


async def read_action_request(waiting_for: str) -> InputAction:
    """Читает и валидирует только заголовок запроса (InputAction)."""
    payload = await _read_json_line("заголовок запроса (InputAction)")

    if (
        waiting_for == "edit_request" and payload["action"] not in ("edit", "export")
    ) or (waiting_for == "generate_request" and payload["action"] != "generate"):
        raise ProtocolError(
            f"Input type: {payload['action']} did not match expected {waiting_for}"
        )

    return _validate_action(payload)
