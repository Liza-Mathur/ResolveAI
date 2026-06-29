from tools.order_lookup import get_order_details, find_orders_by_customer
import json

result = get_order_details("ORD1001")
print(json.dumps(result, indent=2, default=str))

# test by customer_id
result1 = find_orders_by_customer(customer_id="C001")
print("By customer_id:")
print(json.dumps(result1, indent=2, default=str))

print()

# test by name
result2 = find_orders_by_customer(name="Aarav Mehta")
print("By name:")
print(json.dumps(result2, indent=2, default=str))