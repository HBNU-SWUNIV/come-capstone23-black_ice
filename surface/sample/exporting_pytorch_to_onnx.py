import torch
from classification_model import Net
from torch.onnx import OperatorExportTypes

model = Net()
model.eval()

x = torch.zeros([1, 1, 28, 28])
print(x.shape)
torch.onnx.export(model, x, "test.onnx", verbose=True, operator_export_type=OperatorExportTypes.ONNX)