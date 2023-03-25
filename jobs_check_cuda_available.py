"""Job Submission CUDA available test
Checks that GPU resources are available in the job submission
driver script.
"""

import ray
import torch

ray.init()

# For good measure, let's check that we can use the GPU
# in a remote function.
@ray.remote(num_gpus=0.1)
def foo():
  return torch.cuda.is_available()

# Assert that GPU resources are available in the driver script
assert(ray.get(foo.remote()))