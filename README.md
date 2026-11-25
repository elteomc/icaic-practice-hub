# ICAIC Practice Room

Open the [practice hub](https://elteomc.github.io/icaic-practice-hub/) or go straight to the [Hard? list](https://elteomc.github.io/icaic-practice-hub/#hard).

## Make an attempt

1. Select your local profile and open a task. Read **The task**, then check the files and scoring instructions.
2. Download the files and open the starter before starting the timer. Use **Independent** for a countdown or **Learning** for elapsed time. For a contest rehearsal, agree on the same time limit and allowed resources before anyone starts.
3. Save your solution and record the score, validation split and time spent in the task's notes. Progress shows your history and lets you back it up or import a previous backup.

For the six original tasks, open the notebook in Colab, save a copy, and run setup. Use **Download for the hub** when you finish. **Submit & notes** points to the available grading route. The practice validation and final holdout use public fixtures. Keep the latter sealed until the end of a blind attempt.

## Hard?

The list contains two WAICC tasks, Battlecode, an industrial vision challenge, and the EEG transfer challenge. The Global Campus collection includes a brief for each of the five 2026 Algorithm Challenge problems and the organizer's six track indexes.

- **Local evaluator** points to a simulator or an organizer's local scoring package.
- **Organizer account** identifies tasks whose files or submissions use the organizer's platform. Confirm access before scheduling a timed session.
- **Organizer data required** marks briefs for the Global Campus contest. Use any public example to check file format. Obtain permission and the relevant phase files for a scored attempt.

Use the evaluator named on each task page. Keep score, split and runtime together in your practice notes. Third-party files remain with their sources.

## Grade an original task locally

On Linux, download or clone this repository. Install `uv` and `bubblewrap`. The local grader uses the same submitted ZIP format and public practice fixtures as the cloud grader. It runs submitted Python jobs with process isolation and no network.

```sh
uv sync --frozen
uv run --frozen python cloud_grade.py --local admissions /path/to/hub-upload.zip
```

Replace `admissions` with the task ID shown on the task's page. The other IDs are `unet`, `catacombs`, `basketball`, `real-fake`, and `pendulum`. Basketball and Real or Fake Images use their original `submission.zip`. The command returns validation and final practice results, or gives a reason the submission could not be scored.

## Cloud grading

When the hub offers **Open submission form**, attach the exported ZIP to a new GitHub issue and wait for the grading receipt. Owners and collaborators can trigger grading automatically. Other graded requests require the repository owner to add the `grade` label after reviewing the request. Each revised submission needs a new issue. GitHub issue attachments and receipts are public.

The owner can install the [prepared grading workflow](setup/grade.yml) as `.github/workflows/grade.yml`. Then use **Actions → Grade a practice submission → Run workflow → all**. This checks the three China notebooks without posting an issue. Set `cloudGrading` in `docs/tasks.json` to `true` only after the workflow and the `submission` and `grade` labels are available.

GitHub Pages serves `docs` from `main`. The published site and notebooks work without a host laptop. Free Colab runtimes may disconnect, so download your work before leaving.

## Verify the site locally

```sh
node --test tests/hard-navigation.test.cjs
python3 -m http.server 8000 --directory docs
```

Open `http://127.0.0.1:8000/`. The JSON catalogs are loaded over HTTP.
