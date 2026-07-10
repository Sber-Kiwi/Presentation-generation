from models import (
    DraftSlide,
    FinalSlideData,
    PresentationNameAndMetricsList,
    PromptList,
)
from settings import simple_llm, thinking_llm
from tools import data_tools, slide_tools

llm_with_data_tools = thinking_llm.bind_tools(data_tools)
llm_with_edit_tools = thinking_llm.bind_tools(slide_tools)

config_strict = {
    "configurable": {
        "temperature": 0.0,
        "max_tokens": 4500,
    }
}
config_creative = {
    "configurable": {
        "temperature": 0.5,
        "max_tokens": 4500,
    }
}

llm_structured_metrics = simple_llm.with_structured_output(
    PresentationNameAndMetricsList
)

llm_structured_prompts = thinking_llm.with_structured_output(PromptList)

llm_structured_drafts = thinking_llm.with_structured_output(DraftSlide)

llm_structured_final = thinking_llm.with_structured_output(FinalSlideData)
