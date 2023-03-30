import asyncio
import logging
import subprocess
import time
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import ray
from ray import serve

app = FastAPI()

logger = logging.getLogger("ray.serve")

@ray.remote(num_gpus=1)
def stop_ray_on_head_node():
    # Provide a grace period so the response can be returned.
    print("Killing head node in 5...")
    time.sleep(5)
    print("Killing head node!")
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

    @app.get("/healthcheck")
    def respond(self) -> PlainTextResponse:
        logger.info(f"Responding with '{self._response}'.")
        return PlainTextResponse(self._response)

    @app.post("/kill-head-node")
    async def kill(self) -> PlainTextResponse:
        if ray.available_resources().get("GPU", 0) < 1:
            msg = "Insufficient GPU resources for stop_ray_on_head_node task."
            logger.error(msg)
            return PlainTextResponse(msg, status_code=500)
        logger.info(f"Killing head node.")
        stop_ray_on_head_node.remote()
        return PlainTextResponse("ok")

bound = Updatable.bind()
