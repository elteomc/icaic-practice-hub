# Real or Fake Images

Use **Notebook & files** to make your own Colab copy. Export the ZIP when you finish, then follow **Grading & notes** on the task page. The grader returns validation and final practice results from public practice fixtures.

Distinguish real CIFAR images from generated images. Both classes are small RGB images of the same dimensions. Look for repeatable visual evidence rather than memorizing filenames.

## Your first ten minutes

1. Open Starter.ipynb and extract images_train.zip.
2. Display several images from each class, using train.csv as the label map.
3. Run the untrained starter and export its model ZIP to check the submission path.
4. Make a stratified development split before training or changing the network.

## Data and preprocessing

The pack contains 7,000 labeled 32 by 32 RGB training images. Real is 0 and generated is 1. The evaluator reserves 1,500 images for validation and 1,500 different images for final testing from the same public 10,000-image archive. This is a fixed stratified 70/15/15 practice split. Original hidden competition images are unavailable.

Use float32 input tensors in N by 3 by 32 by 32 order, normalized with pixel / 127.5 - 1. Use the same normalization in training and evaluation. The evaluator supplies these normalized tensors directly.

## Model rules

Implement PyTorch class MyModel with a no-argument constructor. Include at least two nn.Conv2d and two nn.MaxPool2d modules, used in the forward pass. Use at most two nn.Linear modules. Permitted activation modules are nn.ReLU, nn.Sigmoid, nn.Tanh, nn.ELU, nn.LeakyReLU, and nn.PReLU. Do not use nn.Sequential. Other leaf modules are not accepted. Tensor operations such as reshape and flatten are allowed.

Return one **probability** per image, shape N or N by 1, between 0 and 1. The evaluator thresholds at 0.5. This differs from Basketball Shooting's raw-logit contract. A final sigmoid is a straightforward way to satisfy it.

## Submit and scoring

Save submission.zip with exactly submission_model.py and submission_dic.pth at its root. The Python file defines MyModel and imports. Save a torch state_dict as the weights file. Keep training outside the submitted class file. Maximum ZIP size is 8 MB.

Feedback reports accuracy, counted convolutional and linear layers, and the practice composite score:

    simplicity = 1 / (number_of_linear_layers + number_of_convolutional_layers + 1)
    score = 0.75 * (accuracy + simplicity)

The original statement mentions a historical bug that doubled accuracy. This practice evaluator uses ordinary accuracy. Its score therefore cannot be compared numerically with that historical leaderboard. The final practice evaluation uses different held-out images.

## Source and review

This is China NOAI 2024 task 2, republished as APOAI 2025 mock task 2. Source_Statement.md contains a reading copy. The public archive supplies 5,000 real and 5,000 generated images. Do not recover withheld labels from the original archive during an independent attempt. Explain one false positive, one false negative, and whether an improvement survived your own development split.
