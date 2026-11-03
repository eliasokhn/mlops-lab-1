# Food-11 MLOps: Labs 4 and 5

Run commands from this repository's root in the VS Code PowerShell terminal.
Dockerfile instructions such as `FROM` and `RUN` belong in files, not in PowerShell.

## Local checks

```powershell
uv sync --frozen
uv run ruff check src tests
uv run pytest -q
uv run python src/food11/validate_data.py data/food11_processed_mini
docker compose config --quiet
```

The current mini dataset has 43 cross-split duplicates, so full validation correctly fails the leakage check. Original DVC data is preserved. A separate cleaned copy is prepared at `data/food11_processed_mini_clean`; it excludes later-split duplicates and keeps the original intact. Reproduce it on a fresh checkout with `uv run python src/food11/clean_data.py data/food11_processed_mini data/food11_processed_mini_clean` (the destination must not exist). The exclusions are recorded inside the cleaned folder. Validator tests demonstrate a clean dataset and deliberate leakage without altering the course data.

## Start Lab 4

Start Docker Desktop and wait for its engine to be ready. Stop any older MLflow server using port 5000 first.

```powershell
docker compose up -d --build mlflow
$env:MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
```

Open MLflow at http://127.0.0.1:5000. This named volume is a NEW registry; the old root `mlflow.db` and `mlruns` are not automatically imported. New experiments use proxied artifact storage, so host training and container inference can both access artifacts.

Validate the cleaned data, then train a baseline:

```powershell
uv run python src/food11/validate_data.py data/food11_processed_mini_clean
# Continue only if every check passes:
uv run python src/food11/train.py --dataset mini --data-dir data/food11_processed_mini_clean --epochs 5 --lr 0.0001
```

Training registers `food11` automatically and logs its model and accuracy in the same run. In the MLflow Models page, assign alias `champion` to the baseline version. Then:

```powershell
docker compose up -d --build
docker compose ps
docker compose logs inference
```

Open http://127.0.0.1:8501 and upload a food image. Inference is private to the Compose network. To follow Lab 4's older Staging convention, move a version to Staging in MLflow, then set `$env:MODEL_URI = 'models:/food11/Staging'` before `docker compose up -d`. The default remains `models:/food11@champion`, matching your existing project and Lab 5.

After changing the selected alias/stage:

```powershell
docker compose restart inference
docker compose down
docker compose up -d
```

The named volume preserves models and registry state. `docker compose down -v` deletes them; use it only for the lab's intentional data-loss experiment after saving needed artifacts.

## Lab 5 promotion and CI

Train two candidate runs with different learning rates after preparing clean data. Read their registered version numbers in MLflow. Use an evaluation size matching the dataset used to measure the champion:

```powershell
$testSize = (Get-ChildItem data/food11_processed_mini_clean/evaluation -Recurse -File | Where-Object { $_.Extension -in '.jpg', '.jpeg', '.png' }).Count
uv run python src/food11/train.py --dataset mini --data-dir data/food11_processed_mini_clean --epochs 5 --lr 0.000001
uv run python src/food11/train.py --dataset mini --data-dir data/food11_processed_mini_clean --epochs 5 --lr 0.0001
# Replace 2 and 3 with your actual candidate versions:
uv run python src/food11/promote.py --version 2 --test-size $testSize
uv run python src/food11/promote.py --version 3 --test-size $testSize
docker compose restart inference
```

Bootstrap the first champion manually. Later promotions require a candidate's `test_accuracy` to exceed the champion by at least two standard errors. Missing metrics or a missing champion cause an error rather than an unsafe promotion. Compare runs on the same evaluation data and size.

`.github/workflows/ci.yml` lints and tests on push/PR, then builds and probes the API with `SKIP_MODEL=1`. On a push to main it publishes `ghcr.io/eliasokhn/mlops-lab-1:<commit-sha>` using `GITHUB_TOKEN`. Linux dependencies use the existing CPU PyTorch index. The real dataset and real model are not needed for CI.

Push your reviewed changes to trigger Actions. In GitHub Settings, add a main branch rule requiring a PR plus the `test` and `smoke` checks. Exercise a failing PR, fix it, and record two run durations. Those remote experiments require repository access and are not implied by local passing tests.

Written answers and the pipeline diagram: [Lab 4](lab/lab4.md), [Lab 5](lab/lab5.md).

Local verification: 14 tests passed; Ruff and Compose configuration checks passed. The full dataset fails its leakage check; [the report](lab/data-validation.txt) lists the 43 duplicate pairs.

Implementation references: [MLflow proxied artifact storage](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/) and [Compose readiness checks](https://docs.docker.com/compose/how-tos/startup-order/).
