import pycuda.autoinit
# from pycuda.compiler import SourceModule
# from pycuda import gpuarray

import numpy
import pycuda.driver as cuda
import sys
from torchvision import transforms
import cv2 as cv

image_path = sys.argv[1]
image = cv.imread(image_path)
image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

transform_ = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
a = transform_(image)

# a_gpu = cuda.mem_alloc(a.nbytes)
a_gpu = cuda.mem_alloc(sys.getsizeof(a.numpy().tobytes()))
cuda.memcpy_htod(a_gpu, a.numpy().tobytes())

a_result = numpy.empty_like(a.numpy().tobytes())
cuda.memcpy_dtoh(a_result, a_gpu)


a_gpu.free()

a_result = numpy.frombuffer(a_result, dtype=numpy.float32).reshape(a.shape)
print(a_result)