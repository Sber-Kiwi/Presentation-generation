import json
from typing import Literal, TypedDict

from models import Json
from pydantic import TypeAdapter
from utils import parse_json_to_draft


# --- Handshake ---
class InputAction(TypedDict):
    task_id: int
    action: Literal["generate", "edit", "export"]


input_action_validator = TypeAdapter(InputAction)


class OutputAction(TypedDict):
    task_id: int
    status: Literal["accepted", "rejected", "ready", "notready"]


class OutputError(TypedDict):
    error_message: str


# --- Generate tasks ---
class GenerateRequest(TypedDict):
    task_id: int
    prompt: str
    output_file: str


class GenerateResponse(TypedDict):
    task_id: int
    output_file: str


# --- Edit tasks ---
class EditRequest(TypedDict):
    task_id: int
    input_file: str
    output_file: str


class EditResponse(TypedDict):
    task_id: int
    output_file: str


# --- Export tasks ---
ExportRequest = EditRequest

ExportResponse = EditResponse


# --- Files schema ---
class EditFileIn(TypedDict):
    edit_prompt: str
    current_slide: Json
    recent_versions_history: list[Json]


class EditFileOut(TypedDict):
    edited_slide: Json


# GenerateFileIn does not exist because input is passed in console


class GenerateFileOut(TypedDict):
    presentation_name: str
    drafts: list[Json]


class ExportFileIn(TypedDict):
    slides: list[Json]


class ExportFileOut(TypedDict):
    final_slides: list[Json]


# --- HELPERS ---
def send_message(data):
    print(json.dumps(data, ensure_ascii=False))


def write_result(data, file: str):
    with open(file, "w+") as f:
        print(json.dumps(data, ensure_ascii=False), file=f)


def read_file_input(
    file: str, type: Literal["edit", "export"]
) -> EditFileIn | ExportFileIn:
    if type == "edit":
        with open(file, "r") as f:
            data = json.load(f)

            return EditFileIn(
                edit_prompt=data["edit_prompt"],
                current_slide=data["current_slide"],
                recent_versions_history=data["recent_versions_history"],
            )
    elif type == "export":
        with open(file, "r") as f:
            data = json.load(f)

            return ExportFileIn(slides=data["slides"])


_action_adapters = {
    "generate": TypeAdapter(GenerateRequest),
    "edit": TypeAdapter(EditRequest),
    "export": TypeAdapter(ExportRequest),
}
