"""Publish a bounded grading receipt after evaluation finishes."""

import json
import os
from pathlib import Path
import urllib.request


def main():
    payload = Path("receipt.json").read_bytes()
    if len(payload) > 64000:
        raise SystemExit("The receipt exceeds the publication limit")
    receipt = json.loads(payload)
    if receipt.get("schema") != "icaic-grade-v1" or type(receipt.get("issue")) is not int:
        raise SystemExit("Invalid grading receipt")
    if receipt["status"] == "graded":
        text = f"Practice grading complete.\n\nValidation: **{receipt['validation']['display']}**\n\nFinal practice holdout: **{receipt['final']['display']}**\n\n"
        text += "These are inspectable practice fixtures. See the task statement for differences from the original contest.\n\n"
    else:
        text = "The submission needs repair. Read the error in the receipt below, then open a new submission with a corrected file.\n\n"
    text += "<!-- icaic-grade-v1 -->\n```json\n" + json.dumps(receipt, indent=2) + "\n```"
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{receipt['issue']}/comments"
    request = urllib.request.Request(url, data=json.dumps({"body": text}).encode(), method="POST", headers={
        "Authorization": "Bearer " + os.environ["GH_TOKEN"], "Accept": "application/vnd.github+json",
        "Content-Type": "application/json", "User-Agent": "ICAIC-Practice-Room"})
    with urllib.request.urlopen(request, timeout=30) as response:
        print("Grading receipt published:", response.status)


if __name__ == "__main__":
    main()
