import asyncio
import ray
import time
import random

# We set num_cpus to zero because this actor will mostly just block on I/O.
@ray.remote(num_cpus=16)
class SignalActor:
    def __init__(self):
        self.ready_event = asyncio.Event()
        self.counter = 0

    def send(self, clear=False):
        self.ready_event.set()
        if clear:
            self.ready_event.clear()

    async def wait(self, should_wait=True):
        if should_wait:
            await self.ready_event.wait()

    def add_count(self):
        print("added")
        self.counter += 1

    def get_count(self):
        return self.counter


@ray.remote
def wait_and_go(signal):
    print("wait...")
    time.sleep(10)

    signal.add_count.remote()

    ray.get(signal.wait.remote())

    print("go!", random.random())

# Start 3 actors to trigger autoscaler
signals = []
for i in range(3):
    signals.append(SignalActor.remote())

tasks = [wait_and_go.remote(signals[i]) for i in range(3)]
print("ready...")
# Tasks will all be waiting for the signals.
print("set..")

while True:
    time.sleep(5)

    count = 0
    for i in range(3):
        count += ray.get(signals[i].get_count.remote())

    if count == 3:
        break

for i in range(3):
  ray.get(signals[i].send.remote())

time.sleep(15)

# Tasks are unblocked.
ray.get(tasks)

time.sleep(15)

for i in range(3):
  ray.kill(signals[i])

print("Done")

# Output is:
# ready...
# set..
# (wait_and_go pid=1528922) wait...
# (wait_and_go pid=1528920) wait...
# (wait_and_go pid=1528919) wait...
# (SignalActor pid=1528917) added
# (SignalActor pid=1528917) added
# (SignalActor pid=1528917) added
# (wait_and_go pid=1528922) go! 0.9970340128799641
# (wait_and_go pid=1528920) go! 0.027701997482486806
# (wait_and_go pid=1528919) go! 0.3428269201176338
