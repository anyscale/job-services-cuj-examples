from ray import serve
from ray.serve.schema import ServeStatus

@serve.deployment
class GetStatus:

    def __call__(self, *args) -> ServeStatus:
        status = serve.status()
        return status

app = GetStatus.bind()
