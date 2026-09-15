import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


# --------------------------------------------------
# Command-line arguments
# --------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument(
    "--dataset",
    choices=["processed", "mini"],
    default="mini"
)

parser.add_argument(
    "--epochs",
    type=int,
    default=5
)

parser.add_argument(
    "--lr",
    type=float,
    default=0.001
)

parser.add_argument(
    "--batch-size",
    type=int,
    default=32
)

args = parser.parse_args()


# --------------------------------------------------
# MLflow configuration
# --------------------------------------------------

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("food11")


# --------------------------------------------------
# NVIDIA GPU if available
# --------------------------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# --------------------------------------------------
# Select dataset
# --------------------------------------------------

if args.dataset == "mini":
    data_dir = Path("data/food11_processed_mini")
else:
    data_dir = Path("data/food11_processed")


# --------------------------------------------------
# Image transformations
# --------------------------------------------------

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# Load datasets using ImageFolder
# --------------------------------------------------

train_dataset = datasets.ImageFolder(
    data_dir / "training",
    transform=transform
)

val_dataset = datasets.ImageFolder(
    data_dir / "validation",
    transform=transform
)

test_dataset = datasets.ImageFolder(
    data_dir / "evaluation",
    transform=transform
)


# --------------------------------------------------
# DataLoaders
# --------------------------------------------------

train_loader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=args.batch_size,
    shuffle=False
)

test_loader = DataLoader(
    test_dataset,
    batch_size=args.batch_size,
    shuffle=False
)


# --------------------------------------------------
# Pretrained ResNet-18
# --------------------------------------------------

model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)

# Replace the 1000-class ImageNet output with 11 classes
model.fc = nn.Linear(model.fc.in_features, 11)

model = model.to(device)


# --------------------------------------------------
# Loss and optimizer
# --------------------------------------------------

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=args.lr
)


# --------------------------------------------------
# MLflow run
# --------------------------------------------------

with mlflow.start_run():

    # Log hyperparameters once at the beginning
    mlflow.log_params({
        "dataset": args.dataset,
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "model": "resnet18"
    })


    # --------------------------------------------------
    # Training
    # --------------------------------------------------

    for epoch in range(args.epochs):

        model.train()

        running_train_loss = 0.0

        for images, labels in train_loader:

            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(outputs, labels)

            loss.backward()

            optimizer.step()

            running_train_loss += loss.item() * images.size(0)


        train_loss = running_train_loss / len(train_dataset)


        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        model.eval()

        running_val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():

            for images, labels in val_loader:

                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)

                loss = criterion(outputs, labels)

                running_val_loss += loss.item() * images.size(0)

                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)

                correct += (predicted == labels).sum().item()


        val_loss = running_val_loss / len(val_dataset)
        val_accuracy = correct / total


        # Log metrics after every epoch
        mlflow.log_metric(
            "train_loss",
            train_loss,
            step=epoch
        )

        mlflow.log_metric(
            "val_loss",
            val_loss,
            step=epoch
        )

        mlflow.log_metric(
            "val_accuracy",
            val_accuracy,
            step=epoch
        )


        print(
            f"Epoch {epoch + 1}/{args.epochs} - "
            f"Train Loss: {train_loss:.4f} - "
            f"Val Loss: {val_loss:.4f} - "
            f"Val Accuracy: {val_accuracy:.4f}"
        )


    # --------------------------------------------------
    # Final evaluation
    # --------------------------------------------------

    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in test_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)

            correct += (predicted == labels).sum().item()


    test_accuracy = correct / total

    mlflow.log_metric(
        "test_accuracy",
        test_accuracy
    )

    print(f"Final Test Accuracy: {test_accuracy:.4f}")


    # --------------------------------------------------
    # Log trained model to MLflow
    # --------------------------------------------------

    mlflow.pytorch.log_model(
        model,
        "model"
    )