import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn

df = pd.read_csv("summer_melt_combined_100k_B.csv")

input_df = df.drop(columns=[
    "true_melt_probability", "student_id", "summer_melt", "risk_score", "risk_category",
    "dynamic_risk_probability", "dynamic_melt_label", "dynamic_risk_score", "dynamic_risk_category",
    "female", "is_asian", "is_black", "is_hispanic_latine",
    "is_white", "is_multiracial_other", "english_learner_status",
    "special_education_iep", "economically_disadvantaged",
    "intended_college_type",
])
melt = df["dynamic_melt_label"]

scaled_features = ["cumulative_gpa", "ela_sbac_sd_units", "math_sbac_sd_units"]

input_train, input_temporary, melt_train, melt_temporary = train_test_split(
    input_df, melt, test_size=0.30, random_state=42, stratify=melt
)
input_valid, input_test, melt_valid, melt_test = train_test_split(
    input_temporary, melt_temporary, test_size=0.50, random_state=42, stratify=melt_temporary
)

scaler = StandardScaler()
input_train[scaled_features] = scaler.fit_transform(input_train[scaled_features])
input_valid[scaled_features] = scaler.transform(input_valid[scaled_features])
input_test[scaled_features] = scaler.transform(input_test[scaled_features])

joblib.dump(scaler, "model_B_scaler.pkl")
joblib.dump(list(input_df.columns), "model_B_feature_order.pkl")

X_train = torch.tensor(input_train.values, dtype=torch.float32)
X_valid = torch.tensor(input_valid.values, dtype=torch.float32)
y_train = torch.tensor(melt_train.values, dtype=torch.float32).reshape(-1, 1)
y_valid = torch.tensor(melt_valid.values, dtype=torch.float32).reshape(-1, 1)


class MeltRiskNet(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.layer1 = nn.Linear(input_size, 16)
        self.relu1 = nn.ReLU()
        self.layer2 = nn.Linear(16, 10)
        self.relu2 = nn.ReLU()
        self.layer3 = nn.Linear(10, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.layer2(x)
        x = self.relu2(x)
        x = self.layer3(x)
        return x


model = MeltRiskNet(input_size=13)

n_no_melt = (melt_train == 0).sum()
n_melt = (melt_train == 1).sum()
pos_weight_tensor = torch.tensor([n_no_melt / n_melt])
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

EPOCHS = 200
best_val_loss = float("inf")
patience = 20
epochs_no_improve = 0

for epoch in range(EPOCHS):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

    model.eval()
    with torch.no_grad():
        val_loss = criterion(model(X_valid), y_valid)

    if val_loss.item() < best_val_loss:
        best_val_loss = val_loss.item()
        epochs_no_improve = 0
        torch.save(model.state_dict(), "model_B_final.pt")
    else:
        epochs_no_improve += 1

    if epochs_no_improve >= patience:
        print(f"Model B: stopped early at epoch {epoch}, best val_loss={best_val_loss:.4f}")
        break

print("Model B training complete. Saved: model_B_final.pt, model_B_scaler.pkl, model_B_feature_order.pkl")