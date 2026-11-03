import io
import os
from contextlib import asynccontextmanager
from typing import Annotated

import mlflow
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

# MLflow tracking server
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


model = None


# Food-11 categories
CATEGORIES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


# Same preprocessing used during training
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


@asynccontextmanager
async def lifespan(app):
    global model
    model = None
    if not os.environ.get("SKIP_MODEL"):
        model = mlflow.pyfunc.load_model(
            os.getenv("MODEL_URI", "models:/food11@champion"),
            model_config={"device": "cpu"},
        )
    yield
    model = None


app = FastAPI(lifespan=lifespan)



@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_uuid": getattr(getattr(model, "metadata", None), "model_uuid", None),
    }


@app.post("/predict")
async def predict(file: Annotated[UploadFile, File()]):

    if model is None:
        raise HTTPException(503, "Model is not loaded")

    image_bytes = await file.read()

    try:
        with Image.open(io.BytesIO(image_bytes)) as uploaded:
            image = uploaded.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(400, "Upload a valid image") from exc

    image_tensor = transform(image)

    # Add batch dimension:
    # [3, 128, 128] -> [1, 3, 128, 128]
    batch = image_tensor.unsqueeze(0).numpy()

    predictions = model.predict(batch)

    logits = np.asarray(predictions)[0]

    # Softmax -> probabilities
    exp_logits = np.exp(logits - np.max(logits))
    probabilities = exp_logits / exp_logits.sum()

    predicted_index = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_index])

    return {
        "category": CATEGORIES[predicted_index],
        "confidence": confidence
    }
