from settings import WORKERS_POOL_SIZE, simple_llm, thinking_llm
from tools import data_tools, slide_tools
from models import PresentationNameAndMetricsList, PromptList, DraftSlide

llm_with_data_tools = thinking_llm.bind_tools(data_tools)
llm_with_edit_tools = thinking_llm.bind_tools(slide_tools)

config_strict = {
    "configurable": {
        "temperature": 0.0,
        "max_tokens": 3000,
        "max_concurrency": WORKERS_POOL_SIZE,
    }
}
config_creative = {
    "configurable": {
        "temperature": 0.5,
        "max_tokens": 3000,
        "max_concurrency": WORKERS_POOL_SIZE,
    }
}

llm_structured_metrics = simple_llm.with_structured_output(
    PresentationNameAndMetricsList
)

llm_structured_prompts = thinking_llm.with_structured_output(PromptList)

llm_structured_drafts = thinking_llm.with_structured_output(DraftSlide)
