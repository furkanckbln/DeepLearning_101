import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class FraudClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.sequential = nn.Sequential(
            nn.Linear(30, 64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.sequential(x)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = FraudClassifier().to(device)
pth_path = os.path.join(BASE_DIR, "fraud_classifier.pth")
try:
    model.load_state_dict(torch.load(pth_path, map_location=device, weights_only=True))
except TypeError:
    model.load_state_dict(torch.load(pth_path, map_location=device))
model.eval()

df = pd.read_csv(os.path.join(BASE_DIR, "creditcard.csv"))
X = df.drop("Class", axis=1).values
y = df["Class"].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
scaler.fit(X_train)

FEATURES = list(df.drop("Class", axis=1).columns)
fraud_indices = np.where(y_test == 1)[0]
normal_indices = np.where(y_test == 0)[0]

app = FastAPI(title="Fraud Detector API")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


class TransactionData(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float


@app.post("/predict")
def predict(data: TransactionData):
    values = [getattr(data, f) for f in FEATURES]
    arr = np.array(values, dtype=np.float64).reshape(1, -1)
    scaled = scaler.transform(arr)
    tensor = torch.tensor(scaled, dtype=torch.float32).to(device)
    with torch.inference_mode():
        prob = torch.sigmoid(model(tensor)).item()
    return {
        "probability": round(prob, 6),
        "is_fraud": prob >= 0.5,
        "label": "FRAUD" if prob >= 0.5 else "NORMAL",
    }


@app.get("/sample/{label}")
def sample(label: int):
    if label not in (0, 1):
        raise HTTPException(status_code=400, detail="label must be 0 or 1")
    pool = fraud_indices if label == 1 else normal_indices
    idx = int(np.random.choice(pool))
    return {name: float(val) for name, val in zip(FEATURES, X_test[idx])}
