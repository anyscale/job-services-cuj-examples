import time
import ray

@ray.remote(num_cpus=16)
def foo():
  count = 1
  while count < 3:
    print("A loop...")
    time.sleep(10)
    count += 1
  return True

futures = [foo.remote() for _ in range(3)]

ray.get(futures)
