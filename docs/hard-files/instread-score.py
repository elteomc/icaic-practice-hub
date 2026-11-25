"""Score labeled InstRead practice predictions with the organizer's formula."""

import argparse
import csv
from math import fsum, isfinite, sqrt
from pathlib import Path


def read_answers(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        if rows.fieldnames != ["subtaskID", "datapointID", "answer"]:
            raise ValueError(f"{path}: expected subtaskID,datapointID,answer")
        answers = {}
        for row in rows:
            try:
                ident = int(row["datapointID"])
                answer = float(row["answer"])
            except (TypeError, ValueError):
                raise ValueError(f"{path}: invalid ID or answer on line {rows.line_num}") from None
            if row["subtaskID"] != "1" or ident in answers or not isfinite(answer) or None in row:
                raise ValueError(f"{path}: invalid or duplicate row on line {rows.line_num}")
            answers[ident] = answer
    return answers


def score(reference, predictions):
    if reference.keys() != predictions.keys() or len(reference) < 2:
        raise ValueError("Both files need the same IDs and at least two observations")
    truth = list(reference.values())
    predicted = [predictions[ident] for ident in reference]
    truth_mean = fsum(truth) / len(truth)
    predicted_mean = fsum(predicted) / len(predicted)
    centered_truth = [value - truth_mean for value in truth]
    centered_predicted = [value - predicted_mean for value in predicted]
    truth_variation = fsum(value ** 2 for value in centered_truth)
    predicted_variation = fsum(value ** 2 for value in centered_predicted)
    error = fsum((actual - guess) ** 2 for actual, guess in zip(truth, predicted))

    if truth_variation:
        r_squared = max(0.0, 1 - error / truth_variation)
    else:
        r_squared = float(error == 0)
    denominator = sqrt(truth_variation) * sqrt(predicted_variation)
    correlation = fsum(a * b for a, b in zip(centered_truth, centered_predicted)) / denominator if denominator else 0
    return 50 * (r_squared + min(1.0, abs(correlation)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labeled_holdout", help="CSV of reference answers with subtaskID,datapointID,answer")
    parser.add_argument("predictions", help="CSV of your predictions with the same IDs")
    args = parser.parse_args()
    try:
        result = score(read_answers(args.labeled_holdout), read_answers(args.predictions))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Local InstRead score: {result:.4f} / 100")


if __name__ == "__main__":
    main()
