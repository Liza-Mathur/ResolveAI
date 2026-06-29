import pandas as pd
import json

def load_orders():
    with open("data/orders.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def load_products():
    with open("data/products.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def load_customers():
    with open("data/customers.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))