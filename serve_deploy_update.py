import asyncio

from ray import serve
from typing import Any, Dict

@serve.deployment(user_config={"response": "Hello world!", "should_fail": False})
class Updatable:
    def __init__(self):
        self._response: str = ""

    async def reconfigure(self, d: Dict[str, Any]):
        self._response = d.get("response", "Hello default!")
        self._should_fail = d.get("should_fail", False)
        await asyncio.sleep(10) # Sleep to avoid the UPDATING state being very transient.

    def check_health(self):
        if self._should_fail:
            raise Exception("Intentionally failing.")

    async def __call__(self, *args) -> str:
        return self._response

bound = Updatable.bind()
