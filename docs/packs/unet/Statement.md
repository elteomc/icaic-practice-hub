# Debugging U-Net

Use **Notebook & files** to make your own Colab copy. Export the ZIP when you finish, then follow **Grading & notes** on the task page. The grader returns validation and final practice results from public practice fixtures.

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
Package `submission.py`, exporting `BrokenUNet` and `calculate_miou`. Do not include notebook display or training code in that file. The starter already separates the editable submission from the notebook checks. The evaluator runs code in an isolated process with a 90-second wall-clock limit. No GPU or model training is needed.

Validation feedback lists passed and failed checks. The final practice evaluation uses a separate set of generated tensors. Scores are automated pilot checks out of 20, not an official exam mark.

## Explain before moving on
Why does cropping lose border information? How does an always-background prediction behave under pixel accuracy versus mean IoU? Which test caught a mistake your first example missed?

## Provenance
Source: Singapore NOAI 2026 final assessment, programming task 2, published by AISGNUSNOAI. The supplied task and architecture are retained. Corrections and the pilot's automated evaluation are identified above. `Source_Reading.ipynb` preserves the source content for comparison, with outputs removed and punctuation normalized.
