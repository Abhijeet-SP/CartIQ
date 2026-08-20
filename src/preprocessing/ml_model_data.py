import pandas as pd
from pathlib import Path 
from src.preprocessing.base_layer import generate_association_rules
from sklearn.model_selection import GroupShuffleSplit

file_path = Path(__file__).resolve().parent.parent.parent
orders = pd.read_csv(file_path/ "data"/ "processed"/ "master_orders.csv")

splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx =  next(splitter.split(orders, groups=orders["order_id"]))

train_orders = orders.iloc[train_idx].copy()
test_orders = orders.iloc[test_idx].copy()

train_association = generate_association_rules(train_orders)
test_association = generate_association_rules(test_orders)

def ml_model_data_preparation(orders_data, association_matrix):

    association_df = association_matrix[['antecedents', 
                                         'consequents', 
                                         'support', 
                                         'confidence',
                                         'lift']]
    
    # data conversion from frozen set to list for merging
    association_df['antecedents_list'] = association_df['antecedents'].apply(lambda x: next(iter(x)))
    association_df['consequents_list'] = association_df['consequents'].apply(lambda x: next(iter(x)))

    final_dataset = pd.merge(orders_data, association_df, 
                            left_on='product_name', 
                            right_on='antecedents_list', 
                            how='inner')

    # validation columns for history purchase and base layer recommendation matching
    actual_products = orders_data[["order_id", 
                              "product_name", 
                              "add_to_cart_order"]].copy()

    actual_products = actual_products.rename(columns={"product_name": "actual_product_name",
                                                      "add_to_cart_order": "actual_add_to_cart_order"})

    model_df = pd.merge(final_dataset, 
                        actual_products, 
                        left_on=["order_id", "consequents_list"],
                        right_on=["order_id", "actual_product_name"],
                        how="left")

    # lable for the final ml_data based on base layer recommendation and purchase history [target column]
    model_df["label"] = (model_df["actual_add_to_cart_order"] > model_df["add_to_cart_order"]).astype(int)

    # extra table for product restructuring 
    product_t = orders_data[[  "product_name", 
                          "product_id", 
                          "department_id", 
                          "department"]].drop_duplicates("product_id").copy()

    product_t = product_t.rename(
        columns={
            "product_id": "recommended_product_id",
            "product_name": "recommended_product_name",
            "department_id": "recommended_department_id",
            "department": "recommended_department_name"
        }
    )

    ml_data = model_df.merge(
        product_t,
        left_on="consequents_list",
        right_on="recommended_product_name",
        how="left",
        validate="many_to_one"
    )

    # Final ml_dataset_output for ml csv
    final_ml_model_data = ml_data[
        [
            "order_id",
            "order_dow",
            "order_hour_of_day",
            "days_since_prior_order",
            "order_number",
            "add_to_cart_order",
            "product_id",
            "product_name",
            "reordered",
            "recommended_product_id",
            "recommended_product_name",
            "recommended_department_id",
            "recommended_department_name",
            "support",
            "confidence",
            "lift",
            "label"
        ]
    ].copy()

    final_ml_model_data = final_ml_model_data.rename(
        columns={
            "product_id": "trigger_product_id",
            "product_name": "trigger_product_name",
            "add_to_cart_order": "cart_size",
            "reordered" : "trigger_reordered"
        }
    )

    return final_ml_model_data

output_path = file_path/ "data" / "processed" 

train_model_data = ml_model_data_preparation(train_orders, train_association)
test_model_data = ml_model_data_preparation(test_orders, test_association)


train_model_data.to_csv(output_path / "train_order_data.csv", index=False)
test_model_data.to_csv(output_path / "test_order_data.csv", index=False)


print("The output for train_model_data is completed. \n")
print("The output for test_model_data is completed. \n")