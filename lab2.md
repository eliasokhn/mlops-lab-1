question 1:
pyproject.toml was updated to include the new direct dependencies required for training and experiment tracking: MLflow, PyTorch, torchvision, and scikit-learn. uv.lock was also updated with the exact resolved versions of these packages and their transitive dependencies. pyproject.toml describes what the project depends on, while uv.lock locks the exact dependency versions to make the environment reproducible.
question 2:
--backend-store-uri is where MLFlow stores all expirements
--default-artifact-root defines where MLflow stores larger files produced by runs

question 3:
mlflow.db and mlruns/ are locally run and generated from the output so they can change frequently its is better not to store them in git

question4:
The first time mlflow.set_experiment("food11") is called, MLflow checks whether an experiment with that name exists. If it does not, MLflow automatically creates it. The training run is then recorded under the new food11 experiment, which becomes visible in the MLflow UI.

question 5:
mlflow.log_param records a parameter that is fixed for the entire run, such as the learning rate, batch size, number of epochs, or model architecture.

mlflow.log_metric records a value produced during training, such as training loss, validation loss, or validation accuracy. Metrics can change throughout the run.

log_metric takes a step argument because the same metric can be recorded multiple times, for example once after every epoch. The step identifies which epoch the value belongs to. Parameters do not need a step because they are fixed for the entire run.

here are the results:
              Epoch 1   Epoch 2   Epoch 3   Epoch 4   Epoch 5

train_loss     1.8263    1.1389    0.5993    0.4146    0.3069
val_loss       8.5365    2.0734    1.5713    1.7352    2.4834
val_accuracy   27.74%    46.90%    55.75%    53.38%    50.00%

questrion 6:
In the MLflow UI, the run contains the parameters dataset, epochs, lr, batch_size, and model. The metrics include train_loss, val_loss, val_accuracy, and test_accuracy. The metrics logged after each epoch can be visualized as charts showing their evolution during training. The model is logged as an artifact under model. Since the MLflow server was configured with --default-artifact-root ./mlruns, the model artifacts are stored locally inside the project's mlruns directory.

questio 7:
lr: 0.0001 epoch:5 batch_size: 32.
showed the best results


question 8:
A larger learning rate such as 0.01 makes larger parameter updates, so the model can reduce the loss quickly at the beginning. However, the updates may be too large near a good minimum, causing the optimizer to overshoot or oscillate instead of converging precisely. A smaller learning rate such as 0.001 generally makes more controlled updates and may therefore achieve better final accuracy.

question 9:
With lr=0.1, I would expect training to become unstable and possibly fail to converge. The parameter updates would likely be too large, causing the optimizer to repeatedly overshoot good solutions. The loss could fluctuate significantly or even increase, resulting in poor validation accuracy.