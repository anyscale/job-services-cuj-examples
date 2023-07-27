import time
import ray

@ray.remote(num_cpus=16)
def foo():
  count = 1
  while count < 10:
    print("A loop...")
    time.sleep(10)
    count += 1
  return True

assert(ray.get(foo.remote()))
