# CartIQ
The logistics problem every e-commerce and quick commerce company faces. Whenever the order basket is small the profit margin are razor thin and company losses its profit or get to break even situation. The company only becomes profitable when the order basket is above an average value threshold.

Even though the algorithm "Frequently Bought Together or Earlier Bought" is there to increase the cart value, but forcing the user to scroll through carousels of irrelevant product creates a decision fatigue and increase cart abandonment rates.

## Simple solution 
A hyper-relevant one click dynamic bundle at the exact moment of purchase. Instead of just what product are bought together the system understand when and why they are bought together. 

## Data Source

Using the [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) dataset (real order data, not synthetic).

- orders.csv — order metadata + time/day context (order_dow, order_hour_of_day, days_since_prior_order)
- order_products__prior.csv — actual basket contents (core data for the Base Layer's MBA computation)
- products.csv — item names, mapped to product_id
- aisles.csv / departments.csv — optional, for category-level grouping
- order_products__train.csv — not used (belongs to a different Kaggle competition task, not this project's scope)

Sampling down to ~50k–100k orders for tractable local processing.

## The three layer solution
1. **Base layer:-** Calculates the absolute mathematical probability that two items belong together. Using mlxtend (a library in python). Will be calculating Support, Confidence and Lift metrics.
2. **Intelligent Layer:-** Storing those mathematical pairs against real-time constraints, like time of the day, day of the week or current cart size. Serving the single optimal bundle.
3. **Business Layer:-** Deliverable: PRD, but with the honest reasoning chain.
   - Lift/LightGBM = candidate generation and ranking only, not proof of causal impact
   - Proposed A/B test design: treatment (popup shown) vs. control (not shown) comparing attach rate / AOV between groups, since only that separates "would've bought it anyway" from "actually caused by the nudge"
   - Unit economics: per-item margin minus handling cost (the ₹10 − ₹3 = ₹7 logic) weighed against friction/abandonment risk on non-converters.
   - Decision rule: ship only if total gains from conversions outweigh total losses from abandonment — determined by the test, not assumed in advance

## TechStack 
1. Sqlite for Database
2. mlxtend for analysis
3. LightGBM for score and ranking

## Current Problems wrt to ProjectScope
#### All theory problem
Lift and the LightGBM ranking identify which bundles are statistically worth testing. They cannot prove the recommendation causes incremental revenue — for that, we'd need an A/B test comparing customers who see the suggestion against those who don't, because a high co-occurrence in past data could simply reflect existing behaviour rather than an effect of the recommendation itself. **PRD will be delivered, explaining the real world problem of implementing the feature.**

## Phase deliveries
### Phase 1 — Data Engineering

Goal is a populated SQLite database, not just raw CSVs sitting around. Clean tables for orders, order_products, and products, properly joined on order_id and product_id, sampled down to a working size of roughly 50k–100k orders. Sampling is done by user rather than randomly by row, so a user's order history isn't broken mid-sequence, since that sequence matters later for context features like days since prior order. Basic hygiene checks are done and documented, covering nulls, orphaned rows, and reasonable value ranges. The whole pipeline is reproducible through a single script from raw CSV to clean database, not a one-off manual clean.

Ends with a database file, the script that regenerates it, and a Data Architecture Spec describing the schema and sampling rationale.

### Phase 2 — ML Architecture

The Base Layer uses mlxtend to compute Support, Confidence, and Lift across item pairs from the basket data, with a defined and justified minimum threshold so only meaningfully strong pairs are kept. The Intelligent Layer trains a LightGBM model that takes a candidate bundle plus context like day of week, hour, and cart size, and outputs a ranking score. This layer includes an offline evaluation metric such as precision@k, documented clearly as a ranking-quality metric and not a revenue claim, along with a function that given a product in cart plus context returns the single best bundle suggestion.

Ends with a Model Evaluation Report containing real Support, Confidence, and Lift numbers plus offline precision, and a working function that produces one ranked suggestion given an input.

### Phase 3 — Business Layer

This phase isn't code, it's the PRD itself. It covers the problem framing around thin margins and AOV, an honest statement of what the offline system proves versus what it doesn't, a proposed A/B test design covering unit of randomization, treatment versus control, primary and guardrail metrics, and a rough sample size estimate. It also covers the unit economics logic, margin minus handling cost weighed against abandonment risk, generalized as a simple formula, and ends with an explicit decision rule framed as a hypothesis to be tested rather than a claimed result.

Ends with a single PRD file containing those sections, filled in with real numbers pulled from Phase 1 and 2 outputs wherever possible rather than placeholders.

## Project Structure

cartiq/
├── data/
│   ├── raw/                  # original Instacart CSVs
│   └── cartiq.db             # cleaned SQLite database (Phase 1 output)
├── src/
│   ├── build_db.py           # raw CSV → cartiq.db
│   ├── mba.py                # Support/Confidence/Lift computation (Base Layer)
│   ├── train_ranker.py       # LightGBM training (Intelligent Layer)
│   └── suggest.py            # given product_id + context → returns bundle
├── reports/
│   ├── data_architecture_spec.md
│   ├── model_evaluation_report.md
│   └── PRD.md
├── requirements.txt
└── README.md

## How to run

# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the database from raw Instacart CSVs
python src/build_db.py --input data/raw/ --output data/cartiq.db

# 3. Run Market Basket Analysis (Base Layer)
python src/mba.py --db data/cartiq.db --min-support 0.01 --min-lift 1.2

# 4. Train the LightGBM ranker (Intelligent Layer)
python src/train_ranker.py --db data/cartiq.db

# 5. Get a suggestion for a given product
python src/suggest.py --product_id 24852 --hour 18 --dow 5
