from setup_data import load_orders, load_customers, load_products


orders = load_orders()
customers = load_customers()
products = load_products()

def get_order_details(order_id: str) -> dict:
    """
    Fetch order details by order_id, enriched with customer and product info.
    """

    order_row = orders[orders["order_id"] == order_id]

    if order_row.empty:
        return {"error": f"No order found with ID {order_id}"}

    order = order_row.iloc[0].to_dict()

    # enrich with customer info
    customer_row = customers[customers["customer_id"] == order["customer_id"]]
    customer_info = customer_row.iloc[0].to_dict() if not customer_row.empty else {}

    # enrich with product details (order["products"] is a list of dicts with product_id)
    enriched_products = []
    for p in order.get("products", []):
        prod_row = products[products["product_id"] == p["product_id"]]
        if not prod_row.empty:
            prod_data = prod_row.iloc[0].to_dict()
            prod_data["quantity"] = p.get("quantity")
            enriched_products.append(prod_data)

    return {
        "order_id": order["order_id"],
        "delivery_date":order["delivery_date"],
        "order_status": order.get("status"),
        "total_amount": order.get("total_amount"),
        "customer": {
            "customer_id": customer_info.get("customer_id"),
            "name": customer_info.get("name"),
            "loyalty_tier": customer_info.get("loyalty_tier"),
        },
        "products": enriched_products,
    }


def find_orders_by_customer(customer_id: str = None, name: str = None) -> list:
    """
    Find orders for a customer when order_id is unknown.
    Returns a list of candidate orders (summarized) for the agent/LLM to narrow down.
    """

    if not customer_id and name:
        match = customers[customers["name"].str.lower() == name.lower()]
        if match.empty:
            return []
        customer_id = match.iloc[0]["customer_id"]

    if not customer_id:
        return []

    customer_orders = orders[orders["customer_id"] == customer_id]

    if customer_orders.empty:
        return []
    

    # return a lightweight summary list, not full enrichment yet
    candidates = []
    for _, row in customer_orders.iterrows():
        candidates.append({
            "order_id": row["order_id"],
            "total_amount": row.get("total_amount"),
            "products": [
                products[products["product_id"] == p]["name"].values[0]
                for p in [p["product_id"] for p in row.get("products", [])]
            ]
        })

    return candidates