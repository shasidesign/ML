import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load dataset
data = pd.read_csv('dataset/clothing_data.csv')

# Convert text data into numbers
gender_encoder = LabelEncoder()
body_encoder = LabelEncoder()
size_encoder = LabelEncoder()

data['Gender'] = gender_encoder.fit_transform(data['Gender'])
data['BodyType'] = body_encoder.fit_transform(data['BodyType'])
data['Size'] = size_encoder.fit_transform(data['Size'])

# Inputs
X = data[['Height', 'Weight', 'Age', 'Gender', 'BodyType']]

# Output
y = data['Size']

# Create model
model = DecisionTreeClassifier()

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, 'model/size_model.pkl')
joblib.dump(gender_encoder, 'model/gender_encoder.pkl')
joblib.dump(body_encoder, 'model/body_encoder.pkl')
joblib.dump(size_encoder, 'model/size_encoder.pkl')

print('Model trained successfully')