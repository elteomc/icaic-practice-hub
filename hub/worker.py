"""Execute one task inside the restricted evaluation filesystem."""

import importlib.util
import json
import math
from pathlib import Path
import sys
import traceback


def evaluate_unet(partition):
    import numpy as np
    import torch
    import torch.nn as nn

    torch.set_num_threads(2)
    torch.manual_seed(2026 if partition == "validation" else 90317)
    spec = importlib.util.spec_from_file_location("student_submission", "/work/submission.py")
    submission = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(submission)
    checks = []

    def check(name, category, operation):
        try:
            operation()
            checks.append({"name": name, "category": category, "passed": True})
        except Exception as exc:
            checks.append({"name": name, "category": category, "passed": False,
                           "message": f"{type(exc).__name__}: {str(exc)[:240]}"})

    def crop_case(shape, target):
        model = submission.BrokenUNet()
        tensor = torch.arange(math.prod(shape)).reshape(shape)
        got = model.center_crop(tensor, target)
        height, width = target[-2:]
        top = (shape[-2] - height) // 2
        left = (shape[-1] - width) // 2
        expected = tensor[..., top:top + height, left:left + width]
        assert isinstance(got, torch.Tensor) and torch.equal(got, expected), "Return the centered slice with unchanged pixel values"

    shapes = [((1, 2, 9, 13), (1, 2, 5, 7)), ((2, 3, 12, 15), (2, 3, 7, 8)),
              ((1, 1, 8, 8), (1, 1, 8, 8)), ((2, 1, 5, 9), (2, 1, 1, 2))]
    if partition == "test":
        shapes = [((2, 4, 17, 21), (2, 4, 10, 12)), ((1, 1, 11, 10), (1, 1, 4, 5)),
                  ((3, 2, 7, 7), (3, 2, 7, 7)), ((1, 3, 6, 13), (1, 3, 3, 4))]
    for index, (shape, target) in enumerate(shapes):
        check(f"Centered crop {index + 1}", "architecture", lambda shape=shape, target=target: crop_case(shape, target))

    expected_layers = {
        "enc1_1": (3, 64, 3), "enc1_2": (64, 64, 3), "enc2_1": (64, 128, 3),
        "enc2_2": (128, 128, 3), "bot1": (128, 256, 3), "bot2": (256, 256, 3),
        "dec1_1": (256, 128, 3), "dec1_2": (128, 64, 3), "final": (64, 2, 1),
    }

    def architecture():
        model = submission.BrokenUNet()
        for name, (inputs, outputs, kernel) in expected_layers.items():
            layer = getattr(model, name)
            assert isinstance(layer, nn.Conv2d), f"Keep the supplied {name} convolution"
            assert (layer.in_channels, layer.out_channels, layer.kernel_size, layer.padding) == (inputs, outputs, (kernel, kernel), (0, 0)), f"Keep the supplied dimensions and valid padding in {name}"
        assert isinstance(model.upconv1, nn.ConvTranspose2d)
        assert (model.upconv1.in_channels, model.upconv1.out_channels, model.upconv1.kernel_size, model.upconv1.stride) == (256, 128, (2, 2), (2, 2))
        for name in ("pool1", "pool2"):
            assert isinstance(getattr(model, name), nn.MaxPool2d) and getattr(model, name).kernel_size == 2

    check("Supplied layer structure", "architecture", architecture)

    def forward(height, width):
        model = submission.BrokenUNet().eval()
        tensor = torch.randn(1, 3, height, width, requires_grad=True)
        output = model(tensor)
        expected_h = 2 * (((height - 4) // 2 - 4) // 2 - 4) - 4
        expected_w = 2 * (((width - 4) // 2 - 4) // 2 - 4) - 4
        assert tuple(output.shape) == (1, 2, expected_h, expected_w), f"Expected output (1,2,{expected_h},{expected_w}), got {tuple(output.shape)}"
        assert torch.isfinite(output).all(), "Output contains non-finite values"
        output.sum().backward()
        assert tensor.grad is not None and tensor.grad.abs().sum() > 0, "The output must depend on the input through the network"

    check("Full 256 by 256 forward pass", "architecture", lambda: forward(256, 256))
    check("Rectangular forward pass", "architecture", lambda: forward(128, 192) if partition == "validation" else forward(192, 128))

    metric_cases = [
        (torch.tensor([[[0, 0], [1, 1]]]), torch.tensor([[[0, 1], [1, 1]]]), 2, "Mixed overlap"),
        (torch.tensor([[[0, 0], [0, 1]]]), torch.zeros((1, 2, 2), dtype=torch.long), 2, "False-positive class remains in the union"),
        (torch.zeros((1, 3, 4), dtype=torch.long), torch.zeros((1, 3, 4), dtype=torch.long), 2, "Absent in both maps"),
        (torch.ones((1, 3, 4), dtype=torch.long), torch.zeros((1, 3, 4), dtype=torch.long), 2, "No overlap"),
        (torch.empty((0, 2, 2), dtype=torch.long), torch.empty((0, 2, 2), dtype=torch.long), 2, "Empty batch"),
    ]
    for index in range(4):
        classes = 2 if index < 3 else 3
        pred = torch.randint(classes, (2, 5 + index, 7))
        truth = torch.randint(classes, pred.shape)
        metric_cases.append((pred, truth, classes, f"Generated class maps {index + 1}"))

    def metric(pred, truth, classes):
        predicted, actual = pred.numpy(), truth.numpy()
        values = []
        for cls in range(classes):
            p, t = predicted == cls, actual == cls
            union = np.logical_or(p, t).sum()
            if union:
                values.append(float(np.logical_and(p, t).sum() / union))
        expected = float(np.mean(values)) if values else 0.0
        got = float(submission.calculate_miou(pred, truth, classes))
        assert math.isfinite(got) and abs(got - expected) < 1e-6, f"Expected {expected:.6f}, got {got}"

    for pred, truth, classes, name in metric_cases:
        check(name, "metric", lambda pred=pred, truth=truth, classes=classes: metric(pred, truth, classes))
    score = sum(10 * sum(item["passed"] for item in checks if item["category"] == category) / sum(item["category"] == category for item in checks)
                for category in ("architecture", "metric"))
    passed = sum(item["passed"] for item in checks)
    return {"score": round(score, 4), "metric": "Checks / 20", "display": f"{score:.2f} / 20",
            "checks": checks, "summary": f"{passed} of {len(checks)} checks passed.",
            "details": [{"name": "Architecture", "value": f"{sum(item['passed'] for item in checks if item['category'] == 'architecture')} / 7"},
                        {"name": "Metric", "value": f"{sum(item['passed'] for item in checks if item['category'] == 'metric')} / 9"}],
            "partition": partition}


def evaluate_catacombs(partition):
    from collections import deque
    import numpy as np
    import gymnasium as gym
    import creepy_catacombs_s1

    payload = json.loads(Path("/work/policy.json").read_text())
    if not isinstance(payload, dict) or set(payload) != {"actions", "mc_q", "sarsa_q"}:
        raise ValueError("Use exactly the keys actions, mc_q, and sarsa_q")
    actions = payload["actions"]
    if not isinstance(actions, list) or len(actions) > 500 or any(type(action) is not int or action not in range(4) for action in actions):
        raise ValueError("actions must contain at most 500 integer actions from 0 through 3")
    tables = {}
    for name in ("mc_q", "sarsa_q"):
        table = np.asarray(payload[name], dtype=float)
        if table.shape != (56, 4) or not np.isfinite(table).all():
            raise ValueError(f"{name} must be a finite 56 by 4 numeric table")
        tables[name] = table
    env = gym.make("CreepyCatacombs-v0")
    _, info = env.reset(seed=2025)
    grid = info["grid"].copy()
    start, goal = tuple(info["agent_pos"]), tuple(info["goal_pos"])
    queue = deque([(start, 0)])
    seen = {start}
    shortest = None
    while queue:
        (row, col), distance = queue.popleft()
        if (row, col) == goal:
            shortest = distance
            break
        for dy, dx in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            pos = row + dy, col + dx
            if 0 <= pos[0] < 8 and 0 <= pos[1] < 7 and grid[pos] >= 0 and pos not in seen:
                seen.add(pos)
                queue.append((pos, distance + 1))
    if shortest is None:
        raise RuntimeError("The reference map has no safe route")

    def rollout(sequence=None, table=None, seed=7):
        state, info = env.reset(seed=2025)
        rng = np.random.default_rng(seed)
        reward_sum = 0.0
        step_count = 0
        success = False
        safe_route = True
        for index in range(len(sequence) if sequence is not None else 500):
            if sequence is not None:
                action = sequence[index]
            else:
                values = table[int(state)]
                action = int(rng.choice(np.flatnonzero(values == values.max())))
            position = tuple(info["agent_pos"])
            dy, dx = ((-1, 0), (0, 1), (1, 0), (0, -1))[action]
            destination = (position[0] + dy, position[1] + dx)
            if not (0 <= destination[0] < 8 and 0 <= destination[1] < 7) or grid[destination] < 0:
                safe_route = False
            state, reward, terminated, truncated, info = env.step(action)
            reward_sum += reward
            step_count += 1
            success = bool(terminated and destination == goal and safe_route)
            if terminated or truncated:
                break
        quality = 0.5 + 0.5 * min(1.0, shortest / max(step_count, 1)) if success else 0.0
        return {"escaped": bool(success), "steps": step_count, "return": float(reward_sum), "quality": float(quality)}

    route = rollout(sequence=actions)
    seeds = [7, 11, 19, 23, 31] if partition == "validation" else [101, 103, 107, 109, 113]
    runs = {name: [rollout(table=table, seed=seed) for seed in seeds] for name, table in tables.items()}
    score = 20 * route["quality"] + sum(40 * float(np.mean([run["quality"] for run in results])) for results in runs.values())
    details = [{"name": "Route", "value": f"{'Escaped' if route['escaped'] else 'Not escaped'}, {route['steps']} steps, return {route['return']:g}"},
               {"name": "Shortest safe route", "value": shortest}]
    for name, label in [("mc_q", "Monte Carlo"), ("sarsa_q", "SARSA")]:
        results = runs[name]
        details.append({"name": label, "value": f"{sum(run['escaped'] for run in results)} / 5 escapes, mean return {np.mean([run['return'] for run in results]):.1f}"})
    env.close()
    return {"score": round(score, 4), "metric": "Pilot points / 100", "display": f"{score:.2f} / 100",
            "details": details, "route": route, "rollouts": runs, "partition": partition,
            "summary": "Measured on the fixed 2025 map. Notebook review is needed to verify learning and the optional experiments."}


def main():
    try:
        task, partition = sys.argv[1:3]
        if task == "unet":
            report = evaluate_unet(partition)
        elif task == "catacombs":
            report = evaluate_catacombs(partition)
        else:
            raise ValueError("Unknown evaluation task")
    except Exception as exc:
        report = {"error": f"{type(exc).__name__}: {str(exc)[:1000]}"}
    Path("/work/result.json").write_text(json.dumps(report, allow_nan=False))


if __name__ == "__main__":
    main()
