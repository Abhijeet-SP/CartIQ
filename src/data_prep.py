from pathlib import Path
import pandas as pd

data_file = Path(__file__).resolve().parent.parent/'data'
print(data_file)

orders = pd.read_csv(data_file/ "raw"/ "orders.csv")
products = pd.read_csv(data_file / "raw"/ "products.csv")
order_product_prior = pd.read_csv(data_file / "raw"/ "order_products_prior.csv")
departments = pd.read_csv(data_file / "raw"/ "departments.csv")

# fixing the seed and size of orders
random_order_id = orders[orders['eval_set'] == 'prior']['order_id'].sample(n=200000, random_state=42)
print("\nData is selected for sample size of 200000 with random_state=42. \n")

# merging preparation
order_data = orders[orders['order_id'].isin(random_order_id)][[ 'order_id', 
                                                                'order_dow',
                                                                'order_hour_of_day', 
                                                                'days_since_prior_order',
                                                                'order_number']]

product_data = products[['product_id', 'product_name', 'department_id']]
print("Data is prepared for merge operation. \n")

#merging operation
merge_on_order_id = pd.merge(order_data, order_product_prior, on='order_id')
merge_on_product_id = pd.merge(merge_on_order_id, product_data, on='product_id')
merge_on_department_id = pd.merge(merge_on_product_id, departments, on='department_id')
print("The data is merged. \n")

# changing days_since_prior_order NaN to -1 for categorization on their first order
merge_on_department_id.loc[merge_on_department_id['days_since_prior_order'].isna(),
                           'days_since_prior_order'] = -1
print("The days_since_prior_order NaN value is changed to -1 for categorisation. \n")

output_path = data_file / "processed" / "master_orders.csv"
merge_on_department_id.to_csv(output_path, index=False)
print("The output for master_orders.csv is completed. \n")
