from langchain_core.runnables import ConfigurableField

from settings import llm
from tools import tools
from constants.json_schemas import JSON_SCHEMA_DRAFT
from models import PresentationNameAndMetricsList, PromptList, DraftSlide

llm_with_tools = llm.bind_tools(tools)

llm = llm.configurable_fields(temperature=ConfigurableField(id="temperature"))

config_strict = {"configurable": {"temperature": 0.0}}
config_creative = {"configurable": {"temperature": 1.0}}

llm_structured_metrics = llm.with_structured_output(PresentationNameAndMetricsList)

llm_structured_prompts = llm.with_structured_output(PromptList)

llm_structured_jsons = llm.with_structured_output(DraftSlide)
