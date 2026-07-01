from langchain_openai import ChatOpenAI

from langchain_mistralai import ChatMistralAI

from dotenv import load_dotenv

from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from httpx import HTTPStatusError

from duckdb import DuckDBPyConnection, DuckDBPyRelation

load_dotenv()

WORKERS_POOL_SIZE = 1


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HTTPStatusError),
    reraise=True,
)
def call_llm(llm, messages, config=None):
    return llm.invoke(messages, config=config)


llm = ChatOpenAI(
    model="qwen2.5-7b-instruct",
    # base_url="http://192.168.50.81:1234/v1",
    # base_url="http://127.0.0.1:1234/v1",
    base_url="http://100.94.157.2:1234/v1",
    temperature=0.0,
)


# llm = ChatMistralAI(temperature=0)
# llm = ChatMistralAI(model_name="mistral-large-latest", temperature=0)
# llm = ChatMistralAI(model_name="mistral-small-2503", temperature=0)

sql_data: DuckDBPyRelation | None = None
con: DuckDBPyConnection | None = None
