"""Job Submission CUDA available test
Checks that GPU resources are available in the job submission
driver script.
"""

import ray
import torch

# For good measure, let's check that we can use the GPU
# in a remote function.
@ray.remote(num_gpus=0.1)
def foo():
  return torch.cuda.is_available()

print("Starting Check Cuda Available Job")
ray.init(address="auto")
# Assert that GPU resources are available in the driver script
result = ray.get(foo.remote())

assert result, "CUDA is not available in the driver script"

print("Check Cuda Available Job Succeeded")

