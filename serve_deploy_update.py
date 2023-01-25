from ray import serve
from typing import Any, Dict

@serve.deployment(user_config={"response": "Hello world!", "should_fail": False})
class Updateable:
    def __init__(self):
        self._response: str = ""

    def reconfigure(self, d: Dict[str, Any]):
        self._response = d.get("response", "Hello default!")
        self._should_fail = d.get("should_fail", False)

    def check_health(self):
        if self._should_fail:
            raise Exception("Intentionally failing.")

    def __call__(self, *args) -> str:
        return self._response

bound = Updateable.bind()
