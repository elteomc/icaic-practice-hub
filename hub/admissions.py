"""Admission prediction validation and evaluation."""

import csv
import io
import math


class SubmissionError(ValueError):
    pass


def validate_predictions(payload: bytes, expected_ids: list[int]) -> dict[int, float]:
    try:
        reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
        if reader.fieldnames != ["ID", "Felvételi Eredmény"]:
            raise SubmissionError("Use exactly the columns ID,Felvételi Eredmény")
        predictions = {}
        for row in reader:
            row_id = int(row["ID"])
            if row_id in predictions:
                raise SubmissionError(f"Found a duplicate ID: {row_id}")
            probability = float(row["Felvételi Eredmény"])
            if not math.isfinite(probability) or not 0 <= probability <= 1:
                raise SubmissionError(f"ID {row_id} needs a finite probability between 0 and 1")
            predictions[row_id] = probability
    except (UnicodeError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, SubmissionError):
            raise
        raise SubmissionError("Could not read the CSV IDs and probabilities") from exc
    if set(predictions) != set(expected_ids):
        missing = len(set(expected_ids) - set(predictions))
        extra = len(set(predictions) - set(expected_ids))
        raise SubmissionError(f"Match all required IDs exactly, missing {missing}, extra {extra}")
    return predictions


def grade_predictions(payload, answers, partition="validation"):
    from sklearn.metrics import log_loss, roc_auc_score

    predictions = validate_predictions(payload, [int(value) for value in answers["ID"]])
    selected = answers.loc[answers["partition"] == partition]
    probabilities = [predictions[int(value)] for value in selected["ID"]]
    truth = selected["Felvételi Eredmény"].to_numpy()
    auc = float(roc_auc_score(truth, probabilities))
    return {"score": auc, "metric": "ROC AUC", "display": f"{auc:.4f}",
            "details": [{"name": "ROC AUC", "value": round(auc, 6)},
                        {"name": "Log loss", "value": round(float(log_loss(truth, probabilities)), 6)},
                        {"name": "Evaluated rows", "value": len(selected)}],
            "summary": f"Scored {len(selected)} {partition} rows. Higher ROC AUC is better.",
            "partition": partition}
