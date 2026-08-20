import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit

data_file = Path(__file__).resolve().parent.parent/'data'
training_data = pd.read_csv(data_file / "processed" / "train_order_data.csv")
testing_data = pd.read_csv(data_file / "processed" / "test_order_data.csv")

features = [
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order",
    "order_number",
    "cart_size",
    "trigger_product_id",
    "trigger_reordered",
    "recommended_product_id",
    "recommended_department_id",
    "support",
    "confidence",
    "lift"
    ]

split_column = "order_id"
target = "label"

def features_targets(data):

    X = data[features].copy()
    y = data[target].copy()

    # interpret these values for category (as product 11341 is a product_id)
    categorical_columns = [
        "order_dow",
        "order_hour_of_day",
        "trigger_product_id",
        "recommended_product_id",
        "recommended_department_id",
    ]

    for column in categorical_columns:
        X[column] = X[column].astype("category")

    numeric_columns = [
        "days_since_prior_order",
        "order_number",
        "cart_size",
        "trigger_reordered",
        "support",
        "confidence",
        "lift",
    ]

    for column in numeric_columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    X[numeric_columns] = X[numeric_columns].fillna(0)

    # target
    y = y.astype(int)

    return X, y




