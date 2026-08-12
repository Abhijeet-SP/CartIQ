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
Lift and the LightGBM ranking identify which bundles are statistically worth testing. They cannot prove the recommendation causes incremental revenue — for that, we'd need an A/B test comparing customers who see the suggestion against those who don't, because a high co-occurrence in past data could simply reflect existing behaviour rather than an effect of the recommendation itself.

#### PRD will be delivered, explaining the real world problem of implementing the feature.

