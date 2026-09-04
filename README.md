# CartIQ

CartIQ is an offline product-recommendation project for grocery and quick-commerce baskets. It learns which products a customer is likely to add next, using their purchase history, current cart size, and order context. The intended product surface is a focused add-to-cart suggestion—not a broad, generic recommendation carousel.

> Project status: this repository contains the data-preparation and offline-modeling workflow. It does **not** yet contain a deployed API, frontend, real-time feature store, or A/B-test results.

![CartIQ pipeline](docs/screenshots/data-pipeline.png)

## Problem and scope

Small baskets often have limited margin. A relevant suggestion can increase basket value, but irrelevant suggestions add friction and may increase abandonment. CartIQ addresses the ranking problem: from a manageable set of eligible products, rank products that are most likely to be added later in the same order.

In scope:

- Build product-level prior and train-order tables from Instacart data.
- Derive user, user-product, cart-state, product, and order-context features.
- Generate candidates from a customer's product history and globally popular products.
- Train a LightGBM binary classifier and evaluate order-level top-10 rankings.

Out of scope:

- Proving incremental revenue, conversion lift, or reduced abandonment.
- Serving recommendations in production.
- Real-time inventory, price, margin, or promotion-aware ranking.

An online experiment is required before claiming business impact. Offline ranking metrics measure how well the model recovers products later added to the basket; they do not establish that showing a recommendation caused a purchase.

## How it works

1. `notebooks/preprocessing.ipynb` joins order timing, basket, product, and department data, then writes product-level prior and train-order tables.
2. `notebooks/model_data_prep.ipynb` creates customer features, customer-product history, partial-cart states, candidate products, labels, and the final Parquet training table.
3. `notebooks/model.ipynb` splits on unique `order_id` values, trains LightGBM, scores validation candidates, and reports Precision@10 and Recall@10.

For each train order, the notebook creates a partial cart from the first half of the basket. Products in the remaining half are positive targets. Candidates are the customer's historical products (up to 30) plus globally popular products (up to 20), after removing products already in the cart.

## Data source

The data is the [Instacart Market Basket Analysis dataset](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis). Large data files are intentionally ignored by Git, so download them separately and place the renamed CSVs under `data/raw/`.

| Local file | Purpose |
| --- | --- |
| `fact_orders_timing.csv` | Order, customer, day, hour, and time-since-prior-order context |
| `fact_orders_basket_prior.csv` | Products in historical (`prior`) orders |
| `fact_orders_basket_train.csv` | Products in labeled `train` orders |
| `dim_products.csv` | Product name, aisle, and department key |
| `dim_departments.csv` | Department labels |

The current raw dataset contains 3.42M order records, 32.43M prior basket rows, 1.38M train basket rows, 49,688 products, and 21 departments.

## Data and model snapshot

![Training dataset snapshot](docs/screenshots/dataset-snapshot.png)

The generated `model_data.parquet` in this checkout has 5,334,991 candidate rows across 124,364 train orders. It has 23 columns and no missing values after feature preparation. The positive class rate is 3.95%, so evaluation should be interpreted with that imbalance in mind.

### Model features

| Feature group | Included signals |
| --- | --- |
| Order context | order number, day of week, hour, days since prior order, partial-cart size |
| Customer profile | total prior orders, average basket size, average reorder interval, average order hour |
| Customer-product history | prior orders, reorders, first/last order, reorder rate, bought-before flags |
| Product metadata | product ID, aisle ID, department ID |

## Offline evaluation

![Offline evaluation snapshot](docs/screenshots/model-evaluation.png)

The saved output in `notebooks/model.ipynb` reports:

| Metric | Result | Meaning |
| --- | ---: | --- |
| Precision@5 | 20.67% | On average, about 1.07 of the ten highest-ranked candidates was purchased later. |
| Recall@10 | 63.65% | The top ten captured about 63.65% of the products later added from the evaluated candidate set. |

These figures are offline ranking results from the notebook's order-level validation split. They are not a business-impact metric and should be recomputed after any data, candidate-generation, feature, or model change.

## Repository layout

```text
CartIQ/
├── data/
│   ├── raw/                         # Downloaded Instacart inputs (Git-ignored)
│   └── processed/                   # Generated tables and model dataset (Git-ignored)
├── docs/screenshots/                # README pipeline, dataset, and evaluation snapshots
├── notebooks/
│   ├── preprocessing.ipynb          # Raw tables → order-product tables
│   ├── model_data_prep.ipynb        # Features, cart states, candidates → model_data.parquet
│   └── model.ipynb                  # LightGBM training and Precision@10/Recall@10
├── reports/
│   └── model_evaluation.md          # Reserved for a standalone evaluation report
├── src/
│   ├── preprocessing/base_layer.py  # Association-rule exploration utility
│   ├── ft_split.py                  # Earlier feature-split experiment
│   └── train_model.py               # Earlier LightGBM experiment
├── requirements.txt
└── README.md
```

The notebooks are the current end-to-end workflow. The Python files under `src/ft_split.py`, `src/train_model.py`, and `src/preprocessing/base_layer.py` are earlier exploratory work and are not the path used to create the checked-in processed artifacts.

## Run the workflow

### Prerequisites

- Python 3.10+
- Jupyter Notebook or JupyterLab
- Sufficient local storage for the raw and processed data (the processed files are several GB)
- At least 16 GB RAM is recommended: the prior-order table alone was recorded at about 4.5 GB in memory during preparation

### Setup

```bash
git clone <your-repository-url>
cd CartIQ
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install jupyter
```

Download the Instacart files, rename them to the local filenames in the [data source table](#data-source), and put them in `data/raw/`.

The notebooks currently use an absolute path to this author's checkout. Before executing them in another clone, replace:

```text
/Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ
```

with your local repository path.

### Execute in order

```bash
jupyter notebook
```

Then use **Run All** in this sequence:

1. `notebooks/preprocessing.ipynb`
2. `notebooks/model_data_prep.ipynb`
3. `notebooks/model.ipynb`

Expected generated artifacts:

| Step | Key outputs |
| --- | --- |
| Preprocessing | `order_product_data_prior.csv`, `order_product_data_train.csv` |
| Feature and candidate preparation | `user_orders.csv`, `user_features.csv`, `user_product_history.pkl`, `training_states.pkl`, `order_training_states.pkl`, `model_data.parquet` |
| Modeling | LightGBM training output plus Precision@10 and Recall@10 in the notebook |

## Next steps

1. Move the notebook logic into parameterized, repo-relative scripts for repeatable runs.
2. Save the trained model and add a small inference function that accepts cart and customer context.
3. Add catalog, availability, price, margin, and policy filters before recommendation display.
4. Run an A/B test with attach rate, conversion, average order value, margin, and abandonment as metrics.

## Tech stack

- Python, pandas, and PyArrow for data preparation and Parquet storage
- scikit-learn for the order-level validation split
- LightGBM for binary ranking scores
- mlxtend for the retained association-rule exploration utility

## License and attribution

This repository uses the Instacart Market Basket Analysis data for project and modeling purposes. Review and comply with the dataset's [Kaggle terms and license](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) before redistributing data or using it beyond that scope.
