import argparse
import math
import os

from mlflow import MlflowClient


def promote(client, name, version, n, metric="test_accuracy"):
    if n <= 0:
        raise ValueError("Test-set size must be positive")
    candidate = client.get_model_version(name, version)
    champion = client.get_model_version_by_alias(name, "champion")
    if str(candidate.version) == str(champion.version):
        raise ValueError("Candidate is already champion")
    a = client.get_run(candidate.run_id).data.metrics[metric]
    p = client.get_run(champion.run_id).data.metrics[metric]
    if not all(math.isfinite(x) and 0 <= x <= 1 for x in (a, p)):
        raise ValueError("Accuracies must be finite and between 0 and 1")
    margin = 2 * math.sqrt(p * (1 - p) / n)
    decision = "champion" if a >= p + margin else "challenger"
    tags = {"gate.decision": decision, "gate.candidate_accuracy": a,
            "gate.champion_accuracy": p, "gate.margin": margin,
            "gate.test_size": n, "gate.previous_champion": champion.version}
    for key, value in tags.items():
        client.set_model_version_tag(name, version, key, str(value))
    client.set_registered_model_alias(name, decision, version)
    print(f"{decision}: candidate={a:.6f}, champion={p:.6f}, "
          f"2*se={margin:.6f} ({100 * margin:.2f} percentage points), n={n}")
    return decision


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--name", default="food11")
    parser.add_argument("--test-size", required=True, type=int)
    parser.add_argument("--metric", default="test_accuracy")
    args = parser.parse_args()
    promote(MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")),
            args.name, args.version, args.test_size, args.metric)
