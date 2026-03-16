
# A/B Testing Experiment Analysis

## Goal
Evaluate whether product version B improves conversion compared to version A.

## Tasks
1. Calculate conversion rate per variant.
2. Compute uplift.
3. Perform statistical significance testing using Python.

## Example Python
import pandas as pd

df = pd.read_csv("ab_test_data.csv")
conversion = df.groupby("variant")["converted"].mean()
print(conversion)

## Skills Demonstrated
- Experiment Analysis
- Statistical Testing
- Product Metrics
