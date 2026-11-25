"""Pilot grading orchestration."""

import ast
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

import pandas as pd

from .admissions import SubmissionError, grade_predictions
from .china import CHINA_TASKS, grade_china
from .sandbox import run_isolated


class Grader:
    def __init__(self, project, state):
        self.project = Path(project)
        self.state = Path(state)
        (self.state / "evaluation").mkdir(parents=True, exist_ok=True, mode=0o700)

    def grade(self, task, path, partition="validation"):
        path = Path(path)
        started = time.monotonic()
        if task == "admissions":
            answers = pd.read_csv(self.state / "judge" / "admissions-labels.csv")
            result = grade_predictions(path.read_bytes(), answers, partition)
        elif task == "unet":
            try:
                tree = ast.parse(path.read_text())
            except (SyntaxError, UnicodeError) as exc:
                raise SubmissionError(f"The Python file could not be parsed: {str(exc)[:180]}") from None
            for node in ast.walk(tree):
                modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                if any(module.split(".")[0] not in ("torch", "numpy") for module in modules):
                    raise SubmissionError("This task permits only torch and NumPy imports")
            result = self.isolated(task, path, partition)
        elif task == "catacombs":
            result = self.isolated(task, path, partition)
        elif task in CHINA_TASKS:
            result = grade_china(self.project, self.state, task, path, partition)
        else:
            raise SubmissionError("Unknown task")
        result["runtime_seconds"] = round(time.monotonic() - started, 3)
        return result

    def isolated(self, task, path, partition):
        with tempfile.TemporaryDirectory(dir=self.state / "evaluation") as folder:
            work = Path(folder)
            target = "submission.py" if task == "unet" else "policy.json"
            shutil.copyfile(path, work / target)
            result = run_isolated(Path(sys.executable), self.project / "hub" / "worker.py", work,
                                  timeout=90, arguments=(task, partition))
            output = work / "result.json"
            if result.returncode != 0 or not output.exists():
                diagnostic = (result.stderr or result.stdout).strip()[-1200:]
                raise SubmissionError("Evaluation did not finish. " + diagnostic)
            report = json.loads(output.read_text())
            if "error" in report:
                raise SubmissionError(report["error"])
            return report
