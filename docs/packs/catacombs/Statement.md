# Catacomb Adventure

Use **Notebook & files** to open your own Colab copy. The final export cell creates the ZIP for **Submit & notes**. Both validation and final practice scores are returned on each submission. The free hub uses public practice fixtures and a personal browser timer.

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
