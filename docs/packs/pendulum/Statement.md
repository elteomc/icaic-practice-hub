# Pendulum Motion

Use **Notebook & files** to make your own Colab copy. Export the ZIP when you finish, then follow **Grading & notes** on the task page. The grader returns validation and final practice results from public practice fixtures.

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

Package submission.py defining solve(frame). frame is a pandas DataFrame with t and theta only. Return exactly a dictionary with finite numeric values for l, miu, F, t_nextzerotheta, and t_Fput. The function is called independently on each recording. t_nextzerotheta must be the first zero crossing strictly after the final observation. Maximum source size is 2 MB. Validation evaluation has a 90-second total time limit.

This callable replaces the original full submission notebook so the room can rerun a method on withheld recordings. Keep derivations, plots, and training steps in Starter.ipynb for review. The linked original statement describes submission_train.csv, submissionA.csv, and submissionB.csv. Those files are not the room's submission contract.

## Scoring

For absolute errors e_l, e_miu, e_F, e_next, and e_switch:

    score = (exp(-10*e_l) + exp(-10*e_miu) + 2*exp(-e_F)
             + 2*exp(-10*e_next) + 2*exp(-10*e_switch)) / 8

The room averages this score across recordings. One is perfect and larger is better. Feedback includes each parameter's mean absolute error. The grader also evaluates separate final practice recordings. This uses the source metric on practice fixtures, not official hidden A or B data.

## Source and review

China NOAI 2024 task 4, republished as APOAI 2025 mock task 4. Source_Statement.md includes the problem and score, with the solved appendix omitted. Explain how you handle the gap, why a force change modifies the frequency, and how you check the inferred trajectory against the observed one.
