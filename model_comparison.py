import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns   

# LOAD DATASET

data = pd.read_csv(
    'dataset/clothing_data.csv'
)

# ENCODING

gender_encoder = LabelEncoder()

body_encoder = LabelEncoder()

size_encoder = LabelEncoder()

data['Gender'] = gender_encoder.fit_transform(
    data['Gender']
)

data['BodyType'] = body_encoder.fit_transform(
    data['BodyType']
)

data['Size'] = size_encoder.fit_transform(
    data['Size']
)

# FEATURES

X = data[
    ['Height',
     'Weight',
     'Age',
     'Gender',
     'BodyType']
]

# TARGET

y = data['Size']

# SPLIT DATA

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42
)

# MODELS

models = {

    'Decision Tree':
    DecisionTreeClassifier(),

    'Random Forest':
    RandomForestClassifier(),

    'Logistic Regression':
    LogisticRegression(max_iter=1000)
}

# TRAIN + TEST

accuracies = []

model_names = []
best_model = None
best_accuracy = 0
best_predictions = None
for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = name
        best_predictions = predictions

    accuracies.append(accuracy)
    model_names.append(name)

    print(f"{name} Accuracy: {accuracy:.2f}")

# VISUALIZATION

plt.figure(figsize=(8,5))

plt.bar(model_names, accuracies)

plt.xlabel("Models")

plt.ylabel("Accuracy")

plt.title("ML Model Comparison")

plt.ylim(0,1)

plt.savefig("static/model_comparison.png")

plt.show()
# CONFUSION MATRIX

cm = confusion_matrix(
    y_test,
    best_predictions
)

plt.figure(figsize=(6,5))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues'
)

plt.title(
    f'Confusion Matrix - {best_model}'
)

plt.xlabel("Predicted")

plt.ylabel("Actual")

plt.savefig(
    "static/confusion_matrix.png"
)

plt.close()

print(f"\nBest Model: {best_model}")
print(f"Best Accuracy: {best_accuracy:.2f}")