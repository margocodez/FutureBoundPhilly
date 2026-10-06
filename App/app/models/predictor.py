import os
from dataclasses import asdict

import joblib
import pandas as pd
import torch

from app.models.melt_risk_net import MeltRiskNet

SCALED_FEATURES = ["cumulative_gpa", "ela_sbac_sd_units", "math_sbac_sd_units"]

# Model A uses all features; Model B excludes demographics and intended_college_type.
MODEL_SPECS = {
    "A": {"weights": "model_A_final.pt", "scaler": "model_A_scaler.pkl",
          "features": "model_A_feature_order.pkl", "hidden": (30, 25)},
    "B": {"weights": "model_B_final.pt", "scaler": "model_B_scaler.pkl",
          "features": "model_B_feature_order.pkl", "hidden": (16, 10)},
}


def risk_category(score):
    if score >= 67:
        return "red"
    if score >= 34:
        return "yellow"
    return "green"


class MeltPredictor:
    def __init__(self, artifact_dir, model_key):
        spec = MODEL_SPECS[model_key]
        self.model_key = model_key
        self.scaler = joblib.load(os.path.join(artifact_dir, spec["scaler"]))
        self.feature_order = joblib.load(os.path.join(artifact_dir, spec["features"]))

        self.net = MeltRiskNet(len(self.feature_order), *spec["hidden"])
        self.net.load_state_dict(torch.load(os.path.join(artifact_dir, spec["weights"])))
        self.net.eval()

    def predict(self, student):
        row = pd.DataFrame([asdict(student)])[self.feature_order]
        row[SCALED_FEATURES] = self.scaler.transform(row[SCALED_FEATURES])

        with torch.no_grad():
            logit = self.net(torch.tensor(row.values, dtype=torch.float32))
        probability = torch.sigmoid(logit).item()
        score = round(probability * 100)

        return {
            "model": self.model_key,
            "probability": probability,
            "risk_score": score,
            "risk_category": risk_category(score),
        }


_predictors = {}


def get_predictor(artifact_dir, model_key):
    """Load each model once and reuse it across requests."""
    if model_key not in _predictors:
        _predictors[model_key] = MeltPredictor(artifact_dir, model_key)
    return _predictors[model_key]
