# CartIQ
The logistics problem every e-commerce and quick commerce company faces. Whenever the order basket is small the profit margin are razor thin and company losses its profit or get to break even situation. The company only becomes profitable when the order basket is above an average value threshold.

Even though the algorithm "Frequently Bought Together or Earlier Bought" is there to increase the cart value, but forcing the user to scroll through carousels of irrelevant product creates a decision fatigue and increase cart abandonment rates.

## Simple solution 
A hyper-relevant one click dynamic bundle at the exact moment of purchase. Instead of just what product are bought together the system understand when and why they are bought together. 

## The three layer solution

1. **Base layer:-** Calculates the absolute mathematical probability that two items belong together. Using mlxtend (a library in python). Will be calculating Support, Confidence and Lift metrics.
2. **Intelligent Layer:-** Storing those mathematical pairs against real-time constraints, like time of the day, day of the week or current cart size. Serving the single optimal bundle.
3. **UX Layer:-** A frictionless, zero-distraction user interface that presents the bundle clearly without interrupting the checkout flow.

