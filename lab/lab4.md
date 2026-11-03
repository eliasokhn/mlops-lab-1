# Lab 4 answers

1. Without a volume, data survives stopping and starting the same container, but removing that container loses its database and artifacts. A new container has an empty registry.
2. A named volume is managed by Docker and independent of the checkout and host path. A bind mount also persists data, but requires choosing a host path and handling permissions.
3. Compose puts these services on the same network and provides DNS entries matching their service names.
4. An environment variable lets the same frontend image work inside Compose and in standalone/local deployments.
5. Only MLflow (5000) and the frontend (8501) publish ports. The frontend's Python process reaches inference on the internal network at `inference:8000`.
6. Loading before MLflow is ready fails startup and exits inference. This implementation waits for MLflow's healthcheck and restarts inference on failure. A missing model/alias must still be registered before inference can load it.
7. Expected configuration: localhost ports 5000 and 8501 are published; inference has only internal port 8000. Actual `docker compose ps` evidence requires the Docker engine to be running.
8. The old model remains in memory until `docker compose restart inference`. The existing project uses the `champion` alias; set `MODEL_URI=models:/food11/Staging` if demonstrating the lab's Staging stage.
9. The image contains inference code and dependencies; the selected registry model is downloaded at startup, so changing an alias needs no image rebuild.
10. `down` preserves the named volume, including registry assignments. `down -v` deletes that volume and loses this stack's database and artifacts. Do not use `-v` for routine shutdown.
11. Multiple replicas need routing/load balancing; machine failure recovery needs multi-host scheduling and replicated/external storage. A production MLflow service would normally use an external database and durable object storage. Compose alone does not provide multi-host failover.

## Verification status

Compose configuration validates locally. Docker Desktop was started and image builds were launched, but dependency downloads are slow. Prediction uploads, alias reload and volume persistence remain to be exercised once the builds finish; no observations for those experiments are invented here. Follow the root README.
