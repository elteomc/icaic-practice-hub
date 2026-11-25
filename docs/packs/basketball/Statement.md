# Basketball Shooting

Use **Notebook & files** to open your own Colab copy. The final export cell creates the ZIP for **Submit & notes**. Both validation and final practice scores are returned on each submission. The free hub uses public practice fixtures and a personal browser timer.

Use the location of a basketball shot to predict whether it goes in. Start by asking whether shots near the basket have a different success rate. A small model and a sound validation split matter more than a large network here.

## Your first ten minutes

1. Open Starter.ipynb. It loads train.csv and shows the first rows.
2. Plot loc_x against loc_y, colouring points by shot_made_flag.
3. Run the deliberately untrained starter once to check packaging and submission.
4. Make a development split inside train.csv before choosing a training method.

## Data and model rules

The supplied train.csv contains 17,500 labeled shots, 70% of the 25,000 rows in the public mirror. Validation and final test each use 3,750 different rows. Their labels are reserved for evaluation. The free repository's practice fixtures are public and inspectable. These are practice partitions, not the original hidden competition test.

Use **only loc_x and loc_y as model inputs**, in that order. Predict shot_made_flag, where 1 means a made shot. The other columns are supplied for context and cannot be inputs. Do not fetch the original public labels for the withheld rows.

Implement PyTorch class MyModel with a no-argument constructor. Use one to three nn.Linear layers, each with at most eight output neurons. Other permitted leaf modules are nn.ReLU, nn.Sigmoid, nn.Tanh, nn.ELU, nn.LeakyReLU, and nn.PReLU. Do not use nn.Sequential. Return one **raw logit** per row, shape N or N by 1. The evaluator applies sigmoid and thresholds at 0.5. Fit preprocessing on your training rows only and include it in the exported model. Inputs at evaluation are the original CSV coordinates.

## Submit and improve

Save submission.zip with exactly submission_model.py and submission_dic.pth at its root. The Python file defines MyModel and imports. The weights file is a torch state_dict. Do not include training code that executes when imported. Maximum ZIP size is 8 MB. The notebook includes a packaging cell.

Validation feedback reports accuracy and majority-class accuracy. The final practice evaluation uses the other 3,750 rows. Each cloud submission receives both validation and final results. Accuracy is the primary score. Save the split, seed, loss, and one explanation of your errors in the notebook.

## Source and changes

This is China NOAI 2024 task 1, republished as APOAI 2025 mock task 1. The linked original statement describes 20,000 training rows, while the public mirror contains 25,000. This room uses the mirror and its own disclosed partitions. The architecture and model ZIP contract are retained. Read Source_Statement.md for a punctuation-normalized source reading copy.
