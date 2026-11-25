## Question 4 of APOAI2025 Mock Competition: Solving the Pendulum Motion with Missing Data
**Introduction**: This is the Question 4 of APOAI2025 Mock Competition, and it is also the fourth question of the NOAI2024(China).

### I. Question Overview

A dataset for pendulum motion is provided, which is stored in a .csv file and contains two variables:

* **t**: Time, unit: second (s), it is in the standard unit, and there is no need to consider unit conversion during the problem-solving process,
* **theta**: The angle of the pendulum, with positive and negative values indicating the direction, and the unit is radian, that is, there is no need to consider unit conversion when using the sin function for operations.

Based on the above dataset, please use PyTorch to regress the relevant parameters of the pendulum motion with resistance, fill in the missing data and make predictions.


### II. Data Set

There are three datasets.

(1) Training set: pendulum_train.csv, Address of the training set: [Training Set](https://bohrium.dp.tech/competitions/1723157880?tab=datasets),

(2) Test set A: pendulum_testA.csv. Contestants cannot directly download Test set A during the competition,

(3) Test set B: pendulum_testB.csv. Contestants cannot directly download Test set B during the competition.

The data in the training set is all visible, which can help contestants generate methods for solving parameters. The data of Test set A is invisible to contestants, but it will be displayed in the Leaderboard A, which can help contestants verify whether the method for solving parameters is correct. The data of Test set B is invisible to contestants and will finally be used when calculating scores in the Leaderboard B.

**Note**: The differential equation parameters of the training set, Test set A and Test set B are all different. What contestants need to submit is a solution method that can be applied to different data. When importing different data sets, that is, when importing the training set, Test set A and Test set B, the correct parameters can be solved.

### III. Task

In machine learning, we sometimes encounter scenarios where we need to extract the patterns in data with a small amount of data. In such scenarios, how to make full use of prior knowledge (formulas) to process data, design models and successfully solve unknown parameters is the key to solving the problem. Now consider a pendulum scenario.

![alt](https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/article/18653/5ccbf3267faa4091b3f030b5bf8964d2/cc39ba2e-009a-4df2-90c2-0ad48cb67860.png)

As shown in the above figure, there is a small ball with a mass of 1 ($m = 1$) that can be regarded as a particle, which is suspended by a light rope with a length of $l$ at a fixed point $O$. Let $\theta(t)$ be the angle between the rope and the vertical line passing through $O$ at time $t$, which is called the pendulum angle. Stretch the rope straight and release the small ball with an initial pendulum angle ${{\theta }_{0}}<\pi /2$ (in radian measure). At $t = 0$, release the small ball without an initial velocity, and then the small ball can move in the plane corresponding to the light rope and the vertical line. Here, taking the initial pendulum angle ${{\theta }_{0}}$ as positive, when the small ball is on the left side of the vertical line, the sign of the pendulum angle $\theta(t)$ is recorded as positive, and when it is on the right side of the vertical line, the sign of the pendulum angle $\theta(t)$ is recorded as negative. Let the acceleration due to gravity be $g = 9.8$ (during the whole problem-solving process, there is no need to consider unit conversion, and you can directly operate on the numerical values). Consider the air resistance whose magnitude is proportional to the velocity and whose direction is opposite to the velocity, and the magnitude of the air resistance $\mu$ remains constant during the motion.

There is a sensor that can accurately record the pendulum angle of the small ball. However, during the experiment, the sensor had a problem. It suddenly interrupted for several seconds ($\ge 1s$) during the recording and was restarted only after that, and it stopped working before the small ball stopped moving. **It is known that starting from a certain moment ${{t}_{Fput}}$ during the interrupted period, the small ball was subjected to a constant external force $F$ in the vertical downward direction, and this continued until the end of the motion**. Please try to infer and predict the situation of the small ball based on the recorded data. The data is in the .csv file, which includes two columns. The first column records the time stamp $t$ of the small ball's motion, represented by the variable $t$, and the second column records the pendulum angle information $\theta$ of the small ball, represented by the variable theta. We plot the pendulum angle data $\theta(t)$ in the training set as follows:

![alt](https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/article/18653/5ccbf3267faa4091b3f030b5bf8964d2/db279895-a660-4fdd-a23c-d679c38075c6.png)

To solve this problem, you need to have prior knowledge of differential equations. During the whole motion process, the angular velocity $\omega(t)$ refers to the instantaneous change rate of $\theta(t)$ (with positive and negative values), and the angular acceleration $a(t)$ refers to the instantaneous change rate of the angular velocity $\omega(t)$ (with positive and negative values), that is, $\omega(t)=\frac{d\theta(t)}{dt}$, $a(t)=\frac{d\omega(t)}{dt}$. Then, in the above pendulum problem, $a(t)$ should satisfy the following differential equation with $\omega(t)$ and $\theta(t)$:

$a(t)=-\alpha \cdot \omega(t)-\beta \sin \left( \theta(t) \right)$, where $\alpha, \beta$ are parameters. According to Newton's second law, $\alpha =\frac{\mu }{m}$.

When $0\le t<{{t}_{Fput}}$, no external force is applied. At this time, $\beta ={{\beta }_{1}}=\frac{g}{l}$,

When $t\ge {{t}_{Fput}}$, an external force $F$ is applied. At this time, $\beta ={{\beta }_{2}}=\frac{g}{l}+\frac{F}{ml}$.

Using the differential equation, if $\alpha, {{\beta }_{1}}, {{\beta }_{2}}$ are known, when the angular velocity $\omega(t)$ and the pendulum angle $\theta(t)$ at time $t$ are known, $a(t)$ can be calculated according to the differential equation. However, the problem in this question is that $\alpha, {{\beta }_{1}}, {{\beta }_{2}}$ are unknown, and only the pendulum angle data $\theta(t)$ recorded at each moment is available. You need to "regress" $\alpha, {{\beta }_{1}}, {{\beta }_{2}}$ according to the provided data. This is the core task in this question. After obtaining $\alpha, {{\beta }_{1}}, {{\beta }_{2}}$, it is equivalent to obtaining the entire differential equation, and then you can use the differential equation to complete and predict the pendulum angle data of the small ball.

Specifically, you need to solve the following parameters according to the time $t$ and $\theta(t)$ data recorded in the.csv file:

1. The length of the rope: $l$,
2. The air resistance: $\mu$,
3. The magnitude of the external force applied in the middle: $F$,
4. Predict the moment when the pendulum angle $\theta(t) = 0$ after the sensor detection ends (after the data recording ends) and after the external force is applied: ${{t}_{nextzerotheta}}$,
5. The time when the external force is applied: ${{t}_{Fput}}$.

### IV. Submission

Please submit the submission.ipynb file, which contains the entire process of training the model and the entire process of parameter solution.

The submission.ipynb needs to be able to generate three files:

1. The parameter solution results of the training set are stored in submission_train.csv,
2. The parameter solution results of Test set A are stored in submissionA.csv,
3. The parameter solution results of Test set B are stored in submissionB.csv.

The storage format of the parameters is shown in the following table. If some parameters are not solved, please fill in a default parameter, for example, 1, and do not leave it blank:

| l   | miu | F   | t_nextzerotheta | t_Fput |
| --- | --- | --- | --------------- | ------ |
| 1   | 1   | 10  | 1               | 1      |

You can refer to the submission format in baseline.ipynb.

baseline.ipynb address: [Question 4 of APOAI2025 Mock Competition_baseline](https://bohrium.dp.tech/notebooks/47347521216)

### V. Scoring

1. The final scoring matrix is as follows: where $X\_pre$ is the predicted value of parameter $X$ by the contestant, and $X\_real$ is the real value of parameter $X$,

   (1) Scoring for solving the length of the rope $l$: ${{S}_{1}}=\exp (-10\left| l\_pre-l\_real \right|)$,

   (2) Scoring for solving the air resistance $\mu$: ${{S}_{2}}=\exp (-10\left| \mu\_pre-\mu\_real \right|)$,

   (3) Scoring for solving the external force $F$: ${{S}_{3}}=\exp (-\left| F\_pre-F\_real \right|)$,

   (4) Scoring for solving the moment when the next pendulum angle $\theta(t) = 0$, ${{t}_{nextzerotheta}}$: ${{S}_{4}}=\exp (-10\left| {{t}_{nextzerotheta}}\_pre-{{t}_{nextzerotheta}}\_real \right|)$,

   (5) Scoring for solving the moment when the external force is applied, ${{t}_{Fput}}$: ${{S}_{5}}=\exp (-10\left| {{t}_{Fput}}\_pre-{{t}_{Fput}}\_real \right|)$,

   (6) Final score: $Score=\frac{{{S}_{1}}+{{S}_{2}}+2{{S}_{3}}+2{{S}_{4}}+2{{S}_{5}}}{8}$.

2. If the submission is not in the required format: 0 points.

