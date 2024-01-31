from ray import serve
from ray.serve.schema import ServeStatus

from typing import Dict

@serve.deployment
class GetStatus:

    def __init__(self, version: str):
        self.version = version

    def __call__(self, *args) -> ServeStatus:
        status = serve.status()
        return {
            "status": status,
            "version": self.version,
        }


def build_app(args: Dict[str, str]):
    return GetStatus.bind(args["version"])
