"""Evaluate a GitHub attachment using the same isolated task graders."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from urllib.parse import urlsplit
import urllib.request
import zipfile

from hub.grading import Grader
from hub.packs import TASKS


def parse_issue(body):
    fields = dict(re.findall(r"^### ([^\n]+)\n+([\s\S]*?)(?=^### |\Z)", body, re.MULTILINE))
    task = fields.get("Task", "").strip()
    name = fields.get("Participant", "").strip()
    if task not in TASKS:
        raise ValueError("Choose a known task")
    if name not in ("Angelo", "Colin", "Anna"):
        raise ValueError("Choose a known participant profile")
    links = re.findall(r"https://github\.com/user-attachments/files/[0-9]+/[A-Za-z0-9_.-]+\.zip", fields.get("Submission", ""))
    if len(links) != 1:
        raise ValueError("Attach exactly one ZIP using GitHub's attachment button")
    return {"task": task, "name": name, "url": links[0], "mode": fields.get("Practice mode", "Learning").strip()[:80]}


class SafeRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urlsplit(newurl)
        allowed = url.hostname == "github.com" or (url.hostname or "").endswith((".githubusercontent.com", ".amazonaws.com", ".githubassets.com"))
        if url.scheme != "https" or not allowed:
            raise ValueError("The attachment redirected outside GitHub's file storage")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_attachment(url, path):
    request = urllib.request.Request(url, headers={"User-Agent": "ICAIC-Practice-Room"})
    with urllib.request.build_opener(SafeRedirects).open(request, timeout=45) as response:
        data = response.read(8 * 1024 ** 2 + 1)
    if len(data) > 8 * 1024 ** 2:
        raise ValueError("The attached ZIP exceeds 8 MB")
    path.write_bytes(data)


def unwrap_submission(task, archive_path, directory):
    if task in ("basketball", "real-fake"):
        return archive_path
    expected = TASKS[task]["upload_name"]
    with zipfile.ZipFile(archive_path) as archive:
        items = archive.infolist()
        if len(items) != 1 or items[0].filename != expected or items[0].file_size > 2 * 1024 ** 2:
            raise ValueError(f"For this task, attach a ZIP containing only {expected} at its root")
        output = directory / expected
        output.write_bytes(archive.read(items[0]))
        return output


def evaluate(project, state, request, path):
    receipt = {"schema": "icaic-grade-v1", "task": request["task"], "name": request["name"],
               "mode": request["mode"], "created": int(time.time()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "evaluation": "Public practice fixtures, not protected official test data"}
    grader = Grader(project, state)
    try:
        receipt["validation"] = grader.grade(request["task"], path, "validation")
        receipt["final"] = grader.grade(request["task"], path, "test")
        receipt["status"] = "graded"
    except Exception as exc:
        receipt["status"] = "needs-repair"
        receipt["error"] = str(exc)[:1500]
    return receipt


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--smoke-task", choices=["all", "basketball", "real-fake", "pendulum"])
    mode.add_argument("--local", nargs=2, metavar=("TASK", "ZIP"),
                      help="score your own exported practice submission")
    args = parser.parse_args()
    project = Path(__file__).resolve().parent
    state = project / "evaluation-state"
    state.mkdir(exist_ok=True)
    (state / 'evaluation').mkdir(exist_ok=True)
    if args.local:
        task, path = args.local
        path = Path(path).resolve()
        if task not in TASKS:
            parser.error(f"Choose a task ID from: {', '.join(TASKS)}")
        if not path.is_file() or path.suffix.lower() != '.zip' or path.stat().st_size > 8 * 1024 ** 2:
            parser.error("Choose a submission ZIP no larger than 8 MB")
        try:
            with tempfile.TemporaryDirectory() as folder:
                submission = unwrap_submission(task, path, Path(folder))
                request = {"task": task, "name": "Local practice", "mode": "Local"}
                receipt = evaluate(project, state, request, submission)
        except (ValueError, OSError, zipfile.BadZipFile) as exc:
            parser.error(str(exc))
        print(json.dumps(receipt, indent=2, allow_nan=False))
        if receipt['status'] != 'graded':
            raise SystemExit(1)
        return
    if args.smoke_task:
        from nbclient import NotebookClient
        import nbformat
        tasks = ("basketball", "real-fake", "pendulum") if args.smoke_task == "all" else (args.smoke_task,)
        results = []
        for task in tasks:
            with tempfile.TemporaryDirectory() as folder:
                workspace = Path(folder) / task
                shutil.copytree(project / "docs" / "packs" / task, workspace)
                notebook = nbformat.read(workspace / "Starter.ipynb", as_version=4)
                NotebookClient(notebook, timeout=90, resources={"metadata": {"path": str(workspace)}}).execute()
                request = {"task": task, "name": "Angelo", "mode": "Infrastructure check"}
                receipt = evaluate(project, state, request, workspace / TASKS[task]["upload_name"])
                results.append(receipt)
                print(task, receipt["status"], receipt.get("validation", {}).get("display", receipt.get("error")))
        (project / "smoke-results.json").write_text(json.dumps(results, indent=2))
        if any(item["status"] != "graded" for item in results):
            raise SystemExit("A cloud grading check failed")
        return
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = event["issue"]
    try:
        request = parse_issue(issue.get("body") or "")
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            attachment = directory / "attachment.zip"
            fetch_attachment(request["url"], attachment)
            path = unwrap_submission(request["task"], attachment, directory)
            receipt = evaluate(project, state, request, path)
        receipt["issue"] = issue["number"]
        receipt["author"] = issue["user"]["login"]
    except Exception as exc:
        receipt = {"schema": "icaic-grade-v1", "status": "needs-repair", "issue": issue["number"], "error": str(exc)[:1500]}
    (project / "receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False))
    print("Submission evaluated:", receipt["status"])


if __name__ == "__main__":
    main()
