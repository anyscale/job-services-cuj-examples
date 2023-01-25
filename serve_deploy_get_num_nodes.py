from typing import Dict

import ray
from ray import serve

@serve.deployment
class GetNumNodes:
    def __init__(self):
        pass

    def __call__(self, *args) -> Dict[str, int]:
        r = {"alive": 0, "dead": 0}
        nodes = ray.nodes()
        for node in ray.nodes():
            if node["Alive"]:
                r["alive"] += 1
            else:
                r["dead"] += 1

        return r

get_num_nodes = GetNumNodes.bind()
