import cv2 as cv
import numpy as np
import torchvision.transforms as transforms
from datetime import datetime
import sys
import argparse
import pycuda.driver as cuda
import tensorrt as trt
import pycuda.autoinit
import torch.nn.functional as F


import torch

class CustomDegbuger:
    def __init__(self):
        self.called = 0

    def debug(self, stream):
        self.called += 1
        print(f'##########{self.called}##########\n', file=stream, flush=True)


### https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#python_topics
### https://docs.nvidia.com/deeplearning/tensorrt/release-notes/index.html#rel-8-2-1
### https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-821/quick-start-guide/index.html



TRT_LOGGER = trt.Logger(trt.Logger.INFO)
EXPLICIT_BATCH = 1 << (int)(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
runtime = trt.Runtime(TRT_LOGGER)
host_inputs  = []
cuda_inputs  = []
host_outputs = []
cuda_outputs = []
bindings = []

def PrepareEngine(_path, seed = None):
    with trt.Builder(TRT_LOGGER) as builder, builder.create_network(EXPLICIT_BATCH) as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
        config = builder.create_builder_config()
        config.set_flag(trt.BuilderFlag.FP16)  # float16 모드 활성화

        #config.set_flag(trt.BuilderFlag.INT8)  # int8 모드 활성화
        #config.int8_calibrator = YourInt8Calibrator()  # Calibration을 위한 Calibrator 지정
        #config.max_workspace_size = 1 << 30
        
        config.max_workspace_size = 2147483648
        # with open(onnx_path, 'rb') as model:
        #     if not parser.parse(model.read()):
        #         print ('ERROR: Failed to parse the ONNX file.')
        #         for error in range(parser.num_errors):
        #             print (parser.get_error(error))


        serialized_engine = builder.build_serialized_network(network, config)
        # with open(f"{onnx_path.split('.')[0]}.trt", "wb") as f:
        #     f.write(serialized_engine)
        with open(f"{_path.split('.')[0]}.trt", 'rb') as f:
            serialized_engine = f.read()
        engine = runtime.deserialize_cuda_engine(serialized_engine)

        # create buffer
        for binding in range(engine.num_bindings): #모든 바인딩 순회, 바인딩은 모델의 입출력
            size = trt.volume(engine.get_binding_shape(binding))
            host_mem = cuda.pagelocked_empty(shape=[size],dtype=np.float32)
            cuda_mem = cuda.mem_alloc_like(host_mem)

            #print(type(host_mem), host_mem)
            #print(type(cuda_mem), cuda_mem)

            bindings.append(int(cuda_mem))
            if engine.binding_is_input(binding):
                host_inputs.append(host_mem)
                cuda_inputs.append(cuda_mem)
            else:
                host_outputs.append(host_mem)
                cuda_outputs.append(cuda_mem)
                output_shape = engine.get_binding_shape(binding)

        return engine, output_shape

def mem_free(ml):
    for mem in ml:
        cuda.mem_free(mem)



if __name__ == "__main__":
    try:
        #######################
        d = CustomDegbuger()
        #######################
        parser = argparse.ArgumentParser()
        parser.add_argument('-mp', '--model_path', type=str, required=True)
        parser.add_argument('-ip', '--image_path', type=str, required=True)

        args = parser.parse_args()

        # 이미지 불러오기
        image_path = args.image_path
        image = cv.imread(image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # 이미지 전처리 및 텐서 변환
        transform_ = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        input_tensor = transform_(image)
        #input_tensor = input_tensor.unsqueeze(0).cuda()
        input_tensor = input_tensor.unsqueeze(0)


        # Create a stream in which to copy inputs/outputs and run inference.
        engine, output_shape = PrepareEngine(args.model_path, seed = 42)
        stream = cuda.Stream()
        context = engine.create_execution_context()


        #host_input = np.array(input_tensor.numpy(), dtype=np.float32, order='C')
        #print(host_input)
        #print(host_input.shape)
        #print(host_input.dtype, host_input.nbytes, host_input.itemsize, sys.getsizeof(host_input))
        input_data_bytesize = cuda.mem_alloc(sys.getsizeof(input_tensor.numpy().tobytes()))
        cuda.memcpy_htod(input_data_bytesize, input_tensor.numpy().tobytes())


        # run inference
        context.execute_v2(bindings)

        a_result = np.empty(shape=output_shape, dtype=np.float32)
        cuda.memcpy_dtoh(a_result, input_data_bytesize)

        #cuda.memcpy_dtoh_async(host_outputs[0], cuda_outputs[0], stream)
        stream.synchronize()
        input_data_bytesize.free()

        # postprocess results
        a_result = np.frombuffer(a_result, dtype=np.float32).reshape(a_result.shape)
        # print(a_result)

        #output_data = torch.Tensor(a_result).reshape(int(engine.max_batch_size), int(host_outputs[0][0]))
        output_data = torch.Tensor(a_result)
        probabilities = F.softmax(output_data, dim=1)
        d.debug(stream=sys.stdout) ############################################################################
        #pycuda.driver.Context.pop()

        # 가장 높은 확률과 해당 클래스 인덱스 찾기
        max_probability, predicted_class = torch.max(probabilities, dim=1) 
        #max_probability, predicted_class = outputs.topk(k=1, dim=1, largest=True, sorted=True)

        now = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        print(now, predicted_class.item(), max_probability.item())

    
        # mem_free(host_inputs)
        # mem_free(cuda_inputs)
        # mem_free(host_outputs)
        # mem_free(cuda_outputs)

        
    except Exception as e:
        print(f'{type(e)} {e}', file=sys.stderr)
        sys.exit(1) 


    # finally:
    #     for cur in globals().items():
    #         if isinstance(cur, cuda.DeviceMemoryPool):
    #             cur.free()