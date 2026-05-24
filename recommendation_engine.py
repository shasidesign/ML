import pandas as pd

from sklearn.preprocessing import LabelEncoder

from sklearn.neighbors import NearestNeighbors

# LOAD DATASET

data = pd.read_csv(
    'dataset/clothing_data.csv'
)

# ENCODERS

gender_encoder = LabelEncoder()

body_encoder = LabelEncoder()

# ENCODE

data['Gender'] = gender_encoder.fit_transform(
    data['Gender']
)

data['BodyType'] = body_encoder.fit_transform(
    data['BodyType']
)

# FEATURES

X = data[
    ['Height',
     'Weight',
     'Age',
     'Gender',
     'BodyType']
]

# TRAIN KNN

model = NearestNeighbors(n_neighbors=3)

model.fit(X)

# SAMPLE USER

sample = [[170, 65, 21, 1, 2]]

# FIND SIMILAR USERS

distances, indices = model.kneighbors(sample)

print("\nRecommended Styles:\n")

for index in indices[0]:

    print(data.iloc[index]['Style'])