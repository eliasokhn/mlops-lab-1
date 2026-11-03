# Lab 4 answers

1. Without a volume, data survives stopping and starting the same container, but removing that container loses its database and artifacts. A new container has an empty registry.
2. A named volume is managed by Docker and independent of the checkout and host path. A bind mount also persists data, but requires choosing a host path and handling permissions.
3. Compose puts these services on the same network and provides DNS entries matching their service names.
4. An environment variable lets the same frontend image work inside Compose and in standalone/local deployments.
5. Only MLflow (5000) and the frontend (8501) publish ports. The frontend's Python process reaches inference on the internal network at `inference:8000`.
6. Loading before MLflow is ready fails startup and exits inference. This implementation waits for MLflow's healthcheck and restarts inference on failure. A missing model/alias must still be registered before inference can load it.
7. Verified on the running stack: only localhost ports 5000 and 8501 are published. Inference has internal port 8000 only.
8. The old model remains in memory until `docker compose restart inference`. The existing project uses the `champion` alias; set `MODEL_URI=models:/food11/Staging` if demonstrating the lab's Staging stage.
9. The image contains inference code and dependencies; the selected registry model is downloaded at startup, so changing an alias needs no image rebuild.
10. `down` preserves the named volume, including registry assignments. `down -v` deletes that volume and loses this stack's database and artifacts. Do not use `-v` for routine shutdown.
11. Multiple replicas need routing/load balancing; machine failure recovery needs multi-host scheduling and replicated/external storage. A production MLflow service would normally use an external database and durable object storage. Compose alone does not provide multi-host failover.

## Verification results

All three images built. A real browser upload predicted Bread (99.1%); see `frontend-prediction.jpg`. Before restart, moving Staging from version 1 to version 3 kept the old loaded model ID and 72.72% bread confidence. After restart, the loaded model ID changed and confidence became 99.08%.

Versions 1, 2, 3 and champion version 3 survived `docker compose down` followed by `up`, and inference still produced a prediction. Evidence: `compose-results.json`.

The destructive experiment used a separate disposable Compose project, preserving the real trained models. Its registered model survived `down`/`up` and disappeared after `down -v`/`up`; see `volume-experiment.json`.
