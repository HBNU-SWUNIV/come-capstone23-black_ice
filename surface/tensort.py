import argparse
import sys
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit
import tensorrt as trt
import cv2 as cv
from datetime import datetime
import torch
from torchvision import transforms

def build_trt_engine(onnx_path):
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    with open(onnx_path, 'rb') as model:
        success = parser.parse(model.read())
        if not success:
            raise Exception('Failed to parse ONNX model')

    config = builder.create_builder_config()
    serialized_engine = builder.build_serialized_network(network, config)
    return serialized_engine

def infer_image(engine, context, input_data):
    bindings = []
    for binding in engine:
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        host_mem = cuda.pagelocked_empty(trt.volume(engine.get_binding_shape(binding)), dtype=dtype)
        cuda_mem = cuda.mem_alloc(host_mem.nbytes)
        bindings.append(int(cuda_mem))
        if engine.binding_is_input(binding):
            input_tensor = host_mem
        else:
            output_tensor = host_mem

    cuda.memcpy_htod(input_tensor, input_data)
    context.execute(bindings=bindings)
    cuda.memcpy_dtoh(output_data, output_tensor)
    cuda.mem_free(cuda_mem)

    return output_data

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-mp', '--model_path', type=str, required=True)
        parser.add_argument('-ip', '--image_path', type=str, required=True)
        
        args = parser.parse_args()

        serialized_engine = build_trt_engine(args.model_path)
        runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
        engine = runtime.deserialize_cuda_engine(serialized_engine)
        context = engine.create_execution_context()

        image_path = args.image_path
        image = cv.imread(image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        transform_ = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        input_tensor = transform_(image)
        input_tensor = input_tensor.unsqueeze(0)

        output_data = infer_image(engine, context, input_tensor.numpy())

        probabilities = np.round(output_data * 1000) / 1000
        predicted_class = np.argmax(probabilities)

        now = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        print(now, predicted_class, max(probabilities))

    except Exception as e:
        print(f'{type(e)} {e}', file=sys.stderr)
        sys.exit(1)
