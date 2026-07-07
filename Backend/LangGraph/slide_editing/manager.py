import asyncio

from models import DraftSlide
from state import EditAgentState

from .subgraph import build_edit_subgraph

edit_subgraph = build_edit_subgraph()


class EditRequestManager:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self._active = 0
        self._lock = asyncio.Lock()
        self.pending_tasks: set[asyncio.Task] = set()

    async def submit(
        self,
        slide_num: int,
        current_slide: DraftSlide,
        change_prompt: str,
        on_complete,
    ) -> bool:
        async with self._lock:
            if self._active >= self.max_concurrent:
                return False
            self._active += 1

        async def _run():
            try:
                sub_input: EditAgentState = {
                    "change_prompt": change_prompt,
                    "current_slide": current_slide,
                    "slide_versions": [],
                    "messages": [],
                    "slide_changed": False,
                }
                result = await edit_subgraph.ainvoke(sub_input)
                on_complete(slide_num, result["current_slide"], None)
            except Exception as e:
                on_complete(slide_num, None, e)
            finally:
                async with self._lock:
                    self._active -= 1

        task = asyncio.create_task(_run())
        self.pending_tasks.add(task)
        task.add_done_callback(self.pending_tasks.discard)
        return True

    async def wait_all(self):
        if self.pending_tasks:
            await asyncio.gather(*self.pending_tasks, return_exceptions=True)
