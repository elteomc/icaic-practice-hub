"""Run submitted models with input data and no evaluation labels."""

import importlib.util
import json
from pathlib import Path
import sys


def load_module(filename):
    spec = importlib.util.spec_from_file_location("candidate", Path.cwd() / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(task):
    import numpy as np
    import torch
    from torch import nn
    torch.set_num_threads(2)
    if task == "pendulum":
        import pandas as pd
        candidate = load_module("submission.py")
        predictions = []
        for path in sorted(Path.cwd().glob("recording-*.csv")):
            answer = candidate.solve(pd.read_csv(path))
            predictions.append({key: float(value) for key, value in answer.items()})
        return {"predictions": predictions}
    module = load_module("submission_model.py")
    model = module.MyModel()
    if not isinstance(model, nn.Module):
        raise ValueError("MyModel must be a torch.nn.Module")
    modules = list(model.modules())[1:]
    if any(isinstance(item, nn.Sequential) for item in modules):
        raise ValueError("nn.Sequential is not permitted")
    leaves = [item for item in modules if not list(item.children())]
    activations = (nn.ReLU, nn.Sigmoid, nn.Tanh, nn.ELU, nn.LeakyReLU, nn.PReLU)
    allowed = (nn.Linear,) + activations + (() if task == "basketball" else (nn.Conv2d, nn.MaxPool2d))
    if any(type(item) not in allowed for item in leaves):
        raise ValueError("The model contains a leaf module outside the permitted layer and activation list")
    linear = [item for item in leaves if isinstance(item, nn.Linear)]
    convolution = [item for item in leaves if isinstance(item, nn.Conv2d)]
    pools = [item for item in leaves if isinstance(item, nn.MaxPool2d)]
    if task == "basketball":
        if not 1 <= len(linear) <= 3 or any(item.out_features > 8 for item in linear):
            raise ValueError("Use one to three linear layers with at most eight output neurons each")
    elif len(convolution) < 2 or len(pools) < 2 or len(linear) > 2:
        raise ValueError("Use at least two Conv2d, two MaxPool2d, and at most two Linear layers")
    weights = torch.load("submission_dic.pth", map_location="cpu", weights_only=True)
    model.load_state_dict(weights, strict=True)
    model.eval()
    inputs = np.load("inputs.npz")["x"]
    if task == "real-fake":
        inputs = inputs.astype(np.float32).transpose(0, 3, 1, 2) / 127.5 - 1
    called = set()
    handles = [item.register_forward_hook(lambda module, args, output: called.add(id(module))) for item in leaves]
    results = []
    with torch.no_grad():
        for start in range(0, len(inputs), 128):
            batch = torch.tensor(inputs[start:start+128], dtype=torch.float32)
            output = model(batch)
            if not isinstance(output, torch.Tensor) or tuple(output.shape) not in ((len(batch),), (len(batch), 1)):
                raise ValueError("Return a tensor with shape N or N by 1")
            results.extend(output.reshape(-1).tolist())
    for handle in handles:
        handle.remove()
    required = linear if task == "basketball" else convolution + pools + linear
    if any(id(item) not in called for item in required):
        raise ValueError("All counted model layers must be used in the forward pass")
    return {"predictions": results, "linear": len(linear), "conv": len(convolution)}


if __name__ == "__main__":
    try:
        report = evaluate(sys.argv[1])
    except Exception as exc:
        report = {"error": f"{type(exc).__name__}: {str(exc)[:1000]}"}
    Path("predictions.json").write_text(json.dumps(report))
