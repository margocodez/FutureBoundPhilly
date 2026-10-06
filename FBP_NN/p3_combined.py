#p3 Model A
#pandas to clean dataset
import pandas as pd
#to standardize the numerical features
from sklearn.preprocessing import StandardScaler
#splitting the dataset in a 70/15/15 split
from sklearn.model_selection import train_test_split
#pytorch
import torch
import torch.nn as nn

df = pd.read_csv("summer_melt_combined_100k_B.csv")

print(df["summer_melt"].value_counts())

#separate data frameworks that contain the input values to the nn and the melt outcomes that the nn should be able to identify
input_df = df.drop(columns=[
    # the usual non-feature columns
    "true_melt_probability", "student_id", "summer_melt", "risk_score", "risk_category",
    # the new dynamic-target columns (these belong to Model B's target, not Model A's inputs)
    "dynamic_risk_probability", "dynamic_melt_label", "dynamic_risk_score", "dynamic_risk_category",
])

#target melt values
melt=df["summer_melt"]

#these are the features that need to be standardized because they are on a scale that the ML model can work with more effectively
scaled_features = [
    "cumulative_gpa",
    "ela_sbac_sd_units",
    "math_sbac_sd_units",
]

#split the dataset (input_df) into training and temporary --> which will then be split into testing and validating

input_train, input_temporary, melt_train, melt_temporary = train_test_split(
    input_df,
    melt,
    test_size=0.30,
    random_state=42,
    stratify=melt
    )

#split input_temporary and melt_temporary into testing and validating datasets

input_valid, input_test, melt_valid, melt_test = train_test_split(
    input_temporary,
    melt_temporary,
    test_size=0.50,
    random_state=42,
    stratify=melt_temporary
)

#standardize the features

scaler = StandardScaler() #uses the specific scaling tool from scikit-learn

#fit the scaler for the training data
input_train[scaled_features] = scaler.fit_transform(input_train[scaled_features])

#use training scaler for validation + testing
input_valid[scaled_features] = scaler.transform(input_valid[scaled_features])
input_test[scaled_features] = scaler.transform(input_test[scaled_features])

#CONVERT DATA TO TENSORS

#convert features to tensors
X_train = torch.tensor(input_train.values, dtype=torch.float32)
X_valid = torch.tensor(input_valid.values, dtype=torch.float32)
X_test = torch.tensor(input_test.values, dtype=torch.float32)

#convert labels to tensors
y_train = torch.tensor(melt_train.values, dtype = torch.float32).reshape(-1, 1)
y_valid = torch.tensor(melt_valid.values, dtype = torch.float32).reshape(-1, 1)
y_test = torch.tensor(melt_test.values, dtype = torch.float32).reshape(-1, 1)

print(X_train.shape, y_train.shape)

#BUILDING NETOWRK ARCHITECTURE

class MeltRiskNet(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.layer1 = nn.Linear(input_size, 30)   # 21 inputs -> 16 neurons
        self.relu1 = nn.ReLU()
        self.layer2 = nn.Linear(30, 25)          # what should this be?
        self.relu2 = nn.ReLU()
        self.layer3 = nn.Linear(25, 1)           # and this?
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.layer2(x)          # apply layer2
        x = self.relu2(x)           # apply relu2
        x = self.layer3(x)          # apply layer3
        return x

#MODEL TRAINING

model = MeltRiskNet(input_size=23)

#makes it so the model treats mistakes for the minority class as more costly
n_no_melt = (melt_train == 0).sum()
n_melt = (melt_train == 1).sum()
pos_weight_value = n_no_melt / n_melt
print(pos_weight_value)

#loss optimizer
pos_weight_tensor = torch.tensor([pos_weight_value])
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

EPOCHS = 200
best_val_loss = float("inf")
best_epoch = 0
patience = 20
epochs_no_improve = 0

for epoch in range(EPOCHS):
    # --- Training phase ---
    model.train()                    # tells PyTorch we're in training mode

    optimizer.zero_grad()                  # (1) what needs to happen to gradients
                                      #     before each new forward pass?

    outputs = model(X_train)             # (2) forward pass — which tensor goes in?

    loss = criterion(outputs, y_train)   # (3) compare predictions to what?

    loss.backward()                       # (4) compute gradients — which method
                                      #     does that in PyTorch?

    optimizer.step()                  # (5) actually update the weights

    # --- Validation phase (no training happening here) ---
    
    model.eval()
    with torch.no_grad():
        val_outputs = model(X_valid)
        val_loss = criterion(val_outputs, y_valid)

    if val_loss.item() < best_val_loss:
        best_val_loss = val_loss.item()
        best_epoch = epoch
        epochs_no_improve = 0
        torch.save(model.state_dict(), "best_model3.pt")   # save the best version
    else:
        epochs_no_improve += 1

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: train_loss={loss.item():.4f}, val_loss={val_loss.item():.4f}")

    if epochs_no_improve >= patience:
        print(f"Stopping early at epoch {epoch}. Best epoch was {best_epoch} with val_loss={best_val_loss:.4f}")
        break

#TESTING AND ADJUSTING
model.eval()
with torch.no_grad():
    test_logits = model(X_test)
    test_probs = torch.sigmoid(test_logits)       # convert logits -> actual probabilities (0 to 1)
    test_preds = (test_probs >= 0.5).float()       # convert probabilities -> 0/1 predictions

accuracy = (test_preds == y_test).float().mean()
print(f"Test accuracy: {accuracy.item():.4f}")

from sklearn.metrics import confusion_matrix, classification_report

y_test_np = y_test.numpy()
test_preds_np = test_preds.numpy()

print(confusion_matrix(y_test_np, test_preds_np))
print(classification_report(y_test_np, test_preds_np, target_names=["no_melt", "melt"]))

from sklearn.metrics import roc_auc_score

test_probs_np = test_probs.numpy()
auc = roc_auc_score(y_test_np, test_probs_np)
print(f"Test AUC: {auc:.4f}")

from sklearn.metrics import precision_recall_curve
import numpy as np

precisions, recalls, thresholds = precision_recall_curve(y_test_np, test_probs_np)

for p, r, t in zip(precisions[::20], recalls[::20], np.append(thresholds[::20], None)):
    print(f"threshold={t}, precision={p:.3f}, recall={r:.3f}")

from sklearn.metrics import roc_auc_score
import numpy as np

baseline_auc = roc_auc_score(y_test_np, test_probs_np)
print(f"Baseline AUC: {baseline_auc:.4f}\n")

feature_names = input_test.columns.tolist()

for i, name in enumerate(feature_names):
    X_test_shuffled = X_test.clone()
    perm = torch.randperm(X_test_shuffled.shape[0])
    X_test_shuffled[:, i] = X_test_shuffled[perm, i]

    with torch.no_grad():
        shuffled_logits = model(X_test_shuffled)
        shuffled_probs = torch.sigmoid(shuffled_logits).numpy()

    shuffled_auc = roc_auc_score(y_test_np, shuffled_probs)
    drop = baseline_auc - shuffled_auc
    print(f"{name}: AUC drop = {drop:.4f}")

print("Training:", input_train.shape)
print("Validation:", input_valid.shape)
print("Testing:", input_test.shape)
