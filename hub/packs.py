"""Prepared task assets and source provenance."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

import nbformat

from .china import CHINA_TASKS, build_china_packs
import pandas as pd
from sklearn.model_selection import train_test_split


TASKS = {
    "admissions": {
        "id": "admissions", "number": "01", "code": "D04-01", "title": "University Admissions",
        "division": "Classical learning", "subtitle": "Build a predictor you can defend.",
        "description": "Learn from synthetic applicant records, validate your choices, and submit admission probabilities.",
        "duration": 90, "metric": "ROC AUC", "extension": ".csv", "upload_name": "predictions.csv",
        "source": "https://github.com/Hungarian-AI-Olympiad/HAIO-Hungarian-AI-Olympiad/tree/main/2025/nyari-online",
        "source_name": "Hungarian AI Olympiad, 2025 online qualifier", "kind": "Tabular prediction",
        "deliverable": "One CSV with ID and Felvételi Eredmény for every validation and test row.",
        "adaptation": "Original public training data is split into training, validation, and final holdout. Scores are local practice ROC AUC, not the original leaderboard.",
    },
    "unet": {
        "id": "unet", "number": "02", "code": "D05-02", "title": "Debugging U-Net",
        "division": "Deep learning", "subtitle": "Make the shapes and the metric agree.",
        "description": "Repair the supplied network's center crop and implement mean intersection over union.",
        "duration": 90, "metric": "Checks / 20", "extension": ".py", "upload_name": "submission.py",
        "source": "https://github.com/AISGNUSNOAI/NOAI-2026/blob/main/question_2_v20022026.ipynb",
        "source_name": "Singapore NOAI, 2026 programming task 2", "kind": "Code and correctness",
        "deliverable": "One Python file exporting BrokenUNet and calculate_miou.",
        "adaptation": "The pilot uses automated checks for the two coding parts. The supplied notebook's missing-class example is corrected to 0.375. The architecture produces 110 by 110 outputs for 256 by 256 inputs.",
    },
    "catacombs": {
        "id": "catacombs", "number": "03", "code": "D06-01", "title": "Catacomb Adventure",
        "division": "Reinforcement learning", "subtitle": "Turn experience into a way out.",
        "description": "Explore the authentic environment, find a safe route, and learn Monte Carlo and SARSA action values.",
        "duration": 120, "metric": "Pilot points / 100", "extension": ".json", "upload_name": "policy.json",
        "source": "https://github.com/Hungarian-AI-Olympiad/HAIO-Hungarian-AI-Olympiad/blob/main/2025/nyari-orszagos/feladatok/katakomba-kaland.en.ipynb",
        "source_name": "Hungarian AI Olympiad, 2025 summer final", "kind": "Environment and policy",
        "deliverable": "One JSON file with actions, mc_q, and sarsa_q. Each Q table has shape 56 by 4.",
        "adaptation": "Automated pilot scoring covers the fixed 2025 map, a route, and two learned tables. The original plots, zombie experiments, and written explanations remain available for peer review and are not automatically graded.",
    },
}


TASKS.update(CHINA_TASKS)

def clean_text(value):
    return value.replace("\u2014", ", ").replace("\u2013", "-").replace(";", ",")


def reading_copy(source):
    notebook = nbformat.read(source, as_version=4)
    cells = []
    for cell in notebook.cells:
        if cell.cell_type not in ("markdown", "code"):
            continue
        text = clean_text(cell.source)
        text = re.sub(r"The translation was produced[^.]*\.", "", text)
        if cell.cell_type == "markdown":
            text = re.sub(r'<(?:div|span|img)\b[^>]*>|</(?:div|span)>', '', text)
            text = re.sub(r'!\[[^\]]*\]\(data:[^)]+\)', '[Figure omitted in this reading copy]', text)
            copied = nbformat.v4.new_markdown_cell(text)
            if cell.get("attachments"):
                copied["attachments"] = cell["attachments"]
        else:
            copied = nbformat.v4.new_code_cell(text)
        cells.append(copied)
    return nbformat.v4.new_notebook(cells=cells)


def notebook(cells):
    result = nbformat.v4.new_notebook()
    result.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    result.cells = [nbformat.v4.new_markdown_cell(text) if kind == "md" else nbformat.v4.new_code_cell(text)
                    for kind, text in cells]
    return result


ADMISSIONS_STATEMENT = """# University Admissions

You work with synthetic applicant records from the Hungarian AI Olympiad's 2025 online qualifier. Predict the probability that each applicant is admitted.

## Your first ten minutes
1. Open `Starter.ipynb` and run the baseline from top to bottom.
2. Inspect the labeled rows and the class balance.
3. Write down what ROC AUC measures and why the output is a probability rather than a hard label.
4. Submit the generated `predictions.csv` through the hub.

## Supplied files
- `train.csv`: labeled examples. The target is `Felvételi Eredmény` and the identifier is `ID`.
- `validation.csv`: unlabeled rows used for feedback during an attempt.
- `test.csv`: unlabeled rows used only for final evaluation after you finish.
- `counties.geojson`: the original geographic companion file.
- `original_test.csv`: the original competition's unlabeled test set, included for completeness. It is not part of pilot scoring.
- `Source_Reading.ipynb`: the original source notebook as a reading copy, with outputs removed and punctuation normalized. Its original platform paths are not the pilot's paths.

The supplied training rows are 70% of the original public training data. Validation and final test each contain 15%, with a fixed stratified split. Their labels are held by the evaluator. Do not use external data or attempt to recover withheld answers from the source repository.

## Work and improve
Make a development split inside `train.csv` before choosing features and models. The provided baseline uses only school prestige. Compare it with one carefully chosen improvement. Inspect errors and record the split and metric. Optional geographic features can use the county names and coordinates in the supplied GeoJSON.

Use Python, NumPy, pandas, scikit-learn, and the supplied companion data. All required packages are installed. No downloads are needed.

## Submit
Upload one UTF-8 CSV with exactly two columns: `ID,Felvételi Eredmény`. Include every ID from both `validation.csv` and `test.csv` exactly once. Every prediction must be finite and between 0 and 1. Row order does not matter.

The hub returns validation ROC AUC and log loss. Higher ROC AUC is better. After closing an attempt, up to two final candidates receive holdout results. The better selected holdout AUC is the attempt's final result.

## Explain before moving on
Which feature change helped on your own development split? Could an identifier, duplicate, or county grouping create misleading validation? Can someone else recreate the CSV from your saved notebook?

## Provenance and pilot changes
Source: Hungarian AI Olympiad, 2025 summer online qualifier. English translation credited to Tamás Takács, CC BY-NC-SA 4.0. This educational adaptation preserves source credit. The local split and submission arrangement differ from the original Kaggle event. These are practice results, not official competition scores.
"""

UNET_STATEMENT = """# Debugging U-Net

The supplied network has valid convolutions, so its feature maps shrink. Its skip connection does not fit the decoder tensor. Repair the center crop and implement a trustworthy segmentation metric.

## Your first ten minutes
1. Open `submission.py` beside `Starter.ipynb` in JupyterLab.
2. Run the notebook's initial check and read the failure.
3. Trace height and width through the supplied layers on paper.
4. Edit the two unfinished methods in `submission.py`, save it, and rerun the notebook checks.

## Part 1: architecture, 10 points
Keep the supplied architecture, convolution padding, layer names, and forward order. Implement `BrokenUNet.center_crop(layer, target_shape)` and use it to align the encoder feature map before concatenation. For an odd difference, put the extra discarded pixel on the bottom or right.

The grader checks cropping on varied tensor shapes and values, layer structure, output dimensions, and a real forward pass. A 256 by 256 input produces a 110 by 110 output with this exact architecture. Do not resize the final output to 256 by 256.

## Part 2: metric, 10 points
Implement `calculate_miou(pred_mask, true_mask, num_classes=2)`. Inputs are integer class maps of shape B by H by W. For each class, divide intersection by union. Average the values of classes with a nonzero union. Skip a class only when it appears in neither prediction nor truth. Return 0.0 for an empty input.

You may loop over classes. Do not loop over individual pixels or batches. Use only torch, torch.nn, torch.nn.functional, and NumPy. Metric wrappers and architecture substitutions are not permitted.

## Important source correction
The original notebook's additional missing-class self-check is inconsistent with its own formula. For prediction `[[0,0],[0,1]]` and truth `[[0,0],[0,0]]`, class 0 has IoU 3/4 and class 1 has IoU 0/1. The correct mean is **0.375**, not 0.75. A false positive still contributes to the union. The pilot's checks follow the formula.

The original output-size examples are illustrative and do not match this exact architecture. The pilot uses the measured output size of 110 by 110.

## Submit
Upload `submission.py`, exporting `BrokenUNet` and `calculate_miou`. Do not include notebook display or training code in that file. The starter already separates the editable submission from the notebook checks. The evaluator runs code in an isolated process with a 90-second wall-clock limit. No GPU or model training is needed.

Validation feedback lists passed and failed checks. Final evaluation after closing uses a separate set of generated tensors. Scores are automated pilot checks out of 20, not an official exam mark.

## Explain before moving on
Why does cropping lose border information? How does an always-background prediction behave under pixel accuracy versus mean IoU? Which test caught a mistake your first example missed?

## Provenance
Source: Singapore NOAI 2026 final assessment, programming task 2, published by AISGNUSNOAI. The supplied task and architecture are retained. Corrections and the pilot's automated evaluation are identified above. `Source_Reading.ipynb` preserves the source content for comparison, with outputs removed and punctuation normalized.
"""

CATACOMBS_STATEMENT = """# Catacomb Adventure

Help the heroine escape the authentic CreepyCatacombs-v0 environment. Learn how a route, a reward, and an action-value table describe different parts of the same decision problem.

## Your first ten minutes
1. Open `Starter.ipynb` and reset the environment with seed 2025.
2. Display the map and locate the entrance, exit, walls, and pits.
3. Take one action and inspect observation, reward, termination, and truncation.
4. Run the starter export and submit `policy.json` once to establish a measured starting point.

## The environment
The pinned package is `creepy-catacombs-s1==0.1.4`, the version used by the original task. It has 56 discrete states on an 8 by 7 map and four actions: 0 up, 1 right, 2 down, 3 left. Reset with seed 2025 for the pilot. Do not confuse an episode ending naturally with its time limit being reached.

The automated pilot uses the original no-zombie map. The full source notebook also includes changing layouts, zombies, plots, Monte Carlo control, SARSA, and visualizations. Those remain useful extensions for peer review.

Version 0.1.4 terminates when entering the goal but leaves `agent_pos` on the preceding square and gives the ordinary -1 step reward. Identify success from termination and the attempted destination, not a positive reward or the final reported position. The pilot also requires a safe route without wall, pit, or out-of-bounds steps. Use a separate `np.random.default_rng` for exploration because the environment reset also resets NumPy's global random seed.

## Build three results
1. Find a safe action sequence from entrance to exit on the fixed map.
2. Implement Monte Carlo control and export its learned Q table.
3. Implement SARSA and export its learned Q table.

Train on the supplied fixed environment. Exploration is allowed during training. During evaluation, the table chooses a greedy action. Ties are broken with a documented evaluation seed. Use complete episode returns for Monte Carlo and the next chosen action for SARSA. Keep terminated and truncated separate in your loop.

## Submit
Upload a JSON object with three keys:
- `actions`: at most 500 integer actions from 0 through 3.
- `mc_q`: 56 rows of 4 finite action values from your Monte Carlo run.
- `sarsa_q`: 56 rows of 4 finite action values from your SARSA run.

The notebook contains an export cell. No executable code or saved Python objects are uploaded for this task. Save the notebook and reward curves in your own workspace for review.

## Pilot scoring
The route contributes 20 points, Monte Carlo contributes 40, and SARSA contributes 40. A failed escape receives 0 for that part. A successful escape receives half the part's points plus the other half multiplied by shortest safe route length divided by steps taken. A shortest successful route earns full credit. Value tables are evaluated over five rollouts with fixed, published tie-breaking seeds for validation. Final evaluation uses five different tie-breaking seeds.

This is a fixed-map demonstration. It does not measure generalization to unseen maps. Plots, whether a table was actually learned, the zombie experiments, and the original written explanations require notebook review. The pilot's automated score is not the original 100-plus-15-point rubric.

## Explain before moving on
Show one state whose action values changed during learning. Explain one difference between Monte Carlo and SARSA. Show that a successful policy can be reloaded without retraining. Then try the optional zombie experiment in the source notebook.

## Provenance
Source: Hungarian AI Olympiad, 2025 summer national final. English translation credited to Tamás Takács, CC BY-NC-SA 4.0. The pilot adds a JSON submission format and the clearly described automatic scoring above. The original question sequence is supplied in `Source_Reading.ipynb` as a reading copy.
"""


def build_packs(project, state):
    project, state = Path(project), Path(state)
    cache = project / ".source-cache"
    judge = state / "judge"
    judge.mkdir(parents=True, exist_ok=True, mode=0o700)
    judge.chmod(0o700)
    source_manifest = json.loads((cache / "manifest.json").read_text())
    by_file = {item["file"]: item for item in source_manifest}
    for task_id, source_name in [("admissions", "admissions-starter.ipynb"), ("unet", "unet-starter.ipynb"), ("catacombs", "catacombs-starter.ipynb")]:
        pack = project / "packs" / task_id
        pack.mkdir(parents=True, exist_ok=True)
        nbformat.write(reading_copy(cache / source_name), pack / "Source_Reading.ipynb")
        metadata = {**TASKS[task_id], "pack_version": "pilot-1", "original_source": by_file[source_name],
                    "reading_copy_changes": "Outputs removed, punctuation normalized, local attribution style applied. Use Starter.ipynb for execution."}
        (pack / "Provenance.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
        statement = {"admissions": ADMISSIONS_STATEMENT, "unet": UNET_STATEMENT, "catacombs": CATACOMBS_STATEMENT}[task_id]
        (pack / "Statement.md").write_text(statement)
    pack = project / "packs" / "admissions"
    frame = pd.read_csv(cache / "admissions-train.csv")
    train, held = train_test_split(frame, test_size=0.30, random_state=20261104, stratify=frame["Felvételi Eredmény"])
    validation, test = train_test_split(held, test_size=0.5, random_state=20261105, stratify=held["Felvételi Eredmény"])
    train.to_csv(pack / "train.csv", index=False)
    for name, split in [("validation", validation), ("test", test)]:
        split.drop(columns="Felvételi Eredmény").to_csv(pack / f"{name}.csv", index=False)
    answers = pd.concat([validation[["ID", "Felvételi Eredmény"]].assign(partition="validation"),
                         test[["ID", "Felvételi Eredmény"]].assign(partition="test")])
    answers.to_csv(judge / "admissions-labels.csv", index=False)
    (judge / "admissions-labels.csv").chmod(0o600)
    shutil.copyfile(cache / "admissions-test.csv", pack / "original_test.csv")
    shutil.copyfile(cache / "counties.geojson", pack / "counties.geojson")
    admission_cells = [
        ("md", "# University Admissions\n\nRun the baseline, submit once, then improve it. Read Statement.md for the exact task contract. The target column is Hungarian because the original data is retained."),
        ("code", "from pathlib import Path\nimport numpy as np\nimport pandas as pd\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import roc_auc_score\n\ntrain = pd.read_csv('train.csv')\nvalidation = pd.read_csv('validation.csv')\ntest = pd.read_csv('test.csv')\nTARGET = 'Felvételi Eredmény'\nprint('Training rows:', len(train))\nprint('Admission rate:', train[TARGET].mean())\ntrain.head()"),
        ("md", "## 1. Establish a development result\n\nThe supplied baseline uses school prestige. Choose any improvements using your development split, then refit on all supplied training rows."),
        ("code", "features = ['Középiskola Presztízse']\nfit, dev = train_test_split(train, test_size=0.2, stratify=train[TARGET], random_state=2026)\nmodel = LogisticRegression(max_iter=1000, random_state=2026)\nmodel.fit(fit[features], fit[TARGET])\nprint('Development ROC AUC:', roc_auc_score(dev[TARGET], model.predict_proba(dev[features])[:, 1]))"),
        ("md", "## 2. Write a submission\n\nThis file must include validation and final-test IDs. The hub keeps their labels private. Submit the CSV using the upload button on the task page."),
        ("code", "model.fit(train[features], train[TARGET])\nquery = pd.concat([validation, test], ignore_index=True)\noutput = pd.DataFrame({'ID': query['ID'], TARGET: model.predict_proba(query[features])[:, 1]})\noutput.to_csv('predictions.csv', index=False)\nprint('Saved predictions.csv with', len(output), 'rows')\noutput.head()"),
        ("md", "## 3. Your next experiment\n\nRecord one hypothesis before changing the baseline. Consider the numeric and categorical columns, fit preprocessing only on your training split, and inspect errors. Use counties.geojson only if it helps a clear hypothesis. Save a copy of predictions.csv before replacing it."),
        ("code", "# Write your next experiment here\n"),
    ]
    nbformat.write(notebook(admission_cells), pack / "Starter.ipynb")
    source = nbformat.read(cache / "unet-starter.ipynb", as_version=4)
    architecture = source.cells[6].source
    architecture = architecture.replace("        # TODO Step 4: Return center-cropped tensor", "        # TODO Step 4: Return center-cropped tensor\n        raise NotImplementedError('Implement the center crop')")
    metric = '''def calculate_miou(pred_mask, true_mask, num_classes=2):
    """Average class IoUs, skipping classes with zero union."""
    raise NotImplementedError("Implement mean IoU")
'''
    submission = clean_text("import torch\nimport torch.nn as nn\nimport torch.nn.functional as F\nimport numpy as np\n\n" + architecture + "\n\n" + metric)
    (project / "packs" / "unet" / "submission.py").write_text(submission)
    unet_cells = [
        ("md", "# Debugging U-Net\n\nOpen submission.py in a second JupyterLab tab. Edit that file, save it, and rerun these checks. The provided functions intentionally need your repair. Read Statement.md for the source correction and exact requirements."),
        ("code", "import importlib\nimport torch\nimport submission\ntorch.set_num_threads(2)\nimportlib.reload(submission)\nmodel = submission.BrokenUNet()\ntry:\n    with torch.no_grad():\n        output = model(torch.randn(1, 3, 256, 256))\n    print('Output shape:', tuple(output.shape))\n    assert tuple(output.shape) == (1, 2, 110, 110)\nexcept Exception as error:\n    print(type(error).__name__ + ':', error)"),
        ("md", "## Check center cropping\n\nThe values matter as well as the shape. A resize is not a crop."),
        ("code", "importlib.reload(submission)\nx = torch.arange(63).reshape(1, 1, 7, 9)\ntry:\n    cropped = submission.BrokenUNet().center_crop(x, (1, 1, 3, 5))\n    assert torch.equal(cropped, x[:, :, 2:5, 2:7])\n    print('Center crop passed')\nexcept Exception as error:\n    print(type(error).__name__ + ':', error)"),
        ("md", "## Check the metric\n\nThe second case below corrects an error in the original source self-check. A predicted class with no true pixels still has a nonzero union."),
        ("code", "importlib.reload(submission)\ncases = [(torch.tensor([[[0, 0], [1, 1]]]), torch.tensor([[[0, 1], [1, 1]]]), 7 / 12),\n         (torch.tensor([[[0, 0], [0, 1]]]), torch.zeros((1, 2, 2), dtype=torch.long), 0.375),\n         (torch.zeros((1, 2, 2), dtype=torch.long), torch.zeros((1, 2, 2), dtype=torch.long), 1.0)]\nfor predicted, truth, expected in cases:\n    try:\n        actual = float(submission.calculate_miou(predicted, truth, 2))\n        print('Got', actual, 'expected', expected)\n        assert abs(actual - expected) < 1e-6\n    except Exception as error:\n        print(type(error).__name__ + ':', error)"),
        ("md", "## Submit and explain\n\nSave submission.py, then upload it on the hub task page. Keep your reasoning here: why was the skip larger, what does cropping discard, and why is accuracy insufficient for this task?"),
    ]
    nbformat.write(notebook(unet_cells), project / "packs" / "unet" / "Starter.ipynb")
    cat_cells = [
        ("md", "# Catacomb Adventure\n\nAll packages are already installed. Start by reading the map and one transition. The initial exported policy is deliberately weak. The full original exercise is in Source_Reading.ipynb. Read Statement.md before submitting."),
        ("code", "import json\nfrom pathlib import Path\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport gymnasium as gym\nimport creepy_catacombs_s1\n\nenv = gym.make('CreepyCatacombs-v0', render_mode='rgb_array')\nstate, info = env.reset(seed=2025)\nprint('Observation:', state, 'actions:', env.action_space.n)\nprint('Start:', info['agent_pos'], 'goal:', info['goal_pos'])\nprint(info['grid'])\nplt.imshow(env.render())\nplt.axis('off')\nplt.show()"),
        ("md", "## 1. Inspect one transition\n\nActions are 0 up, 1 right, 2 down, 3 left. Reset before testing another route."),
        ("code", "state, info = env.reset(seed=2025)\nnext_state, reward, terminated, truncated, info = env.step(0)\nprint('Next state:', next_state, 'reward:', reward)\nprint('Terminated:', terminated, 'truncated:', truncated)"),
        ("md", "## 2. Establish a route\n\nReplace the sequence with your safe route. Walls are -1, pits are -2, the start is 1, and the exit is 2. The source notebook guides a breadth-first search if you prefer to compute it."),
        ("code", "actions = [0, 0]\nstate, info = env.reset(seed=2025)\ntotal_reward = 0\nfor action in actions:\n    state, reward, terminated, truncated, info = env.step(action)\n    total_reward += reward\n    if terminated or truncated:\n        break\nprint('Route reward:', total_reward, 'position:', info['agent_pos'])"),
        ("md", "## 3. Learn action values\n\nImplement Monte Carlo control and SARSA in the cells below. Begin with zero-filled tables of shape 56 by 4, use exploratory episodes while training, and log episode returns. For Monte Carlo, update using complete returns. For SARSA, update from reward and the next chosen action value. Reset to seed 2025 for this fixed-map pilot. You can use the original notebook's unfinished training loops as scaffolding."),
        ("code", "mc_q = np.zeros((env.observation_space.n, env.action_space.n))\nsarsa_q = np.zeros_like(mc_q)\nmc_returns = []\nsarsa_returns = []\n\n# Implement your training loops here\n"),
        ("md", "## 4. Export your submission\n\nThe export cell already runs. Improve the route and tables, rerun it, then upload policy.json. Keep your notebook and plots for peer review."),
        ("code", "payload = {'actions': [int(a) for a in actions], 'mc_q': mc_q.tolist(), 'sarsa_q': sarsa_q.tolist()}\nPath('policy.json').write_text(json.dumps(payload, allow_nan=False))\nprint('Saved policy.json')\nprint('Validation tie seeds: 7, 11, 19, 23, 31')"),
        ("md", "## 5. Review\n\nPlot raw episode returns and a moving average after training. Explain one changed state-action value and compare the two learning rules. Then attempt the optional source exercises with zombies. Automatic points cover the fixed map only."),
        ("code", "env.close()"),
    ]
    nbformat.write(notebook(cat_cells), project / "packs" / "catacombs" / "Starter.ipynb")
    build_china_packs(project, state, notebook)
    for task_id in TASKS:
        pack = project / "packs" / task_id
        with zipfile.ZipFile(project / "packs" / f"{task_id}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(pack.iterdir()):
                if file.is_file():
                    archive.write(file, f"{task_id}/{file.name}")

