import os

from dotenv import load_dotenv
from duckdb import DuckDBPyConnection, DuckDBPyRelation
from httpx import HTTPStatusError
from langchain.chat_models import init_chat_model
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()

WORKERS_POOL_SIZE = os.getenv("WORKERS_POOL_SIZE")
if WORKERS_POOL_SIZE is None or int(WORKERS_POOL_SIZE) < 0:
    WORKERS_POOL_SIZE = 1
else:
    WORKERS_POOL_SIZE = int(WORKERS_POOL_SIZE)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HTTPStatusError),
    reraise=True,
)
async def call_llm(llm, messages, config=None):
    return await llm.ainvoke(messages, config=config)


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HTTPStatusError),
    reraise=True,
)
def call_llm_sync(llm, messages, config=None):
    return llm.invoke(messages, config=config)


if simple_model_name := os.getenv("SIMPLE_CHAT_MODEL_NAME"):
    simple_llm = init_chat_model(
        simple_model_name,
        base_url=os.getenv("CONNECT_BASE_URL"),
        configurable_fields=("temperature", "max_concurrency", "max_tokens"),
        temperature=0.0,
    )
if thinking_model_name := os.getenv("THINKING_CHAT_MODEL_NAME"):
    thinking_llm = init_chat_model(
        thinking_model_name,
        base_url=os.getenv("CONNECT_BASE_URL"),
        configurable_fields=("temperature", "max_concurrency", "max_tokens"),
        temperature=0.0,
    )

if (simple_model_name is None or simple_model_name == "") and (
    thinking_model_name is None or thinking_model_name == ""
):
    raise ValueError(
        'At least one of "SIMPLE_CHAT_MODEL_NAME" or "THINKING_CHAT_MODEL_NAME" was needed, but not provided.'
    )
if simple_model_name is None or simple_model_name == "":
    simple_llm = thinking_llm
if thinking_model_name is None or thinking_model_name == "":
    thinking_llm = simple_llm

sql_data: DuckDBPyRelation | None = None
con: DuckDBPyConnection | None = None
