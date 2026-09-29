question 1:
The registered model was given a version number, such as Version 1, while the logged model belongs to one run and the registered model is managed separately in the Model Registry.
question 2:
MLflow now uses aliases like champion instead of old stages, and aliases are useful because they can be moved to another model version easily.
question 3:
Using models:/food11@champion avoids hardcoding a model file, and to serve a newer model I only need to move the champion alias.
question 4:
Copying pyproject.toml and uv.lock first lets Docker cache dependencies, so changing only serve.py does not reinstall everything.
question 5:
The multi-stage image is smaller because unnecessary build tools are left out, and the biggest layers are usually the Python and ML dependencies.
question 6:
Without .dockerignore, Docker sends unnecessary files like the dataset and .venv, which makes builds slower and larger.
question 7:
127.0.0.1 inside Docker refers to the container itself, while host.docker.internal lets the container reach the host machine.
question 8:
Yes, a new container can use the same image without rebuilding because the app is already in the image and the model is loaded from MLflow at runtime.