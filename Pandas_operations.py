# Performing some basic pandas operations for the users ans purchases data sets
# Merge with #inner join.

import pandas as pd
users = pd.read_csv ('users.csv')
purchases = pd.read_csv ('purchases.csv')
df = purchases.merge (users, how = "inner", on = "uid")

# 2. How many unique clients are there?
df ["uid"]. nunique ()

# 3. How many unique pricing are there?
df ["price"]. nunique ()

# 4. At what price, how many were sold?
df ["price"]. value_counts ()

# 5. How many sales were there from which country?
df ["country"]. value_counts ()

# 6. How much is the total earned from sales by country?
df.groupby (["country"]). agg (("price": "sum"})

# 7. What are the sales numbers by device types?
#Alternative 1
df ["device"]. value_counts ()

#Alternative 2:
df.groupby ("device"). agg (("price": "count"})

# 8 What are the price averages by country?
df.groupby (["country"]). agg (("price": "mean"})

# 9 What are the price averages by device?
df.groupby (["device"]). agg ({"price": "mean"})

# 10 What are the averages of prices in country-device breakdown?
df.groupby (["country", "device"]). agg ({"price": "mean"})