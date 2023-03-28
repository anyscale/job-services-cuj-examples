import asyncio
import logging
import subprocess
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import ray
from ray import serve

app = FastAPI()

logger = logging.getLogger("ray.serve")

@ray.remote(num_gpus=1)
def stop_ray_on_head_node():
    return subprocess.check_output("ray stop -f", shell=True)


@serve.deployment(user_config={"response": "Hello world!", "should_fail": False})
@serve.ingress(app)
class Updatable:
    def __init__(self):
        self._response: str = ""

    async def reconfigure(self, d: Dict[str, Any]):
        self._response = d.get("response", "Hello default!")
        self._should_fail = d.get("should_fail", False)
        await asyncio.sleep(10) # Sleep to avoid the UPDATING state being very transient.

    def check_health(self):
        if self._should_fail:
            logger.info("Failing health check intentionally.")
            raise Exception("Intentionally failing.")

    @app.get("/")
    def respond(self) -> PlainTextResponse:
        logger.info(f"Responding with '{self._response}'.")
        return PlainTextResponse(self._response)

    @app.post("/kill-head-node")
    async def kill(self) -> PlainTextResponse:
        logger.info(f"Killing head node.")
        await stop_ray_on_head_node.remote()
        return PlainTextResponse("ok")

bound = Updatable.bind()
