# University Admissions

Use **Notebook & files** to open your own Colab copy. The final export cell creates the ZIP for **Submit & notes**. Both validation and final practice scores are returned on each submission. The free hub uses public practice fixtures and a personal browser timer.

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

The supplied training rows are 70% of the original public training data. Validation and final test each contain 15%, with a fixed stratified split. Their labels are reserved for evaluation. The free repository's practice fixtures are public and inspectable. Do not use external data or attempt to recover withheld answers from the source repository.

## Work and improve
Make a development split inside `train.csv` before choosing features and models. The provided baseline uses only school prestige. Compare it with one carefully chosen improvement. Inspect errors and record the split and metric. Optional geographic features can use the county names and coordinates in the supplied GeoJSON.

Use Python, NumPy, pandas, scikit-learn, and the supplied companion data. All required packages are installed. No downloads are needed.

## Submit
Upload one UTF-8 CSV with exactly two columns: `ID,Felvételi Eredmény`. Include every ID from both `validation.csv` and `test.csv` exactly once. Every prediction must be finite and between 0 and 1. Row order does not matter.

The hub returns validation ROC AUC and log loss. Higher ROC AUC is better. Each cloud submission receives validation and final practice holdout results together. Submit after finishing an independent attempt.

## Explain before moving on
Which feature change helped on your own development split? Could an identifier, duplicate, or county grouping create misleading validation? Can someone else recreate the CSV from your saved notebook?

## Provenance and pilot changes
Source: Hungarian AI Olympiad, 2025 summer online qualifier. English translation credited to Tamás Takács, CC BY-NC-SA 4.0. This educational adaptation preserves source credit. The local split and submission arrangement differ from the original Kaggle event. These are practice results, not official competition scores.
