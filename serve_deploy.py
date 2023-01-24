from ray import serve
from fastapi import FastAPI

app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class App:
    def __init__(self):
        self.should_fail = False

    @app.get("/healthcheck")
    def healthcheck(self):
        if self.should_fail:
            raise RuntimeError("Oh no")
        return "ok"

    @app.post("/set_should_fail")
    def set_should_fail(self):
        self.should_fail = True
        return "ok"

bound = App.bind()

if __name__ == "__main__":
    serve.run(bound)
