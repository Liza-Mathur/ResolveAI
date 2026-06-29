from mcp.server.fastmcp import FastMCP
from tools.order_lookup import get_order_details, find_orders_by_customer
from tools.policy_search import search_policy

mcp = FastMCP("resolveai-tools")

@mcp.tool()
def get_order_details_tool(order_id: str) -> dict:
    """Fetch order details by order_id, enriched with customer and product info."""
    return get_order_details(order_id)

@mcp.tool()
def find_orders_by_customer_tool(customer_id: str = None, name: str = None) -> list:
    """Find orders for a customer when order_id is unknown. Provide either customer_id or name."""
    return find_orders_by_customer(customer_id=customer_id, name=name)

@mcp.tool()
def search_policy_tool(query: str, source_filter: str = None, k: int = 3) -> list:
    """
    Search Stryde policy documents (returns, warranty, shipping policies) for relevant information.
    Optional source_filter: 'returns_policy.md', 'warranty_policy.md', or 'shipping_policy.md'.
    """
    return search_policy(query, source_filter=source_filter, k=k)

if __name__ == "__main__":
    mcp.run()