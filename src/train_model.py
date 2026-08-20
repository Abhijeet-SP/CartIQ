import lightgbm as lgb
from src.ft_split import (
    features_targets,
    testing_data,
    training_data
)

dataset = features_targets(training_data)
X_train = dataset[0]
y_train = dataset[1]

dataset_02 = features_targets(testing_data)
X_test = dataset_02[0]
y_test = dataset_02[1]
print(f'The dataset is loaded with {X_train.shape[0]} rows and {X_train.shape[1]} columns.')

model = lgb.LGBMClassifier(
    objective="binary",
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42,
)

model.fit(X_train, y_train)
print("Model training completed.")