"""China task packs, private fixtures, and parent process scoring."""

import ast
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import zipfile

import nbformat
import numpy as np
import pandas as pd
from PIL import Image
from scipy.integrate import solve_ivp
from sklearn.model_selection import train_test_split

from .admissions import SubmissionError
from .sandbox import run_isolated


CHINA_TASKS = {}
for identifier, number, division, title, subtitle, metric, source_number, source_file in [
    ("basketball", "04", "Classical learning", "Basketball Shooting", "Can two coordinates predict a shot?", "Accuracy", 31, "e_en.md"),
    ("real-fake", "05", "Computer vision", "Real or Fake Images", "Learn visual evidence, then test it.", "Practice composite", 32, "e_en.md"),
    ("pendulum", "06", "Time series and sensors", "Pendulum Motion", "Recover the physics behind missing observations.", "Weighted score / 1", 35, "event_description_en.md"),
]:
    model_task = identifier != "pendulum"
    CHINA_TASKS[identifier] = {
        "id": identifier, "number": number, "code": {"basketball": "D04-02", "real-fake": "D07-01", "pendulum": "D10-01"}[identifier],
        "title": title, "division": division, "subtitle": subtitle, "description": subtitle,
        "duration": 90 if model_task else 120, "metric": metric,
        "extension": ".zip" if model_task else ".py", "upload_name": "submission.zip" if model_task else "submission.py",
        "source": f"https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/competition/{source_number}/{source_file}",
        "source_name": "China NOAI 2024 task, republished in the APOAI 2025 mock", "kind": "Model and weights" if model_task else "Physics and inference",
        "deliverable": "One ZIP containing submission_model.py and submission_dic.pth." if model_task else "One Python file exporting solve(frame), returning the five named parameters.",
        "adaptation": "Practice uses a fixed 70/15/15 split of the public data. Original hidden competition data is unavailable. " +
            ("Image scoring uses ordinary accuracy, without the historical doubling bug." if identifier == "real-fake" else "Scores measure this practice split.") if model_task else
            "Practice uses synthetic recordings from the stated equation with known answers. Submit solve(frame) instead of the original complete notebook. Original hidden A and B recordings are unavailable.",
        "max_upload_mb": 8 if model_task else 2,
    }


STATEMENTS = {
"basketball": """# Basketball Shooting

Use the location of a basketball shot to predict whether it goes in. Start by asking whether shots near the basket have a different success rate. A small model and a sound validation split matter more than a large network here.

## Your first ten minutes

1. Open Starter.ipynb. It loads train.csv and shows the first rows.
2. Plot loc_x against loc_y, colouring points by shot_made_flag.
3. Run the deliberately untrained starter once to check packaging and submission.
4. Make a development split inside train.csv before choosing a training method.

## Data and model rules

The supplied train.csv contains 17,500 labeled shots, 70% of the 25,000 rows in the public mirror. Validation and final test each use 3,750 different rows. Their labels are kept by the local evaluator. These are practice partitions, not the original hidden competition test.

Use **only loc_x and loc_y as model inputs**, in that order. Predict shot_made_flag, where 1 means a made shot. The other columns are supplied for context and cannot be inputs. Do not fetch the original public labels for the withheld rows.

Implement PyTorch class MyModel with a no-argument constructor. Use one to three nn.Linear layers, each with at most eight output neurons. Other permitted leaf modules are nn.ReLU, nn.Sigmoid, nn.Tanh, nn.ELU, nn.LeakyReLU, and nn.PReLU. Do not use nn.Sequential. Return one **raw logit** per row, shape N or N by 1. The evaluator applies sigmoid and thresholds at 0.5. Fit preprocessing on your training rows only and include it in the exported model. Inputs at evaluation are the original CSV coordinates.

## Submit and improve

Save submission.zip with exactly submission_model.py and submission_dic.pth at its root. The Python file defines MyModel and imports. The weights file is a torch state_dict. Do not include training code that executes when imported. Maximum ZIP size is 8 MB. The notebook includes a packaging cell.

Validation feedback reports accuracy and majority-class accuracy. Final evaluation after closing an attempt uses the other 3,750 rows. Accuracy is the primary score. Save the split, seed, loss, and one explanation of your errors in the notebook.

## Source and changes

This is China NOAI 2024 task 1, republished as APOAI 2025 mock task 1. The linked original statement describes 20,000 training rows, while the public mirror contains 25,000. This room uses the mirror and its own disclosed partitions. The architecture and model ZIP contract are retained. Read Source_Statement.md for a punctuation-normalized source reading copy.
""",
"real-fake": """# Real or Fake Images

Distinguish real CIFAR images from generated images. Both classes are small RGB images of the same dimensions. Look for repeatable visual evidence rather than memorizing filenames.

## Your first ten minutes

1. Open Starter.ipynb and extract images_train.zip.
2. Display several images from each class, using train.csv as the label map.
3. Run the untrained starter and export its model ZIP to check the submission path.
4. Make a stratified development split before training or changing the network.

## Data and preprocessing

The pack contains 7,000 labeled 32 by 32 RGB training images. Real is 0 and generated is 1. The evaluator reserves 1,500 images for validation and 1,500 different images for final testing from the same public 10,000-image archive. This is a fixed stratified 70/15/15 practice split. Original hidden competition images are unavailable.

Use float32 input tensors in N by 3 by 32 by 32 order, normalized with pixel / 127.5 - 1. Use the same normalization in training and evaluation. The evaluator supplies these normalized tensors directly.

## Model rules

Implement PyTorch class MyModel with a no-argument constructor. Include at least two nn.Conv2d and two nn.MaxPool2d modules, used in the forward pass. Use at most two nn.Linear modules. Permitted activation modules are nn.ReLU, nn.Sigmoid, nn.Tanh, nn.ELU, nn.LeakyReLU, and nn.PReLU. Do not use nn.Sequential. Other leaf modules are not accepted. Tensor operations such as reshape and flatten are allowed.

Return one **probability** per image, shape N or N by 1, between 0 and 1. The evaluator thresholds at 0.5. This differs from Basketball Shooting's raw-logit contract. A final sigmoid is a straightforward way to satisfy it.

## Submit and scoring

Save submission.zip with exactly submission_model.py and submission_dic.pth at its root. The Python file defines MyModel and imports. Save a torch state_dict as the weights file. Keep training outside the submitted class file. Maximum ZIP size is 8 MB.

Feedback reports accuracy, counted convolutional and linear layers, and the practice composite score:

    simplicity = 1 / (number_of_linear_layers + number_of_convolutional_layers + 1)
    score = 0.75 * (accuracy + simplicity)

The original statement mentions a historical bug that doubled accuracy. This practice evaluator uses ordinary accuracy. Its score therefore cannot be compared numerically with that historical leaderboard. Final evaluation after closing uses different held-out images.

## Source and review

This is China NOAI 2024 task 2, republished as APOAI 2025 mock task 2. Source_Statement.md contains a reading copy. The public archive supplies 5,000 real and 5,000 generated images. Do not recover withheld labels from the original archive during an independent attempt. Explain one false positive, one false negative, and whether an improvement survived your own development split.
""",
"pendulum": """# Pendulum Motion

A sensor records a damped pendulum, loses a continuous interval, then resumes recording. During that gap, a constant downward force is switched on. Recover the physical parameters and predict the next zero crossing after the last observation.

## Your first ten minutes

1. Open Starter.ipynb and plot t against theta from pendulum_train.csv.
2. Inspect consecutive time differences and locate the missing interval.
3. Read the equation below and identify what changes when the force begins.
4. Open submission.py. Its solve(frame) function initially returns deliberately poor default values. Run it once and make a first submission to check the path.

## Given physics

Mass is 1 and gravity is 9.8. Initial angular velocity is zero. Angles are radians and time is seconds.

    theta''(t) = -alpha * theta'(t) - beta * sin(theta(t))
    alpha = miu
    beta_before = 9.8 / l
    beta_after = (9.8 + F) / l

The force starts once during the missing interval and stays on. Use PyTorch for the regression step. NumPy, pandas, SciPy, and math are also available. Do not estimate a derivative by connecting observations across the missing interval. Your approach must adapt to a new recording, not return constants fitted to the supplied one.

## Data and practice evaluation

pendulum_train.csv is the original public 734-row recording, with columns t and theta. Its hidden true parameters are not publicly supplied, so the room does not invent an official score for it.

Validation uses two synthetic recordings from the stated equation, with different parameters. Final testing uses two further recordings. All have initial velocity zero, one missing interval longer than one second, and a force switch inside that gap. Practice lengths are 3 to 6, resistance 0.2 to 0.6, forces 20 to 45, initial angles 0.6 to 1.1, and observations from 0 to 15 seconds. These are disclosed practice ranges, not inferred limits of the original contest.

## Submission contract

Submit submission.py defining solve(frame). frame is a pandas DataFrame with t and theta only. Return exactly a dictionary with finite numeric values for l, miu, F, t_nextzerotheta, and t_Fput. The function is called independently on each recording. t_nextzerotheta must be the first zero crossing strictly after the final observation. Maximum source size is 2 MB. Validation evaluation has a 90-second total time limit.

This callable replaces the original full submission notebook so the room can rerun a method on withheld recordings. Keep derivations, plots, and training steps in Starter.ipynb for review. The linked original statement describes submission_train.csv, submissionA.csv, and submissionB.csv. Those files are not the room's submission contract.

## Scoring

For absolute errors e_l, e_miu, e_F, e_next, and e_switch:

    score = (exp(-10*e_l) + exp(-10*e_miu) + 2*exp(-e_F)
             + 2*exp(-10*e_next) + 2*exp(-10*e_switch)) / 8

The room averages this score across recordings. One is perfect and larger is better. Feedback includes each parameter's mean absolute error. Closing an attempt evaluates different final recordings. This uses the source metric on practice fixtures, not official hidden A or B data.

## Source and review

China NOAI 2024 task 4, republished as APOAI 2025 mock task 4. Source_Statement.md includes the problem and score, with the solved appendix omitted. Explain how you handle the gap, why a force change modifies the frequency, and how you check the inferred trajectory against the observed one.
""",
}


def extract_model(path, destination):
    try:
        with zipfile.ZipFile(path) as archive:
            items = archive.infolist()
            expected = {"submission_model.py", "submission_dic.pth"}
            if len(items) != 2 or {item.filename for item in items} != expected:
                raise SubmissionError("The ZIP must contain exactly submission_model.py and submission_dic.pth at its root")
            if any(stat.S_ISLNK(item.external_attr >> 16) or item.flag_bits & 1 for item in items):
                raise SubmissionError("Encrypted files and links are not accepted")
            if sum(item.file_size for item in items) > 32 * 1024 ** 2 or any(item.file_size > 24 * 1024 ** 2 for item in items):
                raise SubmissionError("The model expands beyond the 32 MB limit")
            destination.mkdir(parents=True, exist_ok=True)
            for item in items:
                (destination / item.filename).write_bytes(archive.read(item))
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise SubmissionError(f"The model ZIP could not be read: {exc}") from None


def check_source(path, task):
    allowed = {"torch", "numpy", "math"}
    if task == "pendulum":
        allowed |= {"pandas", "scipy"}
    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, UnicodeError) as exc:
        raise SubmissionError(f"The submission could not be parsed: {str(exc)[:180]}") from None
    for node in ast.walk(tree):
        modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        if any(module.split('.')[0] not in allowed for module in modules):
            raise SubmissionError("Permitted submission imports: " + ", ".join(sorted(allowed)))
    if task == "pendulum" and not any(isinstance(node, (ast.Import, ast.ImportFrom)) and
        any(name == "torch" or name.startswith("torch.") for name in ([a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""])) for node in ast.walk(tree)):
        raise SubmissionError("Use PyTorch for the regression step and import it in submission.py")


KEYS = ("l", "miu", "F", "t_nextzerotheta", "t_Fput")


def score_pendulum(predictions, truths, partition):
    if len(predictions) != len(truths) or not predictions:
        raise SubmissionError("Return one parameter dictionary per recording")
    errors = []
    for prediction, truth in zip(predictions, truths):
        if not isinstance(prediction, dict) or set(prediction) != set(KEYS):
            raise SubmissionError("Return exactly l, miu, F, t_nextzerotheta, and t_Fput")
        try:
            values = np.array([float(prediction[key]) for key in KEYS])
        except (ValueError, TypeError):
            raise SubmissionError("All returned parameters must be finite numbers") from None
        if not np.isfinite(values).all():
            raise SubmissionError("All returned parameters must be finite numbers")
        errors.append(np.abs(values - [truth[key] for key in KEYS]))
    errors = np.array(errors)
    scores = (np.exp(-errors * [10, 10, 1, 10, 10]) * [1, 1, 2, 2, 2]).sum(axis=1) / 8
    score = float(scores.mean())
    return {"score": score, "metric": "Weighted score / 1", "display": f"{score:.5f} / 1",
            "partition": partition, "summary": f"Mean source-formula score over {len(truths)} synthetic practice recordings.",
            "details": [{"name": f"{key} mean absolute error", "value": f"{error:.6g}"} for key, error in zip(KEYS, errors.mean(axis=0))]}


def grade_china(project, state, task, path, partition):
    judge = Path(state) / "judge"
    if partition not in ("validation", "test"):
        raise SubmissionError("Unknown evaluation partition")
    with tempfile.TemporaryDirectory(dir=Path(state) / "evaluation") as folder:
        work = Path(folder)
        if task == "pendulum":
            shutil.copyfile(path, work / "submission.py")
            check_source(work / "submission.py", task)
            recordings = sorted((judge / f"pendulum-{partition}").glob("*.csv"))
            for recording in recordings:
                shutil.copyfile(recording, work / recording.name)
        else:
            extract_model(path, work)
            check_source(work / "submission_model.py", task)
            shutil.copyfile(judge / f"{task}-{partition}-inputs.npz", work / "inputs.npz")
        process = run_isolated(Path(sys.executable), Path(project) / "hub" / "china_worker.py", work,
                               timeout=90, arguments=(task,))
        output = work / "predictions.json"
        if process.returncode or not output.exists():
            raise SubmissionError("Evaluation did not finish. " + (process.stderr or process.stdout)[-1000:])
        report = json.loads(output.read_text())
        if "error" in report:
            raise SubmissionError(report["error"])
        if task == "pendulum":
            truths = json.loads((judge / f"pendulum-{partition}-answers.json").read_text())
            return score_pendulum(report["predictions"], truths, partition)
        labels = np.load(judge / f"{task}-{partition}-labels.npz")["y"]
        values = np.asarray(report["predictions"], dtype=float)
        if values.shape != labels.shape or not np.isfinite(values).all():
            raise SubmissionError("Return one finite prediction per example")
        if task == "basketball":
            accuracy = float(((values >= 0) == labels).mean())
            score = accuracy
        else:
            if ((values < 0) | (values > 1)).any():
                raise SubmissionError("Image predictions must be probabilities between zero and one")
            accuracy = float(((values >= .5) == labels).mean())
            score = .75 * (accuracy + 1 / (report["linear"] + report["conv"] + 1))
        return {"score": score, "metric": CHINA_TASKS[task]["metric"],
                "display": f"{accuracy:.2%}" if task == "basketball" else f"{score:.5f}", "partition": partition,
                "summary": "Measured on the practice holdout. No original hidden competition data is used.",
                "details": [{"name": "Accuracy", "value": f"{accuracy:.2%}"},
                            {"name": "Majority-class accuracy", "value": f"{max(labels.mean(), 1-labels.mean()):.2%}"},
                            {"name": "Linear / convolutional layers", "value": f"{report['linear']} / {report['conv']}"}]}


def synthetic_recording(seed):
    rng = np.random.default_rng(seed)
    length, resistance, force = rng.uniform(3, 6), rng.uniform(.2, .6), rng.uniform(20, 45)
    switch, initial = rng.uniform(3.7, 5.7), rng.uniform(.6, 1.1)
    def rhs(extra):
        return lambda t, y: [y[1], -resistance*y[1] - (9.8+extra)/length*np.sin(y[0])]
    before = solve_ivp(rhs(0), [0, switch], [initial, 0], dense_output=True, rtol=1e-11, atol=1e-13, max_step=.025)
    after = solve_ivp(rhs(force), [switch, 45], before.y[:, -1], dense_output=True, rtol=1e-11, atol=1e-13, max_step=.025)
    t = np.linspace(0, 15, 1000)
    t = t[(t <= 3) | (t >= 7)]
    theta = np.array([before.sol(x)[0] if x < switch else after.sol(x)[0] for x in t])
    def zero(t, y):
        return y[0]
    zero.terminal = True
    future = solve_ivp(rhs(force), [15, 45], after.sol(15), events=zero, rtol=1e-11, atol=1e-13, max_step=.025)
    truth = {"l": length, "miu": resistance, "F": force, "t_nextzerotheta": float(future.t_events[0][0]), "t_Fput": switch}
    return pd.DataFrame({"t": t, "theta": theta}), truth


def build_china_packs(project, state, make_notebook):
    project, state = Path(project), Path(state)
    cache, judge = project / ".source-cache", state / "judge"
    manifest = json.loads((cache / "china-manifest.json").read_text())
    for record in manifest:
        if hashlib.sha256((cache / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            raise RuntimeError("China source checksum mismatch: " + record["file"])
    def split_indexes(labels):
        train, held = train_test_split(np.arange(len(labels)), test_size=.3, random_state=20261104, stratify=labels)
        validation, test = train_test_split(held, test_size=.5, random_state=20261105, stratify=np.asarray(labels)[held])
        return train, validation, test
    for task, metadata in CHINA_TASKS.items():
        pack = project / "packs" / task
        pack.mkdir(parents=True, exist_ok=True)
        (pack / "Statement.md").write_text(STATEMENTS[task])
        source = (cache / f"{task}-statement.md").read_text()
        source = source.split("### VI. Appendix")[0]
        source = re.sub(r"\(in radian measure\.[^)]+\)", "(in radian measure)", source)
        source = re.sub(r"\(if you don't understand[^)]+\)", "", source)
        source = source.replace("\u2014", ", ").replace("\u2013", "-").replace(";", ",")
        (pack / "Source_Statement.md").write_text(source)
        (pack / "Provenance.json").write_text(json.dumps({**metadata, "pack_version": "china-1", "sources": manifest,
            "reading_changes": "Punctuation normalized, solved pendulum appendix and unrelated advice omitted."}, indent=2) + "\n")
        cells = starter_cells(task)
        nbformat.write(make_notebook(cells), pack / "Starter.ipynb")
        if task == "pendulum":
            shutil.copyfile(cache / "pendulum_train.csv", pack / "pendulum_train.csv")
            (pack / "submission.py").write_text('import torch\n\n\ndef solve(frame):\n    # Replace these defaults with a method that fits the supplied recording\n    return {"l": 1.0, "miu": 1.0, "F": 10.0, "t_nextzerotheta": 16.0, "t_Fput": 4.0}\n')
            for partition, seeds in [("validation", [411, 527]), ("test", [683, 799])]:
                directory = judge / f"pendulum-{partition}"
                directory.mkdir(exist_ok=True)
                truths = []
                for index, seed in enumerate(seeds):
                    frame, truth = synthetic_recording(seed)
                    frame.to_csv(directory / f"recording-{index}.csv", index=False)
                    truths.append(truth)
                (judge / f"pendulum-{partition}-answers.json").write_text(json.dumps(truths))
        elif task == "basketball":
            frame = pd.read_csv(cache / "basketball_train.csv")
            train, validation, test = split_indexes(frame.shot_made_flag)
            frame.iloc[train].to_csv(pack / "train.csv", index=False)
            for partition, indexes in [("validation", validation), ("test", test)]:
                split = frame.iloc[indexes]
                np.savez_compressed(judge / f"{task}-{partition}-inputs.npz", x=split[["loc_x", "loc_y"]].to_numpy(dtype=np.float32))
                np.savez_compressed(judge / f"{task}-{partition}-labels.npz", y=split.shot_made_flag.to_numpy(dtype=int))
            (pack / "submission_model.py").write_text(BASKETBALL_MODEL)
        else:
            with zipfile.ZipFile(cache / "train_v1.zip") as original:
                files = sorted(name for name in original.namelist() if name.endswith(".png") and ("/cifar/" in name or "/uvit/" in name))
                labels = np.array([int("/uvit/" in name) for name in files])
                train, validation, test = split_indexes(labels)
                rows = []
                with zipfile.ZipFile(pack / "images_train.zip", "w", zipfile.ZIP_DEFLATED) as images:
                    for index in train:
                        name = f"images/{index:05d}.png"
                        images.writestr(name, original.read(files[index]))
                        rows.append({"file": name, "label": int(labels[index])})
                pd.DataFrame(rows).to_csv(pack / "train.csv", index=False)
                for partition, indexes in [("validation", validation), ("test", test)]:
                    inputs = np.array([np.asarray(Image.open(io.BytesIO(original.read(files[index]))).convert("RGB")) for index in indexes])
                    np.savez_compressed(judge / f"{task}-{partition}-inputs.npz", x=inputs)
                    np.savez_compressed(judge / f"{task}-{partition}-labels.npz", y=labels[indexes])
            (pack / "submission_model.py").write_text(IMAGE_MODEL)


BASKETBALL_MODEL = '''import torch
from torch import nn


class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.output = nn.Linear(2, 1)

    def forward(self, x):
        return self.output(x)
'''

IMAGE_MODEL = '''import torch
from torch import nn


class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 4, 3)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(4, 4, 3)
        self.pool2 = nn.MaxPool2d(2)
        self.activation = nn.ReLU()
        self.output = nn.Linear(4 * 6 * 6, 1)
        self.probability = nn.Sigmoid()

    def forward(self, x):
        x = self.pool1(self.activation(self.conv1(x)))
        x = self.pool2(self.activation(self.conv2(x)))
        return self.probability(self.output(x.flatten(1)))
'''


def starter_cells(task):
    title = CHINA_TASKS[task]["title"]
    cells = [("md", f"# {title}\n\nRead Statement.md before changing code. This starter checks the input and export path. It deliberately contains no trained solution. Keep your experiments and reasoning here.")]
    if task == "pendulum":
        cells += [("code", "import pandas as pd\nimport matplotlib.pyplot as plt\nimport importlib\nimport submission\n\nframe = pd.read_csv('pendulum_train.csv')\nprint(frame.head())\nprint('Largest observed gap:', frame.t.diff().max())\nplt.plot(frame.t, frame.theta, '.')\nplt.xlabel('Time (seconds)')\nplt.ylabel('Angle (radians)')\nplt.show()"),
                  ("md", "## Fit a method\n\nEdit solve(frame) in submission.py. Use the supplied equation and PyTorch for regression. Keep observations on either side of the missing interval separate when estimating derivatives. The same function must work on recordings with different parameters."),
                  ("code", "importlib.reload(submission)\nanswers = submission.solve(frame.copy())\nprint(answers)\nassert set(answers) == {'l', 'miu', 'F', 't_nextzerotheta', 't_Fput'}"),
                  ("md", "## Submit\n\nSave submission.py and submit that file, not this notebook. The initial constants are only an export check. The hub runs your function on new practice recordings. Keep this notebook for review.")]
        return cells
    if task == "basketball":
        cells += [("code", "import pandas as pd\nimport matplotlib.pyplot as plt\ntrain = pd.read_csv('train.csv')\nprint(train.shape)\nprint(train.head())\nprint('Made-shot rate:', train.shot_made_flag.mean())\nplt.scatter(train.loc_x, train.loc_y, c=train.shot_made_flag, s=2, alpha=.2)\nplt.xlabel('loc_x')\nplt.ylabel('loc_y')\nplt.show()"),
                  ("md", "## Your training experiment\n\nCreate a stratified development split. Train using only loc_x and loc_y. The supplied single linear layer is a permitted but untrained starting model. Choose an appropriate loss for raw logits, inspect your development accuracy, and make preprocessing part of the exported model."),
                  ("code", "import torch\nfrom submission_model import MyModel\ntorch.set_num_threads(2)\ntorch.manual_seed(2026)\nmodel = MyModel()\nx = torch.tensor(train[['loc_x', 'loc_y']].to_numpy(), dtype=torch.float32)\ny = torch.tensor(train.shot_made_flag.to_numpy(), dtype=torch.float32).reshape(-1, 1)\nprint('Input shape:', x.shape, 'output shape:', model(x[:4]).shape)\n\n# Add your development split and training here\n")]
    else:
        cells += [("code", "import zipfile\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nfrom PIL import Image\nwith zipfile.ZipFile('images_train.zip') as archive:\n    archive.extractall('.')\ntrain = pd.read_csv('train.csv')\nprint(train.groupby('label').size())\nfig, axes = plt.subplots(1, 6, figsize=(9, 2))\nfor axis, row in zip(axes, train.iloc[:6].itertuples()):\n    axis.imshow(Image.open(row.file))\n    axis.set_title('Generated' if row.label else 'Real')\n    axis.axis('off')\nplt.show()"),
                  ("md", "## Your training experiment\n\nSplit the rows into training and development sets. Load pixels as float32, reorder H,W,C to C,H,W, and normalize with pixel / 127.5 - 1. The supplied CNN meets the structure rules but has no trained weights. It returns probabilities. Add your data loader, loss, optimizer, and development check."),
                  ("code", "import torch\nfrom submission_model import MyModel\ntorch.set_num_threads(2)\ntorch.manual_seed(2026)\nmodel = MyModel()\nfirst = np.asarray(Image.open(train.iloc[0]['file']).convert('RGB'), dtype=np.float32)\nx = torch.tensor(first.transpose(2, 0, 1) / 127.5 - 1).unsqueeze(0)\nprint('Input shape:', x.shape, 'output:', model(x).detach())\n\n# Add your development split and training here\n")]
    cells += [("md", "## Export and submit\n\nRun this after training. If you change the architecture, update submission_model.py to match before exporting. Only the class definition and trained state dictionary belong in the ZIP. The cell also works now to establish an untrained baseline."),
              ("code", "from pathlib import Path\nimport zipfile\nmodel.eval()\ntorch.save(model.state_dict(), 'submission_dic.pth')\nwith zipfile.ZipFile('submission.zip', 'w', zipfile.ZIP_DEFLATED) as archive:\n    for name in ['submission_model.py', 'submission_dic.pth']:\n        archive.write(name, name)\nprint('Saved submission.zip:', Path('submission.zip').stat().st_size, 'bytes')"),
              ("md", "## Keep evidence\n\nRecord your development split, seed, result, and one next hypothesis. Submit submission.zip. A successful upload checks the pipeline, while improved development performance checks whether your training helps.")]
    return cells
