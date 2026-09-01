import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

def generate_association_rules(orders):

    transactions = (
        orders
        .groupby("order_id")["product_name"]
        .apply(list)
        .tolist()
    )

    te = TransactionEncoder()

    encoded = te.fit(transactions).transform(transactions)

    basket = pd.DataFrame(
        encoded,
        columns=te.columns_
    )

    frequent_items = apriori(
        basket,
        min_support=0.0005,
        use_colnames=True
    )

    rules = association_rules(
        frequent_items,
        metric="confidence",
        min_threshold=0.05
    )

    # keep only 1 -> 1 rules; downstream joins a single cart product to a single
    # antecedent, so a multi-item antecedent cannot be checked and would fire wrongly
    rules = rules[
        (rules["antecedents"].map(len) == 1)
        & (rules["consequents"].map(len) == 1)
    ].copy()

    return rules
